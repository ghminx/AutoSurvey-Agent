# user_input/analyzer.py
from user_input.text_mining import TextMiningProcessor
from user_input.llm_extractor import LLMExtractor

class UserInputAnalyzer:
    """사용자 입력 분석 전체 프로세스 (Text Mining + LLM 추출)"""
    
    def __init__(self, stopword_path: str, model: str = "gpt-5-mini"):
        self.stopword_path = stopword_path
        self.text_mining = TextMiningProcessor()
        self.llm_extractor = LLMExtractor(model=model)

    def __call__(self, text: str) -> dict:
        """사용자 입력 텍스트를 구조화된 정보로 변환"""
        
        # 키워드 추출
        keywords = self.text_mining.extract_keywords(text, self.stopword_path)
        if not keywords:
            print("키워드가 추출되지 않았습니다. 입력 텍스트를 확인하세요.")
            return {}

        # LLM 기반 구조화
        structured_info = self.llm_extractor.extract_info(text, keywords)

        return structured_info


if __name__ == "__main__":
    analyzer = UserInputAnalyzer(stopword_path="./user_input/stopword.txt", model="gpt-5")
    text = "소방장비의 운영 및 관리 실태를 파악하고 문제점과 통합지원 필요성을 진단하는 설문을 하려고합니다 대상은 소방공무원 입니다. 10문항으로 설문지를 구성해주세요"
    
    result = analyzer(text)

    print("분석 결과:")
    print(result)