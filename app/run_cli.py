import argparse
import sys
from app.vectorstore import (
    build_or_load_dds_index,
    build_or_update_store_index,
    load_dds_index,
    load_store_index,
    load_dds_docs,
    load_store_docs,
)
from app.llm_factory import get_llm

def main():
    parser = argparse.ArgumentParser(description="DDS RAG Chatbot CLI")
    parser.add_argument("--dds-id", type=str, required=True, help="DDS ID")
    parser.add_argument("--store-id", type=str, required=True, help="Store ID")
    parser.add_argument("--llm-provider", type=str, required=True, help="LLM provider (huggingface/openai/anthropic)")
    parser.add_argument("--llm-model", type=str, required=True, help="LLM model name")
    parser.add_argument("--hf-embedding", action="store_true", help="Use HuggingFace embeddings for FAISS")
    parser.add_argument("--dds-file", type=str, required=True, help="Path to DDS training JSON")
    parser.add_argument("--store-file", type=str, required=True, help="Path to Store sales JSON")

    args = parser.parse_args()

    dds_id = args.dds_id
    store_id = args.store_id
    llm_provider = args.llm_provider.lower()
    llm_model_name = args.llm_model
    hf_embedding = args.hf_embedding
    dds_file = args.dds_file
    store_file = args.store_file

    # ===== Load or build DDS index =====
    try:
        dds_index = load_dds_index(dds_id, hf_embedding=hf_embedding, hf_model_name=llm_model_name)
        if dds_index is None:
            print(f"Building DDS index for {dds_id}...")
            dds_docs = load_dds_docs(dds_file)
            dds_index = build_or_load_dds_index(dds_id, dds_docs, hf_embedding=hf_embedding, hf_model_name=llm_model_name)
        print(f"✅ DDS index ready for {dds_id}")
    except Exception as e:
        print("Error building DDS index:", e)
        sys.exit(1)

    # ===== Load or build Store index =====
    try:
        store_index = load_store_index(store_id, hf_embedding=hf_embedding, hf_model_name=llm_model_name)
        if store_index is None:
            print(f"Building Store index for {store_id}...")
            store_index = build_or_update_store_index(store_id, store_file, hf_embedding=hf_embedding, hf_model_name=llm_model_name)
        print(f"✅ Store index ready for {store_id}")
    except Exception as e:
        print("Error building Store index:", e)
        sys.exit(1)

    # ===== Initialize LLM =====
    try:
        llm = get_llm(provider=llm_provider, model_name=llm_model_name, hf_embedding=hf_embedding)
    except Exception as e:
        print("Error initializing LLM:", e)
        sys.exit(1)

    print("\n🚀 DDS Chatbot CLI Ready. Type 'exit' to quit.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        # Simple FAISS retrieval from DDS index
        try:
            results = dds_index.similarity_search(user_input, k=3)
            context = " ".join([doc.page_content for doc in results])
        except Exception:
            context = ""

        # Prepare prompt
        prompt = f"Context: {context}\nQuestion: {user_input}\nAnswer:"

        # Query LLM
        try:
            if llm_provider == "huggingface" and hf_embedding:
                # Only show retrieved context for embedding-only models
                response = context or "No relevant documents found."
            else:
                response = llm(prompt)
        except Exception as e:
            response = f"Error generating response: {e}"

        print("Bot:", response)


if __name__ == "__main__":
    main()
