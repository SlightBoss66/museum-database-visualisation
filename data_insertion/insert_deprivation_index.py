import os
import pandas as pd

def load_deprivation_index(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mapping = {
        'Area_Deprivation_index': 'area_deprivation_index',
        'Area_Deprivation_index_crime': 'area_deprivation_index_crime',
        'Area_Deprivation_index_education': 'area_deprivation_index_education',
        'Area_Deprivation_index_employment': 'area_deprivation_index_employment',
        'Area_Deprivation_index_health': 'area_deprivation_index_health',
        'Area_Deprivation_index_housing': 'area_deprivation_index_housing',
        'Area_Deprivation_index_income': 'area_deprivation_index_income',
        'Area_Deprivation_index_services': 'area_deprivation_index_services',
        'museum_id': 'museum_id'
    }

    deprivation_data = museums_data[list(column_mapping.keys())].rename(columns=column_mapping)

    required_columms = ['area_deprivation_index', 'area_deprivation_index_crime', 
                        'area_deprivation_index_education', 'area_deprivation_index_employment',
                        'area_deprivation_index_health', 'area_deprivation_index_housing',
                        'area_deprivation_index_income', 'area_deprivation_index_services', 'museum_id']
    
    deprivation_data = deprivation_data[required_columms]

    deprivation_data.to_sql('deprivation_index', engine, if_exists='append', index=False)

    print("Deprivation Index data inserted successfully.")