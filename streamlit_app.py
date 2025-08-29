import streamlit as st
import openai
import requests
import base64
import json

# Google Vision API
def google_ocr(image_file, api_key):
    content = base64.b64encode(image_file.read()).decode("utf-8")
    body = {
        "requests": [
            {
                "image": {"content": content},
                "features": [{"type": "TEXT_DETECTION"}],
            }
        ]
    }
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"
    response = requests.post(url, json=body)
    result = response.json()

    try:
        return result["responses"][0]["fullTextAnnotation"]["text"]
    except Exception:
        return "No text detected."

# OpenAI OCR (using GPT-4o-mini with image input)
def openai_ocr(image_file, api_key):
    openai.api_key = api_key

    # Convert to base64
    image_b64 = base64.b64encode(image_file.read()).decode("utf-8")

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an OCR assistant. Extract text accurately."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract text from this image:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ]
            }
        ],
        max_tokens=500
    )
    return response.choices[0].message["content"]

# Streamlit UI
st.title("📑 OCR App (OpenAI + Google Vision)")

uploaded_file = st.file_uploader("Upload an image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    if st.button("Run OCR"):
        text_result = None

        if "OPENAI_API_KEY" in st.secrets:
            st.info("Using OpenAI OCR...")
            uploaded_file.seek(0)  # reset file pointer
            text_result = openai_ocr(uploaded_file, st.secrets["OPENAI_API_KEY"])

        elif "GOOGLE_API_KEY" in st.secrets:
            st.info("Using Google Vision OCR...")
            uploaded_file.seek(0)  # reset file pointer
            text_result = google_ocr(uploaded_file, st.secrets["GOOGLE_API_KEY"])

        else:
            st.error("No API key found in secrets. Please add OPENAI_API_KEY or GOOGLE_API_KEY.")

        if text_result:
            st.subheader("Extracted Text")
            st.text_area("Result", text_result, height=300)
