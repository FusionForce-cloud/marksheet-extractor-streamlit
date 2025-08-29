# app/extractor.py
import re
from collections import defaultdict

LABEL_KEYWORDS = {
    "name": ["name", "candidate name", "student name"],
    "father_name": ["father", "father's name", "s/o", "son of"],
    "mother_name": ["mother", "mother's name"],
    "dob": ["date of birth", "dob", "d.o.b"],
    "roll_no": ["roll", "roll no", "roll number", "roll no."],
    "registration_no": ["registration", "reg no", "registration no", "registration number"],
    "exam_year": ["year of examination", "exam year", "year"],
    "board": ["board", "university", "board/university"],
    "institution": ["institution", "college", "school"]
}

def flatten_tokens(pages):
    tokens = []
    for p in pages:
        tokens.extend(p.get("tokens", []))
    # sort left-to-right top-to-bottom
    tokens = sorted(tokens, key=lambda t: (t['bbox'][1], t['bbox'][0]))
    return tokens

def find_label_matches(tokens):
    text_blob = "\n".join([t["text"] for t in tokens])
    found = {}
    for key, kws in LABEL_KEYWORDS.items():
        pattern = r"(?i)(" + "|".join([re.escape(k) for k in kws]) + r")[:\s\-]*([^\n]{0,120})"
        m = re.search(pattern, text_blob)
        if m:
            val = m.group(2).strip().split("\n")[0].strip(":- ")
            if val:
                found[key] = {"value": val, "confidence": 0.6, "source": "label-match"}
    return found

def regex_extract(tokens):
    tb = " ".join([t["text"] for t in tokens])
    cands = {}
    dob = re.search(r'\b(\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4})\b', tb)
    if dob:
        cands["dob"] = {"value": dob.group(1), "confidence": 0.8, "source": "regex"}
    roll = re.search(r'(?i)\broll(?:[:\s]*no\.?|[:\s]*number)?[:\s]*([A-Za-z0-9\-\/]+)\b', tb)
    if roll:
        cands["roll_no"] = {"value": roll.group(1), "confidence": 0.75, "source": "regex"}
    reg = re.search(r'(?i)\b(registration|reg)\s*(?:no\.?|number)?[:\s]*([A-Za-z0-9\-\/]+)\b', tb)
    if reg:
        cands["registration_no"] = {"value": reg.group(2), "confidence": 0.7, "source": "regex"}
    year = re.search(r'\b(19|20)\d{2}\b', tb)
    if year:
        cands["exam_year"] = {"value": year.group(0), "confidence": 0.7, "source": "regex"}
    return cands

def parse_subjects(pages):
    # naive parsing: find lines that contain subject-like words and numbers adjacent
    subjects = []
    for p in pages:
        toks = p.get("tokens", [])
        # bucket tokens by their mid-y
        rows = {}
        for t in toks:
            midy = (t["bbox"][1] + t["bbox"][3]) // 2
            rows.setdefault(midy, []).append(t)
        for midy, row in rows.items():
            row_sorted = sorted(row, key=lambda x: x['bbox'][0])
            line = " ".join([r['text'] for r in row_sorted])
            m = re.search(r'([A-Za-z\-\&\(\)\/\s]{3,})\s+(\d{1,3})\s+(\d{1,3})(?:\s+([A-Za-z0-9]))?', line)
            if m:
                subj = m.group(1).strip()
                maxm = int(m.group(2))
                obt = int(m.group(3))
                grade = m.group(4) if m.group(4) else None
                # bbox take min x of first token to max x of last token
                bbox = [row_sorted[0]['bbox'][0], min([r['bbox'][1] for r in row_sorted]),
                        row_sorted[-1]['bbox'][2], max([r['bbox'][3] for r in row_sorted])]
                subjects.append({"subject": subj, "max_marks": maxm, "obtained": obt, "grade": grade, "confidence": 0.6, "bbox": bbox})
    return subjects

def extract_raw(pages):
    tokens = flatten_tokens(pages)
    fields = {}
    fields.update(find_label_matches(tokens))
    fields.update(regex_extract(tokens))
    subjects = parse_subjects(pages)
    # fallback for name: choose longest multi-word token
    multi = [t['text'] for t in tokens if len(t['text'].split())>1]
    if multi and "name" not in fields:
        fields["name"] = {"value": max(multi, key=len), "confidence": 0.35, "source": "longest-text"}
    return {"fields": fields, "subjects": subjects, "tokens": tokens}
