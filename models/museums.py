from psycopg2.extras import DateRange
from sqlalchemy import MetaData, Table, Column, Integer, String, TypeDecorator, ForeignKey

class DateRangeType(TypeDecorator):
    impl = String
    cache_ok= True

    def process_bind_param(self, value, dialect):
        if value is not None and isinstance(value, str):
            return value
        elif value is not None and isinstance(value, DateRange):
            return f'[{value.lower},{value.upper}]'
        return value

    def process_result_value(self, value, dialect):
        if value is not None and isinstance(value, str):
            lower, upper = value[1:-1].split(',')
            return DateRange(int(lower), int(upper))
        return value
    
def define_museums_table(metadata):
    museums = Table('museums', metadata,
        Column('museum_id', String(50), primary_key=True),
        Column('name_of_museum', String(100), nullable=True),
        Column('alternate_museum_name', String(100), nullable=True),
        Column('address_line_1', String(100), nullable=True),
        Column('address_line_2', String(50), nullable=True),
        Column('address_line_3', String(50), nullable=True),
        Column('village_town_city', String(50), nullable=True),
        Column('postcode', String(10), nullable=True),
        Column('region_country', String(50), nullable=True),
        Column('adminarea_id', Integer, ForeignKey('adminarea.adminarea_id')),
        Column('size', String(10), nullable=True),
        Column('size_provenance', String(50), nullable=True),
        Column('year_opened', DateRangeType),
        Column('year_opened_source', String(500), nullable=True),
        Column('year_closed', DateRangeType),
        Column('year_closed_source', String(500), nullable=True),
        Column('founder', String(500), nullable=True),
        Column('founder_source', String(500), nullable=True),
        Column('notes', String(1000), nullable=True)
    )
    return museums
