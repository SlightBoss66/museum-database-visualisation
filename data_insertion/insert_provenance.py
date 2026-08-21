import os
import pandas as pd

def load_provenance(engine):
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mappings = {'Primary_provenance_of_data': 'primary_provenance_data',
                       'Identifier_used_in_primary_data_source': 'identifier_primary_datasource',
                       'museum_id': 'museum_id'}
    
    provenance_data = museums_data[list(column_mappings.keys())].rename(columns=column_mappings)

    required_columns = ['primary_provenance_data', 'identifier_primary_datasource', 'museum_id']

    provenance_data = provenance_data[required_columns]

    provenance_data.to_sql('provenance', engine, if_exists='append', index=False)

    print("Provenance data inserted successfully")