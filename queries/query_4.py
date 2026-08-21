from sqlalchemy import MetaData, select, func, cast, Integer
from models.museums import define_museums_table

def run_query(engine):

    metadata = MetaData()
    museums_table = define_museums_table(metadata)

    query = select(museums_table).where(
        cast(func.substr(museums_table.c.year_opened, 2, 4), Integer) >= 2000
    )

    with engine.connect() as connection:
        results = connection.execute(query).fetchall()

    if not results:
        print("No museums found that were opened after the year 2000.")
        return

    print("Museum ID | Museum Name | Year Opened")
    print("--------------------------------------")
    for row in results:
        print(f"{row.museum_id} | {row.name_of_museum} | {row.year_opened}")

