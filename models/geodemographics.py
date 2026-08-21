from sqlalchemy import Table, Column, String, Integer,  Numeric, ForeignKey

def define_geodemographics_table(metadata):
    geodemographics_table = Table('geodemographics', metadata,
        Column('geodemographics_id', Integer, primary_key=True, autoincrement=True),
        Column('latitude', Numeric(9, 6)),
        Column('longitude', Numeric(9, 6)),
        Column('area_demographic_group', String(50)),
        Column('area_demographic_group_code', String(50)),
        Column('area_geodemographic_subgroup', String(50)),
        Column('area_geodemographic_subgroup_code', String(50)),
        Column('area_geodemographic_supergroup', String(50)),
        Column('area_geodemographic_supergroup_code', String(50)),
        Column('museum_id', String(50), ForeignKey('museums.museum_id'), nullable=False)                              
    )
    return geodemographics_table