import os
from dotenv import load_dotenv
import uvicorn
import pyodbc
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

# Load API key from .env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing. Please check your .env file.")

# Initialize FastAPI
app = FastAPI()

# SQL Server Connection
def connect_db():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=Chaitanya;"  # Replace with your SQL Server name
        "DATABASE=synthea_db;"   # Replace with your database name
        "Trusted_Connection=yes;"  # Windows authentication
    )

# Test database connection
@app.get("/test_db")
def test_db():
    try:
        connect_db()
        return {"status": "Connected to SQL Server!"}
    except Exception as e:
        return {"error": str(e)}

# Fetch database schema (tables & columns)
@app.get("/get_schema")
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

# Initialize LangChain with Groq's Llama3-8B model
llm = ChatGroq(
    model_name="llama3-8b-8192",
    api_key=groq_api_key
)

# SQL Prompt Template
sql_prompt = PromptTemplate.from_template(
    "Convert this natural language query into a SQL statement: {query}"
)

class QueryRequest(BaseModel):
    query: str

# Generate and execute SQL query
@app.post("/generate_sql")
def generate_sql(request: QueryRequest):
    try:
        # Fetch schema
        schema_response = get_schema()
        database_schema = schema_response.get("database_schema", {})

        # Format schema for LLM
        schema_text = "\n".join(
            [f"Table: {table}, Columns: {', '.join([col['column'] for col in columns])}"
             for table, columns in database_schema.items()]
        )

        # Prompt the LLM with database schema
        formatted_query = f"""
        Here is the database schema:
        {schema_text}

        Convert this natural language question into a **valid SQL Server SELECT query** using the given schema.
        Ensure the SQL follows SQL Server syntax (use `TOP` instead of `LIMIT`).
        Return **only the SQL query**, without explanations or markdown formatting.

        Question: {request.query}
        SQL:
        """

        # Generate SQL from LLM
        sql_response = llm.invoke(formatted_query)

        # Extract SQL query and clean formatting
        sql_query = sql_response.content.strip().replace("```sql", "").replace("```", "").strip()
        if not sql_query.lower().startswith(("select", "with")):
            return {"error": "Only SELECT queries are allowed."}

        # Execute SQL query
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()

        # Format results as JSON
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in result]

        return {"query": sql_query, "results": data}

    except Exception as e:
        return {"error": str(e)}

# Run FastAPI server
if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
