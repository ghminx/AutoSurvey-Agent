# user_input/llm_extractor.py

from openai import OpenAI
import json

class LLMExtractor:
    """
    텍스트 마이닝으로 도출된 키워드와 원문을 기반으로
    조사 목적, 대상, 도메인, 주요 변수 등을 구조화된 JSON으로 추출하는 모듈
    """
    def __init__(self, model: str = "gpt-5"):
        self.client = OpenAI()
        self.model = model

    def extract_info(self, text: str, keywords: list[str]) -> dict:
        """
        LLM을 이용한 구조화된 정보 추출
        """
        
        system_prompt = """
        너는 전문 조사기획자이자 설문 설계 전문가이다. 
        너의 역할은 사용자가 작성한 요구사항 문서나 RFP(Request for Proposal)를 분석하여, 
        설문조사 설계에 필요한 정보를 구조화된 JSON 형태로 추출하는 것이다. 
        출력은 반드시 유효한 JSON 형식으로 반환해야 하며, 키와 값은 모두 한국어로 작성함. 

        분석 시 다음 항목을 반드시 포함하라:
        - 조사 목적: 조사의 전체적인 목표와 취지
        - 조사 대상: 응답자가 속하는 주요 집단 (예: 대학생, 직장인, 고객 등)
        - 주요 측정 변수: 설문을 통해 파악하려는 핵심 개념 또는 속성 (예: 만족도, 인식, 행동의도 등)
        - 요청 문항 수: 문항 수에 대한 언급이 있을 경우 추출, 없으면 비워둘 것
        - 특수 요구사항: 설문 방법, 형식, 응답 척도 등과 관련된 제약이나 추가 조건

        출력 형식은 다음과 같이 고정한다:

        {
        "조사목적": "",
        "조사대상": "",
        "주요측정변수": [],
        "요청문항수": "",
        "특수요구사항": ""
        }
        """

        user_prompt = f"""
        
        다음은 사용자가 작성한 조사 요청 내용이다.
        이 문서는 설문 설계에 필요한 요구사항을 설명하고 있으며, 
        너는 이 문장을 기반으로 조사의 구조적 정보를 도출해야함.

        [사용자 입력 문서]
        {text}

        이 문서의 주요 내용에서 다음과 같은 핵심 키워드들이 텍스트 마이닝 과정을 통해 추출됨:
        {', '.join(keywords)}

        위 텍스트와 키워드를 참고하여, 
        조사 목적, 대상, 주요 측정 변수, 요청 문항 수, 특수 요구사항을 JSON 객체로 작성해야함.
        
        """

        response = self.client.responses.create(
            model=self.model,
            reasoning={"effort": "low"},   # GPT-5 reasoning 모드
            max_output_tokens=1024,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        # 모델 출력 파싱
        output_text = response.output_text.strip()

        # JSON 파싱 처리
        try:
            structured_data = json.loads(output_text)
        except json.JSONDecodeError:
            structured_data = {"error": "JSON parsing failed", "raw_output": output_text}

        return structured_data
    



