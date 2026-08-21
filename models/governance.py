from sqlalchemy import MetaData, Table, Column, String, Integer, ForeignKey

def define_governance_table(metadata):
    governance_table = Table('governance' ,metadata,
        Column('governance_id', Integer, primary_key=True, autoincrement=True),
        Column('governance_name', String(255)),
        Column('governance_source', String(500)),
        Column('museum_id', String(50), ForeignKey('museums.museum_id'), nullable=False),
        Column('hierarchy_id', Integer, ForeignKey('governance_hierarchy.hierarchy_id'))
    )
    return governance_table