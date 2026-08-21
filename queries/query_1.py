from sqlalchemy import MetaData, select
from models.museums import define_museums_table
from models.accreditation import define_accreditation

def run_query(engine):
    metadata = MetaData()

    museums_table = define_museums_table(metadata)
    accreditation_table = define_accreditation(metadata)

    query = select(
        accreditation_table.c.accreditation,
        museums_table.c.museum_id,
        museums_table.c.name_of_museum,
        museums_table.c.address_line_1,
        museums_table.c.address_line_2,
        museums_table.c.village_town_city,
        museums_table.c.postcode,
        museums_table.c.region_country,
        museums_table.c.size,
        museums_table.c.year_opened,
        museums_table.c.year_closed
    ).select_from(
        museums_table.join(accreditation_table, museums_table.c.museum_id == accreditation_table.c.museum_id)
    ).where(
        accreditation_table.c.accreditation == 'Unaccredited'
    )

    with engine.connect() as connection:
        result = connection.execute(query).fetchall()

        for row in result:
            print(f"{row.accreditation} | {row.museum_id}, {row.name_of_museum}, {row.address_line_1}, {row.address_line_2}, {row.village_town_city}, {row.postcode}, {row.region_country}, {row.size}, {row.year_opened}, {row.year_closed}")
