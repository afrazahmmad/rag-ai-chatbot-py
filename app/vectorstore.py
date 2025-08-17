"""
vectorstore.py
- DDS index (static) → ek dafa build & cache
- Store index (dynamic) → cache + hash-based change detection (+ optional TTL)
"""

import os
import json
import hashlib
import time
from typing import List, Tuple
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from .config import (
    EMBEDDING_MODEL, OPENAI_API_KEY, INDEX_ROOT, FORCE_REBUILD,
    SALES_CACHE_TTL_MIN, now_ts,
)

# ---------- Embeddings factory ----------
def _emb():
    return OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)

# ---------- Paths ----------
def _dds_dir(dds_id: str) -> str:
    return os.path.join(INDEX_ROOT, "dds", f"dds_{dds_id}")

def _store_dir(store_id: str) -> str:
    return os.path.join(INDEX_ROOT, "store", f"store_{store_id}")

def _meta_path(folder: str) -> str:
    return os.path.join(folder, "meta.json")

def _exists(folder: str) -> bool:
    return os.path.isdir(folder) and os.path.exists(os.path.join(folder, "index.faiss"))

# ---------- Helpers ----------
def _hash_jsonable(obj) -> str:
    """
    JSON hash for change detection.
    Ensures consistent string (sorted keys) → stable hash.
    """
    s = json.dumps(obj, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def _read_meta(folder: str) -> dict:
    try:
        with open(_meta_path(folder), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write_meta(folder: str, meta: dict):
    try:
        with open(_meta_path(folder), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
    except Exception:
        pass

# ---------- DDS index (static) ----------
def build_or_load_dds_index(dds_id: str, docs: List[Document]) -> FAISS:
    """
    DDS training is static → build once, then load from disk.
    Only rebuild if FORCE_REBUILD is true or index missing.
    """
    folder = _dds_dir(dds_id)
    os.makedirs(folder, exist_ok=True)
    emb = _emb()
    if _exists(folder) and not FORCE_REBUILD:
        return FAISS.load_local(folder, emb, allow_dangerous_deserialization=True)

    vs = FAISS.from_documents(docs, emb)
    vs.save_local(folder)
    # save small meta (optional)
    _write_meta(folder, {"type": "dds", "dds_id": dds_id, "built_at": now_ts()})
    return vs

# ---------- Store index (dynamic, API) ----------
def build_or_update_store_index(store_id: str, docs: List[Document], raw_sales_json: dict) -> FAISS:
    """
    Store-wise index:
    - Uses hash(raw_sales_json) to decide whether to rebuild
    - Optional TTL (minutes) can also force refresh if too old
    """
    folder = _store_dir(store_id)
    os.makedirs(folder, exist_ok=True)
    emb = _emb()

    incoming_hash = _hash_jsonable(raw_sales_json)
    meta = _read_meta(folder)
    have_index = _exists(folder)

    # TTL check (if configured)
    ttl_expired = False
    if SALES_CACHE_TTL_MIN > 0 and meta.get("built_at"):
        age_min = (now_ts() - int(meta["built_at"])) / 60.0
        ttl_expired = age_min >= SALES_CACHE_TTL_MIN

    # Decide rebuild
    must_rebuild = FORCE_REBUILD or (not have_index) or ttl_expired or (meta.get("data_hash") != incoming_hash)

    if not must_rebuild:
        # Reuse existing index → fast startup
        return FAISS.load_local(folder, emb, allow_dangerous_deserialization=True)

    # Rebuild index (simple & robust)
    vs = FAISS.from_documents(docs, emb)
    vs.save_local(folder)

    # Update meta (hash + timestamps)
    _write_meta(folder, {
        "type": "store",
        "store_id": store_id,
        "data_hash": incoming_hash,
        "built_at": now_ts(),
        "ttl_min": SALES_CACHE_TTL_MIN
    })
    return vs
