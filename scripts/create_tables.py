from sqlalchemy import MetaData
from models.museums import define_museums_table
from models.adminarea import define_adminarea_table
from models.governance import define_governance_table
from models.governance_hierarchy import define_governance_hierarchy_table
from models.subject_matter_hierarchy import define_subject_matter_hierarchy_table
from models.geodemographics import define_geodemographics_table
from models.areademographics import define_areademographics_table
from models.domus_subjectmatter import define_DOMUS_subjectmatter_table
from models.aim_size import define_aim_size
from models.ace_sizedesignation_hierarchy import define_ACE_sizedesignation_hierarchy_table
from models.ace_sizedesignation import define_ACE_sizedesignation_table
from models.accreditation import define_accreditation
from models.provenance import define_provenance_table
from models.deprivation_index import define_deprivation_index_table
from models.notes import define_notes_table
from models.visitors import define_visitors_table

def create_tables(engine):
    metadata = MetaData()
    define_museums_table(metadata)
    define_adminarea_table(metadata)
    define_governance_hierarchy_table(metadata)
    define_governance_table(metadata)
    define_subject_matter_hierarchy_table(metadata)
    define_geodemographics_table(metadata)
    define_areademographics_table(metadata)
    define_DOMUS_subjectmatter_table(metadata)
    define_aim_size(metadata)
    define_ACE_sizedesignation_hierarchy_table(metadata)
    define_ACE_sizedesignation_table(metadata)
    define_accreditation(metadata)
    define_provenance_table(metadata)
    define_deprivation_index_table(metadata)
    define_notes_table(metadata)
    define_visitors_table(metadata)

    metadata.create_all(engine)
    print("Tables created successfully.")

# import os
# import sys

# # Add the project root directory to the sys.path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from sqlalchemy import MetaData
# from models.museums import define_museums_table
# from models.governance import define_governance_table
# from models.visitors import define_visitor_statistics_table
# from main import get_engine

# def create_tables(engine):
#     metadata = MetaData()

#     museums_table = define_museums_table(metadata)
#     governance_table = define_governance_table(metadata)
#     # visitor_statistics_table = define_visitor_statistics_table(metadata)

#     metadata.create_all(engine)
#     print("Tables created successfully.")

# if __name__ == "__main__":
#     engine = get_engine()
#     create_tables(engine)
