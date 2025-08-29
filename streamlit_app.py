import streamlit as st
import openai

# Load API key from Streamlit secrets (set this in Streamlit Cloud → Settings → Secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="AI Marksheet Reader", page_icon="📄", layout="centered")

st.title("📄 AI Marksheet Reader")
st.write("Upload your marksheet (PDF/Image) and extract student details using AI.")

# File uploader
uploaded_file = st.file_uploader("Upload your marksheet", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully!")

    # Show uploaded file preview if image
    if uploaded_file.type in ["image/png", "image/jpeg"]:
        st.image(uploaded_file, caption="Uploaded Marksheet", use_column_width=True)
    else:
        st.info("PDF uploaded. Preview not available here.")

    st.write("⏳ Extracting details...")

    # Example prompt (replace with OCR + parsing later if needed)
    prompt = """
    You are an AI marksheet reader. Extract the following details from the text:

    - Candidate Name
    - Father's Name / Mother's Name
    - Roll No
    - Registration No
    - Date of Birth
    - Exam Year
    - Board/University
    - Institution
    - Subject-wise marks

    Format the output as JSON.
    """

    try:
        # Call OpenAI API
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            temperature=0
        )

        result = response.choices[0].text.strip()
        st.subheader("📌 Extracted Details")
        st.json(result)

    except Exception as e:
        st.error(f"❌ Error: {e}")
