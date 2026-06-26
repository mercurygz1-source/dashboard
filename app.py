import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from data_loader import (
    get_available_years, get_available_months,
    load_factory_data
)

st.set_page_config(
    page_title="건재사업본부 손익 대시보드",
    page_icon="📊",
    layout="wide"
)

# ── 로그인 ────────────────────────────────────────────────────
USERS = st.secrets.get("users", {"tongyang": "6150"})

def login():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a1628 0%, #1a3a5c 50%, #0d2137 100%);
    }
    [data-testid="stHeader"] { background: transparent; }
    .login-left {
        color: white;
        padding: 60px 40px;
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .login-left h1 {
        font-size: 3em;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 30px;
        color: white;
    }
    .login-left p {
        font-size: 1.1em;
        color: rgba(255,255,255,0.8);
        line-height: 2;
    }
    .stTextInput > label { color: rgba(255,255,255,0.7) !important; }
    .stTextInput > div > div > input {
        background: #2a3f55 !important;
        border: 1px solid #3a5f80 !important;
        color: white !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        background: #1a56db !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1em !important;
        padding: 12px !important;
        letter-spacing: 2px !important;
        margin-top: 10px;
    }
    .stButton > button:hover { background: #1e40af !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown("""
        <div class="login-left">
            <p style="color:rgba(255,255,255,0.5);font-size:0.9em;font-weight:700;letter-spacing:3px;">EUGENE GROUP</p>
            <h1>Your Dream is<br>Our Passion</h1>
            <p>당신의 가능성을 응원합니다.<br>
               당신의 꿈이 우리의 미래입니다.<br>
               당신의 가능성은 세계보다 넓습니다.<br>
               당신의 꿈을 맘껏 펼치세요.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:#1e2d3d;border-radius:16px;padding:50px 40px;margin:40px 0;">
        <h2 style="color:white;font-size:1.3em;font-weight:700;letter-spacing:1px;margin-bottom:30px;text-align:center;">
        건재사업본부 손익 대시보드</h2>
        </div>
        """, unsafe_allow_html=True)
        username = st.text_input("아이디", placeholder="아이디를 입력하세요")
        password = st.text_input("패스워드", type="password", placeholder="패스워드를 입력하세요")
        if st.button("LOGIN", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("아이디 또는 패스워드가 틀렸습니다.")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ── 공통 CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none; }
[data-testid="stHeader"] { background: #0a1628; }
.top-header {
    background: #0a1628;
    padding: 10px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: -1rem -1rem 0 -1rem;
}
.top-header .logo {
    color: white;
    font-size: 1.2em;
    font-weight: 800;
    letter-spacing: 2px;
}
.top-header .user-info {
    color: rgba(255,255,255,0.7);
    font-size: 0.9em;
}
</style>
""", unsafe_allow_html=True)

# ── 상단 헤더 ─────────────────────────────────────────────────
col_logo, col_filter, col_user = st.columns([2, 4, 2])

with col_logo:
    st.markdown("""
    <div style="padding:10px 0;">
        <span style="font-size:1.3em;font-weight:900;color:#0a1628;letter-spacing:2px;">📊 건재사업본부</span>
    </div>
    """, unsafe_allow_html=True)

with col_filter:
    fc1, fc2 = st.columns(2)
    years = get_available_years()
    selected_year = fc1.selectbox("연도", years, label_visibility="collapsed")
    months = get_available_months(selected_year)
    selected_month = fc2.selectbox("월", months, format_func=lambda x: f"{x}월", label_visibility="collapsed")

with col_user:
    st.markdown(f"""
    <div style="text-align:right;padding:10px 0;color:#666;font-size:0.9em;">
        👤 {st.session_state['username']}
    </div>
    """, unsafe_allow_html=True)
    if st.button("로그아웃", use_container_width=True):
        st.session_state["logged_in"] = False
        st.rerun()

st.markdown("<hr style='margin:0 0 10px 0;border-color:#e0e0e0;'>", unsafe_allow_html=True)

# ── 상단 네비게이션 ───────────────────────────────────────────
selected_menu = option_menu(
    menu_title=None,
    options=["건재 손익", "레미콘", "건자재", "골재", "임대"],
    icons=["bar-chart-fill", "truck", "building", "gem", "house"],
    menu_icon=None,
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0", "background-color": "#f8f9fa", "border-radius": "8px"},
        "icon": {"color": "#1a56db", "font-size": "16px"},
        "nav-link": {
            "font-size": "15px",
            "font-weight": "600",
            "text-align": "center",
            "padding": "12px 20px",
            "color": "#333",
        },
        "nav-link-selected": {
            "background-color": "#1a56db",
            "color": "white",
            "border-radius": "8px",
        },
    }
)

