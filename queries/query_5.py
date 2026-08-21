from sqlalchemy import MetaData, select
from models.museums import define_museums_table
from models.adminarea import define_adminarea_table

def run_query(engine):

    metadata = MetaData()

    museums_table = define_museums_table(metadata)
    adminarea_table = define_adminarea_table(metadata)

    query = select(adminarea_table.c.adminarea_id
    ).where(adminarea_table.c.child_id == 'Manchester (English District or Borough)')

    with engine.connect() as connection:
        adminarea_result = connection.execute(query).fetchone()
        if adminarea_result is None:
            print("No adminarea found for the specified child_id.")
            return

        adminarea_id = adminarea_result[0]

        query_museums = select(
            museums_table.c.museum_id,
            museums_table.c.name_of_museum,
            museums_table.c.address_line_1,
            museums_table.c.address_line_2,
            museums_table.c.village_town_city,
            museums_table.c.postcode,
            museums_table.c.region_country,
            museums_table.c.size,
            museums_table.c.year_opened,
            museums_table.c.year_closed,
            adminarea_table.c.child_id
        ).select_from(
            museums_table.join(adminarea_table, museums_table.c.adminarea_id == adminarea_table.c.adminarea_id)
        ).where(
            museums_table.c.adminarea_id == adminarea_id
        )

        result = connection.execute(query_museums).fetchall()

    if result:
        for row in result:
            print(f"Museum ID: {row.museum_id}, Name: {row.name_of_museum}, Address: {row.address_line_1}, "
                  f"{row.address_line_2}, {row.village_town_city}, {row.postcode}, Region: {row.region_country}, "
                  f"Size: {row.size}, Year Opened: {row.year_opened}, Year Closed: {row.year_closed}, "
                  f"Admin Area: {row.child_id}")
    else:
        print("No museums found for the specified admin area.")
