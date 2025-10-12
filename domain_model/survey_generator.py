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
            1. 설문지는 반드시 두 부분으로 구성해야 한다:
                (1) **응답자 특성 문항(SQ)** — 인구통계 및 배경 관련 문항.
                    - 예시: 성별, 연령, 학력, 직업, 근속기간 등.
                (2) **본 문항(Q)** — 조사 목적과 주요 측정 변수에 직접 관련된 문항.
            2. 모든 문항은 명확하고 측정 가능한 응답 형식을 가져야 한다.
            3. 응답 형식은 5점 척도형(전혀 그렇지 않다~매우 그렇다), 객관식, 다중응답, 또는 주관식 형태로 구성.
            4. 문항 번호는 SQ1~SQn, Q1~Qn 형식으로 표기하고, 각 문항 아래에 보기(①~⑤ 등)를 제시한다.
            5. 하위 영역이 있다면 적절한 소제목을 붙인다.
            6. 요청된 문항 수({num_questions})를 기준으로 전체 문항 수를 조정한다.
            7. 출력 시 다음 형식을 따를 것:

            예시 형식:

            ### 응답자 특성 문항
            SQ1. 귀하의 성별은 무엇입니까?
            - ① 남성
            - ② 여성

            SQ2. 귀하의 고용형태는 어떠합니까?
            - ① 정규직
            - ② 비정규직
            - ③ 계약직
            - ④ 기타

            ### 본 문항
            Q1. 귀하는 근무하는 직장생활에 만족하십니까?
            - ① 매우 불만족
            - ② 불만족
            - ③ 보통이다
            - ④ 만족
            - ⑤ 매우 만족

            Q2. 조직문화를 개선하는 데 있어 가장 큰 방해 요소는 무엇이라 생각하십니까?
            - ① 변화의 필요성을 못 느낌
            - ② 개선이 필요하지만 너무 오래 이어져 온 사내 악습
            - ③ 조직의 분위기를 흐리는 특정 인물들
            - ④ 개방성·자율성을 용납하지 않는 조직 분위기
            - ⑤ 기타

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

    def __call__(self, user_input: dict, context: str = "None") -> str:
        """
        LLM을 통해 설문지를 생성하고 문자열 형태로 반환.
        """
        prompt_text = self._build_prompt(user_input, context)
        response = (self.model | self.parser).invoke(prompt_text)
        return response


if __name__ == "__main__":
    user_input = {'조사목적': '소방장비의 운영 및 관리 실태를 파악하고  문제점과 통합지원의 필요성을 진단하기 위함', 
                  '조사대상': '소방공무원', 
                  '주요측정변수': ['소방장비 운영 실태', '소방장비 관리 체계 및 프로세스', '운영·관리 상의 주요 문제점', '통합지원(예: 예산·시스템·인력·유지보수) 필요 성', '통합지원의 우선순위 및 기대효과'], 
                  '요청문항수': '10문항', 
                  '설문요구사항': ''}

    context = """
    관련 설문지 없음
    """

    generator = SurveyGenerator(model_name='gemma-ps')
    result = generator(user_input, context)

    print("\n 생성된 설문지 초안:\n")
    print(result)


