from sqlalchemy import MetaData, Table, Column, String, Integer, ForeignKey

def define_governance_hierarchy_table(metadata):
    governance_hierarchy_table = Table('governance_hierarchy', metadata,
        Column('hierarchy_id', Integer, primary_key=True, autoincrement=True),                           
        Column('parent_id', String(50)),
        Column('child_id', String(50))                   
    )
    return governance_hierarchy_table