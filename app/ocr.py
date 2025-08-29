# app/ocr.py
import os
from pdf2image import convert_from_path
import easyocr
import uuid
from PIL import Image
from typing import List, Dict

_reader = None

def get_reader(lang_list=['en'], use_gpu=False):
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(lang_list, gpu=use_gpu)
    return _reader

def save_uploadedfile(uploaded_file, dest_folder="/tmp"):
    os.makedirs(dest_folder, exist_ok=True)
    ext = uploaded_file.name.split('.')[-1].lower()
    fname = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(dest_folder, fname)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def pdf_to_images(pdf_path, dpi=300):
    pages = convert_from_path(pdf_path, dpi=dpi)
    out_paths = []
    for i, page in enumerate(pages):
        out = f"/tmp/{os.path.basename(pdf_path)}_p{i}.png"
        page.save(out, "PNG")
        out_paths.append(out)
    return out_paths

def ocr_image(path, lang_list=['en'], use_gpu=False):
    reader = get_reader(lang_list, use_gpu)
    raw = reader.readtext(path, detail=1)  # list of (bbox, text, conf)
    tokens = []
    for bbox_pts, text, conf in raw:
        xs = [p[0] for p in bbox_pts]
        ys = [p[1] for p in bbox_pts]
        bbox = [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]
        tokens.append({"text": text.strip(), "confidence": float(conf), "bbox": bbox})
    return tokens

def ocr_file(path, lang_list=['en'], use_gpu=False):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        images = pdf_to_images(path)
    else:
        images = [path]
    pages = []
    for img in images:
        toks = ocr_image(img, lang_list, use_gpu)
        pages.append({"image_path": img, "tokens": toks})
    return pages
