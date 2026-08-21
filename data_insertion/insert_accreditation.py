import os
import pandas as pd

def load_accreditation(engine):

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mappings = { 'Accreditation': 'accreditation',
                       'Accreditation Source': 'accreditation_source',
                       'museum_id': 'museum_id'}

    accreditation_data = museums_data[list(column_mappings.keys())].rename(columns= column_mappings)

    required_columns = ['accreditation', 'accreditation_source', 'museum_id']

    accreditation_data = accreditation_data[required_columns]

    accreditation_data.to_sql('accreditation', engine, if_exists='append', index=False)

    print("Accreditation data inserted successfully")