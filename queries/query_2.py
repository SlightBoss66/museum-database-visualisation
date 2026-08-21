from sqlalchemy import MetaData, select
from models.museums import define_museums_table
from models.aim_size import define_aim_size

def run_query(engine):
    metadata = MetaData()

    museums_table = define_museums_table(metadata)
    aim_size_table = define_aim_size(metadata)

    query = select(
        aim_size_table.c.aim_size,
        museums_table
    ).select_from(
        museums_table.join(aim_size_table, museums_table.c.museum_id == aim_size_table.c.museum_id)
    ).where(
        aim_size_table.c.aim_size.like('Small Museum%')
    )

    with engine.connect() as connection:
        result = connection.execute(query).fetchall()

        for row in result:
            print(f"{row.aim_size} | {row.museum_id}, {row.name_of_museum}, {row.address_line_1}, {row.address_line_2}, {row.village_town_city}, {row.postcode}, {row.region_country}, {row.size}, {row.year_opened}, {row.year_closed}")