if selected_menu == "건재 손익":
    sub = option_menu(
        menu_title=None,
        options=["손익 총괄", "공장별 손익"],
        icons=["table", "bar-chart"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0", "background-color": "#fff"},
            "nav-link": {"font-size": "13px", "padding": "8px 16px", "color": "#555"},
            "nav-link-selected": {"background-color": "#e8f0fe", "color": "#1a56db", "border-radius": "6px"},
        }
    )
elif selected_menu == "레미콘":
    sub = option_menu(
        menu_title=None,
        options=["공헌이익 분석", "공장별 비교"],
        icons=["graph-up", "bar-chart-line"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0", "background-color": "#fff"},
            "nav-link": {"font-size": "13px", "padding": "8px 16px", "color": "#555"},
            "nav-link-selected": {"background-color": "#e8f0fe", "color": "#1a56db", "border-radius": "6px"},
        }
    )
else:
    sub = None

st.markdown("<hr style='margin:10px 0;border-color:#e0e0e0;'>", unsafe_allow_html=True)

# ── 데이터 로드 ───────────────────────────────────────────────
@st.cache_data
def get_data(year, month):
    return load_factory_data(year, month)

df_all = get_data(selected_year, selected_month)

if df_all is None:
    st.error(f"{selected_year}년 {selected_month}월 데이터 파일을 찾을 수 없습니다.")
    st.stop()

REMICON_FACTORIES = [
    '안양', '인천', '파주', '김포', '부산', '서부산', '김해',
    '정관', '양산', '창원', '대구', '울산', '아산', '전주',
    '군산', '원주', '제주'
]

def fmt_mil(val):
    if val is None or pd.isna(val): return "-"
    return f"{val:,.0f}"

def fmt_unit(val):
    if val is None or pd.isna(val): return "-"
    return f"{val:,.0f}"


