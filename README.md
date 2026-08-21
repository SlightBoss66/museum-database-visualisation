Overview
This project focuses on the design and implementation of a relational database schema to manage hierarchical data for UK museums. The project involves transforming a dataset of UK museums, which originally contained unstructured data, into a normalized database schema stored in PostgreSQL. The dataset includes information on museum governance, accreditation, subject matter, visitor statistics, and geographic distribution.

Key Features
Hierarchical Data Normalization: The project processes multi-level hierarchical data and transforms it into a normalized relational database schema.
SQLAlchemy: Utilizes SQLAlchemy, an Object-Relational Mapper (ORM) for Python, to manage database connections and execute queries efficiently.
PostgreSQL: Data is stored in a PostgreSQL database, ensuring data integrity through foreign keys and proper indexing.
Error Handling: Comprehensive error handling to ensure data consistency and prevent invalid operations.
Interactive Queries: A series of predefined SQL queries are implemented to retrieve data based on specific requirements.

Technologies Used
Python: The core language used to process the data and interact with the database.
SQLAlchemy: ORM used for database management and query execution.
PostgreSQL: Relational database used to store the museum data.
Pandas: Used for data manipulation during the transformation from the unstructured dataset.
Setup and Installation
Prerequisites
Before running this project, ensure you have the following installed:

Python 3.x
PostgreSQL
Required Python packages

Installation Steps

1. Clone the repository:
   git clone https://github.com/yourusername/uk-museums-database.git cd uk-museums-database

2. Set up PostgreSQL database:
  - Create a PostgreSQL database to store the museum data
  - Update the database credentials in db_connector.py

3. Run the database schema creation:

    bash> python data_insertion/insert_museums_data.py

4. Execute queries:

    Run the query scripts in the queries directory to retrieve information.
    For example, to run query 1:
    bash > python queries/query_1.py

Queries Included

1. Get museums with 'Unaccredited' accreditation
2. Get museums with AIM Size as 'Small'
3. Get number of visitors for a particular museum
4. Get museums started after year 2000
5. Get museums in the 'Manchester' admin area
6. Get museums in the 'West Midlands' region
7. Get museums founded by 'Barney Hansford'
8. Update museum data
9. Add a new museum to the database
10. Delete all tables from the database

Conclusion
This project successfully transforms hierarchical, unstructured data into a relational database schema, allowing for efficient querying and updates. Future applications include data visualization tools, reporting systems, and broader collaboration with cultural institutions.
