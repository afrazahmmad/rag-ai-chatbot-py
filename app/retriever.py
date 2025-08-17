# retriever.py
from langchain_community.vectorstores import FAISS
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document

class LoggingEnsembleRetriever:
    """
    Wraps an EnsembleRetriever to track documents retrieved
    and provide source_documents for logging.
    """
    def __init__(self, ensemble: EnsembleRetriever):
        self._ensemble = ensemble

    def get_relevant_documents(self, query: str, **kwargs) -> list[Document]:
        """
        Returns documents relevant to the query.
        Wraps the original EnsembleRetriever.
        """
        docs = self._ensemble.get_relevant_documents(query, **kwargs)
        # attach docs for logging
        self.source_documents = docs
        return docs

def build_ensemble_retriever(
    store_vs: FAISS,
    dds_vs: FAISS,
    k_store: int = 30,
    k_dds: int = 10,
    weights = (0.7, 0.3),
) -> LoggingEnsembleRetriever:
    """
    Combines store and DDS retrievers with given weights and wraps for logging.
    """
    store_ret = store_vs.as_retriever(search_kwargs={"k": k_store})
    dds_ret = dds_vs.as_retriever(search_kwargs={"k": k_dds})
    ensemble = EnsembleRetriever(retrievers=[store_ret, dds_ret], weights=list(weights))
    return LoggingEnsembleRetriever(ensemble)
