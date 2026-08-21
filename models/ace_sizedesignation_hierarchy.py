from sqlalchemy import Table, Column, Integer, String

def define_ACE_sizedesignation_hierarchy_table(metadata):
    ACE_sizedesignation_hierarchy_table = Table('ace_sizedesignation_hierarchy', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('parent_id', String(50)),
        Column('child_id', String(50))
    )
    return ACE_sizedesignation_hierarchy_table