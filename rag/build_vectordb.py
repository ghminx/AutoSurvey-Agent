# build_vector_store.py

from rag.config import Config
from rag.loader import SurveyLoader
from rag.embedder import SurveyEmbedder

from pathlib import Path
import time



# === 설정 ===
PDF_ROOT = Config().PDF_ROOT
MODEL_NAME = Config().EMBEDDING_MODEL
FAISS_DB = Config().FAISS_DB
BM_DB = Config().BM_DB

if __name__ == "__main__":
    # === 문서 로드 ===
    loader = SurveyLoader(PDF_ROOT)
    docs = loader.load_all()

    # === 임베딩 및 BM25 구축 ===
    embedder = SurveyEmbedder(MODEL_NAME, FAISS_DB, BM_DB)
    embedder.build_vector_db(docs)      # FAISS 저장
    embedder.build_bm25_index(docs)     # BM25 저장