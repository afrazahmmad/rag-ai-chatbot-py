# run_cli.py
import argparse
from app.api_client import fetch_sales_data, fetch_dds_training
from app.data_loader import sales_dict_to_docs, dds_defs_dict_to_docs
from app.vectorstore import build_or_load_dds_index, build_or_update_store_index
from app.retriever import build_ensemble_retriever
from app.chatbot import build_chatbot
from app.config import STORE_K, DDS_K, ENSEMBLE_WEIGHTS
from app.logging_utils import log_full_event
from app.llm_factory import get_llm  # <-- new factory

def parse_args():
    parser = argparse.ArgumentParser(description="DDS Hybrid RAG Chatbot (CLI)")
    parser.add_argument("--dds-id", type=str, help="DDS identifier (e.g., dds_usa)")
    parser.add_argument("--store-id", type=str, help="Store identifier (e.g., 1256)")
    parser.add_argument("--llm-provider", type=str, default="huggingface",
                        help="LLM provider: openai, anthropic, huggingface")
    parser.add_argument("--llm-model", type=str, default="gpt2",
                        help="LLM model name or path (for HuggingFace, e.g., gpt2)")
    return parser.parse_args()

def main():
    args = parse_args()
    dds_id = args.dds_id or input("Enter DDS ID: ").strip()
    store_id = args.store_id or input("Enter Store ID: ").strip()

    # 1) Fetch JSONs
    sales_json = fetch_sales_data(store_id)
    dds_defs = fetch_dds_training(dds_id)

    # 2) Convert JSON → LangChain Documents
    sales_docs, aggregated_doc = sales_dict_to_docs(sales_json)
    dds_docs = dds_defs_dict_to_docs(dds_defs)

    # 3) Build/load indices
    dds_vs = build_or_load_dds_index(dds_id, dds_docs)
    store_vs = build_or_update_store_index(store_id, sales_docs + [aggregated_doc], sales_json)

    # 4) Hybrid retriever
    retriever = build_ensemble_retriever(
        store_vs, dds_vs,
        k_store=STORE_K, k_dds=DDS_K,
        weights=ENSEMBLE_WEIGHTS
    )

    # 5) Build chatbot with chosen LLM
    llm = get_llm(args.llm_provider, args.llm_model)
    bot = build_chatbot(retriever, llm=llm)
    print("\n🚀 DDS Hybrid Chatbot Ready! Type 'exit' to quit.\n")

    session_id = f"{dds_id}:{store_id}"

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if question.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        # Run RAG chatbot
        result = bot.invoke({"question": question}, config={"configurable": {"session_id": session_id}})
        answer = (result.get("answer") or "").strip()
        print("Bot:", answer)

        # Vector info: retrieve number of chunks returned
        vector_info = {
            "chunks_retrieved": len(result.get("source_documents", []))
        }

        # Log single JSON entry with tokens + vector info + cost
        log_full_event(session_id, question, result, vector_info)

if __name__ == "__main__":
    main()
