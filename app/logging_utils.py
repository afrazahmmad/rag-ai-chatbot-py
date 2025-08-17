# logging_utils.py
import logging, json, os
from datetime import datetime

os.makedirs("logs", exist_ok=True)

def get_log_filename():
    today = datetime.now().strftime("%Y-%m-%d")
    return f"logs/ai-{today}.log"

logger = logging.getLogger("ai_logger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(get_log_filename(), encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())

def log_full_event(session_id: str, question: str, result, vector_details: dict):
    """
    Logs token usage + separate vector retrieval cost (store & DDS) + total cost
    """
    usage = result.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    # Token cost
    price_in = 0.150 / 1_000_000
    price_out = 0.600 / 1_000_000
    token_cost = round((input_tokens * price_in) + (output_tokens * price_out), 6)

    # Vector costs (example: store vs DDS)
    store_chunks = vector_details.get("store_chunks", 0)
    dds_chunks = vector_details.get("dds_chunks", 0)
    vector_price_per_unit = 0.096 / 1_000_000

    store_cost = round(store_chunks * vector_price_per_unit, 6)
    dds_cost = round(dds_chunks * vector_price_per_unit, 6)
    vector_cost = round(store_cost + dds_cost, 6)

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
            "store_chunks": store_chunks,
            "dds_chunks": dds_chunks,
            "approx_cost_usd": vector_cost
        },
        "total_estimated_cost_usd": total_cost
    }

    logger.info(json.dumps(log_data))
