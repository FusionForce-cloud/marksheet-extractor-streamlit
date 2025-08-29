import os
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI

# Load API key from environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

st.set_page_config(page_title="AI Marksheet Extractor", layout="wide")

st.title("📄 AI-Based Marksheet Extractor")
st.write("Upload a marksheet (PDF) and extract candidate details + subject scores in JSON.")

# Upload PDF
uploaded_file = st.file_uploader("Upload Marksheet (PDF)", type=["pdf"])

if uploaded_file:
    # Read PDF text
    pdf_reader = PdfReader(uploaded_file)
    text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

    st.subheader("📖 Extracted Raw Text")
    st.text_area("Raw Text", text, height=200)

    if st.button("🔍 Extract Details"):
        try:
            # Prompt for extraction
            prompt = f"""
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

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            result = response.choices[0].message.content
            st.subheader("✅ Extracted JSON")
            st.json(result)

        except Exception as e:
            st.error(f"Error: {e}")
