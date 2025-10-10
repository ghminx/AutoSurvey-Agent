# feedback_output/feedback_analyzer.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Literal

class StructuredFeedback(BaseModel):
    """구조화된 피드백 스키마"""
    feedback_type: Literal[
        '문항 수정', 
        '문항 추가', 
        '문항 삭제', 
        '형식 변경', 
        '순서 조정', 
        '전체 재구성'
    ] = Field(description="피드백의 유형")
    
    target_question: str = Field(
        description="대상 문항 번호 (예: Q3, SQ1) 또는 '전체'"
    )
    
    modification: str = Field(
        description="구체적인 수정 요청 내용을 명확하게 요약"
    )
    
    priority: Literal['높음', '중간', '낮음'] = Field(
        default='중간',
        description="피드백의 우선순위"
    )


class FeedbackAnalyzer:
    """
    사용자의 자연어 피드백을 구조화된 형태로 변환
    """
    
    def __init__(self, model_name="gpt-5-mini"):
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=StructuredFeedback)
        
        self.prompt = PromptTemplate.from_template(
            """
            너는 설문지 피드백 분석 전문가야.
            사용자가 입력한 피드백을 분석하여 구조화된 형태로 변환해야 해.

            ## [현재 설문지]
            {current_survey}

            ## [사용자 피드백]
            {user_feedback}

            ## [분석 지침]
            1. 피드백 유형을 다음 중 하나로 분류:
               - **문항 수정**: 특정 문항의 내용이나 보기를 수정
               - **문항 추가**: 새로운 문항을 추가
               - **문항 삭제**: 기존 문항을 삭제
               - **형식 변경**: 응답 형식(척도, 객관식 등) 변경
               - **순서 조정**: 문항 순서 변경
               - **전체 재구성**: 설문지 전체 구조 변경

            2. 대상 문항을 명확히 식별:
               - 특정 문항 번호(Q1, Q2, SQ1 등)
               - 문항 번호가 명시되지 않았으면 내용으로 추론
               - 전체 설문지 관련이면 "전체"

            3. 수정 요청 내용을 명확하고 구체적으로 요약

            4. 우선순위 판단:
               - 높음: 설문의 핵심을 바꾸는 중요한 변경
               - 중간: 일반적인 수정 요청
               - 낮음: 사소한 표현 수정

            {format_instructions}

            ## [출력 예시]
            {{
                "feedback_type": "형식 변경",
                "target_question": "Q3",
                "modification": "Q3 문항의 응답 형식을 5점 척도에서 7점 척도로 변경",
                "priority": "중간"
            }}
            """
        )

    def __call__(self, current_survey: str, user_feedback: str) -> dict:
        """
        피드백 구조화
        
        Args:
            current_survey: 현재 설문지 전체 텍스트
            user_feedback: 사용자가 입력한 자연어 피드백
        
        Returns:
            구조화된 피드백 딕셔너리
            {
                'feedback_type': str,
                'target_question': str,
                'modification': str,
                'priority': str
            }
        """
        
        # 프롬프트 구성
        format_instructions = self.parser.get_format_instructions()
        
        prompt_text = self.prompt.format(
            current_survey=current_survey,
            user_feedback=user_feedback,
            format_instructions=format_instructions
        )
        
        # LLM 호출 및 파싱
        try:
            result = (self.llm | self.parser).invoke(prompt_text)
            return result
        except Exception as e:
            print(f"⚠️ 피드백 구조화 실패: {e}")
            # 기본값 반환
            return {
                'feedback_type': '문항 수정',
                'target_question': '전체',
                'modification': user_feedback,
                'priority': '중간'
            }


if __name__ == "__main__":
    # 테스트
    analyzer = FeedbackAnalyzer()
    
    test_survey = """
    ### 응답자 특성 문항
    SQ1. 귀하의 성별은 무엇입니까?
    - ① 남성
    - ② 여성
    
    ### 본 문항
    Q1. 조직문화에 만족하십니까?
    - ① 매우 불만족
    - ② 불만족
    - ③ 보통
    - ④ 만족
    - ⑤ 매우 만족
    
    Q2. 조직문화 개선이 필요한 부분은?
    - ① 소통
    - ② 복지
    - ③ 업무환경
    """
    
    # 테스트 케이스들
    test_cases = [
        "Q1을 7점 척도로 바꿔주세요",
        "조직문화 평가 문항을 3개 더 추가해주세요",
        "Q2를 삭제해주세요",
        "SQ1 다음에 연령 문항을 추가해주세요",
        "전체적으로 더 구체적인 문항으로 재작성해주세요"
    ]
    
    for feedback in test_cases:
        print("\n" + "="*60)
        print(f"피드백: {feedback}")
        print("-"*60)
        result = analyzer(test_survey, feedback)
        print(f"유형: {result['feedback_type']}")
        print(f"대상: {result['target_question']}")
        print(f"수정내용: {result['modification']}")
        print(f"우선순위: {result['priority']}")