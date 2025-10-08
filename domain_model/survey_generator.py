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

    def __call__(self, user_input: dict, context: str = "None") -> str:
        """
        LLM을 통해 설문지를 생성하고 문자열 형태로 반환.
        """
        prompt_text = self._build_prompt(user_input, context)
        response = (self.model | self.parser).invoke(prompt_text)
        return response


user_input = {
    '조사목적': '대학생을 대상으로 온라인 강의 만족도를 조사하고, 강의 질 및 교수 피드백을 평가하기 위함',
    '조사대상': '대학생',
    '주요측정변수': ['온라인 강의 전반 만족도', '강의 질', '교수 피드백 만족도'],
    '요청문항수': '10문항',
    '설문요구사항': '온라인 강의 맥락을 반영하고, 교수자 피드백 관련 문항을 포함할 것'
}

context = """
[참조 설문지: 대학생 교육 실태 조사 (2022)]

1. 귀하의 전공은 무엇입니까?
   ① 인문사회계열
   ② 자연과학계열
   ③ 공학계열
   ④ 예체능계열
   ⑤ 기타

2. 본인이 수강한 온라인 강의의 전반적인 만족도는 어떻습니까?
   ① 매우 불만족
   ② 불만족
   ③ 보통
   ④ 만족
   ⑤ 매우 만족

3. 온라인 강의의 영상 화질 및 음질은 만족스러웠습니까?
   ① 매우 불만족
   ② 불만족
   ③ 보통
   ④ 만족
   ⑤ 매우 만족

4. 교수자가 강의 중 질문에 대해 충분한 피드백을 제공했습니까?
   ① 전혀 그렇지 않다
   ② 그렇지 않다
   ③ 보통이다
   ④ 그렇다
   ⑤ 매우 그렇다

5. 온라인 강의 수강 환경(플랫폼, 접속 안정성 등)에 대해 만족하십니까?
   ① 매우 불만족
   ② 불만족
   ③ 보통
   ④ 만족
   ⑤ 매우 만족

6. 온라인 강의 방식이 학습 성취도 향상에 도움이 되었습니까?
   ① 전혀 도움이 안 됨
   ② 도움이 되지 않음
   ③ 보통
   ④ 도움이 됨
   ⑤ 매우 도움이 됨

7. 온라인 강의의 장점으로 가장 중요한 것은 무엇입니까? (복수 선택 가능)
   ① 시간과 장소의 제약이 적다
   ② 반복 학습이 가능하다
   ③ 수업 집중도가 높다
   ④ 교수 피드백이 신속하다
   ⑤ 기타

8. 온라인 강의의 개선이 필요한 부분은 무엇입니까? (복수 선택 가능)
   ① 실시간 소통 부족
   ② 과제 및 시험 관리
   ③ 피드백 지연
   ④ 시스템 안정성
   ⑤ 기타

9. 향후 오프라인 강의와 온라인 강의 중 어떤 방식을 선호하십니까?
   ① 온라인
   ② 오프라인
   ③ 혼합형

10. 온라인 강의와 관련하여 추가로 개선되었으면 하는 점이 있습니까? (주관식)
   _______________________________________________________
"""


generator = SurveyGenerator(model_name='gpt-5')
result = generator(user_input, context)

print("\n🧩 생성된 설문지 초안:\n")
print(result)


