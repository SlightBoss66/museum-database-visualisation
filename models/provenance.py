from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

def define_provenance_table(metadata):
    provenance_table = Table('provenance', metadata,
        Column('provenance_id', Integer, primary_key=True, autoincrement=True),
        Column('primary_provenance_data', String(50)),
        Column('identifier_primary_datasource', String(50)),
        Column('museum_id', String(50), ForeignKey('museums.museum_id'), nullable=False)
        # Column('accredition', String(50)),
        # Column('accredition_source', String(100)),
        # Column('aim_size_designation', String(100)),
        # Column('aim_size_source', String(300)),
        # Column('ace_size_designation', String(100)),
        # Column('ace_size_source', String(300)),
        # Column('domus_subject_matter', String(100)),
        # Column('domus_identifier', Integer),
    )
    return provenance_table
