from user_input.user_input_module import UserInputAnalyzer
from system_orchestration.orchestration import SurveyOrchestration
import time 

# 1. 유저 요구사항 분석 

t1 = time.time()
analyzer = UserInputAnalyzer(stopword_path="./user_input/stopword.txt", model="gpt-5")
text = "병원의 조직문화 개선을 위한 설문을 하려고합니다 대상은 병원에 근무하는 의료진 및 직원들 입니다. 10문항으로 설문지를 구성해주세요"

print('사용자 요구사항 분석 및 출력 진행...')
print(f'사용자 요구사항: \n{text}')
user_input = analyzer(text)

print("분석 결과:")
print(user_input)
print(f'{time.time() - t1:.1f}초 소요')


# 2. 시스템 오케스트레이션 
t2 = time.time()
so = SurveyOrchestration(user_input)
current_survey = so()

print('\n 생성 완료:')
print(current_survey)
print(f'{time.time() - t2:.1f}초 소요\n')

# 3. 피드백 루프
max_iterations = 5
iteration = 1

while iteration <= max_iterations:
    print("\n" + "="*60)
    print(f"버전 {iteration} - 피드백 입력")
    print("="*60)
    print("명령어: 승인, 또는 피드백 입력")
    
    user_input_text = input("\n입력: ").strip()
    
    if user_input_text.upper() == '승인':
        print("\n 설문지 최종 승인!")
        print("\n" + "="*60)
        print("최종 설문지")
        print("="*60)
        print(current_survey)
        break
    
    else:
        # 피드백 처리
        current_survey = so.process_feedback(
            current_survey,
            user_input_text
        )
        
        print("\n 수정 완료:")
        print(current_survey)
        
        iteration += 1

if iteration > max_iterations:
    print("\n 최대 반복 횟수 도달")
    print("\n" + "="*60)
    print("최종 설문지")
    print("="*60)
    print(current_survey)
