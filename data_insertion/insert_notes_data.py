import os
import pandas as pd

def load_notes(engine):

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mapping = {'Notes':'notes', 'museum_id': 'museum_id'}

    notes_data = museums_data[list(column_mapping.keys())].rename(columns= column_mapping)

    required_columnms = ['notes','museum_id']

    notes_data = notes_data[required_columnms]

    notes_data.to_sql('notes', engine, if_exists='append', index=False)

    print("Notes inserted successfully")