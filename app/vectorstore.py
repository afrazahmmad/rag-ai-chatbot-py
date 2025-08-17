import os
from pathlib import Path
import pickle
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

# Directory to save vectorstores
VECTORSTORE_DIR = Path("./vectorstores")
VECTORSTORE_DIR.mkdir(exist_ok=True)


def get_embedding_model(model_name, hf_embedding=False):
    """
    Return the embedding model instance based on hf_embedding flag.
    """
    if hf_embedding:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=model_name)
    else:
        from langchain_community.embeddings import OpenAIEmbeddings
        return OpenAIEmbeddings(model=model_name)


def build_or_load_dds_index(dds_id, docs, embedding_model_name="text-embedding-3-small", hf_embedding=False):
    """
    Build or load FAISS index for DDS documents.

    Args:
        dds_id: str
        docs: list[str]
        embedding_model_name: str
        hf_embedding: bool, if True use HuggingFace embeddings

    Returns:
        FAISS vectorstore instance
    """
    if not docs:
        raise ValueError(f"No documents provided for DDS ID {dds_id}")

    doc_objs = [Document(page_content=text) for text in docs]
    embedding_model = get_embedding_model(embedding_model_name, hf_embedding)

    try:
        vs = FAISS.from_documents(doc_objs, embedding=embedding_model)
    except IndexError as e:
        raise RuntimeError(
            "Failed to create FAISS index. Check if embedding model supports the documents."
        ) from e

    vs_path = VECTORSTORE_DIR / f"dds_{dds_id}.pkl"
    with open(vs_path, "wb") as f:
        pickle.dump(vs, f)

    return vs


def build_or_update_store_index(store_id, new_docs, embedding_model_name="text-embedding-3-small", hf_embedding=False):
    """
    Build or update FAISS index for a store.

    Args:
        store_id: str
        new_docs: list[str]
        embedding_model_name: str
        hf_embedding: bool, if True use HuggingFace embeddings

    Returns:
        Updated FAISS vectorstore instance
    """
    if not new_docs:
        raise ValueError(f"No documents provided to update Store ID {store_id}")

    doc_objs = [Document(page_content=text) for text in new_docs]
    embedding_model = get_embedding_model(embedding_model_name, hf_embedding)

    vs_path = VECTORSTORE_DIR / f"store_{store_id}.pkl"
    vs = None
    if vs_path.exists():
        with open(vs_path, "rb") as f:
            vs = pickle.load(f)

    if vs:
        try:
            vs.add_documents(doc_objs, embedding=embedding_model)
        except Exception as e:
            raise RuntimeError("Failed to update FAISS index.") from e
    else:
        try:
            vs = FAISS.from_documents(doc_objs, embedding=embedding_model)
        except Exception as e:
            raise RuntimeError("Failed to build FAISS index.") from e

    with open(vs_path, "wb") as f:
        pickle.dump(vs, f)

    return vs


def load_dds_index(dds_id):
    """
    Load existing DDS FAISS vectorstore if it exists.
    """
    vs_path = VECTORSTORE_DIR / f"dds_{dds_id}.pkl"
    if not vs_path.exists():
        return None
    with open(vs_path, "rb") as f:
        return pickle.load(f)


def load_store_index(store_id):
    """
    Load existing Store FAISS vectorstore if it exists.
    """
    vs_path = VECTORSTORE_DIR / f"store_{store_id}.pkl"
    if not vs_path.exists():
        return None
    with open(vs_path, "rb") as f:
        return pickle.load(f)
