"""
retriever.py
- Combine store & dds retrievers with weights via EnsembleRetriever
"""

from langchain_community.vectorstores import FAISS
from langchain.retrievers import EnsembleRetriever

def build_ensemble_retriever(
    store_vs: FAISS,
    dds_vs: FAISS,
    k_store: int = 30,
    k_dds: int = 10,
    weights = (0.7, 0.3),
):
    store_ret = store_vs.as_retriever(search_kwargs={"k": k_store})
    dds_ret   = dds_vs.as_retriever(search_kwargs={"k": k_dds})
    return EnsembleRetriever(retrievers=[store_ret, dds_ret], weights=list(weights))
