import os
import pandas as pd
from sqlalchemy import select, insert, MetaData, func
from models.adminarea import define_adminarea_table
from models.museums import define_museums_table

def parse_year_range(year_range_str):
    if not pd.isnull(year_range_str) and isinstance(year_range_str, str):
        # Check if the string contains a colon
        if ':' in year_range_str:
            start_year, end_year = year_range_str.split(':')
        else:
            start_year = end_year = year_range_str

        # Return a string formatted as a range
        return f'[{start_year.strip()},{end_year.strip()}]'
    return None

def load_museums(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    metadata = MetaData()

    museum_table = define_museums_table(metadata)
    adminarea_table = define_adminarea_table(metadata)

    column_mapping = {
        'museum_id': 'museum_id',
        'Name_of_museum': 'name_of_museum',
        'Alternative_museum_name': 'alternate_museum_name',
        'Address_line_1': 'address_line_1',
        'Address_line_2': 'address_line_2',
        'Address_line_3': 'address_line_3',
        'Village,_Town_or_City': 'village_town_city',
        'Postcode': 'postcode',
        'Region_country': 'region_country',
        'Admin_area': 'admin_area',
        'Size': 'size',
        'Size_provenance': 'size_provenance',
        'Year_opened': 'year_opened',
        'Year_opened_source': 'year_opened_source',
        'Year_closed': 'year_closed',
        'Year_closed_source': 'year_closed_source',
        'Founder': 'founder',
        'Founder_source': 'founder_source',
        'Notes': 'notes'
    }

    # Rename the columns in the dataframe
    museums_data = museums_data.rename(columns=column_mapping)
    museums_data = museums_data.fillna('')

    # Apply transformations to year columns
    museums_data['year_opened'] = museums_data['year_opened'].apply(parse_year_range)
    museums_data['year_closed'] = museums_data['year_closed'].apply(parse_year_range)

    museum_data_with_ids = []

    with engine.connect() as connection:
        for _, row in museums_data.iterrows():
            if pd.isna(row['admin_area']):
                adminarea_id = None
            else:
                areas = row['admin_area'].strip().split('/')
                child_area = areas[-1]
                for char in child_area:
                    print(f"Character: '{char}', ASCII: {ord(char)}")

                print(f"Extracted child_area:",child_area,"___________________________________")

                # Select the admin area id using lowercase for comparison
                

                stmt = select(adminarea_table.c.adminarea_id).where(
                        func.lower(func.trim(adminarea_table.c.child_id)) == func.lower(func.trim(child_area))
                        )

                print("stmt................................................", stmt)
                result = connection.execute(stmt).fetchone()

                print(f"Result for admin_area lookup: {result}")
                adminarea_id = result[0] if result else None

            museum_data_with_ids.append({
                'museum_id': row['museum_id'],
                'name_of_museum': row['name_of_museum'],
                'alternate_museum_name': row['alternate_museum_name'],
                'address_line_1': row['address_line_1'],
                'address_line_2': row['address_line_2'],
                'address_line_3': row['address_line_3'],
                'village_town_city': row['village_town_city'],
                'postcode': row['postcode'],
                'region_country': row['region_country'],
                'adminarea_id': adminarea_id,
                'size': row['size'],
                'size_provenance': row['size_provenance'],
                'year_opened': str(row['year_opened']),
                'year_opened_source': row['year_opened_source'],
                'year_closed': str(row['year_closed']),
                'year_closed_source': row['year_closed_source'],
                'founder': row['founder'],
                'founder_source': row['founder_source'],
                'notes': row['notes']
            })

        connection.execute(insert(museum_table), museum_data_with_ids)
        connection.commit()

    print("Museums data inserted successfully.")

if __name__ == "__main__":
    from main import get_engine
    engine = get_engine()
    load_museums(engine)
