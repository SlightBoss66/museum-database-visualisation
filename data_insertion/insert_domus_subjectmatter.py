import os
import pandas as pd

def load_DOMUS_subjectmatter(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mapping = {'DOMUS_Subject_Matter': 'domus_subjectmatter',
                      'DOMUS_identifier':'domus_identifier',
                      'museum_id': 'museum_id'}

    museums_data = museums_data.rename(columns=column_mapping)

    required_columns = ['domus_subjectmatter', 'domus_identifier', 'museum_id']

    museums_data = museums_data[required_columns]

    museums_data.to_sql('domus_subjectmatter', engine, if_exists='append', index=False, method='multi')

    print("Domus Subject Matter inserted successfully.")

