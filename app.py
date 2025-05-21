import streamlit as st
import requests
import json
import pandas as pd

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
            return "Error: Unable to parse response.", None
    else:
        return f"Error: {response.status_code} - {response.text}", None

def format_response(response_json):
    data = response_json.get("answer", [])
    if not data:
        return "No relevant responses found.", None
    
    formatted_output = "Here are the top 3 relevant responses:\n\n"
    responses = []
    for i, item in enumerate(data[:3], start=1):
        question = item["metadata"].get("question", "Unknown Question").strip()
        answer = item["metadata"].get("answer", "No Answer Available").strip()
        responses.append((question, answer))
        formatted_output += f"{i}. *{question}*\n\n   `{answer}`\n\n"
        formatted_output += "-----------------------------------\n\n"
    
    return formatted_output, responses

# Store feedback data
if "feedback_data" not in st.session_state:
    st.session_state.feedback_data = []

# Streamlit UI
st.title("Smartkarma Compliance Bot [BETA]")

# User Input for API Token
api_token = st.text_input("Enter Token", type="password")
user_query = st.text_area("Enter your question")

if st.button("Submit Query"):
    if api_token and user_query:
        with st.spinner("Fetching response..."):
            response_text, responses = call_api(api_token, user_query)
        st.markdown(response_text)
        
        # if responses:
        #     for question, answer in responses:
        #         col1, col2 = st.columns(2)
        #         with col1:
        #             if st.button(f"👍 {question[:30]}...", key=f"up_{question}"):
        #                 st.session_state.feedback_data.append((question, answer, "up"))
                # with col2:
                #     if st.button(f"👎 {question[:30]}...", key=f"down_{question}"):
                #         st.session_state.feedback_data.append((question, answer, "down"))
    else:
        st.error("Please enter both API token and query.")

# Display captured feedback
if st.session_state.feedback_data:
    st.subheader("Feedback Captured")
    feedback_df = pd.DataFrame(st.session_state.feedback_data, columns=["Question", "Answer", "Feedback"])
    st.dataframe(feedback_df)



import streamlit as st
import os
import io
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


# Load credentials from environment (GitHub Secret)
service_account_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/drive.file"]
)

# Build the Google Drive service
drive_service = build("drive", "v3", credentials=credentials)

# Define your target Google Drive folder ID here
TARGET_FOLDER_ID = "1FQkZR9zRe6D1dnjtM2dcGK73__TWKGlz"

# Streamlit file uploader
st.title("Upload Completed DDQ")
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file:
    # Upload to specified folder
    file_metadata = {
        "name": uploaded_file.name,
        "parents": [TARGET_FOLDER_ID]
    }
    media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.type)
    uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    
    st.success(f"File uploaded to Google Drive folder! File ID: {uploaded.get('id')}")