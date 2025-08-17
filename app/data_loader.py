"""
data_loader.py
- JSON (dict) → LangChain Documents conversion
- Profiles auto-build: SALES, MANAGER, FINANCE, etc.
"""

from typing import List, Tuple, Dict, Any
from langchain.docstore.document import Document

def _safe_items(maybe_dict: Any):
    """Dict ke ilawa kuch ho to silent skip karo (robust parsing)."""
    if isinstance(maybe_dict, dict):
        return maybe_dict.items()
    return []

def sales_dict_to_docs(data: Dict[str, Any]) -> Tuple[List[Document], Document]:
    """
    Extended sales JSON ko read kar ke:
      - har person ka profile doc banata hai (roles + metrics lines)
      - aggregated summary doc banata hai (quick lookup ke liye)
    JSON structure flexible hai; safe traversal ke saath iterate karte hain.
    """
    people_profiles: Dict[str, Dict[str, Any]] = {}

    # Top-level roles like: SALESPERSON / MANAGER / FINANCE
    for role, role_blob in _safe_items(data):
        for category, metrics in _safe_items(role_blob):      # e.g., units / front_end_gross / back_end_gross / total_gross
            for metric, people in _safe_items(metrics):       # e.g., MTD / LM / YTD / LAST_90_DAYS / NEW_UNITS_MTD ...
                for person, value in _safe_items(people):     # e.g., "Alice": 12
                    prof = people_profiles.setdefault(person, {"roles": set(), "lines": []})
                    prof["roles"].add(role)
                    # Human-readable line; easy for LLM to use
                    prof["lines"].append(f"- {role} | {category} {metric}: {value}")

    sales_docs: List[Document] = []
    aggregated_lines: List[str] = []

    for person, prof in sorted(people_profiles.items()):
        role_str = ", ".join(sorted(prof["roles"])) if prof["roles"] else "UNKNOWN"
        header = f"{person} is in DDS system ({role_str}). Performance:"
        page = header + "\n" + "\n".join(sorted(prof["lines"]))
        sales_docs.append(
            Document(
                page_content=page,
                metadata={"type": "profile", "name": person, "roles": list(prof["roles"])}
            )
        )
        # aggregated line helps global awareness
        aggregated_lines.append(f"{person}: " + " | ".join(sorted(prof["lines"])))

    aggregated_doc = Document(
        page_content="All profiles summary:\n" + "\n".join(aggregated_lines),
        metadata={"type": "all_summary"}
    )
    return sales_docs, aggregated_doc

def dds_defs_dict_to_docs(defs: Dict[str, Any]) -> List[Document]:
    """
    DDS definitions JSON (static) ko simple key:value docs me convert karta.
    """
    docs: List[Document] = []
    for key, value in (defs or {}).items():
        docs.append(Document(page_content=f"{key}: {value}", metadata={"type": "DDS_term", "key": key}))
    return docs
