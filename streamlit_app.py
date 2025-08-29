import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import openai
import io

# Configure OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("📑 Marksheet Extractor")
st.write("Upload a marksheet (PDF/Image) to extract candidate details and subject-wise marks.")

uploaded_file = st.file_uploader("Upload File", type=["pdf", "png", "jpg", "jpeg"])

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def extract_fields_with_ai(text):
    prompt = f"""
    Extract the following details from the marksheet text below:
    - Candidate Name
    - Father's/Mother's Name
    - Roll Number
    - Registration Number
    - Date of Birth
    - Exam Year
    - Board/University
    - Institution
    - Subject-wise Marks

    Provide the result strictly in JSON format with confidence scores for each field.

    Marksheet Text:
    {text}
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    else:
        text = extract_text_from_image(uploaded_file)

    st.subheader("Extracted Text:")
    st.text_area("Raw Text", text, height=200)

    if st.button("Extract Details"):
        with st.spinner("Extracting details..."):
            result = extract_fields_with_ai(text)
        st.subheader("Extracted JSON:")
        st.json(result)
