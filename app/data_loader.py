# app/data_loader.py

from .data_utils import load_json_file, dicts_to_docs
from langchain.schema import Document
import json

def sales_dict_to_docs(sales_json: dict):
    """
    Convert raw sales JSON into LangChain Documents.
    Returns a list of Document objects + aggregated document for indexing.
    """
    sales_data = sales_json.get("sales", [])
    docs = dicts_to_docs(
        sales_data,
        text_fields=["description", "notes"],
        metadata_fields=["id", "store_id"]
    )

    aggregated_doc = Document(
        page_content=json.dumps(sales_data),
        metadata={"type": "aggregate", "store_id": sales_json.get("store_id")}
    )
    return docs, aggregated_doc

def dds_defs_dict_to_docs(dds_defs: dict):
    """
    Convert DDS definitions JSON into LangChain Documents
    """
    definitions = dds_defs.get("definitions", [])
    return dicts_to_docs(
        definitions,
        text_fields=["text"],
        metadata_fields=["id", "category"]
    )
