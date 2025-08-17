"""
api_client.py
- API se JSON fetch karne ke helpers
- Agar API env vars nahi diye to local fallback files use honge
"""

import os
import json
from typing import Dict, Any, Optional
import requests
from .config import SALES_API_BASE, DDS_API_BASE

def _load_local_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_sales_data(store_id: str, local_fallback: Optional[str] = "data/1256_sales_data_extended.json") -> Dict[str, Any]:
    """
    Sales (dynamic) JSON:
    1) If SALES_API_BASE set → call GET {SALES_API_BASE}/{store_id}
    2) Else → read local fallback file
    """
    if SALES_API_BASE:
        url = f"{SALES_API_BASE.rstrip('/')}/{store_id}"
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        return resp.json()

    if not local_fallback or not os.path.exists(local_fallback):
        raise FileNotFoundError("No SALES_API_BASE and fallback file missing.")
    return _load_local_json(local_fallback)

def fetch_dds_training(dds_id: str, local_dir: Optional[str] = "data") -> Dict[str, Any]:
    """
    DDS training (static) JSON:
    1) If DDS_API_BASE set → call GET {DDS_API_BASE}/{dds_id}/training
    2) Else → try data/dds_training_{dds_id}.json then data/dds_training.json
    """
    if DDS_API_BASE:
        url = f"{DDS_API_BASE.rstrip('/')}/{dds_id}/training"
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        return resp.json()

    # local fallbacks
    candidates = []
    if local_dir:
        candidates.append(os.path.join(local_dir, f"dds_training_{dds_id}.json"))
        candidates.append(os.path.join(local_dir, "dds_training.json"))
    for path in candidates:
        if os.path.exists(path):
            return _load_local_json(path)

    raise FileNotFoundError("No DDS_API_BASE and no local DDS training JSON found.")
