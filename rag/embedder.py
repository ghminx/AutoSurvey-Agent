# rag/embedder.py
import os
import pickle
from tqdm import tqdm
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings


class SurveyEmbedder:
    """
    PDF 문서를 임베딩하여 FAISS 및 BM25 인덱스를 구축하고 저장하는 클래스
    """

    def __init__(self, model_name: str, db_path: str, bm_path: str):
        # === 임베딩 모델 설정 ===
        self.embed_model = OpenAIEmbeddings(model=model_name)

        # === 저장 경로 설정 ===
        self.db_path = Path(db_path)
        self.bm_path = Path(bm_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.bm_path.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # FAISS 벡터DB 구축 및 저장
    # ============================================================
    def build_vector_db(self, docs: List[Document]):
        if not docs:
            raise ValueError("문서 리스트(docs)가 비어 있습니다.")

        print(f"\n 총 {len(docs)}개 문서 임베딩 시작...")

        with tqdm(total=len(docs), desc="Embedding Progress") as pbar:
            vector_store = FAISS.from_documents(documents=docs, embedding=self.embed_model)
            pbar.update(len(docs))

        vector_store.save_local(str(self.db_path))
        print(f"FAISS 벡터DB 저장 완료: {self.db_path}")

        return vector_store

    def load_vector_db(self):
        if not self.db_path.exists():
            raise FileNotFoundError("저장된 FAISS 벡터DB가 없습니다.")
        print(f"기존 벡터DB 로드 중... ({self.db_path})")

        vector_store = FAISS.load_local(
            str(self.db_path),
            embeddings=self.embed_model,
            allow_dangerous_deserialization=True
        )
        return vector_store

    # ============================================================
    # BM25 인덱스 구축 및 저장
    # ============================================================
    def build_bm25_index(self, docs: List[Document], k: int = 3):
        print(f"\n BM25 인덱스 생성 중... ({len(docs)}개 문서)")
        bm25_retriever = BM25Retriever.from_documents(docs)
        bm25_retriever.k = k

        bm25_file = self.bm_path / "bm25.pkl"
        with open(bm25_file, "wb") as f:
            pickle.dump(bm25_retriever, f)

        print(f"BM25 인덱스 저장 완료: {bm25_file}")
        return bm25_retriever

    def load_bm25_index(self):
        bm25_file = self.bm_path / "bm25.pkl"
        if not bm25_file.exists():
            raise FileNotFoundError("저장된 BM25 인덱스가 없습니다.")
        print(f"BM25 인덱스 로드 중... ({bm25_file})")

        with open(bm25_file, "rb") as f:
            bm25_retriever = pickle.load(f)
        return bm25_retriever
