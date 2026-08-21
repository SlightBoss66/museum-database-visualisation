from sqlalchemy import MetaData, select
from models.visitors import define_visitors_table

def parse_visitor_data(visitor_data_str):
    total_visitors = 0
    if not visitor_data_str:
        return total_visitors
    try:
        visitor_entries = visitor_data_str.split(',')

        for entry in visitor_entries:

            visitor_count = int(entry.split(' at ')[0].strip())
            total_visitors += visitor_count
    except Exception as e:
        print(f"Error parsing visitor data: {e}")
    return total_visitors

def run_query(engine):

    metadata = MetaData()
    visitors_table = define_visitors_table(metadata)

    museum_id = input("Enter the museum_id: ")

    query = select(visitors_table.c.visitor).where(visitors_table.c.museum_id == museum_id)

    with engine.connect() as connection:
        results = connection.execute(query).fetchall()

    if not results:
        print(f"Error: The museum with museum_id '{museum_id}' does not exist.")
        return

    total_visitors = 0
    for row in results:
        total_visitors += parse_visitor_data(row.visitor)

    print(f"Total number of visitors for museum_id '{museum_id}': {total_visitors}")
