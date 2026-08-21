import sys
import os
import pandas as pd
from psycopg2.extras import DateRange
from sqlalchemy import create_engine

# Add the project root directory to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import get_engine

def parse_year_range(year_range_str):
    if not pd.isnull(year_range_str):
        years = year_range_str.split(':')
        if len(years) == 1:
            start_year = end_year = years[0]
        else:
            start_year, end_year = years
        return f'[{start_year},{end_year}]'
    return None

def print_max_length(df):
    for col in df.columns:
        print(f"Max length of '{col}': {df[col].astype(str).apply(len).max()}")

def load_data(engine):
    # Construct the absolute paths to the TSV files
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')

    # Load data from the TSV file into the museums table
    museums_data = pd.read_csv(museums_path, sep='\t')

    # Print the column names to verify
    print("Columns in TSV file:", museums_data.columns.tolist())

    # Print the maximum length of data in each column
    print_max_length(museums_data)

    # Check for null values in 'museum_id'
    print("Checking for null values in 'museum_id' column...")
    print(museums_data['museum_id'].isnull().sum())
    print(museums_data[museums_data['museum_id'].isnull()])

    # Define a dictionary to map TSV column names to table column names
    column_mapping = {
        'Name_of_museum': 'name_of_museum',
        'Alternative_museum_name': 'alternate_museum_name',
        'Address_line_1': 'address_line_1',
        'Address_line_2': 'address_line_2',
        'Address_line_3': 'address_line_3',
        'Village,_Town_or_City': 'village_town_city',
        'Postcode': 'postcode',
        'Region_country': 'region_country',
        'Size': 'size',
        'Size_provenance': 'size_provenance',
        'Year_opened': 'year_opened',
        'Year_opened_source': 'year_opened_source',
        'Year_closed': 'year_closed',
        'Year_closed_source': 'year_closed_source',
        'Founder': 'founder',
        'Notes': 'notes'
    }

    # Filter and rename the columns in the DataFrame
    museums_data = museums_data.rename(columns=column_mapping)

    # Define the columns required for the museums table
    required_columns = [
        'museum_id', 'name_of_museum', 'alternate_museum_name', 'address_line_1',
        'address_line_2', 'address_line_3', 'village_town_city', 'postcode',
        'region_country', 'size', 'size_provenance', 'year_opened',
        'year_opened_source', 'year_closed', 'year_closed_source', 'founder', 'notes'
    ]

    # Ensure only required columns are included
    museums_data = museums_data[required_columns]

    # Parse the year_opened and year_closed columns to daterange strings
    museums_data['year_opened'] = museums_data['year_opened'].apply(parse_year_range)
    museums_data['year_closed'] = museums_data['year_closed'].apply(parse_year_range)

    # Check for null values in the final dataset
    print("Final dataset null values check:")
    print(museums_data.isnull().sum())

    # Insert data into the museums table
    museums_data.to_sql('museums', engine, if_exists='append', index=False)

    print("Data inserted successfully.")

if __name__ == "__main__":
    engine = get_engine()
    load_data(engine)
