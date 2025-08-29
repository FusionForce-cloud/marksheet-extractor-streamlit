# Marksheet Extractor - Streamlit

This repository contains a Streamlit app that performs OCR on a marksheet image/PDF, runs pre-extraction heuristics, and uses an LLM (OpenAI) to normalize and return structured JSON with confidence scores.

## Features
- OCR using EasyOCR (supports images & PDFs)
- Heuristic extraction of candidate fields and subject table parsing
- LLM normalization via OpenAI ChatCompletion to produce final JSON schema with confidences
- Streamlit UI for upload, preview, and JSON download

## Requirements
- An OpenAI API key (set as `OPENAI_API_KEY` in Streamlit secrets)
- Streamlit Cloud account (or run locally)

## How to run locally (recommended for development)
1. Create and activate a virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   ## Can try this at:

   https://marksheet-extractor-app-x3tvdcgm3kprng6bxr44uq.streamlit.app/
