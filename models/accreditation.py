from sqlalchemy import Table, Column, Integer, String, ForeignKey

def define_accreditation(metadata):
    accreditation_table = Table('accreditation', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('accreditation', String(100)),
        Column('accreditation_source', String(100)),
        Column('museum_id', String(50), ForeignKey('museums.museum_id'), nullable=False)
    )
    return accreditation_table