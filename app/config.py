"""
config.py
- Central config & env vars
- Yahan models, weights, cache settings define hain
"""

import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# --- OpenAI Keys & Models ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing. Put it in your .env")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# --- Retrieval tuning (top-k for each retriever) ---
STORE_K = int(os.getenv("STORE_K", "30"))  # store (sales) top results
DDS_K = int(os.getenv("DDS_K", "10"))      # dds (training) top results

# --- Ensemble weights (store gets higher weight) ---
ENSEMBLE_WEIGHTS = tuple(
    float(x) for x in os.getenv("ENSEMBLE_WEIGHTS", "0.7,0.3").split(",")
)

# --- Persistence (where indices are saved) ---
INDEX_ROOT = os.getenv("INDEX_ROOT", "vectorstore")

# --- Rebuild flags ---
# FORCE_REBUILD: ignore cache & rebuild indexes
FORCE_REBUILD = os.getenv("FORCE_REBUILD", "0") == "1"

# --- Sales API cache policy ---
# TTL minutes for sales index. If 0 → use hash-based change detection only.
SALES_CACHE_TTL_MIN = int(os.getenv("SALES_CACHE_TTL_MIN", "0"))

# --- Optional API base URLs (if set → use API, else local fallback) ---
SALES_API_BASE = os.getenv("SALES_API_BASE")
DDS_API_BASE = os.getenv("DDS_API_BASE")

def now_ts() -> int:
    """Current epoch seconds (used for TTL checks)."""
    return int(time.time())

def pretty(obj) -> str:
    """Pretty string for logs."""
    try:
        return json.dumps(obj, indent=2)[:5000]
    except Exception:
        return str(obj)[:5000]
