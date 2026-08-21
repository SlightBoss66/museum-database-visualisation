from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

def define_deprivation_index_table(metadata):
    deprivation_index_table = Table('deprivation_index', metadata,
        Column('area_deprivation_index', Integer),
        Column('area_deprivation_index_crime', Integer),
        Column('area_deprivation_index_education', Integer),
        Column('area_deprivation_index_employment', Integer),
        Column('area_deprivation_index_health', Integer),
        Column('area_deprivation_index_housing', Integer),
        Column('area_deprivation_index_income', Integer),
        Column('area_deprivation_index_services', Integer),
        Column('museum_id', String(50), ForeignKey('museums.museum_id'), nullable=False)                       
    )
    return deprivation_index_table