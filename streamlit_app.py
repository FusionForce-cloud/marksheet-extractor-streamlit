import streamlit as st
import pdfplumber
from PIL import Image
import pytesseract
import io
import json

# ----------------------------
# Helper Functions
# ----------------------------
def extract_text_from_pdf(file):
    """Extract text from a PDF using pdfplumber"""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_image(file):
    """Extract text from an image using pytesseract"""
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text

def parse_marksheet_text(text):
    """
    Naive marksheet parser.
    (In real case, use regex/LLM for structured extraction)
    """
    data = {}

    # Very simple demo patterns (adjust per marksheet format)
    lines = text.splitlines()
    for line in lines:
        line = line.strip()

        if "Name" in line and "Father" not in line:
            data["Name"] = line.split(":")[-1].strip()
        elif "Father" in line or "Mother" in line:
            data["Parent"] = line.split(":")[-1].strip()
        elif "Roll" in line:
            data["Roll No"] = line.split(":")[-1].strip()
        elif "Reg" in line:
            data["Registration No"] = line.split(":")[-1].strip()
        elif "DOB" in line:
            data["DOB"] = line.split(":")[-1].strip()
        elif "Year" in line:
            data["Exam Year"] = line.split(":")[-1].strip()
        elif "Board" in line or "University" in line:
            data["Board/University"] = line.split(":")[-1].strip()
        elif "Institution" in line:
            data["Institution"] = line.split(":")[-1].strip()

    # Return dummy confidence scores (real app would calculate using ML/LLM)
    result = {k: {"value": v, "confidence": 0.95} for k, v in data.items()}
    return result


# ----------------------------
# Streamlit UI
# ----------------------------
st.title("📄 Marksheet Extractor")
st.write("Upload a **Marksheet (PDF or Image)** and extract details in JSON format.")

uploaded_file = st.file_uploader("Upload File", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    file_type = uploaded_file.type

    # Extract text
    if "pdf" in file_type:
        text = extract_text_from_pdf(uploaded_file)
    else:
        text = extract_text_from_image(uploaded_file)

    st.subheader("🔎 Extracted Raw Text")
    st.text(text)

    # Parse structured data
    extracted_data = parse_marksheet_text(text)

    st.subheader("📌 Extracted Fields (JSON)")
    st.json(extracted_data)

    # Option to download
    json_str = json.dumps(extracted_data, indent=4)
    st.download_button("Download JSON", json_str, file_name="marksheet_data.json", mime="application/json")
