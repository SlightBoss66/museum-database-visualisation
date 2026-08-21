import os
import pandas as pd
from sqlalchemy import select, insert, MetaData
from models.visitors import define_visitors_table
import pdb

def load_visitors(engine):

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    column_mapping = {'Visitor_Numbers':'visitor', 'museum_id': 'museum_id'}

    visitors_data = museums_data[list(column_mapping.keys())].rename(columns= column_mapping)

    required_columnms = ['visitor','museum_id']

    visitors_data = visitors_data[required_columnms]

    visitors_data.to_sql('visitors', engine, if_exists='append', index=False)

    print("Visitors inserted successfully")