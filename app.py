import streamlit as st
import requests
import json

def call_api(api_token, user_query):
    url = "https://cc4i4qn5g6.execute-api.ap-southeast-1.amazonaws.com/default/compliance_ddq"
    headers = {
        'API-TOKEN': api_token,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"type": "answer", "user-query": user_query})
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        try:
            return format_response(response.json())
        except:
            return "Error: Unable to parse response."
    else:
        return f"Error: {response.status_code} - {response.text}"

def format_response(response_json):
    data = response_json.get("answer", [])
    if not data:
        return "No relevant responses found."
    
    formatted_output = "Here are the top 3 relevant responses:\n\n"
    for i, item in enumerate(data[:3], start=1):
        question = item["metadata"].get("question", "Unknown Question").strip()
        answer = item["metadata"].get("answer", "No Answer Available").strip()
        formatted_output += f"{i}. *{question}*\n\n   `{answer}`\n\n"
        formatted_output += "-----------------------------------\n\n"
    
    return formatted_output

# Streamlit UI
st.title("API Query Interface")

# User Input for API Token
api_token = st.text_input("Enter API Token", type="password")
user_query = st.text_area("Enter your query")

if st.button("Submit Query"):
    if api_token and user_query:
        with st.spinner("Fetching response..."):
            response_text = call_api(api_token, user_query)
        st.markdown(response_text)
    else:
        st.error("Please enter both API token and query.")