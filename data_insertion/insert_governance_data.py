import os
import pandas as pd
from sqlalchemy import select, insert, MetaData
from sqlalchemy.exc import IntegrityError
from models.governance import define_governance_table
from models.governance_hierarchy import define_governance_hierarchy_table

def load_governance(engine):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    metadata = MetaData()
    governance_table = define_governance_table(metadata)
    governance_hierarchy_table = define_governance_hierarchy_table(metadata)

    column_mapping = {
        'Governance': 'governance_name',
        'Governance Source': 'governance_source',
        'museum_id': 'museum_id'
    }

    governance_data = museums_data[list(column_mapping.keys())].rename(columns=column_mapping)

    required_columns = ['governance_name', 'governance_source', 'museum_id']
    governance_data = governance_data[required_columns]

    with engine.connect() as connection:
        for _, row in governance_data.iterrows():
            governance_name = row['governance_name']

            # Split the governance_name into parent and child
            if '-' in governance_name:
                parent_name, child_name = governance_name.split('-', 1)
            else:
                parent_name, child_name = governance_name, None

            # Fetch the hierarchy_id based on parent_id and child_id
            if child_name is None:
                stmt = select(governance_hierarchy_table.c.hierarchy_id).where(
                    governance_hierarchy_table.c.parent_id == parent_name,
                    governance_hierarchy_table.c.child_id.is_(None)
                )
            else:
                stmt = select(governance_hierarchy_table.c.hierarchy_id).where(
                    governance_hierarchy_table.c.parent_id == parent_name,
                    governance_hierarchy_table.c.child_id == child_name
                )

            result = connection.execute(stmt).fetchone()
            hierarchy_id = result[0] if result else None

            governance_insert = insert(governance_table).values(
                governance_name=row['governance_name'],
                governance_source=row['governance_source'],
                museum_id=row['museum_id'],
                hierarchy_id=hierarchy_id
            )

            try:
                connection.execute(governance_insert)
            except IntegrityError as e:
                print(f"Error inserting {row}: {e}")

        connection.commit()

    print("Governance data inserted successfully.")

if __name__ == "__main__":
    from main import get_engine
    engine = get_engine()
    load_governance(engine)
