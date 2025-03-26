from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

# load api key
load_dotenv()

# natural language answer generator
def get_natural_language_response(llm, schema_text, question, sql_query, result):
    response_prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant. Based on the given schema, question, SQL query, and result,
write a clear natural language response that summarizes the result for the user.

<SCHEMA>{schema}</SCHEMA>
Question: {question}
SQL Query: {query}
SQL Result: {result}

Answer:""")

    response_chain = (
            response_prompt
            | llm
            | StrOutputParser()
    )

    return response_chain.invoke({
        "schema": schema_text,
        "question": question,
        "query": sql_query,
        "result": result
    })