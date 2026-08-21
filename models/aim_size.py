from sqlalchemy import Table, Column, Integer, String, ForeignKey

def define_aim_size(metadata):
    aim_size_table = Table('aim_size', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('aim_size', String(100)),
        Column('aim_size_source', String(500)),
        Column('museum_id', String(50), ForeignKey('museums.museum_id'), nullable=False)
    )
    return aim_size_table