from sqlalchemy import MetaData, insert
from models.museums import define_museums_table

def run_query(engine):
    metadata = MetaData()
    museums_table = define_museums_table(metadata)

    # Collecting data from the user
    museum_data = {
        'museum_id': input("Enter the museum ID: ").strip(),
        'name_of_museum': input("Enter the name of the museum: ").strip(),
        'alternate_museum_name': input("Enter the alternate name of the museum (optional): ").strip() or None,
        'address_line_1': input("Enter the address line 1: ").strip(),
        'address_line_2': input("Enter the address line 2 (optional): ").strip() or None,
        'address_line_3': input("Enter the address line 3 (optional): ").strip() or None,
        'village_town_city': input("Enter the village, town, or city: ").strip(),
        'postcode': input("Enter the postcode: ").strip(),
        'region_country': input("Enter the region or country: ").strip(),
        'size': input("Enter the size of the museum: ").strip() or None
    }

    # Constructing the insert statement
    insert_stmt = insert(museums_table).values(**museum_data)

    # Executing the insert statement with commit
    with engine.connect() as connection:
        connection.execute(insert_stmt)
        connection.commit()  # Ensure the transaction is committed
        print(f"Museum with ID {museum_data['museum_id']} has been added successfully.")

if __name__ == "__main__":
    # Ensure you have the get_engine function from your db_connector.py
    from db_connector import get_engine
    engine = get_engine()
    run_query(engine)
