import os
import pandas as pd

def load_aim_size(engine):
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mapping = {'AIM_Size_designation': 'aim_size', 'AIM_size_source': 'aim_size_source',
                      'museum_id': 'museum_id'}

    museums_data = museums_data.rename(columns=column_mapping)

    required_columns = ['aim_size', 'aim_size_source', 'museum_id']

    museums_data = museums_data[required_columns]

    museums_data.to_sql('aim_size', engine, if_exists='append', index=False, method='multi')

    print("AIM Size data inserted successfully.")