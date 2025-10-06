# rag/config.py
from pathlib import Path

class Config:

    PDF_ROOT: Path = Path("./data/설문지/PDF2").resolve()
    FAISS_DB: Path = Path("./rag/vector_store/faiss").resolve()
    BM_DB: Path = Path("./rag/vector_store/bm").resolve()
    EMBEDDING_MODEL: str = "text-embedding-3-small" 
    MODEL_NAME: str = "gpt-5"