import streamlit as st
import requests

# Streamlit UI
st.set_page_config(page_title="MediQ SQL Chatbot", layout="wide")
st.title("LLM SQL Query Chatbot")

# User input
user_query = st.text_input("Ask me anything...")

if st.button("Generate SQL"):
    response = requests.post(
        "http://127.0.0.1:8000/generate_sql",  # Calls FastAPI
        json={"query": user_query}
    )

    if response.status_code == 200:
        response_data = response.json()

        # Show generated SQL query
        st.write("Generated SQL Query:")
        st.code(response_data["query"], language="sql")

        # Show query results
        if "results" in response_data and response_data["results"]:
            st.write("Query Results:")
            st.dataframe(response_data["results"])  # Displays results in a table format
        else:
            st.warning("No results found.")

    else:
        st.error("Error generating SQL.")
