"""
run_cli.py
- CLI entrypoint
- DDS-wise (static) + Store-wise (dynamic) hybrid chatbot
- DDS training index ek dafa build/load
- Store index hash/TTL policy ke sath cache/update
"""

import argparse
from app.api_client import fetch_sales_data, fetch_dds_training
from app.data_loader import sales_dict_to_docs, dds_defs_dict_to_docs
from app.vectorstore import build_or_load_dds_index, build_or_update_store_index
from app.retriever import build_ensemble_retriever
from app.chatbot import build_chatbot
from app.config import STORE_K, DDS_K, ENSEMBLE_WEIGHTS
from app.logging_utils import log_full_event   # 🔄 use merged logger

def parse_args():
    p = argparse.ArgumentParser(description="DDS Hybrid RAG Chatbot (CLI)")
    p.add_argument("--dds-id", type=str, help="DDS identifier (e.g., dds_usa)")
    p.add_argument("--store-id", type=str, help="Store identifier (e.g., 1256)")
    return p.parse_args()

def main():
    args = parse_args()
    dds_id = args.dds_id or input("Enter DDS ID: ").strip()
    store_id = args.store_id or input("Enter Store ID: ").strip()

    # 1) Fetch JSONs (API or local fallback)
    sales_json = fetch_sales_data(store_id)
    dds_defs   = fetch_dds_training(dds_id)

    # 2) Convert JSON → LangChain Documents
    sales_docs, aggregated_doc = sales_dict_to_docs(sales_json)
    dds_docs = dds_defs_dict_to_docs(dds_defs)

    # 3) Build/load indices
    dds_vs   = build_or_load_dds_index(dds_id, dds_docs)                           # static
    store_vs = build_or_update_store_index(store_id, sales_docs + [aggregated_doc], sales_json)  # dynamic

    # 4) Hybrid retriever = Store (0.7) + DDS (0.3)
    retriever = build_ensemble_retriever(
        store_vs, dds_vs,
        k_store=STORE_K, k_dds=DDS_K,
        weights=ENSEMBLE_WEIGHTS
    )

    # 5) Chatbot with memory
    bot = build_chatbot(retriever)
    print("\n🚀 DDS Hybrid Chatbot Ready!  (type 'exit' to quit)\n")

    session_id = f"{dds_id}:{store_id}"

    while True:
        try:
            q = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if q.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        # Run conversational RAG with per-session history
        result = bot.invoke({"question": q}, config={"configurable": {"session_id": session_id}})
        print("Bot:", (result.get("answer") or "").strip())

        # ✅ Log full event (tokens + vector + total cost)
        vector_info = {
            "query": q,
            "chunks_retrieved": result.get("retrieved_chunks", 0),
            "latency_ms": result.get("retrieval_latency_ms", 0),
            "db": "faiss",   # or pinecone/weaviate depending on your setup
            "filters": result.get("applied_filters", {})
        }
        log_full_event(session_id, q, result, vector_info)

if __name__ == "__main__":
    main()
