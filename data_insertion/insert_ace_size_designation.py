import os
import pandas as pd
from sqlalchemy import select, insert, MetaData, func
from models.ace_sizedesignation import define_ACE_sizedesignation_table
from models.ace_sizedesignation_hierarchy import define_ACE_sizedesignation_hierarchy_table

def load_ace_size_designation(engine):

    # Load the dataset
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    museums_path = os.path.join(project_root, 'dataset', 'output.tsv')
    museums_data = pd.read_csv(museums_path, sep='\t')

    # Define tables
    metadata = MetaData()
    ace_size_designation_table = define_ACE_sizedesignation_table(metadata)
    ace_size_designation_hierarchy_table = define_ACE_sizedesignation_hierarchy_table(metadata)

    with engine.connect() as connection:
        ace_size_designation_rows = []

        for index, row in museums_data.iterrows():
            ace_sizedesignation = row['ACE_size_designation']
            museum_id = row['museum_id']

            if pd.notna(ace_sizedesignation):
                ace_sizedesignation = str(ace_sizedesignation)

                if '-' in ace_sizedesignation:
                    parent, child = ace_sizedesignation.split('-', 1)
                    parent = parent.strip()
                    child = child.strip()

                    query = select(ace_size_designation_hierarchy_table.c.id
                    ).where(
                        ace_size_designation_hierarchy_table.c.parent_id == parent,
                        ace_size_designation_hierarchy_table.c.child_id == child
                    )

                    hierarchy_id = connection.execute(query).scalar()

                    if hierarchy_id:
                        ace_size_designation_rows.append({
                            'ace_sizedesignation': ace_sizedesignation,
                            'museum_id': museum_id,
                            'hierarchy_id': hierarchy_id if hierarchy_id else None
                        })

        if ace_size_designation_rows:
            connection.execute(insert(ace_size_designation_table), ace_size_designation_rows)
            connection.commit()

    print("ACE Size Designation data inserted successfully")

if __name__ == "__main__":
    from db_connector import get_engine
    engine = get_engine()
    load_ace_size_designation(engine)
