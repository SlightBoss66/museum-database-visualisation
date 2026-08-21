from sqlalchemy import Integer, String, Table, Column, ForeignKey

def define_visitors_table(metadata):
    visitors_table = Table('visitors', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('visitor', String(1000)),
        Column('museum_id', String(50), ForeignKey('museums.museum_id'), nullable=False)          
    )
    return visitors_table