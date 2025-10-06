# user_input/analyzer.py
from user_input.text_mining import TextMiningProcessor
from user_input.llm_extractor import LLMExtractor

class UserInputAnalyzer:
    """사용자 입력 분석 전체 프로세스 (Text Mining + LLM 추출)"""
    
    def __init__(self, stopword_path: str, model: str = "gpt-5"):
        self.stopword_path = stopword_path
        self.text_mining = TextMiningProcessor()
        self.llm_extractor = LLMExtractor(model=model)

    def analyze(self, text: str) -> dict:
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
    text = "대학생을 대상으로 온라인 강의 만족도를 조사하고자 합니다. 강의 질과 교수자의 피드백에 대해 평가합니다."
    
    result = analyzer.analyze(text)

    print("분석 결과:")
    print(result)