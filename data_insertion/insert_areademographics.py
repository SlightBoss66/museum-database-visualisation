import os
import pandas as pd

def load_areademographics(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mapping = {
        'Area_Geodemographic_subgroup': 'area_geodemographic_subgroup',
        'Area_Geodemographic_subgroup_code': 'area_geodemographic_subgroup_code',
        'Area_Geodemographic_supergroup': 'area_geodemographic_supergroup',
        'Area_Geodemographic_supergroup_code': 'area_geodemographic_supergroup_code',
        'museum_id': 'museum_id'
    }

    geodemographic_data = museums_data[list(column_mapping.keys())].rename(columns=column_mapping)

    required_columns = ['area_geodemographic_subgroup', 'area_geodemographic_subgroup_code',
                        'area_geodemographic_supergroup', 'area_geodemographic_supergroup_code',
                        'museum_id']
    
    geodemographic_data = geodemographic_data[required_columns]

    geodemographic_data.to_sql('areademographics', engine, if_exists='append', index=False, method='multi')

    print("Area demographics data inserted successfully")