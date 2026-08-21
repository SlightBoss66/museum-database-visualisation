import os
import pandas as pd

def load_geodemographics(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mapping = {
        'Latitude': 'latitude',
        'Longitude': 'longitude',
        'Area_Geodemographic_group': 'area_demographic_group',
        'Area_Geodemographic_group_code': 'area_demographic_group_code',
        'Area_Geodemographic_subgroup': 'area_geodemographic_subgroup',
        'Area_Geodemographic_subgroup_code': 'area_geodemographic_subgroup_code',
        'Area_Geodemographic_supergroup': 'area_geodemographic_supergroup',
        'Area_Geodemographic_supergroup_code': 'area_geodemographic_supergroup_code',
        'museum_id': 'museum_id'
    }

    geodemographic_data = museums_data[list(column_mapping.keys())].rename(columns=column_mapping)

    required_columns = ['latitude', 'longitude', 'area_demographic_group',
                        'area_demographic_group_code', 'area_geodemographic_subgroup',
                        'area_geodemographic_subgroup_code', 'area_geodemographic_supergroup',
                        'area_geodemographic_supergroup_code', 'museum_id']
    
    geodemographic_data = geodemographic_data[required_columns]

    geodemographic_data.to_sql('geodemographics', engine, if_exists='append', index=False, method='multi')

    print("Geodemographics data inserted successfully")


