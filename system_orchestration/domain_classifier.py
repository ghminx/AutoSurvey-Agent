from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

class DomainClassifier:
    """LLM 기반 도메인 분류기"""

    def __init__(self, model_name="gpt-5-mini"):
        self.llm = ChatOpenAI(model=model_name)
        self.prompt = PromptTemplate.from_template("""
        너는 사회조사 분야의 전문가야.
        아래의 사용자 조사 요구사항과 일부 참조 설문 문서를 참고하여,
        이 설문이 속하는 주제 도메인을 판단해줘.
        선택지는 다음 중 하나야:

        [공공·사회 / 교육 / 산업·경제 / 의료·보건·복지 / 해당없음]

        ## 사용자 요구사항
        {user_input}

        ## 참조 설문 요약
        {context}

        ## 출력 형식 
        결과는 분류된 도메인명만 출력 
        
        ex1) 공공·사회
        ex2) 교육
        """)

    def __call__(self, user_input: dict, context: str) -> str:
        formatted_input = self.prompt.format(
            user_input=str(user_input),
            context=context[:1000]  # 일부분만 LLM에 입력
        )

        response = self.llm.invoke(formatted_input).content

        return response


