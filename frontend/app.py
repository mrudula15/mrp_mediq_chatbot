import streamlit as st
import requests

# Page setup
st.set_page_config(page_title="MediQ SQL Chatbot", layout="wide")
st.title("MediQ Chatbot")

# Initialize session state
if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "auto_submit" not in st.session_state:
    st.session_state.auto_submit = False

# 🔁 When a follow-up question is clicked, this is triggered
def handle_followup_click(fq):
    st.session_state.user_query = fq
    st.session_state.auto_submit = True


# Text input (populated from session)
user_query = st.text_input("Ask me anything...", value=st.session_state.user_query)

# Manual or auto submission logic
submit_clicked = st.button("Generate SQL")

# Combine both auto and manual trigger
if submit_clicked or st.session_state.auto_submit:
    # Reset auto_submit so it doesn't run again on reload
    st.session_state.auto_submit = False

    if user_query.strip() != "":
        response = requests.post(
            "http://127.0.0.1:8000/generate_sql",
            json={"query": user_query}
        )

        if response.status_code == 200:
            response_data = response.json()

            if "error" in response_data:
                st.error(f"Error: {response_data['error']}")
            else:
                st.subheader("Generated SQL Query:")
                st.code(response_data["query"], language="sql")

                if response_data.get("results") and isinstance(response_data["results"], list):
                    st.subheader("Query Results:")
                    st.dataframe(response_data["results"])
                else:
                    st.warning("No results found.")

                st.subheader("Answer in Natural Language:")
                st.success(response_data["answer"])

                # 🎯 Show follow-up suggestions as buttons
                if "followups" in response_data:
                    st.subheader("Suggested Follow-up Questions:")
                    for fq in response_data["followups"]:
                        st.button(f"👉 {fq}", on_click=handle_followup_click, args=(fq,))


