# rag/loader.py
from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class SurveyLoader:
    def __init__(self, pdf_root: str):
        self.pdf_root = Path(pdf_root)
        
    def _text_splitter(self):
        
        splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap = 200)

        return splitter 
    
    def load_all(self) -> List[Document]:
        docs: List[Document] = []

        for pdf in self.pdf_root.rglob("*.pdf"):
            domain = pdf.parent.name
            loader = PyMuPDFLoader(str(pdf))
            pages = loader.load()
            full_text = "\n".join(p.page_content for p in pages) if pages else ""
            if not full_text.strip():
                continue

            meta: Dict = {
                "file_name": pdf.stem,
                "domain": domain,
                "num_pages": len(pages),
            }

            splitter = self._text_splitter()
            parts = splitter.split_documents(
                [Document(page_content=full_text, metadata=meta)]
            )
            docs.extend(parts)

        return docs



