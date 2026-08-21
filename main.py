from db_connector import get_engine
from scripts.create_tables import create_tables
from data_insertion.insert_museums_data import load_museums
from data_insertion.insert_adminarea import load_adminarea
from data_insertion.insert_governance_data import load_governance
from data_insertion.insert_governance_hierarchy import load_governance_hierarchy
from data_insertion.insert_subject_matter_hierarchy import load_subject_matter_hierarchy
from data_insertion.insert_geodemographics import load_geodemographics
from data_insertion.insert_areademographics import load_areademographics
from data_insertion.insert_domus_subjectmatter import load_DOMUS_subjectmatter
from data_insertion.insert_aim_size import load_aim_size
from data_insertion.insert_ace_size_designation_hierarchy import load_ace_size_designation_hierarchy
from data_insertion.insert_ace_size_designation import load_ace_size_designation
from data_insertion.insert_accreditation import load_accreditation
from data_insertion.insert_provenance import load_provenance
from data_insertion.insert_deprivation_index import load_deprivation_index
from data_insertion.insert_notes_data import load_notes
from data_insertion.insert_visitors import load_visitors

def main():

    engine = get_engine()
    create_tables(engine)

    load_adminarea(engine)
    load_museums(engine)
    load_governance_hierarchy(engine)
    load_governance(engine)
    load_subject_matter_hierarchy(engine)
    load_geodemographics(engine)
    load_areademographics(engine)
    load_DOMUS_subjectmatter(engine)
    load_aim_size(engine)
    load_ace_size_designation_hierarchy(engine)
    load_ace_size_designation(engine)
    load_accreditation(engine)
    load_provenance(engine)
    load_deprivation_index(engine)
    load_notes(engine)
    load_visitors(engine)

if __name__ == "__main__":
    main()











# from sqlalchemy import create_engine

# # Define your database credentials
# user = 'postgres'
# password = 'root'
# host = 'localhost'
# port = '5432'
# db_name = 'museums_db'

# def get_engine():
#     engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')
#     return engine

# if __name__ == "__main__":
#     engine = get_engine()
#     print("Database engine created successfully.")