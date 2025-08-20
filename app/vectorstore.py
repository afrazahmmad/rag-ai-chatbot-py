import os
import json
from pathlib import Path
from typing import List, Optional

from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS

BASE_INDEX_DIR = Path("faiss_indices")
BASE_INDEX_DIR.mkdir(exist_ok=True)

# Optional: import HuggingFace embeddings if available
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None

# ---------------------- JSON -> Documents ----------------------
def load_dds_docs(dds_file: str) -> List[Document]:
    with open(dds_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Document(page_content=f"{k}: {v}", metadata={"type": "dds"}) for k, v in data.items()]

def load_store_docs(store_file: str) -> List[Document]:
    with open(store_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs = []
    for category, metrics in data.items():
        for metric_type, metric_data in metrics.items():
            for name, value in metric_data.items():
                docs.append(
                    Document(
                        page_content=f"{category} | {metric_type} | {name}: {value}",
                        metadata={"type": "store", "category": category, "metric": metric_type, "name": name}
                    )
                )
    return docs

# ---------------------- Vectorstore ----------------------
def build_vectorstore(docs: List[Document], index_name: str, hf_embedding=False, hf_model_name=None):
    index_path = BASE_INDEX_DIR / f"{index_name}.faiss"

    if hf_embedding:
        if HuggingFaceEmbeddings is None:
            raise ImportError("langchain-huggingface not installed. Run: pip install langchain-huggingface")
        embedding_model = HuggingFaceEmbeddings(model_name=hf_model_name)
    else:
        from langchain_openai import OpenAIEmbeddings
        embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

    vs = FAISS.from_documents(docs, embedding_model)
    vs.save_local(str(index_path))
    return vs

def load_vectorstore(index_name: str, hf_embedding=False, hf_model_name=None) -> Optional[FAISS]:
    index_path = BASE_INDEX_DIR / f"{index_name}.faiss"
    if not index_path.exists():
        return None

    if hf_embedding:
        if HuggingFaceEmbeddings is None:
            raise ImportError("langchain-huggingface not installed. Run: pip install langchain-huggingface")
        embeddings = HuggingFaceEmbeddings(model_name=hf_model_name)
    else:
        from dotenv import load_dotenv
        load_dotenv()
        from langchain_openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    return FAISS.load_local(str(index_path), embeddings, allow_dangerous_deserialization=True)

# ---------------------- DDS / Store helpers ----------------------
def build_or_load_dds_index(dds_id, docs, hf_embedding=False, hf_model_name=None):
    vs = load_vectorstore(f"dds_{dds_id}", hf_embedding=hf_embedding, hf_model_name=hf_model_name)
    if vs:
        return vs
    return build_vectorstore(docs, f"dds_{dds_id}", hf_embedding=hf_embedding, hf_model_name=hf_model_name)

def build_or_update_store_index(store_id, store_file, hf_embedding=False, hf_model_name=None):
    vs = load_vectorstore(f"store_{store_id}", hf_embedding=hf_embedding, hf_model_name=hf_model_name)
    if vs:
        return vs
    docs = load_store_docs(store_file)
    return build_vectorstore(docs, f"store_{store_id}", hf_embedding=hf_embedding, hf_model_name=hf_model_name)

def load_dds_index(dds_id, hf_embedding=False, hf_model_name=None) -> Optional[FAISS]:
    return load_vectorstore(f"dds_{dds_id}", hf_embedding=hf_embedding, hf_model_name=hf_model_name)

def load_store_index(store_id, hf_embedding=False, hf_model_name=None) -> Optional[FAISS]:
    return load_vectorstore(f"store_{store_id}", hf_embedding=hf_embedding, hf_model_name=hf_model_name)
