"""
Flask web application for the Museums Database Querying and Visualisation project.

This file extends the original command-line PostgreSQL project into a web-based
museum management system. It provides:
- searchable and paginated museum list
- museum detail page
- create, update and delete operations for administrators
- Chart.js visualisations
- Leaflet map visualisation using latitude/longitude from dataset/output.tsv
- simple role-based access control: admin / viewer
- recommended database index creation and performance inspection page

Run:
    python app.py
Then open:
    http://127.0.0.1:7860
On AutoDL, open the exposed/custom service port 7860.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db_connector import get_engine

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "output.tsv"

app = Flask(__name__)
app.secret_key = os.getenv("MUSEUM_FLASK_SECRET", "museum-web-secret-change-this")

# Default login values are intentionally simple for a student project demo.
# For deployment, set these by environment variables.
ADMIN_USERNAME = os.getenv("MUSEUM_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("MUSEUM_ADMIN_PASSWORD", "admin123")
VIEWER_USERNAME = os.getenv("MUSEUM_VIEWER_USER", "viewer")

PAGE_SIZE_OPTIONS = [10, 20, 50, 100]
DEFAULT_PAGE_SIZE = 20

SORT_COLUMNS = {
    "museum_id": "m.museum_id",
    "name": "m.name_of_museum",
    "city": "m.village_town_city",
    "region": "m.region_country",
    "size": "m.size",
    "year_opened": "opened_year",
    "accreditation": "a.accreditation",
}

ADVANCED_FILTER_FIELDS = {
    "name": {"label": "Museum name", "sql": "m.name_of_museum", "type": "text"},
    "museum_id": {"label": "Museum ID", "sql": "m.museum_id", "type": "text"},
    "city": {"label": "City", "sql": "m.village_town_city", "type": "text"},
    "region": {"label": "Region", "sql": "m.region_country", "type": "text"},
    "postcode": {"label": "Postcode", "sql": "m.postcode", "type": "text"},
    "address": {"label": "Address", "sql": "m.address_line_1", "type": "text"},
    "size": {"label": "Size", "sql": "m.size", "type": "text"},
    "accreditation": {"label": "Accreditation", "sql": "a.accreditation", "type": "text"},
    "aim_size": {"label": "AIM size", "sql": "aim.aim_size", "type": "text"},
    "admin_area": {"label": "Admin area", "sql": "aa.child_id", "type": "text"},
    "founder": {"label": "Founder", "sql": "m.founder", "type": "text"},
    "opened_year": {"label": "Opened year", "sql": "opened_year", "type": "number"},
}

TEXT_FILTER_OPERATORS = {
    "contains": "contains",
    "equals": "equals",
    "starts_with": "starts with",
}

NUMBER_FILTER_OPERATORS = {
    "equals": "=",
    "gte": ">=",
    "lte": "<=",
}

VISUALISATION_DIMENSIONS = {
    "region": {"label": "Region/country", "sql": "COALESCE(m.region_country, 'Unknown')", "order": "value DESC"},
    "accreditation": {"label": "Accreditation", "sql": "COALESCE(a.accreditation, 'Unknown')", "order": "value DESC"},
    "size": {"label": "Size", "sql": "COALESCE(m.size, 'Unknown')", "order": "value DESC"},
    "aim_size": {"label": "AIM size", "sql": "COALESCE(aim.aim_size, 'Unknown')", "order": "value DESC"},
    "city": {"label": "City", "sql": "COALESCE(m.village_town_city, 'Unknown')", "order": "value DESC"},
    "admin_area": {"label": "Admin area", "sql": "COALESCE(aa.child_id, 'Unknown')", "order": "value DESC"},
    "opened_year": {"label": "Opened year", "sql": "COALESCE(NULLIF(SUBSTRING(COALESCE(m.year_opened, '') FROM '[0-9]{4}'), '')::TEXT, 'Unknown')", "order": "label ASC"},
    "opened_decade": {"label": "Opened decade", "sql": "CASE WHEN NULLIF(SUBSTRING(COALESCE(m.year_opened, '') FROM '[0-9]{4}'), '') IS NULL THEN 'Unknown' ELSE ((NULLIF(SUBSTRING(COALESCE(m.year_opened, '') FROM '[0-9]{4}'), '')::INTEGER / 10) * 10)::TEXT || 's' END", "order": "label ASC"},
}

CHILD_TABLES = [
    "accreditation",
    "aim_size",
    "ace_sizedesignation",
    "areademographics",
    "deprivation_index",
    "domus_subjectmatter",
    "geodemographics",
    "governance",
    "notes",
    "provenance",
    "subject_matter_hierarchy",
    "visitors",
]

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_museums_name_lower ON museums (LOWER(name_of_museum));",
    "CREATE INDEX IF NOT EXISTS idx_museums_region ON museums (region_country);",
    "CREATE INDEX IF NOT EXISTS idx_museums_city ON museums (village_town_city);",
    "CREATE INDEX IF NOT EXISTS idx_museums_size ON museums (size);",
    "CREATE INDEX IF NOT EXISTS idx_accreditation_museum_id ON accreditation (museum_id);",
    "CREATE INDEX IF NOT EXISTS idx_accreditation_status ON accreditation (accreditation);",
    "CREATE INDEX IF NOT EXISTS idx_aim_size_museum_id ON aim_size (museum_id);",
    "CREATE INDEX IF NOT EXISTS idx_visitors_museum_id ON visitors (museum_id);",
    "CREATE INDEX IF NOT EXISTS idx_adminarea_child_id ON adminarea (child_id);",
]


def get_db():
    """Return a SQLAlchemy engine configured by db_connector.py."""
    return get_engine()


def current_role() -> str:
    return session.get("role", "viewer")


def is_admin() -> bool:
    return current_role() == "admin"


@app.context_processor
def inject_global_template_values():
    return {
        "current_role": current_role(),
        "is_admin": is_admin(),
    }


def require_admin():
    if not is_admin():
        flash("Admin access is required for this operation.", "warning")
        return redirect(url_for("login"))
    return None


def parse_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def make_year_range(year: Optional[str]) -> Optional[str]:
    """Convert a single year into the same string style used by the original project."""
    year = clean_text(year)
    if not year:
        return None
    if not re.fullmatch(r"\d{4}", year):
        raise ValueError("Year must be a four-digit value, for example 2001.")
    return f"[{year},{year})"


def get_opened_year_sql(alias: str = "m") -> str:
    """Extract the first four-digit year from the stored year_opened string."""
    return f"NULLIF(SUBSTRING(COALESCE({alias}.year_opened, '') FROM '[0-9]{{4}}'), '')::INTEGER"


def row_to_dict(row: Any) -> Dict[str, Any]:
    return dict(row._mapping)


def execute_scalar(sql: str, params: Optional[Dict[str, Any]] = None) -> Any:
    with get_db().connect() as conn:
        return conn.execute(text(sql), params or {}).scalar()


def fetch_all(sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    with get_db().connect() as conn:
        rows = conn.execute(text(sql), params or {}).fetchall()
    return [row_to_dict(row) for row in rows]


def fetch_one(sql: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    with get_db().connect() as conn:
        row = conn.execute(text(sql), params or {}).fetchone()
    return row_to_dict(row) if row else None


def get_filter_options() -> Dict[str, List[str]]:
    sql_map = {
        "regions": "SELECT DISTINCT region_country AS value FROM museums WHERE region_country IS NOT NULL AND region_country <> '' ORDER BY value",
        "sizes": "SELECT DISTINCT size AS value FROM museums WHERE size IS NOT NULL AND size <> '' ORDER BY value",
        "accreditations": "SELECT DISTINCT accreditation AS value FROM accreditation WHERE accreditation IS NOT NULL AND accreditation <> '' ORDER BY value",
        "aim_sizes": "SELECT DISTINCT aim_size AS value FROM aim_size WHERE aim_size IS NOT NULL AND aim_size <> '' ORDER BY value",
        "admin_areas": "SELECT DISTINCT child_id AS value FROM adminarea WHERE child_id IS NOT NULL AND child_id <> '' ORDER BY value",
        "cities": "SELECT DISTINCT village_town_city AS value FROM museums WHERE village_town_city IS NOT NULL AND village_town_city <> '' ORDER BY value LIMIT 300",
    }
    options = {}
    for key, sql in sql_map.items():
        try:
            options[key] = [r["value"] for r in fetch_all(sql)]
        except SQLAlchemyError:
            options[key] = []
    return options


def add_text_filter(filters: List[str], params: Dict[str, Any], sql_expr: str, operator: str, value: str, key: str) -> None:
    if operator == "equals":
        filters.append(f"LOWER(COALESCE({sql_expr}, '')) = LOWER(:{key})")
        params[key] = value
    elif operator == "starts_with":
        filters.append(f"LOWER(COALESCE({sql_expr}, '')) LIKE LOWER(:{key})")
        params[key] = f"{value}%"
    else:
        filters.append(f"LOWER(COALESCE({sql_expr}, '')) LIKE LOWER(:{key})")
        params[key] = f"%{value}%"


def add_number_filter(filters: List[str], params: Dict[str, Any], sql_expr: str, operator: str, value: str, key: str) -> None:
    number = parse_int(value)
    if number is None:
        return
    if operator == "gte":
        filters.append(f"{sql_expr} >= :{key}")
    elif operator == "lte":
        filters.append(f"{sql_expr} <= :{key}")
    else:
        filters.append(f"{sql_expr} = :{key}")
    params[key] = number


def add_advanced_filters(filters: List[str], params: Dict[str, Any], args) -> None:
    for index in range(1, 4):
        field = clean_text(args.get(f"filter_field_{index}"))
        operator = clean_text(args.get(f"filter_op_{index}")) or "contains"
        value = clean_text(args.get(f"filter_value_{index}"))
        if not field or not value or field not in ADVANCED_FILTER_FIELDS:
            continue
        config = ADVANCED_FILTER_FIELDS[field]
        sql_expr = get_opened_year_sql("m") if field == "opened_year" else config["sql"]
        param_key = f"advanced_filter_{index}"
        if config["type"] == "number":
            add_number_filter(filters, params, sql_expr, operator, value, param_key)
        else:
            add_text_filter(filters, params, sql_expr, operator, value, param_key)


def build_museum_filters(args) -> Tuple[str, Dict[str, Any]]:
    filters = []
    params: Dict[str, Any] = {}

    q = clean_text(args.get("q"))
    region = clean_text(args.get("region"))
    size = clean_text(args.get("size"))
    accreditation = clean_text(args.get("accreditation"))
    year_from = parse_int(args.get("year_from"))
    year_to = parse_int(args.get("year_to"))
    city = clean_text(args.get("city"))

    opened_year = get_opened_year_sql("m")

    if q:
        filters.append(
            "(" 
            "LOWER(m.name_of_museum) LIKE LOWER(:q_like) OR "
            "LOWER(m.museum_id) LIKE LOWER(:q_like) OR "
            "LOWER(COALESCE(m.postcode, '')) LIKE LOWER(:q_like) OR "
            "LOWER(COALESCE(m.address_line_1, '')) LIKE LOWER(:q_like)"
            ")"
        )
        params["q_like"] = f"%{q}%"
    if region:
        filters.append("m.region_country = :region")
        params["region"] = region
    if size:
        filters.append("m.size = :size")
        params["size"] = size
    if accreditation:
        filters.append("a.accreditation = :accreditation")
        params["accreditation"] = accreditation
    if city:
        filters.append("LOWER(m.village_town_city) LIKE LOWER(:city_like)")
        params["city_like"] = f"%{city}%"
    if year_from is not None:
        filters.append(f"{opened_year} >= :year_from")
        params["year_from"] = year_from
    if year_to is not None:
        filters.append(f"{opened_year} <= :year_to")
        params["year_to"] = year_to

    add_advanced_filters(filters, params, args)

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""
    return where_clause, params


def base_museums_sql() -> str:
    opened_year = get_opened_year_sql("m")
    return f"""
        FROM museums m
        LEFT JOIN accreditation a ON a.museum_id = m.museum_id
        LEFT JOIN aim_size aim ON aim.museum_id = m.museum_id
        LEFT JOIN adminarea aa ON aa.adminarea_id = m.adminarea_id
    """, opened_year


def load_map_points(
    q: str = "",
    region: str = "",
    city: str = "",
    accreditation: str = "",
    size: str = "",
    aim_size: str = "",
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    limit: int = 1200,
) -> List[Dict[str, Any]]:
    """Use the original TSV for coordinates because the original DB schema does not store latitude/longitude."""
    if not DATASET_PATH.exists():
        return []
    try:
        columns = [
            "museum_id",
            "Name_of_museum",
            "Village,_Town_or_City",
            "Region_country",
            "Latitude",
            "Longitude",
            "Accreditation",
            "Size",
            "AIM_Size_designation",
            "Year_opened",
        ]
        df = pd.read_csv(DATASET_PATH, sep="\t", usecols=columns)
        df = df.dropna(subset=["Latitude", "Longitude"])
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
        df = df.dropna(subset=["Latitude", "Longitude"])

        if q:
            q_lower = q.lower()
            df = df[
                df["Name_of_museum"].fillna("").str.lower().str.contains(q_lower, regex=False)
                | df["museum_id"].fillna("").str.lower().str.contains(q_lower, regex=False)
            ]
        if region:
            df = df[df["Region_country"] == region]
        if city:
            df = df[df["Village,_Town_or_City"].fillna("").str.contains(city, case=False, regex=False)]
        if accreditation:
            df = df[df["Accreditation"] == accreditation]
        if size:
            df = df[df["Size"] == size]
        if aim_size:
            df = df[df["AIM_Size_designation"] == aim_size]
        if year_from is not None or year_to is not None:
            df["opened_year"] = df["Year_opened"].fillna("").astype(str).str.extract(r"([0-9]{4})")[0]
            df["opened_year"] = pd.to_numeric(df["opened_year"], errors="coerce")
            if year_from is not None:
                df = df[df["opened_year"] >= year_from]
            if year_to is not None:
                df = df[df["opened_year"] <= year_to]

        df = df.head(limit)
        return [
            {
                "museum_id": str(row["museum_id"]),
                "name": str(row["Name_of_museum"]),
                "city": "" if pd.isna(row["Village,_Town_or_City"]) else str(row["Village,_Town_or_City"]),
                "region": "" if pd.isna(row["Region_country"]) else str(row["Region_country"]),
                "lat": float(row["Latitude"]),
                "lon": float(row["Longitude"]),
                "accreditation": "" if pd.isna(row["Accreditation"]) else str(row["Accreditation"]),
                "size": "" if pd.isna(row["Size"]) else str(row["Size"]),
                "aim_size": "" if pd.isna(row["AIM_Size_designation"]) else str(row["AIM_Size_designation"]),
            }
            for _, row in df.iterrows()
        ]
    except Exception:
        return []


@app.route("/")
def index():
    try:
        stats = {
            "museums": execute_scalar("SELECT COUNT(*) FROM museums"),
            "regions": execute_scalar("SELECT COUNT(DISTINCT region_country) FROM museums WHERE region_country IS NOT NULL"),
            "unaccredited": execute_scalar("SELECT COUNT(*) FROM accreditation WHERE accreditation = 'Unaccredited'"),
            "small": execute_scalar("SELECT COUNT(*) FROM museums WHERE size = 'small'"),
        }
        recent = fetch_all(
            f"""
            SELECT museum_id, name_of_museum, village_town_city, region_country, size,
                   {get_opened_year_sql('m')} AS opened_year
            FROM museums m
            WHERE {get_opened_year_sql('m')} IS NOT NULL
            ORDER BY opened_year DESC, name_of_museum ASC
            LIMIT 8
            """
        )
    except SQLAlchemyError as exc:
        stats = {"museums": 0, "regions": 0, "unaccredited": 0, "small": 0}
        recent = []
        flash(f"Database connection error: {exc}", "danger")
    return render_template("index.html", stats=stats, recent=recent)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = clean_text(request.form.get("username")) or ""
        password = request.form.get("password") or ""
        role = request.form.get("role") or "viewer"

        if role == "admin":
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session["role"] = "admin"
                session["username"] = username
                flash("Logged in as admin.", "success")
                return redirect(url_for("index"))
            flash("Invalid admin username or password.", "danger")
        else:
            session["role"] = "viewer"
            session["username"] = username or VIEWER_USERNAME
            flash("Logged in as viewer.", "success")
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


@app.route("/museums")
def museums():
    page = max(parse_int(request.args.get("page"), 1) or 1, 1)
    page_size = parse_int(request.args.get("page_size"), DEFAULT_PAGE_SIZE) or DEFAULT_PAGE_SIZE
    if page_size not in PAGE_SIZE_OPTIONS:
        page_size = DEFAULT_PAGE_SIZE

    sort_by = request.args.get("sort_by", "name")
    sort_expr = SORT_COLUMNS.get(sort_by, SORT_COLUMNS["name"])
    sort_order = request.args.get("sort_order", "asc").lower()
    sort_order = "DESC" if sort_order == "desc" else "ASC"

    where_clause, params = build_museum_filters(request.args)
    base_from, opened_year = base_museums_sql()

    count_sql = f"SELECT COUNT(*) FROM (SELECT DISTINCT m.museum_id {base_from} {where_clause}) AS x"
    list_sql = f"""
        SELECT DISTINCT ON (m.museum_id)
            m.museum_id,
            m.name_of_museum,
            m.address_line_1,
            m.village_town_city,
            m.postcode,
            m.region_country,
            m.size,
            m.year_opened,
            m.year_closed,
            {opened_year} AS opened_year,
            COALESCE(a.accreditation, 'Unknown') AS accreditation,
            COALESCE(aim.aim_size, '') AS aim_size,
            COALESCE(aa.child_id, '') AS admin_area
        {base_from}
        {where_clause}
        ORDER BY m.museum_id, {sort_expr} {sort_order} NULLS LAST
        LIMIT :limit OFFSET :offset
    """

    params_for_count = dict(params)
    params_for_list = dict(params)
    params_for_list.update({"limit": page_size, "offset": (page - 1) * page_size})

    try:
        total = execute_scalar(count_sql, params_for_count) or 0
        rows = fetch_all(list_sql, params_for_list)
    except SQLAlchemyError as exc:
        total = 0
        rows = []
        flash(f"Query failed: {exc}", "danger")

    total_pages = max((total + page_size - 1) // page_size, 1)
    options = get_filter_options()
    return render_template(
        "museums.html",
        museums=rows,
        options=options,
        total=total,
        page=page,
        total_pages=total_pages,
        page_size=page_size,
        page_size_options=PAGE_SIZE_OPTIONS,
        sort_by=sort_by,
        sort_order=sort_order.lower(),
        advanced_fields=ADVANCED_FILTER_FIELDS,
        text_filter_operators=TEXT_FILTER_OPERATORS,
        number_filter_operators=NUMBER_FILTER_OPERATORS,
        args=request.args,
    )


@app.route("/museums/<museum_id>")
def museum_detail(museum_id: str):
    sql = f"""
        SELECT
            m.*,
            {get_opened_year_sql('m')} AS opened_year,
            COALESCE(a.accreditation, 'Unknown') AS accreditation,
            COALESCE(a.accreditation_source, '') AS accreditation_source,
            COALESCE(aim.aim_size, '') AS aim_size,
            COALESCE(aim.aim_size_source, '') AS aim_size_source,
            COALESCE(aa.child_id, '') AS admin_area,
            COALESCE(aa.parent_id, '') AS admin_parent
        FROM museums m
        LEFT JOIN accreditation a ON a.museum_id = m.museum_id
        LEFT JOIN aim_size aim ON aim.museum_id = m.museum_id
        LEFT JOIN adminarea aa ON aa.adminarea_id = m.adminarea_id
        WHERE m.museum_id = :museum_id
        LIMIT 1
    """
    try:
        museum = fetch_one(sql, {"museum_id": museum_id})
        if not museum:
            flash("Museum not found.", "warning")
            return redirect(url_for("museums"))
        visitors = fetch_all("SELECT visitor FROM visitors WHERE museum_id = :museum_id", {"museum_id": museum_id})
        notes = fetch_all("SELECT notes FROM notes WHERE museum_id = :museum_id", {"museum_id": museum_id})
    except SQLAlchemyError as exc:
        flash(f"Failed to load museum: {exc}", "danger")
        return redirect(url_for("museums"))
    return render_template("museum_detail.html", museum=museum, visitors=visitors, notes=notes)


@app.route("/museums/add", methods=["GET", "POST"])
def add_museum():
    admin_redirect = require_admin()
    if admin_redirect:
        return admin_redirect

    if request.method == "POST":
        try:
            museum_data = collect_museum_form_data(is_update=False)
            accreditation = clean_text(request.form.get("accreditation"))
            aim_size = clean_text(request.form.get("aim_size"))

            with get_db().begin() as conn:
                conn.execute(
                    text(
                        """
                        INSERT INTO museums (
                            museum_id, name_of_museum, alternate_museum_name, address_line_1,
                            address_line_2, address_line_3, village_town_city, postcode,
                            region_country, size, year_opened, year_closed, founder, notes
                        ) VALUES (
                            :museum_id, :name_of_museum, :alternate_museum_name, :address_line_1,
                            :address_line_2, :address_line_3, :village_town_city, :postcode,
                            :region_country, :size, :year_opened, :year_closed, :founder, :notes
                        )
                        """
                    ),
                    museum_data,
                )
                if accreditation:
                    conn.execute(
                        text("INSERT INTO accreditation (accreditation, museum_id) VALUES (:accreditation, :museum_id)"),
                        {"accreditation": accreditation, "museum_id": museum_data["museum_id"]},
                    )
                if aim_size:
                    conn.execute(
                        text("INSERT INTO aim_size (aim_size, museum_id) VALUES (:aim_size, :museum_id)"),
                        {"aim_size": aim_size, "museum_id": museum_data["museum_id"]},
                    )
            flash("Museum added successfully.", "success")
            return redirect(url_for("museum_detail", museum_id=museum_data["museum_id"]))
        except ValueError as exc:
            flash(str(exc), "warning")
        except IntegrityError:
            flash("Museum ID already exists or a database constraint failed.", "danger")
        except SQLAlchemyError as exc:
            flash(f"Failed to add museum: {exc}", "danger")

    return render_template("museum_form.html", mode="add", museum={}, action_url=url_for("add_museum"))


@app.route("/museums/<museum_id>/edit", methods=["GET", "POST"])
def edit_museum(museum_id: str):
    admin_redirect = require_admin()
    if admin_redirect:
        return admin_redirect

    museum = fetch_one(
        """
        SELECT m.*, a.accreditation, aim.aim_size
        FROM museums m
        LEFT JOIN accreditation a ON a.museum_id = m.museum_id
        LEFT JOIN aim_size aim ON aim.museum_id = m.museum_id
        WHERE m.museum_id = :museum_id
        LIMIT 1
        """,
        {"museum_id": museum_id},
    )
    if not museum:
        flash("Museum not found.", "warning")
        return redirect(url_for("museums"))

    if request.method == "POST":
        try:
            museum_data = collect_museum_form_data(is_update=True)
            museum_data["museum_id"] = museum_id
            accreditation = clean_text(request.form.get("accreditation"))
            aim_size = clean_text(request.form.get("aim_size"))
            with get_db().begin() as conn:
                conn.execute(
                    text(
                        """
                        UPDATE museums SET
                            name_of_museum = :name_of_museum,
                            alternate_museum_name = :alternate_museum_name,
                            address_line_1 = :address_line_1,
                            address_line_2 = :address_line_2,
                            address_line_3 = :address_line_3,
                            village_town_city = :village_town_city,
                            postcode = :postcode,
                            region_country = :region_country,
                            size = :size,
                            year_opened = :year_opened,
                            year_closed = :year_closed,
                            founder = :founder,
                            notes = :notes
                        WHERE museum_id = :museum_id
                        """
                    ),
                    museum_data,
                )
                upsert_one_to_one(conn, "accreditation", "accreditation", accreditation, museum_id)
                upsert_one_to_one(conn, "aim_size", "aim_size", aim_size, museum_id)
            flash("Museum updated successfully.", "success")
            return redirect(url_for("museum_detail", museum_id=museum_id))
        except ValueError as exc:
            flash(str(exc), "warning")
        except SQLAlchemyError as exc:
            flash(f"Failed to update museum: {exc}", "danger")

    return render_template("museum_form.html", mode="edit", museum=museum, action_url=url_for("edit_museum", museum_id=museum_id))


@app.route("/museums/<museum_id>/delete", methods=["POST"])
def delete_museum(museum_id: str):
    admin_redirect = require_admin()
    if admin_redirect:
        return admin_redirect

    try:
        with get_db().begin() as conn:
            for table_name in CHILD_TABLES:
                conn.execute(text(f"DELETE FROM {table_name} WHERE museum_id = :museum_id"), {"museum_id": museum_id})
            result = conn.execute(text("DELETE FROM museums WHERE museum_id = :museum_id"), {"museum_id": museum_id})
        if result.rowcount:
            flash("Museum deleted successfully.", "success")
        else:
            flash("Museum not found.", "warning")
    except SQLAlchemyError as exc:
        flash(f"Failed to delete museum: {exc}", "danger")
    return redirect(url_for("museums"))


def collect_museum_form_data(is_update: bool) -> Dict[str, Any]:
    museum_id = clean_text(request.form.get("museum_id"))
    name = clean_text(request.form.get("name_of_museum"))
    if not is_update and not museum_id:
        raise ValueError("Museum ID is required.")
    if not name:
        raise ValueError("Museum name is required.")

    year_opened = make_year_range(request.form.get("year_opened"))
    year_closed = make_year_range(request.form.get("year_closed")) or "[9999,9999)"

    return {
        "museum_id": museum_id,
        "name_of_museum": name,
        "alternate_museum_name": clean_text(request.form.get("alternate_museum_name")),
        "address_line_1": clean_text(request.form.get("address_line_1")),
        "address_line_2": clean_text(request.form.get("address_line_2")),
        "address_line_3": clean_text(request.form.get("address_line_3")),
        "village_town_city": clean_text(request.form.get("village_town_city")),
        "postcode": clean_text(request.form.get("postcode")),
        "region_country": clean_text(request.form.get("region_country")),
        "size": clean_text(request.form.get("size")),
        "year_opened": year_opened,
        "year_closed": year_closed,
        "founder": clean_text(request.form.get("founder")),
        "notes": clean_text(request.form.get("notes")),
    }


def upsert_one_to_one(conn, table_name: str, field_name: str, value: Optional[str], museum_id: str) -> None:
    existing = conn.execute(text(f"SELECT id FROM {table_name} WHERE museum_id = :museum_id LIMIT 1"), {"museum_id": museum_id}).fetchone()
    if existing:
        conn.execute(text(f"UPDATE {table_name} SET {field_name} = :value WHERE museum_id = :museum_id"), {"value": value, "museum_id": museum_id})
    elif value:
        conn.execute(text(f"INSERT INTO {table_name} ({field_name}, museum_id) VALUES (:value, :museum_id)"), {"value": value, "museum_id": museum_id})


@app.route("/visualisations")
def visualisations():
    dimension = request.args.get("dimension", "region")
    if dimension not in VISUALISATION_DIMENSIONS:
        dimension = "region"
    chart_type = request.args.get("chart_type", "bar")
    if chart_type not in {"bar", "horizontal_bar", "doughnut", "line"}:
        chart_type = "bar"
    region_filter = clean_text(request.args.get("region"))
    year_from = parse_int(request.args.get("year_from"))
    year_to = parse_int(request.args.get("year_to"))
    custom_filters = []
    custom_params: Dict[str, Any] = {}
    opened_year = get_opened_year_sql("m")
    if region_filter:
        custom_filters.append("m.region_country = :visual_region")
        custom_params["visual_region"] = region_filter
    if year_from is not None:
        custom_filters.append(f"{opened_year} >= :visual_year_from")
        custom_params["visual_year_from"] = year_from
    if year_to is not None:
        custom_filters.append(f"{opened_year} <= :visual_year_to")
        custom_params["visual_year_to"] = year_to
    custom_where = "WHERE " + " AND ".join(custom_filters) if custom_filters else ""
    base_from, _ = base_museums_sql()
    dimension_config = VISUALISATION_DIMENSIONS[dimension]
    custom_sql = f"""
        SELECT {dimension_config['sql']} AS label, COUNT(DISTINCT m.museum_id) AS value
        {base_from}
        {custom_where}
        GROUP BY label
        ORDER BY {dimension_config['order']}
        LIMIT 30
    """
    try:
        custom_data = fetch_all(custom_sql, custom_params)
        region_counts = fetch_all(
            """
            SELECT COALESCE(region_country, 'Unknown') AS label, COUNT(*) AS value
            FROM museums
            GROUP BY COALESCE(region_country, 'Unknown')
            ORDER BY value DESC
            """
        )
        accreditation_counts = fetch_all(
            """
            SELECT COALESCE(accreditation, 'Unknown') AS label, COUNT(*) AS value
            FROM accreditation
            GROUP BY COALESCE(accreditation, 'Unknown')
            ORDER BY value DESC
            """
        )
        size_counts = fetch_all(
            """
            SELECT COALESCE(size, 'Unknown') AS label, COUNT(*) AS value
            FROM museums
            GROUP BY COALESCE(size, 'Unknown')
            ORDER BY value DESC
            """
        )
        opened_counts = fetch_all(
            f"""
            SELECT {get_opened_year_sql('m')} AS label, COUNT(*) AS value
            FROM museums m
            WHERE {get_opened_year_sql('m')} IS NOT NULL
              AND {get_opened_year_sql('m')} BETWEEN 1800 AND 2026
            GROUP BY label
            ORDER BY label
            """
        )
    except SQLAlchemyError as exc:
        custom_data = []
        region_counts = accreditation_counts = size_counts = opened_counts = []
        flash(f"Failed to load visualisation data: {exc}", "danger")

    chart_data = {
        "custom": custom_data,
        "regions": region_counts,
        "accreditations": accreditation_counts,
        "sizes": size_counts,
        "opened": opened_counts,
    }
    options = get_filter_options()
    return render_template(
        "visualisations.html",
        chart_data=json.dumps(chart_data),
        dimension=dimension,
        chart_type=chart_type,
        dimensions=VISUALISATION_DIMENSIONS,
        options=options,
        args=request.args,
    )


@app.route("/map")
def map_view():
    q = clean_text(request.args.get("q")) or ""
    region = clean_text(request.args.get("region")) or ""
    city = clean_text(request.args.get("city")) or ""
    accreditation = clean_text(request.args.get("accreditation")) or ""
    size = clean_text(request.args.get("size")) or ""
    aim_size = clean_text(request.args.get("aim_size")) or ""
    year_from = parse_int(request.args.get("year_from"))
    year_to = parse_int(request.args.get("year_to"))
    points = load_map_points(
        q=q,
        region=region,
        city=city,
        accreditation=accreditation,
        size=size,
        aim_size=aim_size,
        year_from=year_from,
        year_to=year_to,
    )
    options = get_filter_options()
    return render_template("map.html", points=json.dumps(points), point_count=len(points), options=options, args=request.args)


@app.route("/database")
def database_tools():
    try:
        table_counts = fetch_all(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )
        counts = []
        for item in table_counts:
            table_name = item["table_name"]
            count = execute_scalar(f"SELECT COUNT(*) FROM {table_name}")
            counts.append({"table_name": table_name, "count": count})
        indexes = fetch_all(
            """
            SELECT tablename, indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
            """
        )
    except SQLAlchemyError as exc:
        counts = []
        indexes = []
        flash(f"Database information failed: {exc}", "danger")
    return render_template("database.html", counts=counts, indexes=indexes, index_statements=INDEX_STATEMENTS)


@app.route("/database/create-indexes", methods=["POST"])
def create_indexes():
    admin_redirect = require_admin()
    if admin_redirect:
        return admin_redirect
    try:
        with get_db().begin() as conn:
            for stmt in INDEX_STATEMENTS:
                conn.execute(text(stmt))
        flash("Recommended indexes were created successfully.", "success")
    except SQLAlchemyError as exc:
        flash(f"Failed to create indexes: {exc}", "danger")
    return redirect(url_for("database_tools"))


@app.route("/database/performance")
def performance_test():
    region = clean_text(request.args.get("region")) or "London"
    q = clean_text(request.args.get("q")) or "museum"
    sql = """
        EXPLAIN ANALYZE
        SELECT m.museum_id, m.name_of_museum, m.region_country, a.accreditation
        FROM museums m
        LEFT JOIN accreditation a ON a.museum_id = m.museum_id
        WHERE m.region_country = :region
          AND LOWER(m.name_of_museum) LIKE LOWER(:q_like)
        ORDER BY m.name_of_museum
        LIMIT 50
    """
    started = time.perf_counter()
    try:
        rows = fetch_all(sql, {"region": region, "q_like": f"%{q}%"})
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        plan = [r["QUERY PLAN"] for r in rows]
    except SQLAlchemyError as exc:
        elapsed_ms = 0
        plan = [f"Performance query failed: {exc}"]
    return render_template("performance.html", plan=plan, elapsed_ms=elapsed_ms, region=region, q=q)


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "7860"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
