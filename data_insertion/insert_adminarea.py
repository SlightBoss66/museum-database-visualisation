import os
import pandas as pd
from sqlalchemy import insert, MetaData, select
from models.adminarea import define_adminarea_table

def load_adminarea(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    metadata = MetaData()

    adminarea_table = define_adminarea_table(metadata)

    adminarea_data = museums_data[['Admin_area']].dropna().drop_duplicates()

    data = []
    seen = set()

    for _, row in adminarea_data.iterrows():
        adminarea_value = row['Admin_area'].strip('/')
        parts = adminarea_value.split('/')

        if len(parts) == 1:
            parent = None
            child = parts[0].strip()
            key = (parent, child)
            if child and key not in seen:
                seen.add(key)
                data.append({'parent_id': parent, 'child_id': child})
        else:
            for i in range(len(parts) - 1):
                parent = parts[i].strip()
                child = parts[i + 1].strip()
                key = (parent, child)
                if parent and child and key not in seen:
                    seen.add(key)
                    data.append({'parent_id': parent, 'child_id': child})

    with engine.connect() as connection:
        for row in data:
            if row['parent_id'] is None:
                exists_stmt = select(adminarea_table.c.adminarea_id).where(
                    adminarea_table.c.parent_id.is_(None),
                    adminarea_table.c.child_id == row['child_id']
                )
            else:
                exists_stmt = select(adminarea_table.c.adminarea_id).where(
                    adminarea_table.c.parent_id == row['parent_id'],
                    adminarea_table.c.child_id == row['child_id']
                )
            if connection.execute(exists_stmt).fetchone():
                continue
            stmt = insert(adminarea_table).values(**row)
            connection.execute(stmt)
        connection.commit()

    print("Admin Area data inserted successfully.")

if __name__ == "__main__":
    from main import get_engine
    engine = get_engine()
    load_adminarea(engine)
