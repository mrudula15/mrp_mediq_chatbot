import pyodbc
import os
import pandas as pd

# Define your database connection parameters
server = 'LAPTOP-0OSF00UQ\\SQLEXPRESS01'  # Change if your SQL Server is on another machine
database = 'synthea_db'

# Create a connection using Windows Authentication (no password required)
try:
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        'Trusted_Connection=yes;'
    )
    cursor = conn.cursor()
    print("Connected to SQL Server successfully.")
except Exception as e:
    print("Failed to connect to SQL Server:", e)

import os
import pandas as pd

# Define the folder path where CSV files are stored
csv_folder_path = r"C:\Users\mrudu\PycharmProjects\health-equity-LLM-chatbot\backend\data\processed"

# Get a list of all CSV files in the folder
csv_files = [f for f in os.listdir(csv_folder_path) if f.endswith('.csv')]

# Check if files are detected
if not csv_files:
    print("No CSV files found in the folder.")
else:
    print(f"Found {len(csv_files)} CSV files in the folder.")

    # # Read and display the first few rows of each file (for testing)
    # for file in csv_files:
    #     file_path = os.path.join(csv_folder_path, file)
    #     df = pd.read_csv(file_path, nrows=3)  # Read first 3 rows only
    #     print(f"\nPreview of {file}:")
    #     print(df)

def create_table_from_csv(file_name, df):
    """
    Create a SQL table based on the structure of the DataFrame.
    If the table already exists, it will not be created again.
    """
    table_name = file_name.replace('.csv', '')  # Remove .csv extension
    columns = ', '.join([f"[{col}] NVARCHAR(MAX)" for col in df.columns])  # Define all columns as text for flexibility

    create_table_sql = f"""
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}')
    BEGIN
        CREATE TABLE {table_name} ({columns});
    END
    """
    cursor.execute(create_table_sql)
    conn.commit()
    print(f"Table '{table_name}' checked/created.")

# Create tables for all CSV files
for file in csv_files:
    file_path = os.path.join(csv_folder_path, file)
    df = pd.read_csv(file_path, nrows=3)  # Read small sample to get structure
    create_table_from_csv(file, df)

def insert_data_into_table(file_name, df):
    """
    Inserts data from a DataFrame into the corresponding SQL table.
    """
    table_name = file_name.replace('.csv', '')  # Match table name to CSV file name

    # Convert DataFrame to a list of tuples for SQL insertion
    records = df.astype(str).values.tolist()

    # Create SQL INSERT statement dynamically
    columns = ', '.join([f"[{col}]" for col in df.columns])
    placeholders = ', '.join(['?' for _ in df.columns])  # SQL placeholders for values
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # Insert records in batches
    try:
        cursor.executemany(insert_sql, records)
        conn.commit()
        print(f"Inserted {len(df)} rows into '{table_name}'.")
    except Exception as e:
        print(f"Error inserting data into '{table_name}': {e}")

# Read all CSVs and insert data
for file in csv_files:
    file_path = os.path.join(csv_folder_path, file)
    df = pd.read_csv(file_path)  # Read full CSV
    insert_data_into_table(file, df)
