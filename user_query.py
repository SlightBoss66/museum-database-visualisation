import os
import sys
import importlib
from db_connector import get_engine  # Make sure this points to your correct DB connection script

def main():
    # Ensure the `queries` folder is in the Python path
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'queries'))

    queries = {
        '1': 'queries.query_1',
        '2': 'queries.query_2',
        '3': 'queries.query_3',
        '4': 'queries.query_4',
        '5': 'queries.query_5',
        '6': 'queries.query_6',
        '7': 'queries.query_7',
        '8': 'queries.query_8',
        '9': 'queries.query_9',
        '10': 'queries.query_10',
    }

    print("Select a query to run:")
    print("1. Run query to get museums with 'Unaccredited' accreditation")
    print("2. Run query to get museums with AIM_Size as 'Small' ")
    print("3. Run query to get number of visitors of a particular museum")
    print("4. Run query to get museums started after year 2000")
    print("5. Run query to get museums with Admin Area at 'Manchester (English District or Borough)'")
    print("6. Run query to get museums from 'West Midlands' region")
    print("7. Run query to get museums that are founded by 'Barney Hansford'")
    print("8. Run a query to update a museums data")
    print("9. Run a query to add a new museum to the database")
    print("10. Run a query to delete the whole database")

    choice = input("Enter the number of the query you want to run: ")

    if choice in queries:
        query_module = importlib.import_module(queries[choice])
        engine = get_engine()  # Create the engine using your db_connector.py
        query_module.run_query(engine)  # Pass the engine to the run_query function
    else:
        print("Invalid choice. Please select a valid query number.")

if __name__ == "__main__":
    main()

