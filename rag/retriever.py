# rag/retriever.py
import os, pickle
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever, BM25Retriever
from rag.config import Config

class SurveyRetriever:
    """FAISS + BM25 앙상블 검색기"""

    def __init__(self, sparse_weight=0.3, dense_weight=0.7, k=3):
        self.embeddings = OpenAIEmbeddings(model=Config.EMBEDDING_MODEL)

        # === FAISS ===
        self.faiss_store = FAISS.load_local(
            folder_path=Config.FAISS_DB,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True,
        )
        faiss_retriever = self.faiss_store.as_retriever(search_kwargs={"k": k})

        # === BM25 ===
        bm25_path = os.path.join(Config.BM_DB, "bm25.pkl")
        with open(bm25_path, "rb") as f:
            bm25_retriever: BM25Retriever = pickle.load(f)
        bm25_retriever.k = k

        # === Ensemble ===
        self.retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever],
            weights=[sparse_weight, dense_weight],
        )

    def get_retriever(self):
        """앙상블 검색기 반환"""
        return self.retriever
