import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title='기업 공시 분석 AI | CareerLens', page_icon='🏢', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
.stApp {background:#f7f8fc;color:#172039;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#171d3c,#252452);}
[data-testid="stSidebar"] * {color:#f5f6ff !important;}
.block-container {padding-top:1.4rem;padding-bottom:3rem;max-width:1600px;}
h1,h2,h3 {color:#1b2440 !important;}
div[data-testid="stMetric"] {background:white;border:1px solid #e5e9f4;border-radius:14px;padding:14px;}
div[data-testid="stVerticalBlockBorderWrapper"] {border-color:#e4e8f3 !important;border-radius:15px !important;background:#fff;}
.stButton>button[kind="primary"] {background:#6554d8;border-color:#6554d8;border-radius:10px;}
.small-note {color:#64708a;font-size:.86rem;}
.headline {padding:12px 18px;border-radius:14px;background:linear-gradient(110deg,#f0edff,#e9f4ff);border:1px solid #e1dcff;}
.risk {padding:13px 16px;background:#fff8ed;border-left:4px solid #eaa352;border-radius:8px;margin:8px 0;}
.source {font-size:.78rem;color:#68738b;}
</style>''', unsafe_allow_html=True)

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

with st.sidebar:
    st.markdown('## ✦ CareerLens AI')
    st.caption('공시로 이해하는 나의 미래 직장')
    st.divider()
    st.markdown('### 기업 분석')
    st.write('📊 재무·사업 분석')
    st.write('🧩 근거 기반 SWOT')
    st.write('💬 공시 질문 챗봇')
    st.divider()
    st.info('데모 모드: 모든 수치·분석 문구는 기능 시연을 위한 **가상 자료**이며 실제 기업 공시 사실이 아닙니다.')

st.title('🏢 기업 공시 분석 AI')
st.caption('기업이 무엇으로 돈을 버는지, 최근 실적은 어떤지, 어떤 위험을 확인해야 하는지 한 화면에서 탐색합니다.')

search_col, year_col, btn_col = st.columns([4,2,1.4],vertical_alignment='bottom')
with search_col:
    selected = st.selectbox('기업 선택', list(SAMPLES.keys()), index=0)
with year_col:
    reporting_year = st.selectbox('분석 기준연도', [2025], index=0)
with btn_col:
    clicked = st.button('🔎 기업 분석하기',type='primary',use_container_width=True)
if 'company' not in st.session_state:
    st.session_state.company = selected
if clicked:
    st.session_state.company = selected
    st.session_state.messages = []
company = st.session_state.company
data = SAMPLES[company]

st.markdown(f'<div class="headline"><strong style="font-size:1.3rem">{company}</strong> &nbsp; <span class="small-note">{data["industry"]} · {reporting_year}년 가상 데이터 기준</span></div>',unsafe_allow_html=True)
st.write('')
left,right = st.columns([1.75,1],gap='large')

with left:
    with st.container(border=True):
        st.subheader('01 · 기업 개요 및 AI 핵심 진단')
        st.write(data['desc'])
        st.markdown('<div class="risk"><b>검토 포인트</b> · 주력 사업의 매출 집중도와 고객 산업의 투자 사이클을 함께 확인하세요. 사업 의존도만으로 미래 실적 변화를 확정할 수는 없습니다.</div>',unsafe_allow_html=True)
    with st.container(border=True):
        st.subheader('02 · 주요 재무지표')
        a,b,c = st.columns(3)
        a.metric('매출액',f'{data["sales"][-1]:,}억 원',f'{(data["sales"][-1]/data["sales"][-2]-1)*100:+.1f}%')
        b.metric('영업이익',f'{data["profit"][-1]:,}억 원',f'{(data["profit"][-1]/data["profit"][-2]-1)*100:+.1f}%')
        c.metric('부채비율',f'{data["debt"]}%',help='부채총계/자본총계 × 100')
        st.caption('예시 수치 / 실제 연결 시 연결·별도 기준, 단위, 기준연도 표시')
    with st.container(border=True):
        st.subheader('03 · 최근 3개년 실적 추이')
        years=['2023','2024','2025']
        fig=go.Figure()
        fig.add_trace(go.Bar(name='매출액',x=years,y=data['sales'],marker_color='#8bb7f1'))
        fig.add_trace(go.Scatter(name='영업이익',x=years,y=data['profit'],mode='lines+markers',line=dict(color='#7957d5',width=3),yaxis='y2'))
        fig.update_layout(height=275,margin=dict(l=8,r=8,t=15,b=0),plot_bgcolor='white',paper_bgcolor='white',legend=dict(orientation='h',y=1.12),yaxis=dict(title='매출액 (억 원)',gridcolor='#edf0f6'),yaxis2=dict(title='영업이익 (억 원)',overlaying='y',side='right'),xaxis=dict(type='category'))
        st.plotly_chart(fig,use_container_width=True)
        st.caption('매출과 영업이익은 서로 다른 축으로 표시한 가상 데이터입니다.')
    with st.container(border=True):
        st.subheader('04 · 사업 구조 및 매출 의존도')
        segments=pd.DataFrame({'사업':list(data['segments']),'매출 비중(%)':list(data['segments'].values())})
        st.bar_chart(segments.set_index('사업'),horizontal=True,color='#8c80dd')
        main_segment=max(data['segments'],key=data['segments'].get)
        st.info(f'핵심 사업인 **{main_segment}**의 가상 매출 비중은 **{data["segments"][main_segment]}%**입니다. 관련 고객 산업이 침체되면 영향을 받을 가능성이 있지만, 실제 영향은 수주·계약 조건을 추가로 확인해야 합니다.')
    with st.container(border=True):
        st.subheader('05 · 공시 근거 기반 SWOT 분석')
        cells=list(data['swot'].items())
        ca,cb=st.columns(2)
        for i,(key,value) in enumerate(cells):
            with (ca if i%2==0 else cb):
                st.markdown(f'**{key}**')
                st.info(value)
        st.caption('시연용 분류 / 실제 서비스에서는 각 항목에 공시 문서명과 근거 링크를 연결')
    with st.container(border=True):
        st.subheader('06 · 향후 주력 방향과 실행 현황')
        for n,desc in enumerate(data['strategy'],1):
            st.write(f'**전략 {n}.** {desc}')
        st.warning('현재 데모에서는 실행 여부를 검증하지 않았습니다. 실제 서비스에서는 계획 공시 → 후속 투자 공시 → 실적 변화를 구분해 표시합니다.',icon='📌')
    with st.container(border=True):
        st.subheader('07 · 취업 준비 체크포인트')
        for q in data['questions']:
            st.markdown('• '+q)

with right:
    st.subheader('🤖 공시자료 AI 챗봇')
    st.caption(f'선택 기업: {company} · 실제 RAG 미연결, 시연용 답변')
    st.markdown('**이어서 물어볼 질문**')
    for i,q in enumerate(data['questions']):
        if st.button(q,key=f'{company}_{i}',use_container_width=True):
            st.session_state.pending_question=q
    if 'messages' not in st.session_state:
        st.session_state.messages=[]
    question=st.chat_input('이 기업에 대해 무엇이 궁금하세요?',key='chatbox')
    if 'pending_question' in st.session_state:
        question=st.session_state.pop('pending_question')
    if question:
        st.session_state.messages.append({'role':'user','content':question})
        st.session_state.messages.append({'role':'assistant','content':f'**[데모 응답]** {company}의 공시자료를 검색하고 위험요인·재무 변화를 설명할 자리입니다. 현재는 공시 원문이 연결되지 않았으므로 실제 근거를 제시할 수 없습니다.\n\n📎 **출처:** 실제 RAG 연결 후 공시명·연도·목차·원문 링크 표시'})
    with st.container(height=580,border=True):
        st.chat_message('assistant').write('안녕하세요! 왼쪽 분석을 읽으면서 궁금한 점을 질문해 보세요. 지금은 **UI 데모 모드**입니다.')
        for m in st.session_state.messages:
            st.chat_message(m['role']).markdown(m['content'])

st.caption('⚠️ 이 앱의 모든 기업별 숫자와 SWOT은 가상 예시입니다. 취업·투자 판단에 사용하지 마세요.')
