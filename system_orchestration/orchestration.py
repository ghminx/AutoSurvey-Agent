# orchestration.py 
from rag.config import Config
from rag.rag_module import SurveyRAG
from system_orchestration.domain_classifier import DomainClassifier
from domain_model.survey_generator import SurveyGenerator
from domain_model.survey_regenerator import SurveyRegenerator
from feedback_output.feedback_analyzer import FeedbackAnalyzer


class SurveyOrchestration:
    
    DOMAIN_MODEL_MAP = {
        "공공·사회": "AutoSurvey-Public",
        "교육": "AutoSurvey-Edu",
        "산업·경제": "AutoSurvey-Industry",
        "의료·보건·복지": "AutoSurvey-Health",
    }

    def __init__(self, user_input):
        """_summary_
        Args:
            user_input (str): 사용자 요구사항 
        """
        self.user_input = user_input

        # 도메인 분류기 
        self.domain_classifier = DomainClassifier()

        # 피드백 분석기 
        self.feedback_analyzer = FeedbackAnalyzer()
        

        # 상태 저장 변수
        self.selected_domain = None      
        self.model_name = None          
        self.context = None              
        
    # 설문지 초안 생성
    def __call__(self):
        
        # 1. RAG 파라미터 동적 조정 및 쿼리 생성
        rag_params = self.adjust_rag_params()
        rag_input = self.build_rag_query()
        
        # 2. RAG 실행
        survey_rag = SurveyRAG(model_name=Config.MODEL_NAME, 
                               sparse_weight=rag_params['sparse_weight'], 
                               dense_weight=rag_params['dense_weight'], 
                               k=rag_params['k'])
        
        print('RAG 진행 중...')
        print(f'RAG 입력 Query:\n{rag_input}')
        self.context = survey_rag(rag_input)
        print('=======================')
        print('검색된 참조 설문지')
        print('=======================')
        
        print(f'RAG 결과:\n{self.context}')
        print('=======================')
            
        # 3. 도메인 모델 선택
        self.selected_domain = self.domain_classifier(self.user_input, self.context)
        self.model_name = self.DOMAIN_MODEL_MAP.get(self.selected_domain, "gpt-5")
        print(f'선택된 도메인 모델: {self.model_name}')

        # 4. 설문지 생성
        # generator = SurveyGenerator(model_name=model_name)
        print('설문지 생성 진행 중...')
        generator = SurveyGenerator(model_name='gpt-5')
        result = generator(self.user_input, self.context)

        return result


    def process_feedback(self, current_survey: str, user_feedback: str) -> str:
        """
        피드백 처리 및 재생성
        
        Args:
            current_survey: 현재 설문지
            user_feedback: 사용자 피드백 (자연어)
        
        Returns:
            수정된 설문지
        """

        # # 초기 생성을 먼저 실행했는지 확인
        # if self.model_name is None:
        #     raise ValueError(
        #         "초기 설문 생성을 먼저 실행해야 합니다. "
        #         "__call__() 메서드를 먼저 호출하세요."
        #     )
            
        # 1. 피드백 구조화
        print(" 피드백 분석 중...")
        structured_feedback = self.feedback_analyzer(current_survey, user_feedback)
        
        print(f"✅ 분석 완료:")
        print(f"  - 유형: {structured_feedback['feedback_type']}")
        print(f"  - 대상: {structured_feedback['target_question']}")
        print(f"  - 내용: {structured_feedback['modification']}")
        
        # 2. 재생성
        print("\n 설문지 재생성 중...")
        
        regenerator = SurveyRegenerator(model_name='gpt-5')
        # regenerator = SurveyRegenerator(model_name=self.model_name)
        
        modified_survey = regenerator(
            previous_survey=current_survey,
            structured_feedback=structured_feedback
        )
        
        return modified_survey
        

    def adjust_rag_params(self):
        """사용자 입력에 따라 RAG 검색 파라미터를 동적으로 조정"""
        params = {
            "sparse_weight": 0.3,
            "dense_weight": 0.7,
            "k": 1,
        }

        values = list(self.user_input.values())

        variables = values[2]
        num_q = values[3]

        # 문항수가 많으면 검색 범위 확장
        if "50" in num_q or "이상" in num_q:
            params["k"] = 2
            print("문항 수가 50이상 검색 범위 확장 (k=2)")
            
        if "70" in num_q or "이상" in num_q:
            params["k"] = 3
            print("문항 수가 70이상 검색 범위 확장 (k=3)")

        # 주요 측정 변수가 많으면 의미기반 검색 비중 강화
        if len(variables) > 5:
            params["dense_weight"] = 0.8
            params["sparse_weight"] = 0.2
            print("주요 변수 많음 → 의미기반 검색 강화")

        return params


    def build_rag_query(self) -> str:
        """구조화된 조사요구사항(dict)을 자연어 질의로 변환"""
        
        values = list(self.user_input.values())
        
        purpose = values[0]
        target = values[1]
        variables = ", ".join(values[2])
        special = values[4]

        query = (
            f"{target}을(를) 대상으로 하는 설문 중 "
            f"{purpose}와 관련된 예시를 찾아줘. "
            f"특히 {variables} 항목을 포함하고, "
            f"{special}."
        )

        return query



