# Museums Database Flask Web System

This web system extends the original command-line PostgreSQL museum database project into a Flask-based browser interface.

## Functions implemented

- Dashboard with summary statistics.
- Multi-condition museum search.
- Pagination and sorting.
- Museum detail page.
- Admin-only add, edit and delete functions.
- Simple viewer/admin role control.
- Chart.js data visualisations.
- Leaflet map visualisation using `dataset/output.tsv` latitude and longitude.
- Recommended PostgreSQL indexes.
- `EXPLAIN ANALYZE` performance inspection page.

## 1. Install dependencies

```bash
cd /root/111
pip install -r requirements.txt
```

If you already installed the previous dependencies, only Flask may still be needed:

```bash
pip install flask
```

## 2. Start PostgreSQL

```bash
service postgresql start
```

## 3. Make sure the database already exists and data has been imported

If you have already run this successfully, you do not need to run it again:

```bash
su - postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD 'wodegnome';\""
su - postgres -c "createdb museums_db"
python main.py
```

If `createdb museums_db` says the database already exists, that is fine.

## 4. Run the web system

```bash
python app.py
```

or:

```bash
bash run_web.sh
```

The application uses port `7860` by default:

```text
http://127.0.0.1:7860
```

On AutoDL, expose or open port `7860` from the custom service / port forwarding panel, then open the generated public URL in your local browser.

## 5. Login roles

Viewer mode:

```text
role: viewer
username: viewer
password: leave empty
```

Admin mode:

```text
role: admin
username: admin
password: admin123
```

You can change admin credentials by environment variables:

```bash
export MUSEUM_ADMIN_USER=admin
export MUSEUM_ADMIN_PASSWORD=your_password
python app.py
```

## 6. Useful pages

```text
/                  Dashboard
/museums           Search, pagination and sorting
/museums/add       Add museum, admin only
/visualisations    Charts
/map               Museum map
/database          Table counts and indexes
/database/performance  EXPLAIN ANALYZE test
```

## 7. Notes for the final report

The web system satisfies the main project requirements:

- Web-based querying: `/museums`.
- Updating: add, edit and delete pages.
- Visualisation: `/visualisations` and `/map`.
- Database improvement: recommended indexes in `/database`.
- Performance evaluation: `/database/performance`.
- Role control: admin/viewer login.
- Validation: required museum ID/name and year format validation in forms.
