from sqlalchemy import Table, Column, String, ForeignKey

def define_areademographics_table(metadata):
    areademographics_table = Table('areademographics', metadata,
        Column('area_geodemographic_subgroup', String(50)),
        Column('area_geodemographic_subgroup_code', String(50)),
        Column('area_geodemographic_supergroup', String(50)),
        Column('area_geodemographic_supergroup_code', String(50)),
        Column('museum_id', String(100), ForeignKey('museums.museum_id'), nullable=False)
    )
    return areademographics_table