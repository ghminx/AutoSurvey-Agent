# survey_generator.py
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class SurveyGenerator:
    """
    사용자 요구사항(user_input)과 참조 문서(context)를 기반으로
    설문지 초안을 자동 생성하는 클래스.
    """

    def __init__(self, model_name, temperature=0.5):
        
        # 일반 모델
        if model_name == 'gpt-5':
            self.model = ChatOpenAI(model=model_name, temperature=temperature)
        
        # 도메인 파인튜닝 모델 
        else:
            self.model = ChatOllama(model=model_name, temperature=temperature)
        
        self.parser = StrOutputParser()
        self.prompt = PromptTemplate.from_template(
            """
            너는 사회조사 전문가이자 설문지 설계 전문가야.
            아래의 사용자 요구사항과 참조 설문지를 기반으로,
            새로운 설문지를 작성하되 다음 조건을 반드시 지켜야 해.
            참조 설문지는 없을 수도 있음.

            ## [사용자 요구사항]
            조사 목적:
            {purpose}

            조사 대상:
            {target}

            주요 측정 변수:
            {variables}

            요청 문항 수:
            {num_questions}

            설문 요구사항:
            {special}

            ## [참조 설문지]
            {context}

            ## [작성 지침]
            1. 설문지는 총 {num_questions}으로 구성하되, 각 문항은 명확하고 측정 가능한 응답 형식을 가질 것.
            2. 모든 문항은 조사 목적과 주요 측정 변수(특히 ‘{variables}’)와 연관되어야 함.
            3. 응답 형식은 5점 척도형(전혀 그렇지 않다~매우 그렇다), 객관식, 다중응답(여러응답선택), 주관식 형태로 구성.
            4. 문항 번호는 1번부터 순서대로 표기하고, 각 문항 아래에 보기(①~⑤)를 제시.
            5. 필요 시 하위 영역별로 문항을 묶어 소제목을 붙일 것.
            """
        )

    def _build_prompt(self, user_input: dict, context: str = "None") -> str:
        """
        사용자 요구사항 딕셔너리와 참조 문서(context)를 프롬프트에 채워 넣음
        """
        values = list(user_input.values())

        prompt = self.prompt.format(
                    purpose=values[0],
                    target=values[1],
                    variables=", ".join(values[2]),
                    num_questions=values[3],
                    special=values[4],
                    context=context)
            
        return prompt

    def generate(self, user_input: dict, context: str = "None") -> str:
        """
        LLM을 통해 설문지를 생성하고 문자열 형태로 반환.
        """
        prompt_text = self._build_prompt(user_input, context)
        response = (self.model | self.parser).invoke(prompt_text)
        return response
