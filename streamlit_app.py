# fastapi_app_openai.py

import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pdfplumber
import openai

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="AI Marksheet Extractor API", description="Upload PDF marksheets and get extracted JSON.")

def call_openai(prompt: str):
    """Call OpenAI ChatCompletion API."""
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

@app.post("/extract")
async def extract_marksheet(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are supported"})

    # Read PDF text
    text = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    # Prepare prompt for OpenAI
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

    try:
        result = call_openai(prompt)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

