from sqlalchemy import MetaData, select, update
from models.museums import define_museums_table

def run_query(engine):

    metadata = MetaData()
    museums_table = define_museums_table(metadata)

    with engine.connect() as connection:
        transaction = connection.begin()
        try:

            while True:
                museum_id = input("Enter the museum ID you want to update: ")

                query_check = select(museums_table.c.museum_id).where(museums_table.c.museum_id == museum_id)
                result = connection.execute(query_check).fetchone()

                if not result:
                    print(f"No museum found with ID {museum_id}. Please try again.")
                    continue

                print("What would you like to update?")
                print("1. Name")
                print("2. Address Line 1")
                print("3. Postcode")
                print("4. Size")
                print("5. Exit")

                choice = input("Enter the number of the field you want to update: ")

                if choice == '1':
                    new_name = input("Enter the new name of the museum: ")
                    update_stmt = update(museums_table).where(museums_table.c.museum_id == museum_id).values(name_of_museum=new_name)
                elif choice == '2':
                    new_address = input("Enter the new address line 1: ")
                    update_stmt = update(museums_table).where(museums_table.c.museum_id == museum_id).values(address_line_1=new_address)
                elif choice == '3':
                    new_postcode = input("Enter the new postcode: ")
                    update_stmt = update(museums_table).where(museums_table.c.museum_id == museum_id).values(postcode=new_postcode)
                elif choice == '4':
                    new_size = input("Enter the new size: ")
                    update_stmt = update(museums_table).where(museums_table.c.museum_id == museum_id).values(size=new_size)
                elif choice == '5':
                    print("Exiting update process.")
                    break
                else:
                    print("Invalid choice. Please select a valid option.")
                    continue

                connection.execute(update_stmt)
                print(f"Museum ID {museum_id} updated successfully.")

                continue_choice = input("Do you want to continue updating this museum? (yes/no): ").strip().lower()
                if continue_choice != 'yes':
                    print("Update process completed.")
                    break

            transaction.commit()
        except Exception as e:
            transaction.rollback()
            print(f"An error occurred: {e}")