import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu
from data_loader import get_available_years, get_available_months, load_factory_data

st.set_page_config(page_title="건재사업본부 손익", page_icon="📊", layout="wide")

# ── 전체 CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif; }

[data-testid="stAppViewContainer"] { background: #f4f6f9; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

.top-nav {
    background: linear-gradient(90deg, #0f2044 0%, #1a3a6c 100%);
    padding: 0 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}
.top-nav .brand {
    color: white;
    font-size: 1.1em;
    font-weight: 900;
    letter-spacing: 1px;
}
.top-nav .user {
    color: rgba(255,255,255,0.8);
    font-size: 0.85em;
}

.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    border-left: 4px solid #1a56db;
    height: 100%;
}
.kpi-card.green { border-left-color: #16a34a; }
.kpi-card.red { border-left-color: #dc2626; }
.kpi-card.orange { border-left-color: #ea580c; }
.kpi-card.purple { border-left-color: #7c3aed; }

.kpi-label {
    color: #6b7280;
    font-size: 0.82em;
    font-weight: 500;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.kpi-value {
    color: #111827;
    font-size: 1.8em;
    font-weight: 900;
    line-height: 1;
    margin-bottom: 8px;
}
.kpi-unit { color: #9ca3af; font-size: 0.75em; font-weight: 400; }
.kpi-delta-pos { color: #16a34a; font-size: 0.85em; font-weight: 600; }
.kpi-delta-neg { color: #dc2626; font-size: 0.85em; font-weight: 600; }
.kpi-delta-sub { color: #9ca3af; font-size: 0.78em; margin-left: 4px; }

.section-title {
    font-size: 1em;
    font-weight: 700;
    color: #1f2937;
    margin: 20px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #e5e7eb;
}

.chart-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}

.page-header {
    background: white;
    padding: 16px 30px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 20px;
}

.badge {
    background: #eff6ff;
    color: #1d4ed8;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 600;
}
.badge.red { background: #fef2f2; color: #dc2626; }
.badge.green { background: #f0fdf4; color: #16a34a; }

table.custom-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88em;
}
table.custom-table th {
    background: #1a3a6c;
    color: white;
    padding: 10px 12px;
    text-align: center;
    font-weight: 600;
}
table.custom-table td {
    padding: 9px 12px;
    text-align: right;
    border-bottom: 1px solid #f3f4f6;
    color: #374151;
}
table.custom-table td:first-child { text-align: center; font-weight: 600; color: #1f2937; }
table.custom-table tr:hover td { background: #f8fafc; }
table.custom-table tr.total td { background: #eff6ff; font-weight: 700; color: #1d4ed8; }
.pos { color: #16a34a !important; font-weight: 600; }
.neg { color: #dc2626 !important; font-weight: 600; }

.filter-bar {
    background: white;
    padding: 12px 30px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 16px;
}

.content-area { padding: 20px 30px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 로그인
# ══════════════════════════════════════════════════════════════
USERS = st.secrets.get("users", {"tongyang": "6150"})

def login():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f2044 0%, #1a3a6c 60%, #0f2044 100%) !important;
    }
    .stTextInput > label { color: rgba(255,255,255,0.7) !important; font-size:0.9em !important; }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }
    .stButton > button {
        background: #1a56db !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1em !important;
        height: 48px !important;
        letter-spacing: 2px !important;
        margin-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>" * 3, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("""
        <div style="text-align:center; margin-bottom:40px;">
            <div style="color:rgba(255,255,255,0.5);font-size:0.85em;letter-spacing:4px;margin-bottom:8px;">EUGENE GROUP</div>
            <div style="color:white;font-size:2em;font-weight:900;line-height:1.3;">건재사업본부<br>손익 대시보드</div>
            <div style="color:rgba(255,255,255,0.4);font-size:0.85em;margin-top:12px;">Profit & Loss Dashboard</div>
        </div>
        <div style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.15);border-radius:16px;padding:36px 40px;">
        """, unsafe_allow_html=True)

        username = st.text_input("아이디", placeholder="아이디를 입력하세요")
        password = st.text_input("패스워드", type="password", placeholder="패스워드를 입력하세요")

        if st.button("L O G I N", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("아이디 또는 패스워드가 올바르지 않습니다.")

        st.markdown("""
        </div>
        <div style="text-align:center;color:rgba(255,255,255,0.25);font-size:0.75em;margin-top:24px;">
            © 2026 Eugene Group. All rights reserved.
        </div>
        """, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ══════════════════════════════════════════════════════════════
# 헬퍼 함수
# ══════════════════════════════════════════════════════════════
REMICON_FACTORIES = ['안양','인천','파주','김포','부산','서부산','김해',
                     '정관','양산','창원','대구','울산','아산','전주','군산','원주','제주']

def f(val, decimal=0):
    if val is None or (isinstance(val, float) and pd.isna(val)): return "-"
    fmt = f"{{:,.{decimal}f}}"
    return fmt.format(val)

def delta_html(val, unit=""):
    if val is None or (isinstance(val, float) and pd.isna(val)): return ""
    arrow = "▲" if val >= 0 else "▼"
    cls = "pos" if val >= 0 else "neg"
    return f'<span class="{cls}">{arrow} {f(abs(val))}{unit}</span>'

def kpi_card(label, value, unit, delta=None, delta_label="계획대비", color="blue"):
    delta_html_str = ""
    if delta is not None and not (isinstance(delta, float) and pd.isna(delta)):
        arrow = "▲" if delta >= 0 else "▼"
        cls = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        delta_html_str = f'<div class="{cls}">{arrow} {f(abs(delta))}<span class="kpi-delta-sub">{delta_label}</span></div>'
    color_cls = {"blue": "", "green": "green", "red": "red", "orange": "orange", "purple": "purple"}.get(color, "")
    return f"""
    <div class="kpi-card {color_cls}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit"> {unit}</span></div>
        {delta_html_str}
    </div>
    """

def chart_layout(fig, title="", height=380):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color='#1f2937'), x=0),
        height=height,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11), gridcolor='#f3f4f6'),
        yaxis=dict(tickfont=dict(size=11), gridcolor='#f3f4f6'),
        font=dict(family='Noto Sans KR'),
    )
    return fig

COLORS = {"계획": "#93c5fd", "실적": "#1d4ed8", "전년": "#f87171",
          "양수": "#1d4ed8", "음수": "#dc2626", "green": "#16a34a"}

# ══════════════════════════════════════════════════════════════
# 상단 네비게이션
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="top-nav">
    <div class="brand">📊 건재사업본부 손익 대시보드</div>
    <div class="user">👤 {st.session_state['username']}</div>
</div>
""", unsafe_allow_html=True)

# 필터 + 로그아웃
fc1, fc2, fc3, fc4, fc5 = st.columns([2, 1.2, 1.2, 1, 0.8])
with fc1:
    st.markdown("<div style='padding:8px 30px;font-weight:700;color:#374151;font-size:0.9em;'>기간 선택</div>", unsafe_allow_html=True)
years = get_available_years()
selected_year = fc2.selectbox("연도", years, label_visibility="collapsed")
months = get_available_months(selected_year)
selected_month = fc3.selectbox("월", months, format_func=lambda x: f"{x}월", label_visibility="collapsed")
fc4.markdown("<div style='padding:10px 0;'></div>", unsafe_allow_html=True)
if fc5.button("로그아웃", use_container_width=True):
    st.session_state["logged_in"] = False
    st.rerun()

# 메인 메뉴
selected_menu = option_menu(
    menu_title=None,
    options=["건재 손익", "레미콘", "건자재", "골재", "임대"],
    icons=["bar-chart-fill", "truck", "building", "gem", "house-fill"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0 30px", "background-color": "white",
                      "border-bottom": "2px solid #e5e7eb"},
        "icon": {"font-size": "15px"},
        "nav-link": {"font-size": "14px", "font-weight": "600", "padding": "14px 24px",
                     "color": "#6b7280", "border-radius": "0"},
        "nav-link-selected": {"background-color": "white", "color": "#1d4ed8",
                               "border-bottom": "3px solid #1d4ed8", "border-radius": "0"},
    }
)

# 서브 메뉴
if selected_menu == "건재 손익":
    sub = option_menu(None,
        options=["손익 총괄", "공장별 손익"],
        icons=["grid-3x3-gap", "bar-chart"],
        default_index=0, orientation="horizontal",
        styles={"container": {"padding": "4px 30px", "background": "#f8fafc"},
                "nav-link": {"font-size": "13px", "padding": "8px 18px", "color": "#6b7280"},
                "nav-link-selected": {"background": "#eff6ff", "color": "#1d4ed8", "border-radius": "6px"}})
elif selected_menu == "레미콘":
    sub = option_menu(None,
        options=["공헌이익 분석", "공장별 손익"],
        icons=["graph-up-arrow", "bar-chart-line"],
        default_index=0, orientation="horizontal",
        styles={"container": {"padding": "4px 30px", "background": "#f8fafc"},
                "nav-link": {"font-size": "13px", "padding": "8px 18px", "color": "#6b7280"},
                "nav-link-selected": {"background": "#eff6ff", "color": "#1d4ed8", "border-radius": "6px"}})
else:
    sub = None

# ── 데이터 로드
@st.cache_data
def get_data(year, month):
    return load_factory_data(year, month)

df_all = get_data(selected_year, selected_month)
if df_all is None:
    st.error(f"{selected_year}년 {selected_month}월 데이터를 찾을 수 없습니다.")
    st.stop()

df_rc = df_all[df_all['공장명'].isin(REMICON_FACTORIES)].copy()
df_summary = df_all[df_all['공장명'].isin(['레미콘 계','건자재','골재 계','기타','합계'])].copy()

# ══════════════════════════════════════════════════════════════
# 페이지: 건재 손익 > 손익 총괄
# ══════════════════════════════════════════════════════════════
if selected_menu == "건재 손익" and sub == "손익 총괄":
    with st.container():
        st.markdown(f'<div style="padding:16px 30px 0;"><span style="font-size:1.15em;font-weight:900;color:#1f2937;">손익 총괄</span> <span class="badge">{selected_year}년 {selected_month}월</span></div>', unsafe_allow_html=True)

    합계row = df_summary[df_summary['공장명'] == '합계']
    레미콘row = df_summary[df_summary['공장명'] == '레미콘 계']

    with st.container():
        st.markdown('<div class="content-area">', unsafe_allow_html=True)

        # KPI 카드
        if not 합계row.empty:
            r = 합계row.iloc[0]
            c1, c2, c3, c4, c5 = st.columns(5)
            cards = [
                (c1, kpi_card("매출 실적", f(r['매출_실적']), "백만원",
                              r.get('매출_차이'), "계획대비", "blue")),
                (c2, kpi_card("영업이익 실적", f(r['영업이익_실적']), "백만원",
                              r.get('영업이익_차이'), "계획대비",
                              "green" if r.get('영업이익_실적', 0) >= 0 else "red")),
                (c3, kpi_card("전년 매출", f(r['매출_전년']), "백만원",
                              r['매출_실적'] - r['매출_전년'] if pd.notna(r.get('매출_전년')) else None,
                              "전년대비", "purple")),
                (c4, kpi_card("전년 영업이익", f(r['영업이익_전년']), "백만원",
                              r['영업이익_실적'] - r['영업이익_전년'] if pd.notna(r.get('영업이익_전년')) else None,
                              "전년대비", "orange")),
                (c5, kpi_card("레미콘 물량", f(레미콘row.iloc[0]['물량_실적'], 1) if not 레미콘row.empty else "-",
                              "천㎥",
                              레미콘row.iloc[0].get('물량_차이') if not 레미콘row.empty else None,
                              "계획대비", "blue")),
            ]
            for col, html in cards:
                col.markdown(html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 차트
        display_names = ['레미콘 계', '건자재', '골재 계', '기타']
        df_disp = df_summary[df_summary['공장명'].isin(display_names)].copy()
        name_map = {'레미콘 계': '레미콘', '골재 계': '골재'}
        df_disp['공장명'] = df_disp['공장명'].map(lambda x: name_map.get(x, x))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_bar(name='계획', x=df_disp['공장명'], y=df_disp['매출_계획'],
                        marker_color=COLORS['계획'], text=df_disp['매출_계획'].apply(lambda x: f(x)),
                        textposition='outside', textfont=dict(size=10))
            fig.add_bar(name='실적', x=df_disp['공장명'], y=df_disp['매출_실적'],
                        marker_color=COLORS['실적'], text=df_disp['매출_실적'].apply(lambda x: f(x)),
                        textposition='outside', textfont=dict(size=10))
            fig.add_bar(name='전년', x=df_disp['공장명'], y=df_disp['매출_전년'],
                        marker_color=COLORS['전년'], text=df_disp['매출_전년'].apply(lambda x: f(x)),
                        textposition='outside', textfont=dict(size=10))
            chart_layout(fig, "사업부문별 매출액 (백만원)")
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_bar(name='계획', x=df_disp['공장명'], y=df_disp['영업이익_계획'], marker_color=COLORS['계획'])
            fig2.add_bar(name='실적', x=df_disp['공장명'], y=df_disp['영업이익_실적'], marker_color=COLORS['실적'])
            fig2.add_bar(name='전년', x=df_disp['공장명'], y=df_disp['영업이익_전년'], marker_color=COLORS['전년'])
            chart_layout(fig2, "사업부문별 영업이익 (백만원)")
            fig2.update_layout(barmode='group')
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 상세 테이블
        st.markdown('<div class="section-title">사업부문별 손익 상세</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)

        rows_to_show = df_summary[df_summary['공장명'].isin(display_names + ['합계'])].copy()
        rows_to_show['공장명'] = rows_to_show['공장명'].map(lambda x: name_map.get(x, x))

        html = """<table class="custom-table">
        <thead><tr>
            <th>구분</th>
            <th>매출 계획</th><th>매출 실적</th><th>차이</th><th>전년</th><th>전년대비</th>
            <th>영업이익 계획</th><th>영업이익 실적</th><th>차이</th><th>전년</th><th>전년대비</th>
        </tr></thead><tbody>"""

        for _, r in rows_to_show.iterrows():
            is_total = r['공장명'] == '합계'
            tr_class = 'class="total"' if is_total else ''
            매출차이 = r.get('매출_차이')
            영업차이 = r.get('영업이익_차이')
            매출전년차이 = r['매출_실적'] - r['매출_전년'] if pd.notna(r.get('매출_전년')) else None
            영업전년차이 = r['영업이익_실적'] - r['영업이익_전년'] if pd.notna(r.get('영업이익_전년')) else None

            def td_delta(val):
                if val is None or (isinstance(val, float) and pd.isna(val)): return '<td>-</td>'
                cls = 'pos' if val >= 0 else 'neg'
                arrow = '▲' if val >= 0 else '▼'
                return f'<td class="{cls}">{arrow} {f(abs(val))}</td>'

            html += f"""<tr {tr_class}>
                <td>{r['공장명']}</td>
                <td>{f(r.get('매출_계획'))}</td>
                <td>{f(r.get('매출_실적'))}</td>
                {td_delta(매출차이)}
                <td>{f(r.get('매출_전년'))}</td>
                {td_delta(매출전년차이)}
                <td>{f(r.get('영업이익_계획'))}</td>
                <td>{f(r.get('영업이익_실적'))}</td>
                {td_delta(영업차이)}
                <td>{f(r.get('영업이익_전년'))}</td>
                {td_delta(영업전년차이)}
            </tr>"""

        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지: 건재 손익 > 공장별 손익
# ══════════════════════════════════════════════════════════════
elif selected_menu == "건재 손익" and sub == "공장별 손익":
    st.markdown(f'<div style="padding:16px 30px 0;"><span style="font-size:1.15em;font-weight:900;color:#1f2937;">공장별 손익</span> <span class="badge">{selected_year}년 {selected_month}월</span></div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="content-area">', unsafe_allow_html=True)

        metric = st.selectbox("지표", ['매출', '영업이익', '물량'],
                               format_func=lambda x: {'매출': '매출액 (백만원)', '영업이익': '영업이익 (백만원)', '물량': '판매물량 (천㎥)'}[x])

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_bar(name='계획', x=df_rc['공장명'], y=df_rc[f'{metric}_계획'], marker_color=COLORS['계획'])
            fig.add_bar(name='실적', x=df_rc['공장명'], y=df_rc[f'{metric}_실적'], marker_color=COLORS['실적'])
            fig.add_bar(name='전년', x=df_rc['공장명'], y=df_rc[f'{metric}_전년'], marker_color=COLORS['전년'])
            chart_layout(fig, f"공장별 {metric}", 420)
            fig.update_layout(barmode='group', xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            df_diff = df_rc[['공장명','영업이익_차이']].dropna()
            colors_diff = [COLORS['양수'] if v >= 0 else COLORS['음수'] for v in df_diff['영업이익_차이']]
            fig2 = go.Figure(go.Bar(
                x=df_diff['영업이익_차이'], y=df_diff['공장명'],
                orientation='h', marker_color=colors_diff,
                text=df_diff['영업이익_차이'].apply(lambda x: f(x)),
                textposition='outside', textfont=dict(size=10)
            ))
            fig2.add_vline(x=0, line_color='#374151', line_width=1.5)
            chart_layout(fig2, "영업이익 계획대비 (백만원)", 420)
            fig2.update_layout(yaxis=dict(autorange='reversed'))
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 테이블
        st.markdown('<div class="section-title">공장별 손익 상세</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)

        html = """<table class="custom-table">
        <thead><tr>
            <th>공장명</th>
            <th>물량 계획</th><th>물량 실적</th><th>차이</th>
            <th>매출 계획</th><th>매출 실적</th><th>차이</th>
            <th>영업이익 계획</th><th>영업이익 실적</th><th>차이</th>
        </tr></thead><tbody>"""

        for _, r in df_rc.iterrows():
            def td_d(val):
                if val is None or (isinstance(val, float) and pd.isna(val)): return '<td>-</td>'
                cls = 'pos' if val >= 0 else 'neg'
                arrow = '▲' if val >= 0 else '▼'
                return f'<td class="{cls}">{arrow} {f(abs(val),1)}</td>'

            html += f"""<tr>
                <td>{r['공장명']}</td>
                <td>{f(r.get('물량_계획'),1)}</td><td>{f(r.get('물량_실적'),1)}</td>{td_d(r.get('물량_차이'))}
                <td>{f(r.get('매출_계획'))}</td><td>{f(r.get('매출_실적'))}</td>{td_d(r.get('매출_차이'))}
                <td>{f(r.get('영업이익_계획'))}</td><td>{f(r.get('영업이익_실적'))}</td>{td_d(r.get('영업이익_차이'))}
            </tr>"""
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지: 레미콘 > 공헌이익 분석
# ══════════════════════════════════════════════════════════════
elif selected_menu == "레미콘" and sub == "공헌이익 분석":
    st.markdown(f'<div style="padding:16px 30px 0;"><span style="font-size:1.15em;font-weight:900;color:#1f2937;">레미콘 공헌이익 분석</span> <span class="badge">{selected_year}년 {selected_month}월</span> <span style="color:#9ca3af;font-size:0.85em;">단위: 원/㎥</span></div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="content-area">', unsafe_allow_html=True)

        rc_sum = df_all[df_all['공장명'] == '레미콘 계']
        if not rc_sum.empty:
            r = rc_sum.iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(kpi_card("판매단가 실적", f(r['판매단가_실적']), "원/㎥",
                                  r['판매단가_실적'] - r['판매단가_전년'] if pd.notna(r.get('판매단가_전년')) else None,
                                  "전년대비", "blue"), unsafe_allow_html=True)
            c2.markdown(kpi_card("변동비 실적", f(r['변동비_실적']), "원/㎥",
                                  r['변동비_실적'] - r['변동비_전년'] if pd.notna(r.get('변동비_전년')) else None,
                                  "전년대비", "red"), unsafe_allow_html=True)
            c3.markdown(kpi_card("공헌이익 실적", f(r['공헌이익_실적']), "원/㎥",
                                  r['공헌이익_실적'] - r['공헌이익_전년'] if pd.notna(r.get('공헌이익_전년')) else None,
                                  "전년대비", "green"), unsafe_allow_html=True)
            c4.markdown(kpi_card("전년 공헌이익", f(r['공헌이익_전년']), "원/㎥", None, "", "purple"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_bar(name='판매단가', x=df_rc['공장명'], y=df_rc['판매단가_실적'],
                        marker_color=COLORS['실적'])
            fig.add_bar(name='변동비', x=df_rc['공장명'], y=df_rc['변동비_실적'],
                        marker_color=COLORS['전년'])
            chart_layout(fig, "공장별 판매단가 vs 변동비 (원/㎥)", 380)
            fig.update_layout(barmode='group', xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            colors_ci = [COLORS['실적'] if v >= 0 else COLORS['음수'] for v in df_rc['공헌이익_실적'].fillna(0)]
            fig2 = go.Figure(go.Bar(
                x=df_rc['공장명'], y=df_rc['공헌이익_실적'],
                marker_color=colors_ci,
                text=df_rc['공헌이익_실적'].apply(lambda x: f(x)),
                textposition='outside', textfont=dict(size=10)
            ))
            fig2.add_hline(y=0, line_dash='dash', line_color='#374151', line_width=1.5)
            chart_layout(fig2, "공장별 공헌이익 실적 (원/㎥)", 380)
            fig2.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 전년대비 차이
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        df_rc2 = df_rc.copy()
        df_rc2['공헌이익_전년대비'] = df_rc2['공헌이익_실적'] - df_rc2['공헌이익_전년']
        df_rc2['판매단가_전년대비'] = df_rc2['판매단가_실적'] - df_rc2['판매단가_전년']
        df_rc2['변동비_전년대비'] = df_rc2['변동비_실적'] - df_rc2['변동비_전년']
        df_yoy = df_rc2.dropna(subset=['공헌이익_전년대비'])

        fig3 = go.Figure()
        fig3.add_bar(name='판매단가 변화', x=df_yoy['공장명'], y=df_yoy['판매단가_전년대비'], marker_color='#60a5fa')
        fig3.add_bar(name='변동비 변화', x=df_yoy['공장명'], y=df_yoy['변동비_전년대비'], marker_color='#f87171')
        fig3.add_scatter(name='공헌이익 변화', x=df_yoy['공장명'], y=df_yoy['공헌이익_전년대비'],
                         mode='lines+markers', line=dict(color='#7c3aed', width=2),
                         marker=dict(size=8))
        fig3.add_hline(y=0, line_dash='dash', line_color='#374151', line_width=1)
        chart_layout(fig3, "전년 대비 공헌이익 변화 분석 (원/㎥)", 350)
        fig3.update_layout(barmode='relative', xaxis_tickangle=-30)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 상세 테이블
        st.markdown('<div class="section-title">공장별 공헌이익 상세</div>', unsafe_allow_html=True)
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)

        html = """<table class="custom-table">
        <thead><tr>
            <th rowspan="2">공장명</th>
            <th colspan="3">판매단가 (원/㎥)</th>
            <th colspan="3">변동비 (원/㎥)</th>
            <th colspan="3">공헌이익 (원/㎥)</th>
        </tr><tr>
            <th>계획</th><th>실적</th><th>전년</th>
            <th>계획</th><th>실적</th><th>전년</th>
            <th>계획</th><th>실적</th><th>전년</th>
        </tr></thead><tbody>"""

        for _, r in df_rc.iterrows():
            ci_cls = 'pos' if (r.get('공헌이익_실적') or 0) >= 0 else 'neg'
            html += f"""<tr>
                <td>{r['공장명']}</td>
                <td>{f(r.get('판매단가_계획'))}</td><td>{f(r.get('판매단가_실적'))}</td><td>{f(r.get('판매단가_전년'))}</td>
                <td>{f(r.get('변동비_계획'))}</td><td>{f(r.get('변동비_실적'))}</td><td>{f(r.get('변동비_전년'))}</td>
                <td>{f(r.get('공헌이익_계획'))}</td>
                <td class="{ci_cls}">{f(r.get('공헌이익_실적'))}</td>
                <td>{f(r.get('공헌이익_전년'))}</td>
            </tr>"""
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지: 레미콘 > 공장별 손익
# ══════════════════════════════════════════════════════════════
elif selected_menu == "레미콘" and sub == "공장별 손익":
    st.markdown(f'<div style="padding:16px 30px 0;"><span style="font-size:1.15em;font-weight:900;color:#1f2937;">레미콘 공장별 손익</span> <span class="badge">{selected_year}년 {selected_month}월</span></div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="content-area">', unsafe_allow_html=True)

        rc_sum = df_all[df_all['공장명'] == '레미콘 계']
        if not rc_sum.empty:
            r = rc_sum.iloc[0]
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(kpi_card("레미콘 매출", f(r['매출_실적']), "백만원", r.get('매출_차이'), "계획대비", "blue"), unsafe_allow_html=True)
            c2.markdown(kpi_card("레미콘 영업이익", f(r['영업이익_실적']), "백만원", r.get('영업이익_차이'), "계획대비",
                                  "green" if (r.get('영업이익_실적') or 0) >= 0 else "red"), unsafe_allow_html=True)
            c3.markdown(kpi_card("레미콘 물량", f(r['물량_실적'],1), "천㎥", r.get('물량_차이'), "계획대비", "purple"), unsafe_allow_html=True)
            c4.markdown(kpi_card("공장 수", "17", "개", None, "", "orange"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_bar(name='계획', x=df_rc['공장명'], y=df_rc['영업이익_계획'], marker_color=COLORS['계획'])
            fig.add_bar(name='실적', x=df_rc['공장명'], y=df_rc['영업이익_실적'], marker_color=COLORS['실적'])
            fig.add_bar(name='전년', x=df_rc['공장명'], y=df_rc['영업이익_전년'], marker_color=COLORS['전년'])
            chart_layout(fig, "공장별 영업이익 (백만원)", 380)
            fig.update_layout(barmode='group', xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            df_rank = df_rc[['공장명','영업이익_실적']].dropna().sort_values('영업이익_실적', ascending=True)
            colors_rank = [COLORS['실적'] if v >= 0 else COLORS['음수'] for v in df_rank['영업이익_실적']]
            fig2 = go.Figure(go.Bar(
                x=df_rank['영업이익_실적'], y=df_rank['공장명'],
                orientation='h', marker_color=colors_rank,
                text=df_rank['영업이익_실적'].apply(lambda x: f(x)),
                textposition='outside', textfont=dict(size=10)
            ))
            fig2.add_vline(x=0, line_color='#374151', line_width=1.5)
            chart_layout(fig2, "영업이익 순위 (백만원)", 380)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지: 건자재 / 골재 / 임대
# ══════════════════════════════════════════════════════════════
elif selected_menu in ["건자재", "골재", "임대"]:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;height:400px;flex-direction:column;">
        <div style="font-size:3em;margin-bottom:16px;">🚧</div>
        <div style="font-size:1.4em;font-weight:700;color:#374151;margin-bottom:8px;">{selected_menu} 손익</div>
        <div style="color:#9ca3af;">준비 중입니다. 곧 업데이트될 예정입니다.</div>
    </div>
    """, unsafe_allow_html=True)
