# app/llm_client.py
import os
import json
import openai
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

SCHEMA_INSTRUCTIONS = """
You MUST ONLY RETURN a single valid JSON object (no extra text).
Structure exactly:
{
  "candidate_details": {
    "name": {"value": string|null, "confidence": number},
    "father_name": {"value": string|null, "confidence": number},
    "mother_name": {"value": string|null, "confidence": number},
    "dob": {"value": string|null, "confidence": number},
    "roll_no": {"value": string|null, "confidence": number},
    "registration_no": {"value": string|null, "confidence": number},
    "exam_year": {"value": string|null, "confidence": number},
    "board_university": {"value": string|null, "confidence": number},
    "institution": {"value": string|null, "confidence": number},
    "issue_place_date": {"value": string|null, "confidence": number}
  },
  "subjects": [
    {"subject": string|null, "max_marks": number|null, "obtained": number|null, "grade": string|null, "confidence": number, "bbox": [x1,y1,x2,y2]|null}
  ],
  "overall": {"result": string|null, "division": string|null, "grade": string|null, "confidence": number},
  "raw_extraction": {}
}
All confidence values must be between 0 and 1.
If uncertain about a value, return null and confidence near 0.0.
"""

def build_prompt(raw):
    prompt = "You are given raw OCR extraction candidates from a marksheet. Normalize, correct obvious OCR errors, infer types (date, number), and return JSON that matches the exact schema.\n\n"
    prompt += "Raw data:\n" + json.dumps(raw, indent=2)
    prompt += "\n\nSchema instructions:\n" + SCHEMA_INSTRUCTIONS
    prompt += "\n\nRules: - Convert dates to DD-MM-YYYY if possible. - Convert numeric fields to numbers. - For each field, include a confidence (0-1). - If you cannot safely determine, return null with low confidence.\n"
    return prompt

def call_openai_normalize(raw, model="gpt-4o-mini", temperature=0.0):
    if OPENAI_API_KEY is None:
        raise RuntimeError("OPENAI_API_KEY not set in environment variables")
    prompt = build_prompt(raw)
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role":"system","content":"You output JSON only."},
                  {"role":"user","content":prompt}],
        max_tokens=800,
        temperature=temperature
    )
    content = resp.choices[0].message['content']
    # parse JSON - be forgiving
    try:
        return json.loads(content)
    except Exception as e:
        # try to extract JSON substring
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            return json.loads(content[start:end+1])
        raise
