from sqlalchemy import MetaData, Integer, String, Table, Column

def define_adminarea_table(metadata):
    adminarea_table = Table('adminarea', metadata,
        Column('adminarea_id', Integer, primary_key=True, autoincrement=True),
        Column('parent_id', String(100)),
        Column('child_id', String(100))
    )
    return adminarea_table