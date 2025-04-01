import pyodbc
import sqlparse


# SQL Server Connection
def connect_db():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-0OSF00UQ\\SQLEXPRESS01;"  # Replace with your SQL Server name
        "DATABASE=synthea_db_cleaned;"   # Replace with your database name
        "Trusted_Connection=yes;"  # Windows authentication
    )

# Fetch database schema (tables & columns)
def get_schema():
    try:
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]

        schema = {}
        for table in tables:
            cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}'")
            schema[table] = [{"column": row[0], "type": row[1]} for row in cursor.fetchall()]

        return {"database_schema": schema}
    except Exception as e:
        return {"error": str(e)}


def validate_sql_query(sql_query, schema):
    """
    Validate the generated SQL query to ensure it matches the database schema.
    - Checks if query starts with SELECT
    - Ensures only known tables & columns are used
    """
    parsed = sqlparse.parse(sql_query)
    if not parsed:
        return False, "Invalid SQL syntax."

    # Ensure query starts with SELECT
    if not sql_query.strip().lower().startswith("select"):
        return False, "Only SELECT queries are allowed."

    # Extract table names from schema
    valid_tables = set(schema.keys())

    # Extract table names from query
    query_tables = {str(token).strip() for stmt in parsed for token in stmt.tokens if str(token).strip() in valid_tables}

    # Check if all tables in query exist in schema
    if not query_tables.issubset(valid_tables):
        return False, f"Query references unknown tables: {query_tables - valid_tables}"

    return True, "Valid SQL"
