# app/data_utils.py

import json
from typing import List, Dict
from langchain.schema import Document

def validate_json(data: dict, required_fields: list) -> bool:
    """Check if JSON has all required fields"""
    return all(field in data for field in required_fields)

def load_json_file(path: str) -> dict:
    """Safely load JSON from file"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON: {e}")
        return {}

def dicts_to_docs(data_list: List[Dict], text_fields: list, metadata_fields: list = None) -> List[Document]:
    """Convert a list of dictionaries to LangChain Document objects"""
    docs = []
    for item in data_list:
        # skip items missing required text fields
        if not all(f in item for f in text_fields):
            continue
        text = " ".join(str(item[f]) for f in text_fields if item.get(f) is not None)
        metadata = {f: item.get(f) for f in (metadata_fields or [])}
        docs.append(Document(page_content=text, metadata=metadata))
    return docs
