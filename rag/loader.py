# rag/loader.py
from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document

class SurveyLoader:
    def __init__(self, pdf_root: str):
        self.pdf_root = Path(pdf_root)

    def load_all(self) -> List[Document]:
        docs = []
        for pdf in self.pdf_root.rglob("*.pdf"):
            # 도메인 = 상위 폴더명 (예: data/설문지/PDF/교육·청소년/xxx.pdf)
            domain = pdf.parent.name
            loader = PyMuPDFLoader(str(pdf))
            pages = loader.load()
            full_text = "\n".join(p.page_content for p in pages)

            meta: Dict = {
                "file_name": pdf.stem,
                "domain": domain,
                "num_pages": len(pages),
            }
            docs.append(Document(page_content=full_text, metadata=meta))
        return docs
