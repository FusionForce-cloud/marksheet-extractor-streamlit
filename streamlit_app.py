import os
import streamlit as st
import pdfplumber
from google.cloud import aiplatform

# Set path to your Google service account JSON key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]

st.set_page_config(page_title="AI Marksheet Extractor (Google)", layout="wide")
st.title("📄 AI-Based Marksheet Extractor (Google)")
st.write("Upload a marksheet (PDF) to extract candidate details + subject scores in JSON.")

uploaded_file = st.file_uploader("Upload Marksheet (PDF)", type=["pdf"])

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_fields_with_google_ai(text):
    try:
        client = aiplatform.gapic.PredictionServiceClient()

        endpoint = st.secrets["GOOGLE_AI_ENDPOINT"]  # Vertex AI endpoint
        instance = {
            "content": f"""
            You are an AI marksheet parser. Extract all details from the following marksheet text
            and return JSON strictly in this structure:

            {{
              "Candidate Name": "",
              "Father's Name": "",
              "Mother's Name": "",
              "Roll No": "",
              "Registration No": "",
              "DOB": "",
              "Exam Year": "",
              "Board/University": "",
              "Institution": "",
              "Subjects": [
                  {{"Subject": "", "Marks": "", "Max Marks": "", "Grade": ""}}
              ]
            }}

            Text:
            {text}
            """
        }

        response = client.predict(endpoint=endpoint, instances=[instance])
        return response.predictions[0]
    except Exception as e:
        st.error(f"⚠️ Google API Error: {e}")
        return None

if uploaded_file:
    raw_text = extract_text_from_pdf(uploaded_file)
    st.subheader("📖 Extracted Raw Text")
    st.text_area("Raw Text", raw_text, height=200)

    if st.button("🔍 Extract Details"):
        extracted_json = extract_fields_with_google_ai(raw_text)
        if extracted_json:
            st.subheader("✅ Extracted JSON")
            st.json(extracted_json)
