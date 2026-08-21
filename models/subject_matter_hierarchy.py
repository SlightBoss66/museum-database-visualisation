from sqlalchemy import MetaData, Table, Column, String, ForeignKey

def define_subject_matter_hierarchy_table(metadata):
    subject_matter_hierarchy = Table('subject_matter_hierarchy', metadata,
        Column('parent_id', String(50)),
        Column('child_id', String(50)),
        Column('museum_id', String(100), ForeignKey('museums.museum_id'), nullable=False)
    )
    return subject_matter_hierarchy