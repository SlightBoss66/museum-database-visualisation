import os
import pandas as pd
from sqlalchemy import insert, MetaData, select
from models.ace_sizedesignation_hierarchy import define_ACE_sizedesignation_hierarchy_table

def load_ace_size_designation_hierarchy(engine):
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    metadata = MetaData()

    ace_size_designation_hierarchy_table = define_ACE_sizedesignation_hierarchy_table(metadata)

    ace_size_designation_hierarchy_data = museums_data[['ACE_size_designation']].dropna().drop_duplicates()

    hierarchy_data = []
    seen = set()

    for _, row in ace_size_designation_hierarchy_data.iterrows():
        ace_size = str(row['ACE_size_designation'])
        if '-' in ace_size:
            parent_name, child_name = ace_size.split('-', 1)
        else:
            parent_name, child_name = ace_size, None

        parent_name = parent_name.strip()
        child_name = child_name.strip() if child_name else None
        key = (parent_name, child_name)

        if parent_name and key not in seen:
            seen.add(key)
            hierarchy_data.append({'parent_id':parent_name, 'child_id':child_name})

    with engine.connect() as connection:
        for row in hierarchy_data:
            if row['child_id'] is None:
                exists_stmt = select(ace_size_designation_hierarchy_table.c.id).where(
                    ace_size_designation_hierarchy_table.c.parent_id == row['parent_id'],
                    ace_size_designation_hierarchy_table.c.child_id.is_(None)
                )
            else:
                exists_stmt = select(ace_size_designation_hierarchy_table.c.id).where(
                    ace_size_designation_hierarchy_table.c.parent_id == row['parent_id'],
                    ace_size_designation_hierarchy_table.c.child_id == row['child_id']
                )
            if connection.execute(exists_stmt).fetchone():
                continue
            stmt = insert(ace_size_designation_hierarchy_table).values(**row)
            connection.execute(stmt)
        connection.commit()
    print("ACE size designation Hierarchy data inserted succesfully.")
                 
