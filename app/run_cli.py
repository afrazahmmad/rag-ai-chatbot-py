import argparse
import os
from app.vectorstore import (
    load_dds_docs,
    load_store_docs,
    build_or_load_dds_index,
    build_or_update_store_index
)

# Multi-LLM imports
from langchain_huggingface.chat_models import ChatHuggingFace
from langchain.chat_models import ChatOpenAI

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dds-id", required=True)
    parser.add_argument("--store-id", required=True)
    parser.add_argument("--llm-provider", choices=["openai", "huggingface"], required=True)
    parser.add_argument("--llm-model", required=True)
    parser.add_argument("--hf-embedding", action="store_true")
    parser.add_argument("--dds-file", required=True)
    parser.add_argument("--store-file", required=True)
    args = parser.parse_args()

    # ------------------- DDS Index -------------------
    print(f"Loading DDS index for {args.dds_id}...")
    dds_docs = load_dds_docs(args.dds_file)
    dds_index = build_or_load_dds_index(
        args.dds_id,
        dds_docs,
        hf_embedding=args.hf_embedding,
        hf_model_name=args.llm_model
    )
    print(f"✅ DDS index ready for {args.dds_id}")

    # ------------------- Store Index -----------------
    print(f"Loading Store index for {args.store_id}...")
    store_index = build_or_update_store_index(
        args.store_id,
        args.store_file,
        hf_embedding=args.hf_embedding,
        hf_model_name=args.llm_model
    )
    print(f"✅ Store index ready for {args.store_id}")

    # ------------------- LLM Provider ----------------
    print(f"Initializing LLM provider: {args.llm_provider}...")
    if args.llm_provider == "huggingface":
        llm = ChatHuggingFace(
            model=args.llm_model,
            temperature=0,
            device="mps"  # or "cpu"
        )
    else:
        llm = ChatOpenAI(
            model=args.llm_model,
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    print("🤖 DDS Chatbot ready! Type 'exit' to quit.")

    # ------------------- Chat Loop -------------------
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            # Placeholder for DDS + Store retrieval logic
            response_text = f"Answering based on DDS + Store docs. User asked: {user_input}"
            print("Bot:", response_text)
        except Exception as e:
            print("Bot Error:", e)

if __name__ == "__main__":
    main()
