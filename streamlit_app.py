# streamlit_app.py
import streamlit as st
from app.ocr import save_uploadedfile, ocr_file
from app.extractor import extract_raw
from app.llm_client import call_openai_normalize
import json
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Marksheet Extractor", layout="wide")

st.title("Marksheet Extractor (Streamlit)")
st.markdown("Upload an image or PDF of a marksheet. The app will run OCR, pre-extract fields, and call an LLM (OpenAI) to normalize and return JSON with confidence scores.")

with st.sidebar:
    st.header("Settings")
    model = st.selectbox("LLM model (OpenAI)", options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0)
    use_gpu = st.checkbox("Use EasyOCR GPU (not available on Streamlit Cloud)", value=False)
    st.info("Set OPENAI_API_KEY in Streamlit Secrets (section: [secrets]) before running. See README for instructions.")

uploaded = st.file_uploader("Upload marksheet (JPG/PNG/PDF)", type=["png","jpg","jpeg","pdf"])
if uploaded is not None:
    try:
        st.info("Saving file...")
        path = save_uploadedfile(uploaded)
        st.info("Running OCR (EasyOCR)...")
        pages = ocr_file(path, use_gpu=use_gpu)
        st.success(f"OCR completed — {len(pages)} page(s)")

        st.info("Running pre-extraction heuristics...")
        raw = extract_raw(pages)
        st.json(raw, expanded=False)

        st.info("Calling LLM to normalize and format JSON...")
        with st.spinner("Contacting OpenAI..."):
            normalized = call_openai_normalize(raw, model=model)
        st.success("LLM returned structured JSON")

        st.subheader("Structured JSON output")
        st.json(normalized)

        # download button
        st.download_button("Download JSON", json.dumps(normalized, indent=2), file_name="marksheet_extraction.json", mime="application/json")

        # visualize first page with bounding boxes if available
        if pages:
            st.subheader("Page 1 preview with token boxes")
            img = Image.open(pages[0]['image_path'])
            draw = ImageDraw.Draw(img)
            for t in pages[0]['tokens']:
                bbox = t.get('bbox')
                if bbox:
                    draw.rectangle(bbox, outline="red", width=2)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue(), use_column_width=True)

    except Exception as e:
        st.error(f"Error: {e}")
