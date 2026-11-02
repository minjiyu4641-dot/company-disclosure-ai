"""CareerLens AI | 카드형 홈 → 분석 상세 + 챗봇

실행: python -m streamlit run company_dashboard_cards.py

이 파일은 UI 프로토타입입니다. 데이터와 챗봇 답변은 실제 공시가 아닙니다.
"""

from pathlib import Path
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="CareerLens AI | 기업 공시 분석",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 이 앱은 기존 style.css 대신 별도 파일을 불러옵니다.
style_file = Path(__file__).with_name("style_cards.css")
if style_file.exists():
    st.markdown(f"<style>{style_file.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ------------------------------------------------------------
# 1. 시연용 샘플 데이터 (실제 기업 공시자료가 아닙니다.)
# ------------------------------------------------------------

SAMPLES = {
    '삼익THK': {'industry':'산업 자동화 부품', 'sales':[950,1100,1200], 'profit':[110,135,150], 'debt':85,
      'desc':'산업기계의 정밀 운동을 돕는 부품과 자동화 솔루션을 공급하는 기업입니다.',
      'segments':{'자동화 부품':65,'기타 산업부품':25,'기타':10},
      'swot':{'S 강점':'정밀 기계부품 관련 기술·사업 기반','W 약점':'설비투자 경기와 연관된 수요 변동 가능성','O 기회':'생산 자동화 관련 수요 확대 가능성','T 위협':'고객 제조업의 투자 축소'},
      'strategy':['기존 주력 부품의 경쟁력 강화','자동화 관련 사업 기회 검토'],
      'questions':['주요 고객 산업이 침체되면 매출에 어떤 영향이 있을까?','영업이익이 매출보다 빠르게 변하는 이유는?','향후 투자 계획은 실제로 실행 중이야?']},
    '티씨케이': {'industry':'반도체 소재·부품','sales':[850,910,1020],'profit':[160,180,210],'debt':42,
      'desc':'반도체 제조 공정 등에 활용되는 소재와 부품을 공급하는 기업입니다.',
      'segments':{'반도체 공정용 부품':78,'기타 제품':17,'기타':5},
      'swot':{'S 강점':'공정용 소재·부품 관련 전문성','W 약점':'반도체 산업 수요 의존 가능성','O 기회':'반도체 설비투자 확대 가능성','T 위협':'업황 악화에 따른 고객 투자 축소'},
      'strategy':['공정 부품의 기술 경쟁력 강화','고객 수요 대응을 위한 생산 역량 검토'],
      'questions':['반도체 업황 침체는 어떤 위험이 될까?','최근 3년 실적의 변화는?','설비투자가 수익성에 어떤 영향을 줄까?']},
    '성광벤드': {'industry':'산업용 배관 부품','sales':[1300,1250,1380],'profit':[130,115,145],'debt':58,
      'desc':'에너지·플랜트 설비 등에 사용되는 산업용 관이음쇠를 생산하는 기업입니다.',
      'segments':{'산업용 관이음쇠':83,'기타 부품':12,'기타':5},
      'swot':{'S 강점':'산업용 배관 분야 사업 경험','W 약점':'플랜트 투자 사이클의 영향 가능성','O 기회':'에너지·인프라 프로젝트 확대','T 위협':'해외 프로젝트 지연 및 수주 변동'},
      'strategy':['산업용 관이음쇠 수주 역량 강화','해외 수요 변화 대응'],
      'questions':['플랜트 수주 감소는 얼마나 위험할까?','매출액 변동 요인을 알려줘','해외 사업의 주요 위험은?']},
}

# ------------------------------------------------------------
# 2. 메인 카드 정의: 제목·설명을 바꾸고 싶으면 여기 수정
# ------------------------------------------------------------

SECTIONS = [
    {"id": "overview", "emoji": "🏢", "title": "기업 한눈에 보기", "tag": "기업 이해",
     "desc": "어떤 일을 하는 회사인지, 핵심 사업부터 알아봐요.", "color": "#E9F1FF",
     "question": "이 기업의 핵심 사업과 주요 고객 산업은 무엇인가요?"},
    {"id": "financial", "emoji": "💰", "title": "주요 재무지표", "tag": "재무",
     "desc": "매출액·영업이익·부채비율을 쉽게 살펴봐요.", "color": "#FFF0E4",
     "question": "최근 매출과 영업이익 변화는 어떤 의미인가요?"},
    {"id": "trend", "emoji": "📈", "title": "최근 3개년 실적", "tag": "변화 추이",
     "desc": "3년간 실적이 좋아졌는지 그래프로 확인해요.", "color": "#EAF9F0",
     "question": "최근 3년간 실적 변동 원인을 설명해 주세요."},
    {"id": "business", "emoji": "🧩", "title": "사업 구조·매출 의존도", "tag": "사업 리스크",
     "desc": "어느 사업에서 매출이 나오고, 무엇에 민감할까요?", "color": "#F0EBFF",
     "question": "주요 고객 산업이 침체되면 매출에 얼마나 영향을 주나요?"},
    {"id": "swot", "emoji": "🌼", "title": "SWOT 분석", "tag": "강점과 위험",
     "desc": "강점·약점·기회·위협을 근거와 함께 정리해요.", "color": "#FFF0F3",
     "question": "이 기업의 가장 중요한 사업 위험은 무엇인가요?"},
    {"id": "strategy", "emoji": "🚀", "title": "미래 전략·실행 현황", "tag": "미래 방향",
     "desc": "발표한 계획이 실제로 실행되고 있는지 살펴봐요.", "color": "#E9F6FF",
     "question": "회사의 향후 투자 계획은 실제로 진행 중인가요?"},
    {"id": "checklist", "emoji": "📝", "title": "취업 준비 체크포인트", "tag": "지원 전 확인",
     "desc": "입사 지원 전에 꼭 확인하면 좋은 질문들이에요.", "color": "#FFF6DB",
     "question": "이 기업에 입사하기 전 추가로 확인할 점은 무엇인가요?"},
]
SECTION_BY_ID = {item["id"]: item for item in SECTIONS}

# ------------------------------------------------------------
# 3. 화면 이동 상태: 기존 화면을 고치지 않고 카드-상세 전환
# ------------------------------------------------------------

if "view" not in st.session_state:
    st.session_state.view = "home"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_company" not in st.session_state:
    st.session_state.last_company = None


def open_section(section_id):
    st.session_state.view = section_id


def back_home():
    st.session_state.view = "home"


# ------------------------------------------------------------
# 4. 공통 헤더 · 기업 선택
# ------------------------------------------------------------

st.markdown('''
<div class="brand-row">
  <div class="brand-symbol">✿</div>
  <div class="brand-copy">
    <div class="brand-title">CareerLens <span>AI</span></div>
    <div class="brand-caption">공시를 쉽게, 내 미래 직장을 더 똑똑하게</div>
  </div>
  <span class="brand-demo">✨ UI 데모</span>
</div>
''', unsafe_allow_html=True)

c_company, c_year = st.columns([3, 1], gap="medium")
with c_company:
    company = st.selectbox("🔎 분석할 기업을 선택하세요", list(SAMPLES), key="company_select")
with c_year:
    reporting_year = st.selectbox("분석 기준연도", [2025], key="reporting_year")

data = SAMPLES[company]
if st.session_state.last_company != company:
    st.session_state.last_company = company
    st.session_state.view = "home"
    st.session_state.messages = []

# ------------------------------------------------------------
# 5. 첫 화면: 예쁜 카드 목록
# ------------------------------------------------------------

if st.session_state.view == "home":
    st.markdown(f'''
    <div class="hero">
      <div class="hero-eyebrow">🔍 취준생을 위한 기업 탐색</div>
      <div class="hero-title">{escape(company)},<br><span>어디부터 알아볼까요?</span></div>
      <p>궁금한 주제의 카드를 골라 보세요. 분석 화면에서 AI 챗봇과 함께 더 깊게 살펴볼 수 있어요.</p>
      <div class="hero-tags"><span>🌿 쉬운 재무 설명</span><span>📚 공시 근거 연동 예정</span><span>💬 함께 묻는 AI</span></div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('### ✨ 알아보고 싶은 주제를 골라주세요')
    st.caption("각 카드의 ‘들어가 보기’ 버튼을 누르면 분석과 챗봇이 함께 열려요.")

    for i in range(0, len(SECTIONS), 3):
        cols = st.columns(3, gap="medium")
        for col, section in zip(cols, SECTIONS[i:i+3]):
            with col:
                with st.container(border=True, key=f'feature_card_{section["id"]}'):
                    st.markdown(
                        f'<div class="feature-icon" style="background:{section["color"]}">{section["emoji"]}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(f'#### {section["title"]}')
                    st.markdown(f'<div class="feature-description">{section["desc"]}</div>', unsafe_allow_html=True)
                    st.caption(section["tag"])
                    if st.button("들어가 보기  →", key=f'open_{section["id"]}', use_container_width=True):
                        open_section(section["id"])
                        st.rerun()

    st.markdown('''
    <div class="home-footer">🧸 <b>참고해 주세요</b> — 현재 내용은 화면 테스트용 가상 데이터예요. 실제 공시 자료와 AI 검색은 다음 개발 단계에서 연결합니다.</div>
    ''', unsafe_allow_html=True)

# ------------------------------------------------------------
# 6. 상세 화면: 선택한 주제 + 우측 챗봇
# ------------------------------------------------------------

else:
    section = SECTION_BY_ID[st.session_state.view]
    nav_a, nav_b = st.columns([2, 5], vertical_alignment="center")
    with nav_a:
        if st.button("←  카드 목록으로", key="go_back"):
            back_home()
            st.rerun()
    with nav_b:
        st.caption(f"{company}  /  {section['tag']}  /  {reporting_year}년 시연용 데이터")

    st.markdown(f'''
    <div class="detail-banner">
       <div class="detail-icon" style="background:{section['color']}">{section['emoji']}</div>
       <div><div class="detail-kicker">{escape(company)}의 기업 리포트</div>
         <div class="detail-title">{section['title']}</div>
         <div class="detail-subtitle">{section['desc']}</div>
       </div>
    </div>
    ''', unsafe_allow_html=True)

    left, right = st.columns([1.7, 1], gap="large")

    with left:
        with st.container(border=True, key="analysis_panel"):
            if section["id"] == "overview":
                st.subheader("🏢 어떤 회사인가요?")
                st.write(data["desc"])
                st.markdown("#### 🔍 이런 부분도 살펴봐요")
                st.info("주력 제품이 무엇인지뿐 아니라, 그 사업이 전체 매출에서 차지하는 비중도 확인하는 것이 좋아요.")
                st.markdown("**분석 시 확인할 공시 항목**")
                st.write("사업의 내용 · 주요 제품 및 서비스 · 매출 및 수주상황")

            elif section["id"] == "financial":
                st.subheader("💰 주요 재무지표")
                a, b, c = st.columns(3)
                a.metric("매출액", f'{data["sales"][-1]:,}억 원',
                         f'{(data["sales"][-1]/data["sales"][-2]-1)*100:+.1f}%')
                b.metric("영업이익", f'{data["profit"][-1]:,}억 원',
                         f'{(data["profit"][-1]/data["profit"][-2]-1)*100:+.1f}%')
                c.metric("부채비율", f'{data["debt"]}%')
                st.markdown("#### 🧸 이렇게 읽어 보세요")
                st.write("매출액은 판매 규모를, 영업이익은 본업에서 남기는 이익을 살펴보는 데 활용해요. 부채비율은 자본 대비 부채의 크기를 확인하는 지표예요.")
                st.info("수치만으로 기업의 고용 안정성이나 미래 실적을 보장할 수는 없어요.")

            elif section["id"] == "trend":
                st.subheader("📈 최근 3개년 실적 추이")
                fig = go.Figure()
                years = ["2023", "2024", "2025"]
                fig.add_trace(go.Bar(x=years, y=data["sales"], name="매출액",
                                     marker_color="#A7C8F2"))
                fig.add_trace(go.Scatter(x=years, y=data["profit"], name="영업이익",
                                         yaxis="y2", mode="lines+markers",
                                         line=dict(color="#8273DE", width=3), marker=dict(size=9)))
                fig.update_layout(
                    height=350, margin=dict(l=8, r=15, t=35, b=10),
                    plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(color="#47546C"),
                    legend=dict(orientation="h", y=1.17),
                    xaxis=dict(type="category"),
                    yaxis=dict(title="매출액(억 원)", gridcolor="#EDF0F6"),
                    yaxis2=dict(title="영업이익(억 원)", overlaying="y", side="right", showgrid=False),
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("이 그래프는 두 지표에 서로 다른 축을 사용한 가상 데이터예요.")
                st.info("매출액과 영업이익의 증가율이 다르다면 원재료비, 판매관리비, 제품 구성 등을 추가로 확인할 필요가 있어요.")

            elif section["id"] == "business":
                st.subheader("🧩 사업 구조와 매출 의존도")
                main_segment = max(data["segments"], key=data["segments"].get)
                fig = go.Figure(go.Bar(
                    x=list(data["segments"].values()),
                    y=list(data["segments"].keys()), orientation="h",
                    marker_color=["#9186E9", "#A9CBF0", "#E9DCF8"],
                    text=[f'{v}%' for v in data["segments"].values()],
                    textposition="auto",
                ))
                fig.update_layout(
                    height=280, margin=dict(l=10, r=20, t=12, b=20),
                    paper_bgcolor="white", plot_bgcolor="white",
                    xaxis=dict(range=[0, 100], title="가상 매출 비중(%)", gridcolor="#EEF0F5"),
                    yaxis=dict(autorange="reversed"),
                    font=dict(color="#49556B"),
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("#### 💡 AI 분석에 넣을 핵심 질문")
                st.write(f'시연용 데이터에서는 **{main_segment}**이 매출의 **{data["segments"][main_segment]}%**를 차지해요. 이 사업에 대한 집중도가 높을 경우 관련 업황 변화가 중요할 수 있어요.')
                st.warning("제품별 매출 비중과 고객 산업별 매출 비중은 서로 달라요. 고객 산업별 정보가 없다면 특정 산업의 영향을 숫자로 단정하지 않아야 해요.")

            elif section["id"] == "swot":
                st.subheader("🌼 SWOT 분석")
                st.caption("아래 항목들은 공시에서 검증되지 않은 시연용 내용이에요.")
                colors = ["#EBFAF2", "#FFF6E8", "#EAF3FF", "#FFF0F1"]
                entries = list(data["swot"].items())
                for row in range(2):
                    columns = st.columns(2, gap="medium")
                    for col, ((name, value), bg) in zip(columns, zip(entries[row*2:row*2+2], colors[row*2:row*2+2])):
                        with col:
                            st.markdown(f'''
                            <div class="swot-box" style="background:{bg}">
                                <div class="swot-name">{escape(name)}</div>
                                <div class="swot-body">{escape(value)}</div>
                            </div>''', unsafe_allow_html=True)
                st.info("실제 서비스에서는 항목마다 사업보고서 연도·목차·원문 링크를 붙이고, 확인된 사실과 AI 해석을 구분할 예정이에요.")

            elif section["id"] == "strategy":
                st.subheader("🚀 미래 전략과 실행 현황")
                for n, strategy in enumerate(data["strategy"], start=1):
                    st.markdown(f'**전략 {n}. {strategy}**')
                    st.caption("시연용 전략 예시 · 실제 공시 확인 전")
                st.divider()
                st.markdown("#### 🗂 확인 순서")
                for label, desc in [
                    ("1. 기업이 발표한 계획", "사업보고서·신규시설투자 공시 등에서 계획 확인"),
                    ("2. 실제 실행 여부", "투자 공시·유형자산·투자활동 현금흐름 비교"),
                    ("3. 사업 성과", "생산능력·매출·수익성 변화 확인"),
                ]:
                    st.markdown(f'**{label}**  \n{desc}')
                st.warning("현재 데모에는 실제 실행 검증 결과가 없어요. 계획과 달성 사실을 혼동하지 않도록 표시해요.")

            elif section["id"] == "checklist":
                st.subheader("📝 입사 지원 전 체크리스트")
                for n, question in enumerate(data["questions"], start=1):
                    st.markdown(f'**{n}. {question}**')
                    st.caption("아래 챗봇에 같은 질문을 보내 추가 확인할 수 있어요.")
                st.info("공시는 재무·사업 현황의 근거가 되지만 조직문화나 실제 고용 안정성을 모두 설명해 주지는 않아요.")

            st.markdown('''
            <div class="source-note">📎 <b>출처 표시 예정</b> — 실제 DART API와 RAG를 연결하면 공시명, 연도, 목차, 원문 링크를 여기에 표시합니다.</div>
            ''', unsafe_allow_html=True)

            if st.button("💬 이 주제를 AI에게 질문하기", key=f'ask_{section["id"]}', use_container_width=True):
                st.session_state.queued_question = section["question"]
                st.rerun()

    # --------------------------------------------------------
    # 7. 우측 챗봇: 추천 질문과 입력 작동, 아직 RAG 미연결
    # --------------------------------------------------------
    with right:
        with st.container(border=True, key="chat_panel"):
            st.markdown('#### 🤖 공시 AI에게 물어봐요')
            st.caption(f"{company} · 지금은 AI 답변 시연 단계예요")

            st.markdown("**이런 질문은 어때요?**")
            suggested = [section["question"]] + [q for q in data["questions"] if q != section["question"]]
            for i, q in enumerate(suggested[:3]):
                if st.button(q, key=f'suggest_{section["id"]}_{i}', use_container_width=True):
                    st.session_state.queued_question = q

            left_clear, right_empty = st.columns([1, 2])
            with left_clear:
                if st.button("대화 지우기", key="clear_chat"):
                    st.session_state.messages = []
                    st.rerun()

            conversation = st.container(height=390, border=True, key="chat_history")
            typed_question = st.chat_input("궁금한 점을 편하게 물어봐요!", key="chat_prompt")
            queued_question = st.session_state.pop("queued_question", None)
            question = queued_question or typed_question

            if question:
                st.session_state.messages.append({"role": "user", "content": question})

                # TODO: RAG 연결 시 이 부분을 실제 질의응답 함수로 교체하세요.
                # answer = answer_with_rag(company, question)
                if any(word in question for word in ["침체", "위험", "의존", "수요"]):
                    answer = (
                        "🧸 **현재는 데모 답변이에요.**  \n"
                        "사업 구조·제품별 매출 비중·원재료 가격·수주 현황을 연결하면 "
                        "고객 산업 변화에 따른 위험을 설명할 수 있어요.  \n\n"
                        "다만 실제 공시를 읽지 않았으므로 이 기업의 위험 수준을 단정하지 않아요."
                    )
                elif any(word in question for word in ["매출", "이익", "실적", "재무"]):
                    answer = (
                        "🧸 **현재는 데모 답변이에요.**  \n"
                        "실제 연결 후에는 3개년 매출·영업이익·현금흐름 변화를 계산하고 "
                        "원인으로 언급된 공시 문장을 함께 찾아 보여줄 거예요."
                    )
                elif any(word in question for word in ["전략", "계획", "투자", "실행"]):
                    answer = (
                        "🧸 **현재는 데모 답변이에요.**  \n"
                        "기업의 발표된 계획과 후속 투자 공시를 비교하고, 확인된 실행 실적과 "
                        "향후 목표를 구분해 설명할 예정이에요."
                    )
                else:
                    answer = (
                        "🧸 **질문은 잘 받았어요!** 지금은 실제 공시 검색이 연결되지 않았어요.  \n"
                        "RAG를 구현하면 선택 기업의 사업보고서에서 관련 내용을 찾아 설명해 드릴게요."
                    )
                answer += "\n\n📎 **출처:** 미연결 (실제 공시 근거 없음)"
                st.session_state.messages.append({"role": "assistant", "content": answer})

            with conversation:
                if not st.session_state.messages:
                    st.chat_message("assistant").write("안녕하세요! 🌷 왼쪽 분석을 보다가 궁금한 점이 생기면 물어보세요.")
                for message in st.session_state.messages:
                    st.chat_message(message["role"]).markdown(message["content"])

    st.caption("⚠️ 이 페이지의 숫자, SWOT, 전략 설명은 실제 기업 공시가 아닌 가상 예시입니다. 취업·투자 판단에 사용하지 마세요.")
