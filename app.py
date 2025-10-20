import time
import streamlit as st
from user_input.user_input_module import UserInputAnalyzer
from system_orchestration.orchestration import SurveyOrchestration
from domain_model.survey_generator import SurveyGenerator
from rag.config import Config
from rag.rag_module import SurveyRAG

# 페이지 설정
st.set_page_config(
    page_title="AutoSurvey - AI 설문지 생성",
    page_icon="📋",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'survey_history' not in st.session_state:
    st.session_state.survey_history = []
if 'current_survey' not in st.session_state:
    st.session_state.current_survey = None
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'user_input' not in st.session_state:
    st.session_state.user_input = None
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'survey_version' not in st.session_state:
    st.session_state.survey_version = 0
# RAG 결과 저장용
if 'rag_context' not in st.session_state:
    st.session_state.rag_context = None
if 'selected_domain' not in st.session_state:
    st.session_state.selected_domain = None
    

# 헤더
st.title("📋 AutoSurvey")
st.markdown("### AI 기반 설문지 자동 생성 시스템")
st.markdown("---")


# ============================================
# 사이드바: 버전 히스토리
# ============================================
with st.sidebar:
    st.header("📚 버전 히스토리")
    
    if len(st.session_state.survey_history) == 0:
        st.info("아직 생성된 설문지가 없습니다.")
    else:
        for idx, (version, survey_text, timestamp) in enumerate(
            reversed(st.session_state.survey_history)
        ):
            with st.expander(f"버전 {version} - {timestamp}"):
                st.text_area(
                    "설문지 내용",
                    survey_text,
                    height=200,
                    key=f"history_{idx}",
                    disabled=True
                )
                if st.button("이 버전으로 복원", key=f"restore_{idx}"):
                    st.session_state.current_survey = survey_text
                    st.rerun()
    
    st.markdown("---")
    if st.button("🔄 전체 초기화", type="secondary", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ============================================
# 메인 영역
# ============================================

# 단계 표시
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.session_state.step >= 1:
        st.success("✅ 1단계: 요구사항 입력")
    else:
        st.info("1단계: 요구사항 입력")
with col2:
    if st.session_state.step >= 2:
        st.success("✅ 2단계: RAG 검색")
    else:
        st.info("2단계: RAG 검색")
with col3:
    if st.session_state.step >= 3:
        st.success("✅ 3단계: 설문지 생성")
    else:
        st.info("3단계: 설문지 생성")
with col4:
    if st.session_state.step >= 4:
        st.success("✅ 4단계: 피드백")
    else:
        st.info("4단계: 피드백")

st.markdown("---")


# ============================================
# 단계 1: 요구사항 입력
# ============================================
st.header("1️⃣ 설문 요구사항 입력")

user_text = st.text_area(
    "설문 요구사항을 입력하세요",
    placeholder="예: 병원의 조직문화 개선을 위한 설문을 하려고합니다. 대상은 병원에 근무하는 의료진 및 직원들입니다. 10문항으로 설문지를 구성해주세요.",
    height=150,
    key="user_text_input"
)


# 생성 버튼
if st.button("🚀 요구사항 분석하기", type="primary", use_container_width=True):
    if not user_text.strip():
        st.error("요구사항을 입력해주세요!")
    else:
        with st.spinner("📊 요구사항 분석 중..."):
            analyzer = UserInputAnalyzer(
                stopword_path="./user_input/stopword.txt",
            )
            st.session_state.user_input = analyzer(user_text)
            st.session_state.step = 2
            
        st.success("✅ 요구사항 분석 완료!")
        st.rerun()

if st.session_state.step >= 2 and st.session_state.user_input:
    with st.expander("🔍 분석된 요구사항 확인"):
        st.json(st.session_state.user_input)
        
# ============================================
# 단계 2: RAG 검색 결과 표시
# ============================================
if st.session_state.step >= 2 and st.session_state.rag_context is None:
    st.markdown("---")
    st.header("2️⃣ 참조 설문지 검색")
    
    if st.button("🔍 참조 설문지 검색 시작", type="primary", use_container_width=True):
        with st.spinner("🔎 유사 설문지 검색 중..."):
            # Orchestrator 초기화
            orchestrator = SurveyOrchestration(st.session_state.user_input)
            
            # RAG만 실행 (설문지 생성 전)
            rag_params = orchestrator.adjust_rag_params()
            rag_input = orchestrator.build_rag_query()
            
            # RAG 진행 상황 표시
            st.info(f"**검색 쿼리**: {rag_input}")
            

            
            survey_rag = SurveyRAG(
                model_name=Config.MODEL_NAME,
                sparse_weight=rag_params['sparse_weight'],
                dense_weight=rag_params['dense_weight'],
                k=rag_params['k']
            )
            
            context = survey_rag(rag_input)
            
            # 결과 저장
            st.session_state.rag_context = context
            st.session_state.orchestrator = orchestrator
            orchestrator.context = context  # orchestrator에도 저장
            st.session_state.step = 3
            
        st.success("✅ 참조 설문지 검색 완료!")
        st.rerun()


# RAG 결과 표시
if st.session_state.rag_context:
    st.markdown("---")
    st.header("2️⃣ 검색된 참조 설문지")
    
    st.markdown("### 📚 RAG 검색 결과")
    with st.expander("🔍 검색된 참조 설문지 내용 보기", expanded=True):
        st.text_area(
            "참조 설문지",
            st.session_state.rag_context,
            height=300,
            disabled=True,
            key="rag_result_display"
        )
    
    if st.session_state.selected_domain:
        st.info(f"**선택된 도메인**: {st.session_state.selected_domain}")


# ============================================
# 단계 3: 설문지 생성
# ============================================
if st.session_state.step >= 3 and st.session_state.current_survey is None:
    st.markdown("---")
    st.header("3️⃣ 설문지 생성")
    
    if st.button("✨ 설문지 생성 진행", type="primary", use_container_width=True):
        with st.spinner("✨ AI 설문지 생성 중..."):
            t_start = time.time()
            
            # 도메인 분류
            orchestrator = st.session_state.orchestrator
            orchestrator.selected_domain = orchestrator.domain_classifier(
                st.session_state.user_input,
                st.session_state.rag_context
            )
            st.session_state.selected_domain = orchestrator.selected_domain

            # 설문지 생성
            generator = SurveyGenerator(model_name='gpt-5')
            survey = generator(st.session_state.user_input, st.session_state.rag_context)
            
            t_elapsed = time.time() - t_start
            
            # 상태 저장
            st.session_state.current_survey = survey
            st.session_state.survey_version += 1
            st.session_state.step = 4
            
            # 히스토리 추가
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.survey_history.append((1, survey, timestamp))
            
        st.success(f"✅ 설문지 생성 완료! ({t_elapsed:.1f}초 소요)")
        st.rerun()


# ============================================
# 생성된 설문지 표시
# ============================================
if st.session_state.current_survey:
    st.markdown("---")
    st.header("3️⃣ 생성된 설문지")
    
    st.markdown("### 📄 설문지 미리보기")
    st.text_area(
        "생성된 설문지",
        st.session_state.current_survey,
        height=400,
        key=f"survey_preview_{st.session_state.survey_version}",
        disabled=True
    )
    
    st.download_button(
        label="💾 설문지 다운로드 (TXT)",
        data=st.session_state.current_survey,
        file_name=f"survey_{time.strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain",
        use_container_width=True
    )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ 최종 승인", type="primary", use_container_width=True):
            st.session_state.step = 5
            st.success("🎉 설문지가 최종 승인되었습니다!")
            
    with col2:
        if st.button("✏️ 피드백 입력하기", use_container_width=True):
            st.session_state.show_feedback = True
            st.rerun()


# ============================================
# 단계 4: 피드백
# ============================================
if st.session_state.get('show_feedback', False) or st.session_state.step >= 5:
    st.markdown("---")
    st.header("4️⃣ 피드백 및 개선")
    
    if st.session_state.step < 5:
        feedback_text = st.text_area(
            "수정 요청 사항을 입력하세요",
            placeholder="예: Q3번 문항을 7점 척도로 변경해주세요\n예: 직무 만족도 관련 문항을 2개 추가해주세요",
            height=100,
            key="feedback_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 재생성", type="primary", use_container_width=True):
                if not feedback_text.strip():
                    st.error("피드백을 입력해주세요!")
                else:
                    with st.spinner("🔍 피드백 분석 및 재생성 중..."):
                        try:
                            modified_survey = st.session_state.orchestrator.process_feedback(
                                st.session_state.current_survey,
                                feedback_text
                            )
                            
                            st.session_state.current_survey = modified_survey
                            st.session_state.survey_version += 1
                            
                            version = len(st.session_state.survey_history) + 1
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.survey_history.append(
                                (version, modified_survey, timestamp)
                            )
                            
                            st.session_state.show_feedback = False
                            st.success("✅ 설문지가 수정되었습니다!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ 오류 발생: {str(e)}")
        
        with col2:
            if st.button("❌ 피드백 취소", use_container_width=True):
                st.session_state.show_feedback = False
                st.rerun()
    
    else:
        st.success("설문지 작성이 완료되었습니다!")
        st.info("사이드바에서 이전 버전을 확인하거나, 새로운 설문지를 생성할 수 있습니다.")


# ============================================
# 푸터
# ============================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>AutoSurvey v1.0 | Powered by LangChain & Streamlit</small>
    </div>
    """,
    unsafe_allow_html=True
)