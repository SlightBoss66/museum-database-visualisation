import os
import pandas as pd
from sqlalchemy import insert, MetaData
from sqlalchemy.exc import IntegrityError
from models.subject_matter_hierarchy import define_subject_matter_hierarchy_table

def load_subject_matter_hierarchy(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    metadata = MetaData()
    subject_matter_hierarchy_table = define_subject_matter_hierarchy_table(metadata)

    subject_matter_data = museums_data[['Subject_Matter', 'museum_id']]
    subject_matter_data = subject_matter_data[subject_matter_data['Subject_Matter'].notna()]

    hierarchy_data = []
    seen = set()

    for _, row in subject_matter_data.iterrows():
        subject_matter_value = row['Subject_Matter']
        museum_id = row['museum_id']

        if '-' in subject_matter_value:
            parent, child = subject_matter_value.split('-', 1)
        else:
            parent, child = subject_matter_value, None

        parent = parent.strip()
        child = child.strip() if child else None
        key = (parent, child, museum_id)
        if parent and key not in seen:
            seen.add(key)
            hierarchy_data.append({'parent_id': parent,
                                   'child_id': child,
                                   'museum_id': museum_id})

    with engine.connect() as connection:
        for row in hierarchy_data:
            stmt = insert(subject_matter_hierarchy_table).values(**row)
            try:
                connection.execute(stmt)
            except IntegrityError as e:
                print(f"Error inserting {row}: {e}")
        connection.commit()
    print("Subject Matter data inserted successfully.")

if __name__ == "__main__":
    from db_connector import get_engine
    engine = get_engine()
    load_subject_matter_hierarchy(engine)

