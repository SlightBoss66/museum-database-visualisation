from sqlalchemy import MetaData
from db_connector import get_engine

def run_query(engine):
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    print("All tables have been dropped successfully.")

if __name__ == "__main__":
    engine = get_engine()
    run_query(engine)
