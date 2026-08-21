from sqlalchemy import create_engine

def get_engine():
    user = 'postgres'
    password = 'wodegnome'
    host = 'localhost'
    port = '5432'
    db_name = 'museums_db'
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db_name}')
    return engine

# import psycopg2
# from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
# from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

# # Define your database credentials
# user = 'postgres'
# password = 'root'
# host = 'localhost'
# port = '5432'
# db_name = 'museums_db'

# # Connect to the default database
# connection = psycopg2.connect(
#     user=user,
#     password=password,
#     host=host,
#     port=port,
#     dbname='postgres'
# )
# connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
# cursor = connection.cursor()

# # Create the museums_db database if it does not exist
# try:
#     cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
#     exists = cursor.fetchone()
#     if not exists:
#         cursor.execute(f"CREATE DATABASE {db_name}")
#         print(f"Database '{db_name}' created successfully.")
#     else:
#         print(f"Database '{db_name}' already exists.")
# except Exception as e:
#     print(f"Failed to create or check database: {e}")
# finally:
#     cursor.close()
#     connection.close()