# ════════════════════════════════════════════════════════════════
# 건재 손익 > 손익 총괄
# ════════════════════════════════════════════════════════════════
if selected_menu == "건재 손익" and sub == "손익 총괄":
    st.subheader(f"건재사업본부 손익 총괄  |  {selected_year}년 {selected_month}월")
    st.markdown("---")

    summary_names = ['레미콘 계', '건자재', '골재 계', '기타', '합계']
    df_summary = df_all[df_all['공장명'].isin(summary_names)].copy()

    합계 = df_summary[df_summary['공장명'] == '합계']
    if not 합계.empty:
        row = 합계.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("매출 실적 (백만원)", fmt_mil(row['매출_실적']), delta=fmt_mil(row['매출_차이']) if pd.notna(row.get('매출_차이')) else None)
        c2.metric("영업이익 실적 (백만원)", fmt_mil(row['영업이익_실적']), delta=fmt_mil(row['영업이익_차이']) if pd.notna(row.get('영업이익_차이')) else None)
        c3.metric("전년 매출 (백만원)", fmt_mil(row['매출_전년']))
        c4.metric("전년 영업이익 (백만원)", fmt_mil(row['영업이익_전년']))

    st.markdown("---")
    display_names = ['레미콘 계', '건자재', '골재 계', '기타']
    df_disp = df_summary[df_summary['공장명'].isin(display_names)].copy()

    if not df_disp.empty:
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_bar(name='계획', x=df_disp['공장명'], y=df_disp['매출_계획'], marker_color='#aec7e8')
            fig.add_bar(name='실적', x=df_disp['공장명'], y=df_disp['매출_실적'], marker_color='#1a56db')
            fig.add_bar(name='전년', x=df_disp['공장명'], y=df_disp['매출_전년'], marker_color='#d62728', opacity=0.6)
            fig.update_layout(title='매출액 (백만원)', barmode='group', height=400,
                              legend=dict(orientation='h', yanchor='bottom', y=1.02))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = go.Figure()
            fig2.add_bar(name='계획', x=df_disp['공장명'], y=df_disp['영업이익_계획'], marker_color='#98df8a')
            fig2.add_bar(name='실적', x=df_disp['공장명'], y=df_disp['영업이익_실적'], marker_color='#2ca02c')
            fig2.add_bar(name='전년', x=df_disp['공장명'], y=df_disp['영업이익_전년'], marker_color='#d62728', opacity=0.6)
            fig2.update_layout(title='영업이익 (백만원)', barmode='group', height=400,
                               legend=dict(orientation='h', yanchor='bottom', y=1.02))
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.subheader("사업부문별 상세 테이블")
    table_df = df_summary[df_summary['공장명'].isin(display_names + ['합계'])].copy()
    table_df = table_df[['공장명', '매출_계획', '매출_실적', '매출_차이', '매출_전년',
                          '영업이익_계획', '영업이익_실적', '영업이익_차이', '영업이익_전년']].copy()
    table_df.columns = ['구분', '매출_계획', '매출_실적', '매출_차이', '매출_전년',
                        '영업이익_계획', '영업이익_실적', '영업이익_차이', '영업이익_전년']
    for col in table_df.columns[1:]:
        table_df[col] = table_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) and x != '' else '-')
    st.dataframe(table_df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════
# 건재 손익 > 공장별 손익
# ════════════════════════════════════════════════════════════════
elif selected_menu == "건재 손익" and sub == "공장별 손익":
    st.subheader(f"레미콘 공장별 손익  |  {selected_year}년 {selected_month}월")
    st.markdown("---")

    df_rc = df_all[df_all['공장명'].isin(REMICON_FACTORIES)].copy()
    metric = st.selectbox("지표 선택", ['매출', '영업이익', '물량'])

    if not df_rc.empty:
        fig = go.Figure()
        fig.add_bar(name='계획', x=df_rc['공장명'], y=df_rc[f'{metric}_계획'], marker_color='#aec7e8')
        fig.add_bar(name='실적', x=df_rc['공장명'], y=df_rc[f'{metric}_실적'], marker_color='#1a56db')
        fig.add_bar(name='전년', x=df_rc['공장명'], y=df_rc[f'{metric}_전년'], marker_color='#d62728', opacity=0.6)
        unit = '백만원' if metric != '물량' else '천㎥'
        fig.update_layout(title=f'공장별 {metric} ({unit})', barmode='group', height=500,
                          xaxis_tickangle=-30, legend=dict(orientation='h', yanchor='bottom', y=1.02))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        df_diff = df_rc[['공장명', '영업이익_차이']].dropna()
        colors = ['#1a56db' if v >= 0 else '#d62728' for v in df_diff['영업이익_차이']]
        fig2 = go.Figure(go.Bar(x=df_diff['공장명'], y=df_diff['영업이익_차이'], marker_color=colors))
        fig2.add_hline(y=0, line_dash='dash', line_color='black')
        fig2.update_layout(title='영업이익 계획 대비 차이 (백만원)', height=400, xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        table_df = df_rc[['공장명', '물량_실적', '매출_계획', '매출_실적', '매출_차이',
                           '영업이익_계획', '영업이익_실적', '영업이익_차이']].copy()
        table_df.columns = ['공장명', '물량(천㎥)', '매출_계획', '매출_실적', '매출_차이',
                             '영업이익_계획', '영업이익_실적', '영업이익_차이']
        for col in table_df.columns[1:]:
            table_df[col] = table_df[col].apply(lambda x: f"{x:,.1f}" if pd.notna(x) else '-')
        st.dataframe(table_df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════
# 레미콘 > 공헌이익 분석
# ════════════════════════════════════════════════════════════════
elif selected_menu == "레미콘" and sub == "공헌이익 분석":
    st.subheader(f"레미콘 공헌이익 분석  |  {selected_year}년 {selected_month}월  (단위: 원/㎥)")
    st.markdown("---")

    df_rc = df_all[df_all['공장명'].isin(REMICON_FACTORIES)].copy()
    rc_sum = df_all[df_all['공장명'] == '레미콘 계']

    if not rc_sum.empty:
        row = rc_sum.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("판매단가 실적", fmt_unit(row['판매단가_실적']),
                  delta=fmt_unit(row['판매단가_실적'] - row['판매단가_전년']) if pd.notna(row['판매단가_전년']) else None)
        c2.metric("변동비 실적", fmt_unit(row['변동비_실적']),
                  delta=fmt_unit(row['변동비_실적'] - row['변동비_전년']) if pd.notna(row['변동비_전년']) else None,
                  delta_color='inverse')
        c3.metric("공헌이익 실적", fmt_unit(row['공헌이익_실적']),
                  delta=fmt_unit(row['공헌이익_실적'] - row['공헌이익_전년']) if pd.notna(row['공헌이익_전년']) else None)
        c4.metric("전년 공헌이익", fmt_unit(row['공헌이익_전년']))

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_bar(name='판매단가', x=df_rc['공장명'], y=df_rc['판매단가_실적'], marker_color='#1a56db')
        fig.add_bar(name='변동비', x=df_rc['공장명'], y=df_rc['변동비_실적'], marker_color='#d62728')
        fig.update_layout(title='판매단가 vs 변동비', barmode='group', height=420, xaxis_tickangle=-30,
                          legend=dict(orientation='h', yanchor='bottom', y=1.02))
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        colors = ['#2ca02c' if v >= 0 else '#d62728' for v in df_rc['공헌이익_실적'].fillna(0)]
        fig2 = go.Figure(go.Bar(x=df_rc['공장명'], y=df_rc['공헌이익_실적'], marker_color=colors))
        fig2.update_layout(title='공헌이익 실적 (원/㎥)', height=420, xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    table_df = df_rc[['공장명', '판매단가_계획', '판매단가_실적', '판매단가_전년',
                       '변동비_계획', '변동비_실적', '변동비_전년',
                       '공헌이익_계획', '공헌이익_실적', '공헌이익_전년']].copy()
    for col in table_df.columns[1:]:
        table_df[col] = table_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else '-')
    st.dataframe(table_df, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════
# 레미콘 > 공장별 비교
# ════════════════════════════════════════════════════════════════
elif selected_menu == "레미콘" and sub == "공장별 비교":
    st.subheader(f"레미콘 공장별 비교  |  {selected_year}년 {selected_month}월")
    st.markdown("---")
    df_rc = df_all[df_all['공장명'].isin(REMICON_FACTORIES)].copy()
    df_rc['공헌이익_전년대비'] = df_rc['공헌이익_실적'] - df_rc['공헌이익_전년']
    df_yoy = df_rc[['공장명', '공헌이익_전년대비']].dropna()
    colors_yoy = ['#1a56db' if v >= 0 else '#d62728' for v in df_yoy['공헌이익_전년대비']]
    fig3 = go.Figure(go.Bar(x=df_yoy['공장명'], y=df_yoy['공헌이익_전년대비'], marker_color=colors_yoy))
    fig3.add_hline(y=0, line_dash='dash', line_color='black')
    fig3.update_layout(title='공헌이익 전년 대비 변화 (원/㎥)', height=450, xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)


# ════════════════════════════════════════════════════════════════
# 건자재 / 골재 / 임대 (준비중)
# ════════════════════════════════════════════════════════════════
elif selected_menu in ["건자재", "골재", "임대"]:
    st.markdown(f"""
    <div style="text-align:center;padding:100px;color:#999;">
        <h2>📋 {selected_menu} 페이지</h2>
        <p>준비 중입니다.</p>
    </div>
    """, unsafe_allow_html=True)
