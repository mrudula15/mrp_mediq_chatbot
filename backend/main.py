import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

# Load API key from .env
load_dotenv()
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_groq import ChatGroq
from backend.answer_generator import get_natural_language_response
from backend.db_utils import connect_db, get_schema, validate_sql_query
from backend.sql_chain import get_sql_chain

# In-memory chat history (temporary)
chat_history = []


groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing. Please check your .env file.")

# Initialize FastAPI
app = FastAPI()

# Test database connection
@app.get("/test_db")
def test_db():
    try:
        connect_db()
        return {"status": "Connected to SQL Server!"}
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
        schema_response = get_schema()
        database_schema = schema_response.get("database_schema", {})

        schema_text = "\n".join(
            [f"Table: {table}, Columns: {', '.join([col['column'] for col in columns])}"
             for table, columns in database_schema.items()]
        )

        # Generate SQL using LangChain chain
        chain = get_sql_chain(lambda: schema_text)

        # Prepare chat history text
        chat_text = "\n".join(chat_history[-5:])  # Keep last 5 exchanges

        # Run chain with history
        sql_query = chain.invoke({
            "question": request.query,
            "chat_history": chat_text
        })

        # Validate SQL before execution
        is_valid, validation_message = validate_sql_query(sql_query, database_schema)
        if not is_valid:
            return {"error": f"Invalid SQL: {validation_message}"}

        # Execute SQL query
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()

        if not result:
            return {"query": sql_query, "results": "No data found."}

        # Format results as JSON
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in result]

        # Get natural language response
        nl_response = get_natural_language_response(llm, schema_text, request.query, sql_query, data)

        # Save to chat history
        chat_history.append(f"User: {request.query}")
        chat_history.append(f"Assistant: {nl_response}")

        # Return final response
        return {
            "query": sql_query,
            "results": data,
            "answer": nl_response
        }


    except Exception as e:
        return {"error": str(e)}


# Run FastAPI server
if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000)