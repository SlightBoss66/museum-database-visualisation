from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

def define_notes_table(metadata):
    notes_table = Table('notes', metadata,
        Column('notes_id', Integer, primary_key=True, autoincrement=True),
        Column('notes', String(1000)),
        Column('museum_id', String(50), ForeignKey('museums.museum_id'), nullable=False)
    )
    return notes_table
