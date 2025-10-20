# rag/rag_module.py
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from rag.retriever import SurveyRetriever
from rag.config import Config



class SurveyRAG:
    """RAG 기반 설문 검색 및 응답 생성 엔진"""

    def __init__(self, model_name, sparse_weight=0.3, dense_weight=0.7, k=1):
        
        
        self.model = ChatOpenAI(model = model_name)
        
        self.retriever = SurveyRetriever(sparse_weight=sparse_weight, dense_weight=dense_weight, k=k).get_retriever()

        # RAG Prompt Template
        self.prompt = PromptTemplate.from_template("""
        너는 전문 설문조사 기획자야.  
        아래에는 검색된 설문 문서와 그 메타데이터가 주어져 있어.  
        각 문서는 설문 도메인의 정보를 포함하며, 내용에는 문항, 보기, 조사 개요 등이 포함되어 있어.
        검색된 설문 문서를 참고하여 사용자의 요청과 관련된
        실제 설문 문항(인구통계학적 특성 : SQ1 ~ SQn(다른 이름 일 수도 있음), 본 문항 : Q1~Qn) 을 중심으로 정리해줘.

        너의 임무는 다음과 같아:
        1. 원문 설문 문항이 있으면 가능한 그대로 출력한다(문항이 너무 많다면 자체적으로 판단해서 중복 문항을 제외하고 중요 문항만 보기와 함께 출력).
        2. 사용자의 질문과 가장 관련된 설문지를 선택해 요약하되, 문항 일부만이 아니라 전체 구조를 이해할 수 있도록 개요를 함께 제공해야함.  
        3. 관련 문서가 없으면 "관련 설문지가 없습니다."라고 답한다.

        출력 형식 예시:
        
        조사 개요 요약
        - 목적: (이 설문이 수행된 이유)
        - 구조: (조사 영역 또는 문항 구분)
        - 핵심 영역: (주요 문항 영역)
        - 추가 영역: (있다면)
        - 응답 형식: (척도형, 객관식, 복수응답 등)

        핵심 문항 및 보기 예시
        SQ1. 귀하의 성별은 무엇입니까? 
        ① 남성
        ② 여성
        
        Q1.온라인 강의의 질에 얼마나 만족하십니까?
        ① 매우 불만족
        ② 불만족
        ③ 보통이다
        ④ 만족
        ⑤ 매우만족

        # 질문:
        {question}

        # 검색된 문서 및 메타데이터:
        {context}

        # 답변:
        """)


    def format_docs(self, docs):
        """검색된 문서를 텍스트로 결합 (메타데이터 포함)"""
        formatted = []
        for doc in docs:
            meta = doc.metadata
            formatted.append(
                f"[도메인: {meta.get('domain', 'N/A')}] "
                f"{doc.page_content}\n"
            )
        return "\n---\n".join(formatted)

    def __call__(self, query: str) -> str:
        """RAG 파이프라인 실행"""
        chain = (
            {"context": self.retriever | self.format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )
        return chain.invoke(query)



if __name__ == "__main__":
    
    rag = SurveyRAG(model_name=Config.MODEL_NAME)
    # query = "학생 교육 실태 조사와 관련된 설문지"
    
    # query = {
    # '조사목적': '대학생을 대상으로 온라인 강의 만족도를 조사하고, 강의 질 및 교수 피드백을 평가하기 위함',
    # '조사대상': '대학생',
    # '주요측정변수': ['온라인 강의 전반 만족도', '강의 질', '교수 피드백 만족도'],
    # '요청문항수': '10문항',
    # '설문요구사항': '온라인 강의 맥락을 반영하고, 교수자 피드백 관련 문항을 포함할 것'
    # }
    query = """
    이번 조사의 목적은 대학생을 대상으로 온라인 강의 만족도를 조사하고, 강의의 질과 교수 피드백을 평가하기 위함입니다.
    조사대상은 대학생이며, 주요 측정변수는 온라인 강의 전반 만족도, 강의 질, 교수 피드백 만족도입니다.
    온라인 강의의 실제 맥락을 반영하고 교수자의 피드백과 관련된 문항을 반드시 포함해야 합니다."""
    
    answer = rag(query)

    print("\n RAG 응답 결과:\n")
    print(answer)