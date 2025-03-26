from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# loading api keys
load_dotenv()


# Load LLM
llm = ChatGroq(
    model_name="llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY")
)

# Create prompt template
sql_prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant that converts natural language questions into SQL Server queries.
<SCHEMA>{schema}</SCHEMA>

Conversation History: {chat_history}

Question: {question}
Write a valid SQL Server SELECT query (use TOP instead of LIMIT). Do not return any explanation or markdown.

SQL Query:
""")

# Chain builder function
def get_sql_chain(get_schema_func):
    return (
        RunnablePassthrough.assign(schema=lambda _: get_schema_func())
        | sql_prompt
        | llm
        | StrOutputParser()
    )
