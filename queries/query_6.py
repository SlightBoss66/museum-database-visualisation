from sqlalchemy import MetaData, select
from models.museums import define_museums_table

def run_query(engine):

    metadata = MetaData()
    museums_table = define_museums_table(metadata)

    query = select(
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
    ).select_from(museums_table
    ).where(museums_table.c.region_country == 'West Midlands')

    with engine.connect() as connection:
        result = connection.execute(query).fetchall()

    if result:
        for row in result:
            print(f"Museum ID: {row.museum_id}")
            print(f"Name: {row.name_of_museum}")
            print(f"Address Line 1: {row.address_line_1}")
            print(f"Address Line 2: {row.address_line_2}")
            print(f"City: {row.village_town_city}")
            print(f"Postcode: {row.postcode}")
            print(f"Region/Country: {row.region_country}")
            print(f"Size: {row.size}")
            print(f"Year Opened: {row.year_opened}")
            print(f"Year Closed: {row.year_closed}")
            print("-" * 40)
    else:
        print("No museums found in the specified region.")


