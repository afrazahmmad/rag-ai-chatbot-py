# vectorstore.py

from langchain_community.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
import os, time, hashlib

CACHE_DIR = "faiss_index"
TTL_SECONDS = 3600  # 1 hour
os.makedirs(CACHE_DIR, exist_ok=True)

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")  # OpenAIEmbeddings instance

def _get_store_index_path(store_id: str) -> str:
    hash_key = hashlib.md5(store_id.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"store_{hash_key}.faiss")

def build_or_load_dds_index(dds_id: str, docs: list[Document]) -> FAISS:
    path = os.path.join(CACHE_DIR, f"dds_{dds_id}.faiss")
    if os.path.exists(path):
        return FAISS.load_local(path, embeddings=embedding_model)  # plural for load_local
    vs = FAISS.from_documents(docs, embedding=embedding_model)   # singular for from_documents
    vs.save_local(path)
    return vs

def build_or_update_store_index(store_id: str, docs: list[Document], sales_json: dict) -> FAISS:
    path = _get_store_index_path(store_id)
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        if time.time() - mtime < TTL_SECONDS:
            return FAISS.load_local(path, embeddings=embedding_model)  # plural
    vs = FAISS.from_documents(docs, embedding=embedding_model)       # singular
    vs.save_local(path)
    return vs
