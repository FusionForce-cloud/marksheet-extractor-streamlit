import streamlit as st
import openai
import pdfplumber
import os
import re

# Load API key from Streamlit secrets
API_KEY = st.secrets["OPENAI_API_KEY"]
openai.api_key = API_KEY

# Function to extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Function to clean and format extracted JSON from LLM response
def extract_json_from_response(response_text):
    try:
        # Find JSON-like structure in response
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            return json_match.group()
        else:
            return "{}"
    except:
        return "{}"

# Function to query OpenAI for structured data extraction
def extract_marksheet_details(text):
    prompt = f"""
    Extract the following details from the given marksheet text and return as JSON:
    - Candidate Name
    - Father’s/Mother’s Name
    - Roll Number
    - Registration Number
    - Date of Birth
    - Exam Year
    - Board/University
    - Institution
    - Subject-wise marks (Subject, Marks Obtained, Max Marks, Result)

    Text:
    {text}
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # You can also use "gpt-4o" or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are an information extraction assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    raw_output = response.choices[0].message.content
    return extract_json_from_response(raw_output)

# Streamlit UI
st.title("📄 Marksheet Data Extractor")
st.write("Upload a marksheet (PDF) and extract structured details in JSON format.")

uploaded_file = st.file_uploader("Upload Marksheet PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)

    st.subheader("Extracted Text")
    st.text_area("Raw Text", extracted_text, height=200)

    if st.button("Extract Details"):
        with st.spinner("Extracting details using AI..."):
            extracted_json = extract_marksheet_details(extracted_text)

        st.subheader("Extracted JSON")
        st.json(extracted_json)
