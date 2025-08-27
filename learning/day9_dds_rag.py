# day9_dds_rag.py (modern memory implementation)

import json
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.docstore.document import Document

# ---------------- Load API ----------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found!")


# ---------- STEP 1: Convert sales JSON ----------
def sales_json_to_docs(filepath):
    """
    Reads extended DDS sales JSON and creates:
    - Individual documents for each entity (salesperson, manager, brand, etc.)
    - Aggregated summary doc for each role
    """

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_docs = []
    aggregated_docs = []

    # Iterate over all roles
    for role, categories in data.items():
        role_docs = []
        aggregated_summary_lines = []

        # categories: units, gross, trend, etc.
        # categories: units, gross, trend, etc.
        for category, metrics in categories.items():
            if not isinstance(metrics, dict):
                continue  # skip lists, numbers, or empty values

            for metric, entities in metrics.items():
                if not isinstance(entities, dict):
                    continue  # skip if it's not a dict

                for name, value in entities.items():
                    # Find existing doc for this entity
                    doc = next(
                        (d for d in role_docs if d.metadata["name"] == name and d.metadata["role"] == role),
                        None
                    )
                    if doc:
                        doc.page_content += f"\n- {category} {metric}: {value}"
                    else:
                        summary = f"{name} is part of {role} in DDS system. Performance:\n"
                        summary += f"- {category} {metric}: {value}"
                        role_docs.append(Document(
                            page_content=summary,
                            metadata={"type": "sales", "role": role, "name": name}
                        ))

        # aggregated summary for this role
        for doc in role_docs:
            name = doc.metadata["name"]
            aggregated_summary_lines.append(
                f"{name}: {doc.page_content.replace(f'{name} is part of {role} in DDS system. Performance:', '').strip()}"
            )

        if aggregated_summary_lines:
            aggregated_doc = Document(
                page_content=f"All {role} summary:\n" + "\n".join(aggregated_summary_lines),
                metadata={"type": "all_sales", "role": role}
            )
            aggregated_docs.append(aggregated_doc)

        all_docs.extend(role_docs)

    return all_docs, aggregated_docs



# ---------- STEP 2: DDS defs ----------
def dds_defs_to_docs(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        defs = json.load(f)
    docs = []
    for key, value in defs.items():
        docs.append(Document(page_content=f"{key}: {value}", metadata={"type": "DDS_term"}))
    return docs


# ---------- STEP 3: Vectorstore ----------
def create_vectorstore(docs):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=api_key)
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore


# ---------- STEP 4: Build Conversational RAG with modern memory ----------
def build_chatbot(vectorstore, k=25):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=api_key)

    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
    )

    # ✅ Use modern memory approach
    store = {}  # to keep session-wise history

    def get_session_history(session_id: str):
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]

    conversational_rag = RunnableWithMessageHistory(
        qa_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    return conversational_rag


# ---------- MAIN ----------
if __name__ == "__main__":
    sales_docs, aggregated_doc = sales_json_to_docs("learning/store_deals_data.json")
    dds_docs = dds_defs_to_docs("learning/dds_training.json")

    all_docs = sales_docs + aggregated_doc + dds_docs
    vectorstore = create_vectorstore(all_docs)

    chatbot = build_chatbot(vectorstore, k=30)

    print("🚀 DDS Sales Chatbot Ready with Modern Memory! (type 'exit' to quit)\n")

    session_id = "default_session"

    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        result = chatbot.invoke({"question": query}, config={"configurable": {"session_id": session_id}})
        print("Bot:", result["answer"])
