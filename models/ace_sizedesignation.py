from sqlalchemy import Table, Column, Integer, String, ForeignKey

def define_ACE_sizedesignation_table(metadata):
    ACE_sizedesignation_table = Table('ace_sizedesignation', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('ace_sizedesignation', String(50)),
        Column('hierarchy_id', Integer, ForeignKey('ace_sizedesignation_hierarchy.id')),
        Column('museum_id', String, ForeignKey('museums.museum_id'), nullable=False)                              
    )
    return ACE_sizedesignation_table
