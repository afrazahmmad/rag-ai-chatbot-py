import argparse
from app.vectorstore import (
    build_or_load_dds_index,
    build_or_update_store_index,
    load_dds_index,
    load_store_index,
)
from app.llm_factory import get_llm
import sys

def main():
    parser = argparse.ArgumentParser(description="DDS RAG Chatbot CLI")
    parser.add_argument("--dds-id", type=str, required=True, help="DDS ID")
    parser.add_argument("--store-id", type=str, required=True, help="Store ID")
    parser.add_argument("--llm-provider", type=str, required=True, help="LLM provider (huggingface/openai/anthropic)")
    parser.add_argument("--llm-model", type=str, required=True, help="LLM model name")
    parser.add_argument("--hf-embedding", action="store_true", help="Use HuggingFace embeddings for FAISS")

    args = parser.parse_args()

    dds_id = args.dds_id
    store_id = args.store_id
    llm_provider = args.llm_provider.lower()
    llm_model_name = args.llm_model
    hf_embedding = args.hf_embedding

    # ===== Build/load DDS index =====
    try:
        dds_index = load_dds_index(dds_id)
        if dds_index is None:
            print(f"Building DDS index for {dds_id}...")
            sample_docs = ["Sample DDS document content. Replace with your actual DDS data."]
            dds_index = build_or_load_dds_index(dds_id, sample_docs, embedding_model_name=llm_model_name, hf_embedding=hf_embedding)
    except Exception as e:
        print("Error building DDS index:", e)
        sys.exit(1)

    # ===== Build/load Store index =====
    try:
        store_index = load_store_index(store_id)
        if store_index is None:
            print(f"Building Store index for {store_id}...")
            sample_docs = ["Sample Store document content. Replace with your actual Store data."]
            store_index = build_or_update_store_index(store_id, sample_docs, embedding_model_name=llm_model_name, hf_embedding=hf_embedding)
    except Exception as e:
        print("Error building Store index:", e)
        sys.exit(1)

    # ===== Initialize LLM via llm_factory =====
    try:
        llm = get_llm(provider=llm_provider, model_name=llm_model_name, hf_embedding=hf_embedding)
    except Exception as e:
        print("Error initializing LLM:", e)
        sys.exit(1)

    print("\n✅ DDS Chatbot CLI Ready. Type 'exit' to quit.")

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
            if llm_provider.lower() == "huggingface" and hf_embedding:
                # For HuggingFace embeddings only, just show similarity results
                response = context or "No relevant documents found."
            else:
                # Generative LLMs
                response = llm(prompt)
        except Exception as e:
            response = f"Error generating response: {e}"

        print("Bot:", response)


if __name__ == "__main__":
    main()
