from user_input.text_mining import TextMiningProcessor
from user_input.llm_extractor import LLMExtractor

# 1텍스트 마이닝 단계
processor = TextMiningProcessor()
text = "대학생을 대상으로 온라인 강의 만족도를 조사하고자 합니다. 강의 질과 교수자의 피드백에 대해 평가합니다."
keywords = processor.extract_keywords(text, "./user_input/stopword.txt")



# LLM 기반 정보 추출 단계
extractor = LLMExtractor(model="gpt-5")
structured_info = extractor.extract_info(text, keywords)

print("🔍 텍스트 마이닝 결과:", keywords)
print("📘 LLM 구조화 결과:", structured_info)



print(structured_info)