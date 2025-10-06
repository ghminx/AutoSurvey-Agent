# user_input/text_mining.py

import re
from konlpy.tag import Okt
from sklearn.feature_extraction.text import TfidfVectorizer

class TextMiningProcessor:
    def __init__(self):
        self.okt = Okt()
        self.vectorizer = TfidfVectorizer(max_features=30)

    def stopwords(self, path: str) -> list:
        """불용어 사전 로드"""
        stopwords = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                word = line.strip()
                if word:
                    stopwords.append(word)
        return stopwords

    def clean_text(self, text: str) -> str:
        """특수문자, 공백 제거"""
        text = re.sub(r"[^가-힣A-Za-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_keywords(self, text: str, path: str, top_k: int = 10) -> list:
        """
        형태소 분석 + TF-IDF 기반 핵심 키워드 추출
        - 명사 중심 추출
        - 불용어 및 단일 음절 제거
        - TF-IDF 가중치 기준 상위 top_k 반환
        """
        
        stopwords = self.stopwords(path)
        
        cleaned = self.clean_text(text)
        words = self.okt.pos(cleaned, norm=True, stem=True)

        nouns = [
            word for word, pos in words
            if pos == "Noun" and len(word) > 1 and word not in stopwords
        ]

        if not nouns:
            return []

        joined = " ".join(nouns)
        tfidf_matrix = self.vectorizer.fit_transform([joined])

        # TF-IDF 벡터에서 (단어, 가중치) 튜플 추출
        feature_names = self.vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # 점수 높은 순으로 정렬
        sorted_keywords = sorted(
            zip(feature_names, scores),
            key=lambda x: x[1],
            reverse=True
        )

        # 상위 top_k 키워드 반환
        return [word for word, _ in sorted_keywords[:top_k]]


if __name__ == "__main__":
    # 인스턴스 생성
    processor = TextMiningProcessor()

    # 테스트 문장
    text = "대학생을 대상으로 온라인 강의 만족도를 조사하고자 합니다. 강의 질과 교수자의 피드백에 대해 평가합니다."

    # 키워드 추출
    keywords = processor.extract_keywords(text, './user_input/stopword.txt')

    print("📘 입력 문장:", text)
    print("🔍 추출된 키워드:", keywords)



