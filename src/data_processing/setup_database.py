import pyodbc

# Define connection details
server = 'Chaitanya'  # Use your server name from Step 1
database = 'synthea_db'  # Use your database name from Step 3
driver = 'ODBC Driver 17 for SQL Server'  # Using ODBC Driver 17

# Connection string using Windows Authentication
conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"

try:
    # Establish connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connected to SQL Server successfully!")

    # Test query to confirm connection
    cursor.execute("SELECT name FROM sys.tables;")  # Fetch list of tables
    tables = cursor.fetchall()
    print("Tables in database:", [table[0] for table in tables])

except Exception as e:
    print("Connection failed:", str(e))

import pandas as pd
import os

# Define folder containing CSV files
csv_folder = r"C:\Users\palad\synthea\output\csv"  

# List of required tables from your schema
required_tables = ["patients", "encounters", "conditions", "claims", "medications", "payers"]

# Find matching CSV files
csv_files = {f.replace('.csv', ''): os.path.join(csv_folder, f) for f in os.listdir(csv_folder) if f.endswith('.csv')}
filtered_files = {table: csv_files[table] for table in required_tables if table in csv_files}

# Print found tables
print(f"Found {len(filtered_files)} required tables:", list(filtered_files.keys()))

# Display column names for each required table
for table, path in filtered_files.items():
    df = pd.read_csv(path, nrows=5)  # Read only first 5 rows for preview
    print(f"\n🔹 Table: {table.upper()}")
    print(df.columns)

# Creating required tables in SQL Server
table_queries = {
       "payers": """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'payers')
        BEGIN
            CREATE TABLE payers (
                Id VARCHAR(200) PRIMARY KEY,
                NAME VARCHAR(50),
                OWNERSHIP VARCHAR(50)
            )
        END;
    """,
    "patients": """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'patients')
        BEGIN
            CREATE TABLE patients (
                Id VARCHAR(200) PRIMARY KEY,
                BIRTHDATE DATE,
                GENDER VARCHAR(2),
                RACE VARCHAR(50),
                ETHNICITY VARCHAR(50),
                ZIP VARCHAR(5),
                HEALTHCARE_EXPENSES FLOAT,
                HEALTHCARE_COVERAGE FLOAT
            )
        END;
    """,
    "encounters": """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'encounters')
        BEGIN
            CREATE TABLE encounters (
                Id VARCHAR(200) PRIMARY KEY,
                PATIENT VARCHAR(200),
                START DATETIME,
                STOP DATETIME,
                ENCOUNTERCLASS VARCHAR(50),
                BASE_ENCOUNTER_COST FLOAT,
                TOTAL_CLAIM_COST FLOAT,
                PAYER_COVERAGE FLOAT,
                FOREIGN KEY (PATIENT) REFERENCES patients(Id)
            )
        END;
    """,
    "conditions": """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'conditions')
        BEGIN
            CREATE TABLE conditions (
                PATIENT VARCHAR(200),
                ENCOUNTER VARCHAR(200),
                CODE VARCHAR(50),
                DESCRIPTION TEXT,
                PRIMARY KEY (PATIENT, ENCOUNTER, CODE),
                FOREIGN KEY (PATIENT) REFERENCES patients(Id)
            )
        END;
    """,
    "claims": """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'claims')
        BEGIN
            CREATE TABLE claims (
                Id VARCHAR(200) PRIMARY KEY,
                PATIENTID VARCHAR(200),
                PRIMARYPATIENTINSURANCEID VARCHAR(200),
                SECONDARYPATIENTINSURANCEID VARCHAR(200),
                FOREIGN KEY (PATIENTID) REFERENCES patients(Id),
                FOREIGN KEY (PRIMARYPATIENTINSURANCEID) REFERENCES payers(Id),
                FOREIGN KEY (SECONDARYPATIENTINSURANCEID) REFERENCES payers(Id)
            )
        END;
    """,
    "medications": """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'medications')
        BEGIN
            CREATE TABLE medications (
                PATIENT VARCHAR(200),
                BASE_COST FLOAT,
                TOTALCOST FLOAT,
                PAYER_COVERAGE FLOAT,
                DISPENSES INT,
                FOREIGN KEY (PATIENT) REFERENCES patients(Id)
            )
        END;
    """
}

# Execute table creation
for table, query in table_queries.items():
    cursor.execute(query)
    conn.commit()

print("Tables created successfully!")
