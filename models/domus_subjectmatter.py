from sqlalchemy import Table, Column, Integer, String, ForeignKey

def define_DOMUS_subjectmatter_table(metadata):
    domus_subjectmatter_table = Table('domus_subjectmatter', metadata,
        Column('domus_subjectmatter_id', Integer, primary_key=True, autoincrement=True),
        Column('domus_subjectmatter', String(50)),
        Column('domus_identifier', Integer),
        Column('museum_id', String(100), ForeignKey('museums.museum_id'), nullable=False)
    )
    return domus_subjectmatter_table