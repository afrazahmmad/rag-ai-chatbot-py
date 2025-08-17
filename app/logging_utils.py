import logging
import json
import os
from datetime import datetime

# Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

def get_log_filename():
    """Return daily log file name like logs/ai-2025-08-17.log"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"logs/ai-{today}.log"

# Setup logger
logger = logging.getLogger("ai_logger")
logger.setLevel(logging.INFO)

# File handler (new file each day)
file_handler = logging.FileHandler(get_log_filename(), encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)

# Console handler (optional for dev)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(console_handler)


def log_full_event(session_id: str, question: str, result, vector_details: dict):
    """
    Logs BOTH token usage + vector db info (with cost estimates)
    in a single JSON log entry.
    """
    usage = result.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    # --- OpenAI token pricing (gpt-4o-mini) ---
    price_in = 0.150 / 1_000_000   # $ per token
    price_out = 0.600 / 1_000_000  # $ per token
    token_cost = round((input_tokens * price_in) + (output_tokens * price_out), 6)

    # --- Vector DB cost (example: Pinecone) ---
    chunks = vector_details.get("chunks_retrieved", 0)
    vector_price_per_unit = 0.096 / 1_000_000   # $ per vector read
    vector_cost = round(chunks * vector_price_per_unit, 6)

    # --- Total combined ---
    total_cost = round(token_cost + vector_cost, 6)

    log_data = {
        "event": "ai_query",
        "session_id": session_id,
        "question": question,
        "token_usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "approx_cost_usd": token_cost
        },
        "vector_retrieval": {
            **vector_details,
            "approx_cost_usd": vector_cost
        },
        "total_estimated_cost_usd": total_cost
    }

    # logger.info(json.dumps(log_data))
