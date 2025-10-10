# survey_regenerator.py

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class SurveyRegenerator:
    """
    피드백을 반영하여 설문지를 재생성하는 클래스
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
            아래의 기존 설문지와 사용자 피드백을 기반으로 설문지를 수정해야 해.

            ## [기존 생성된 설문지]
            {previous_survey}

            ## [사용자 피드백]
            피드백 유형: {feedback_type}
            대상 문항: {target_question}
            수정 요청 내용:
            {modification}

            ## [수정 지침]
            1. 사용자 피드백을 **정확히** 반영하여 설문지를 수정한다.
            
            2. 피드백 유형에 따라 적절히 처리:
               - **문항 수정**: 해당 문항의 내용이나 보기를 수정
               - **문항 추가**: 새로운 문항을 적절한 위치에 삽입하고 번호 재정렬
               - **문항 삭제**: 해당 문항을 제거하고 이후 번호 재정렬
               - **형식 변경**: 응답 형식(5점 척도, 객관식, 주관식 등) 변경
               - **순서 조정**: 문항 순서를 변경하고 번호 재정렬
               - **전체 재구성**: 전체 구조를 재검토하여 재작성
            
            3. **피드백으로 지정되지 않은 문항은 절대 수정하지 말고 그대로 유지**한다.
            
            4. 문항 번호는 SQ1~SQn, Q1~Qn 형식으로 표기한다.
            
            5. 전체 형식은 다음을 따른다:

            ### 응답자 특성 문항
            SQ1. 귀하의 성별은 무엇입니까?
            - ① 남성
            - ② 여성

            ### 본 문항
            Q1. ...
            - ① ...
            - ② ...

            6. **수정된 설문지 전체**를 출력한다.
            """
        )

    def _build_prompt(self, previous_survey: str, structured_feedback: dict) -> str:
        """
        피드백 재생성용 프롬프트 구성
        """
        prompt = self.prompt.format(
            previous_survey=previous_survey,
            feedback_type=structured_feedback.get('feedback_type', '수정'),
            target_question=structured_feedback.get('target_question', '전체'),
            modification=structured_feedback.get('modification', '')
        )
        
        return prompt

    def __call__(self, previous_survey: str, structured_feedback: dict) -> str:
        """
        피드백을 반영한 설문지 재생성
        
        Args:
            previous_survey: 기존 생성된 설문지 전체 텍스트
            structured_feedback: 구조화된 피드백
                {
                    'feedback_type': '문항 수정' | '문항 추가' | '문항 삭제' | ...,
                    'target_question': 'Q3' | 'SQ1' | '전체',
                    'modification': '구체적인 수정 내용'
                }
        
        Returns:
            수정된 설문지 전체 텍스트
        """
        prompt_text = self._build_prompt(previous_survey, structured_feedback)
        response = (self.model | self.parser).invoke(prompt_text)
        return response