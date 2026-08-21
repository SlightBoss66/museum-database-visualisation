import os
import pandas as pd
from sqlalchemy import select, insert, MetaData
from sqlalchemy.exc import IntegrityError
from models.governance_hierarchy import define_governance_hierarchy_table

def load_governance_hierarchy(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    metadata = MetaData()

    governance_hierarchy_table = define_governance_hierarchy_table(metadata)

    governance_data = museums_data[['Governance']].dropna().drop_duplicates()
    hierarchy_data = []
    seen = set()

    for _, row in governance_data.iterrows():
        governance_value = str(row['Governance'])
        if '-' in governance_value:
            parent_name, child_name = governance_value.split('-', 1)
        else:
            parent_name, child_name = governance_value, None

        parent_name = parent_name.strip()
        child_name = child_name.strip() if child_name else None
        key = (parent_name, child_name)

        if parent_name and key not in seen:
            seen.add(key)
            hierarchy_data.append({'parent_id': parent_name, 'child_id': child_name})

    with engine.connect() as connection:
        for row in hierarchy_data:
            if row['child_id'] is None:
                stmt = select(governance_hierarchy_table.c.hierarchy_id).where(
                    governance_hierarchy_table.c.parent_id == row['parent_id'],
                    governance_hierarchy_table.c.child_id.is_(None)
                )
            else:
                stmt = select(governance_hierarchy_table.c.hierarchy_id).where(
                    governance_hierarchy_table.c.parent_id == row['parent_id'],
                    governance_hierarchy_table.c.child_id == row['child_id']
                )

            result = connection.execute(stmt).fetchone()

            if not result:
                hierarchy_insert = insert(governance_hierarchy_table).values(**row)
                try:
                    connection.execute(hierarchy_insert)
                except IntegrityError as e:
                    print(f"Error inserting hierarchy: {e}")
        connection.commit()

    print("Governance hierarchy data inserted successfully.")

if __name__ == "__main__":
    from main import get_engine
    engine = get_engine()
    load_governance_hierarchy(engine)
