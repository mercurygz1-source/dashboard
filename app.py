import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import get_available_years, get_available_months, load_factory_data

st.set_page_config(page_title="건재사업본부 손익", page_icon="📊", layout="wide")

# ══════════════════════════════════════════════════════════════
# 세션 초기화
# ══════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "건재손익_총괄"

USERS = st.secrets.get("users", {"tongyang": "6150"})

# ══════════════════════════════════════════════════════════════
# 로그인 페이지
# ══════════════════════════════════════════════════════════════
if not st.session_state["logged_in"]:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif !important; }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a1628 0%, #0f2044 50%, #0a1628 100%) !important;
    }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding: 80px 0 0 0 !important; max-width: 100% !important; }
    .stTextInput > label {
        color: rgba(255,255,255,0.55) !important;
        font-size: 0.8em !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 14px 16px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #4a90d9 !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1d4ed8, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        height: 52px !important;
        letter-spacing: 3px !important;
        font-size: 0.9em !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown("""
        <div style="text-align:center; margin-bottom:32px;">
            <div style="color:rgba(255,255,255,0.35);font-size:0.72em;letter-spacing:5px;margin-bottom:12px;">EUGENE GROUP</div>
            <div style="color:white;font-size:2em;font-weight:900;line-height:1.3;">건재사업본부<br>손익 대시보드</div>
            <div style="width:36px;height:2px;background:#1d4ed8;margin:18px auto;"></div>
            <div style="color:rgba(255,255,255,0.3);font-size:0.78em;letter-spacing:2px;">PROFIT & LOSS DASHBOARD</div>
        </div>
        <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:36px 32px 28px;">
        """, unsafe_allow_html=True)

        username = st.text_input("ID", placeholder="아이디를 입력하세요")
        password = st.text_input("PASSWORD", type="password", placeholder="패스워드를 입력하세요")

        if st.button("L O G I N", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("아이디 또는 패스워드가 올바르지 않습니다.")

        st.markdown("""
        </div>
        <div style="text-align:center;color:rgba(255,255,255,0.18);font-size:0.72em;margin-top:24px;">
            © 2026 Eugene Group · Confidential
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════
# 대시보드 CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; box-sizing: border-box; }

[data-testid="stAppViewContainer"] { background: #f0f2f5 !important; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── 네비게이션 버튼 스타일 ── */
div[data-testid="stHorizontalBlock"].nav-row button {
    background: none !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    color: #374151 !important;
    font-weight: 600 !important;
    font-size: 0.93em !important;
    height: 64px !important;
    border-radius: 0 !important;
    padding: 0 20px !important;
    width: 100% !important;
    transition: all 0.2s !important;
    letter-spacing: 0 !important;
}
div[data-testid="stHorizontalBlock"].nav-row button:hover {
    color: #1d4ed8 !important;
    border-bottom-color: #1d4ed8 !important;
    background: none !important;
}

/* ── 서브메뉴 버튼 ── */
div[data-testid="stHorizontalBlock"].subnav-row button {
    background: none !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: #6b7280 !important;
    font-weight: 500 !important;
    font-size: 0.87em !important;
    height: 44px !important;
    border-radius: 0 !important;
    padding: 0 16px !important;
    width: 100% !important;
    letter-spacing: 0 !important;
}
div[data-testid="stHorizontalBlock"].subnav-row button:hover {
    color: #1d4ed8 !important;
    background: #eff6ff !important;
}

/* ── 로그아웃 버튼 ── */
.logout-btn button {
    background: none !important;
    border: 1px solid #d1d5db !important;
    color: #6b7280 !important;
    border-radius: 4px !important;
    font-size: 0.82em !important;
    font-weight: 500 !important;
    height: 34px !important;
    padding: 0 14px !important;
    letter-spacing: 0 !important;
}
.logout-btn button:hover { border-color: #1d4ed8 !important; color: #1d4ed8 !important; }

/* ── 기타 selectbox ── */
[data-testid="stSelectbox"] label { display: none !important; }

/* ── 페이지 헤더 ── */
.page-hero {
    background: linear-gradient(135deg, #0f2044 0%, #1a3a6c 100%);
    padding: 32px 40px;
    color: white;
    position: relative;
    overflow: hidden;
}
.page-hero::after {
    content: '';
    position: absolute;
    right: 60px; top: -50px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
}
.page-hero-sub  { color: rgba(255,255,255,0.4); font-size:0.78em; letter-spacing:2px; margin-bottom:6px; }
.page-hero-title{ font-size:1.8em; font-weight:900; line-height:1.2; }
.page-hero-badge{
    display:inline-block; background:rgba(255,255,255,0.12);
    color:rgba(255,255,255,0.85); padding:3px 13px; border-radius:20px;
    font-size:0.78em; margin-top:10px; border:1px solid rgba(255,255,255,0.2);
}

/* ── 컨텐츠 영역 ── */
.content-wrap { padding: 24px 32px; max-width: 1500px; margin: 0 auto; }

/* ── KPI 카드 ── */
.kpi-card {
    background: white; border-radius: 10px; padding: 20px 22px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06); border-top: 4px solid #1d4ed8;
    height: 100%;
}
.kpi-card.green  { border-top-color: #16a34a; }
.kpi-card.red    { border-top-color: #dc2626; }
.kpi-card.amber  { border-top-color: #d97706; }
.kpi-card.purple { border-top-color: #7c3aed; }
.kpi-label { color:#9ca3af; font-size:0.77em; font-weight:600; letter-spacing:0.8px; text-transform:uppercase; margin-bottom:8px; }
.kpi-value { color:#111827; font-size:1.8em; font-weight:900; line-height:1; margin-bottom:6px; }
.kpi-unit  { font-size:0.46em; color:#9ca3af; font-weight:400; vertical-align:middle; }
.kpi-delta { font-size:0.82em; font-weight:600; }
.kpi-delta.pos { color:#16a34a; }
.kpi-delta.neg { color:#dc2626; }
.kpi-delta-sub { color:#d1d5db; font-size:0.85em; font-weight:400; margin-left:3px; }

/* ── 카드 ── */
.card { background:white; border-radius:10px; padding:22px; box-shadow:0 1px 6px rgba(0,0,0,0.06); margin-bottom:18px; }
.card-title {
    font-size:0.92em; font-weight:700; color:#1f2937;
    margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid #f3f4f6;
    display:flex; align-items:center; gap:8px;
}
.card-title::before {
    content:''; display:inline-block; width:4px; height:15px;
    background:#1d4ed8; border-radius:2px; flex-shrink:0;
}

/* ── 테이블 ── */
.tbl-wrap { overflow-x:auto; }
table.pl-table { width:100%; border-collapse:collapse; font-size:0.86em; }
table.pl-table thead tr th {
    background:#0f2044; color:white; padding:10px 13px;
    text-align:center; font-weight:600; white-space:nowrap;
}
table.pl-table thead tr:nth-child(2) th { background:#1a3a6c; font-size:0.9em; }
table.pl-table tbody td {
    padding:9px 13px; text-align:right; border-bottom:1px solid #f3f4f6;
    color:#374151; white-space:nowrap;
}
table.pl-table tbody td:first-child { text-align:center; font-weight:700; color:#1f2937; }
table.pl-table tbody tr:hover td { background:#fafbff; }
table.pl-table tbody tr.total td { background:#eff6ff; font-weight:900; color:#1d4ed8; }
.pos { color:#16a34a !important; font-weight:700; }
.neg { color:#dc2626 !important; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 네비게이션 구조
# ══════════════════════════════════════════════════════════════
NAV_STRUCTURE = {
    "건재손익": ["건재손익_총괄", "건재손익_공장별"],
    "레미콘":   ["레미콘_공헌이익", "레미콘_공장별"],
    "건자재":   ["건자재_손익"],
    "골재":     ["골재_손익"],
    "임대":     ["임대_손익"],
}
PAGE_LABELS = {
    "건재손익_총괄":   "손익 총괄",
    "건재손익_공장별": "공장별 손익",
    "레미콘_공헌이익": "공헌이익 분석",
    "레미콘_공장별":   "공장별 손익",
    "건자재_손익":    "건자재 손익",
    "골재_손익":      "골재 손익",
    "임대_손익":      "임대 손익",
}

current_page = st.session_state["page"]

def get_parent(page):
    for menu, pages in NAV_STRUCTURE.items():
        if page in pages:
            return menu
    return "건재손익"

active_menu = get_parent(current_page)

# ══════════════════════════════════════════════════════════════
# 상단 헤더 (로고 + 유저)
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="background:white;border-bottom:1px solid #e8eaed;padding:0 32px;
            display:flex;align-items:center;justify-content:space-between;height:64px;
            position:sticky;top:0;z-index:999;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
    <div style="display:flex;align-items:center;gap:10px;">
        <div>
            <div style="font-size:1.1em;font-weight:900;color:#0f2044;letter-spacing:-0.5px;line-height:1;">EUGENE</div>
            <div style="font-size:0.6em;color:#9ca3af;font-weight:400;letter-spacing:0.5px;">건재사업본부</div>
        </div>
    </div>
    <div style="color:#6b7280;font-size:0.85em;font-weight:500;">👤 {st.session_state['username']}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 메인 네비게이션 (Streamlit 버튼)
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="nav-row" style="background:white;border-bottom:2px solid #e8eaed;padding:0 20px;">', unsafe_allow_html=True)
nav_cols = st.columns([1,1,1,1,1,3])  # 메뉴 5개 + 여백
menus = list(NAV_STRUCTURE.keys())
for i, menu in enumerate(menus):
    with nav_cols[i]:
        label = f"**{menu}**" if menu == active_menu else menu
        if st.button(label, key=f"menu_{menu}", use_container_width=True):
            st.session_state["page"] = NAV_STRUCTURE[menu][0]
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 서브 네비게이션
sub_pages = NAV_STRUCTURE[active_menu]
if len(sub_pages) > 1:
    st.markdown('<div class="subnav-row" style="background:#f8fafc;border-bottom:1px solid #e8eaed;padding:0 32px;">', unsafe_allow_html=True)
    sub_cols = st.columns([1,1,6])
    for i, pg in enumerate(sub_pages):
        with sub_cols[i]:
            label = f"**{PAGE_LABELS[pg]}**" if pg == current_page else PAGE_LABELS[pg]
            if st.button(label, key=f"sub_{pg}", use_container_width=True):
                st.session_state["page"] = pg
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 필터 + 로그아웃
fc0, fc1, fc2, fc3 = st.columns([0.07, 0.1, 0.1, 0.73])
with fc0:
    st.markdown('<div style="padding-top:9px;padding-left:32px;color:#6b7280;font-size:0.82em;font-weight:600;">기간</div>', unsafe_allow_html=True)
years = get_available_years()
selected_year  = fc1.selectbox("연도", years, label_visibility="collapsed")
months         = get_available_months(selected_year)
selected_month = fc2.selectbox("월", months, format_func=lambda x: f"{x}월", label_visibility="collapsed")
with fc3:
    _, lc = st.columns([0.9, 0.1])
    with lc:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("로그아웃", key="logout"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr style="margin:0;border:none;border-top:1px solid #e8eaed;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 데이터 로드
# ══════════════════════════════════════════════════════════════
REMICON_FACTORIES = ['안양','인천','파주','김포','부산','서부산','김해',
                     '정관','양산','창원','대구','울산','아산','전주','군산','원주','제주']

@st.cache_data
def get_data(year, month):
    return load_factory_data(year, month)

df_all = get_data(selected_year, selected_month)
if df_all is None:
    st.error(f"{selected_year}년 {selected_month}월 데이터를 찾을 수 없습니다.")
    st.stop()

df_rc      = df_all[df_all['공장명'].isin(REMICON_FACTORIES)].copy()
df_summary = df_all[df_all['공장명'].isin(['레미콘 계','건자재','골재 계','기타','합계'])].copy()

# ══════════════════════════════════════════════════════════════
# 헬퍼 함수
# ══════════════════════════════════════════════════════════════
def f(val, d=0):
    if val is None or (isinstance(val, float) and pd.isna(val)): return "-"
    return f"{{:,.{d}f}}".format(val)

def kpi(label, value, unit, delta=None, delta_label="계획대비", color=""):
    ds = ""
    if delta is not None and not (isinstance(delta, float) and pd.isna(delta)):
        arrow = "▲" if delta >= 0 else "▼"
        cls   = "pos" if delta >= 0 else "neg"
        ds = f'<div class="kpi-delta {cls}">{arrow} {f(abs(delta))}<span class="kpi-delta-sub"> vs {delta_label}</span></div>'
    return f"""<div class="kpi-card {color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit"> {unit}</span></div>
        {ds}
    </div>"""

C = {"계획":"#93c5fd","실적":"#1d4ed8","전년":"#f87171","pos":"#16a34a","neg":"#dc2626"}

def base_chart(fig, h=370):
    fig.update_layout(
        height=h, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11), gridcolor='#f3f4f6', linecolor='#e5e7eb'),
        yaxis=dict(tickfont=dict(size=11), gridcolor='#f3f4f6'),
        font=dict(family='Noto Sans KR'),
    )
    return fig

def td_d(val, d=0):
    if val is None or (isinstance(val, float) and pd.isna(val)): return '<td>-</td>'
    cls = "pos" if val >= 0 else "neg"
    arr = "▲" if val >= 0 else "▼"
    return f'<td class="{cls}">{arr}&nbsp;{f(abs(val),d)}</td>'

def hero(title, badge=None):
    b = badge or f"{selected_year}년 {selected_month}월"
    st.markdown(f"""
    <div class="page-hero">
        <div class="page-hero-sub">EUGENE GROUP · 건재사업본부</div>
        <div class="page-hero-title">{title}</div>
        <span class="page-hero-badge">{b}</span>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지: 건재손익 총괄
# ══════════════════════════════════════════════════════════════
if current_page == "건재손익_총괄":
    hero("손익 총괄")
    total  = df_summary[df_summary['공장명'] == '합계']
    rc_row = df_summary[df_summary['공장명'] == '레미콘 계']
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    if not total.empty:
        r = total.iloc[0]
        c1.markdown(kpi("매출 실적", f(r['매출_실적']), "백만원", r.get('매출_차이'), "계획"), unsafe_allow_html=True)
        c2.markdown(kpi("영업이익 실적", f(r['영업이익_실적']), "백만원", r.get('영업이익_차이'), "계획",
                        "green" if (r.get('영업이익_실적') or 0)>=0 else "red"), unsafe_allow_html=True)
        yoy_m = r['매출_실적'] - r['매출_전년'] if pd.notna(r.get('매출_전년')) else None
        c3.markdown(kpi("매출 전년실적", f(r.get('매출_전년')), "백만원", yoy_m, "전년"), unsafe_allow_html=True)
        yoy_o = r['영업이익_실적'] - r['영업이익_전년'] if pd.notna(r.get('영업이익_전년')) else None
        c4.markdown(kpi("영업이익 전년실적", f(r.get('영업이익_전년')), "백만원", yoy_o, "전년", "purple"), unsafe_allow_html=True)
    if not rc_row.empty:
        rr = rc_row.iloc[0]
        c5.markdown(kpi("레미콘 물량", f(rr.get('물량_실적'),1), "천㎥", rr.get('물량_차이'), "계획", "amber"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    dn = ['레미콘 계','건자재','골재 계','기타']
    nm = {'레미콘 계':'레미콘','골재 계':'골재'}
    df_d = df_summary[df_summary['공장명'].isin(dn)].copy()
    df_d['공장명'] = df_d['공장명'].map(lambda x: nm.get(x,x))

    cc1,cc2 = st.columns(2)
    with cc1:
        st.markdown('<div class="card"><div class="card-title">사업부문별 매출액 (백만원)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        for lb,col,clr in [("계획","매출_계획",C["계획"]),("실적","매출_실적",C["실적"]),("전년","매출_전년",C["전년"])]:
            fig.add_bar(name=lb, x=df_d['공장명'], y=df_d[col], marker_color=clr,
                        text=df_d[col].apply(lambda x: f(x)), textposition='outside', textfont=dict(size=10))
        base_chart(fig); fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cc2:
        st.markdown('<div class="card"><div class="card-title">사업부문별 영업이익 (백만원)</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        for lb,col,clr in [("계획","영업이익_계획",C["계획"]),("실적","영업이익_실적",C["실적"]),("전년","영업이익_전년",C["전년"])]:
            fig2.add_bar(name=lb, x=df_d['공장명'], y=df_d[col], marker_color=clr)
        base_chart(fig2); fig2.update_layout(barmode='group')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">사업부문별 손익 상세</div><div class="tbl-wrap">', unsafe_allow_html=True)
    rs = df_summary[df_summary['공장명'].isin(dn+['합계'])].copy()
    rs['공장명'] = rs['공장명'].map(lambda x: nm.get(x,x))
    html = """<table class="pl-table"><thead>
    <tr><th rowspan="2">구분</th>
        <th colspan="4">매출액 (백만원)</th>
        <th colspan="4">영업이익 (백만원)</th></tr>
    <tr><th>계획</th><th>실적</th><th>차이</th><th>전년</th>
        <th>계획</th><th>실적</th><th>차이</th><th>전년</th></tr>
    </thead><tbody>"""
    for _, r in rs.iterrows():
        tc = ' class="total"' if r['공장명']=='합계' else ''
        html += f"""<tr{tc}>
            <td>{r['공장명']}</td>
            <td>{f(r.get('매출_계획'))}</td><td>{f(r.get('매출_실적'))}</td>
            {td_d(r.get('매출_차이'))}<td>{f(r.get('매출_전년'))}</td>
            <td>{f(r.get('영업이익_계획'))}</td><td>{f(r.get('영업이익_실적'))}</td>
            {td_d(r.get('영업이익_차이'))}<td>{f(r.get('영업이익_전년'))}</td>
        </tr>"""
    st.markdown(html + "</tbody></table></div></div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지: 건재손익 공장별
# ══════════════════════════════════════════════════════════════
elif current_page == "건재손익_공장별":
    hero("공장별 손익")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    metric = st.selectbox("조회 지표", ['매출','영업이익','물량'],
                           format_func=lambda x: {'매출':'매출액 (백만원)','영업이익':'영업이익 (백만원)','물량':'판매물량 (천㎥)'}[x])
    cc1,cc2 = st.columns([2.2,1])
    with cc1:
        st.markdown('<div class="card"><div class="card-title">공장별 실적 비교</div>', unsafe_allow_html=True)
        fig = go.Figure()
        for lb,col,clr in [("계획",f"{metric}_계획",C["계획"]),("실적",f"{metric}_실적",C["실적"]),("전년",f"{metric}_전년",C["전년"])]:
            fig.add_bar(name=lb, x=df_rc['공장명'], y=df_rc[col], marker_color=clr)
        base_chart(fig, 400); fig.update_layout(barmode='group', xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">영업이익 계획대비</div>', unsafe_allow_html=True)
        df_d2 = df_rc[['공장명','영업이익_차이']].dropna()
        cs = [C['pos'] if v>=0 else C['neg'] for v in df_d2['영업이익_차이']]
        fig2 = go.Figure(go.Bar(x=df_d2['영업이익_차이'], y=df_d2['공장명'], orientation='h', marker_color=cs,
                                text=df_d2['영업이익_차이'].apply(lambda x: f(x)), textposition='outside', textfont=dict(size=10)))
        fig2.add_vline(x=0, line_color='#374151', line_width=1.5)
        base_chart(fig2, 400); fig2.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">공장별 손익 상세</div><div class="tbl-wrap">', unsafe_allow_html=True)
    html = """<table class="pl-table"><thead>
    <tr><th rowspan="2">공장명</th>
    <th colspan="3">물량 (천㎥)</th><th colspan="3">매출 (백만원)</th><th colspan="3">영업이익 (백만원)</th></tr>
    <tr><th>계획</th><th>실적</th><th>차이</th><th>계획</th><th>실적</th><th>차이</th><th>계획</th><th>실적</th><th>차이</th></tr>
    </thead><tbody>"""
    for _, r in df_rc.iterrows():
        html += f"""<tr><td>{r['공장명']}</td>
            <td>{f(r.get('물량_계획'),1)}</td><td>{f(r.get('물량_실적'),1)}</td>{td_d(r.get('물량_차이'),1)}
            <td>{f(r.get('매출_계획'))}</td><td>{f(r.get('매출_실적'))}</td>{td_d(r.get('매출_차이'))}
            <td>{f(r.get('영업이익_계획'))}</td><td>{f(r.get('영업이익_실적'))}</td>{td_d(r.get('영업이익_차이'))}
        </tr>"""
    st.markdown(html + "</tbody></table></div></div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지: 레미콘 공헌이익
# ══════════════════════════════════════════════════════════════
elif current_page == "레미콘_공헌이익":
    hero("레미콘 공헌이익 분석", f"{selected_year}년 {selected_month}월 · 단위: 원/㎥")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    rc_sum = df_all[df_all['공장명'] == '레미콘 계']
    if not rc_sum.empty:
        r = rc_sum.iloc[0]
        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(kpi("판매단가 실적", f(r['판매단가_실적']), "원/㎥",
                        r['판매단가_실적']-r['판매단가_전년'] if pd.notna(r.get('판매단가_전년')) else None, "전년"), unsafe_allow_html=True)
        c2.markdown(kpi("변동비 실적", f(r['변동비_실적']), "원/㎥",
                        r['변동비_실적']-r['변동비_전년'] if pd.notna(r.get('변동비_전년')) else None, "전년", "red"), unsafe_allow_html=True)
        c3.markdown(kpi("공헌이익 실적", f(r['공헌이익_실적']), "원/㎥",
                        r['공헌이익_실적']-r['공헌이익_전년'] if pd.notna(r.get('공헌이익_전년')) else None, "전년",
                        "green" if (r.get('공헌이익_실적') or 0)>=0 else "red"), unsafe_allow_html=True)
        c4.markdown(kpi("공헌이익 계획대비", f(r.get('공헌이익_계획')), "원/㎥",
                        r['공헌이익_실적']-r['공헌이익_계획'] if pd.notna(r.get('공헌이익_계획')) else None, "계획", "purple"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cc1,cc2 = st.columns(2)
    with cc1:
        st.markdown('<div class="card"><div class="card-title">공장별 판매단가 vs 변동비 (원/㎥)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_bar(name='판매단가', x=df_rc['공장명'], y=df_rc['판매단가_실적'], marker_color=C['실적'])
        fig.add_bar(name='변동비',   x=df_rc['공장명'], y=df_rc['변동비_실적'],   marker_color=C['전년'])
        base_chart(fig, 360); fig.update_layout(barmode='group', xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">공장별 공헌이익 (원/㎥)</div>', unsafe_allow_html=True)
        cs = [C['pos'] if (v or 0)>=0 else C['neg'] for v in df_rc['공헌이익_실적'].fillna(0)]
        fig2 = go.Figure(go.Bar(x=df_rc['공장명'], y=df_rc['공헌이익_실적'], marker_color=cs,
                                text=df_rc['공헌이익_실적'].apply(lambda x: f(x)), textposition='outside', textfont=dict(size=10)))
        fig2.add_hline(y=0, line_dash='dash', line_color='#374151', line_width=1.5)
        base_chart(fig2, 360); fig2.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">전년 대비 공헌이익 변화 분석</div>', unsafe_allow_html=True)
    df_r2 = df_rc.copy()
    df_r2['CI_YoY'] = df_r2['공헌이익_실적'] - df_r2['공헌이익_전년']
    df_r2['SP_YoY'] = df_r2['판매단가_실적'] - df_r2['판매단가_전년']
    df_r2['VC_YoY'] = df_r2['변동비_실적']   - df_r2['변동비_전년']
    df_yoy = df_r2.dropna(subset=['CI_YoY'])
    fig3 = go.Figure()
    fig3.add_bar(name='판매단가 변화', x=df_yoy['공장명'], y=df_yoy['SP_YoY'], marker_color='#60a5fa')
    fig3.add_bar(name='변동비 변화',   x=df_yoy['공장명'], y=df_yoy['VC_YoY'], marker_color='#f87171')
    fig3.add_scatter(name='공헌이익 변화', x=df_yoy['공장명'], y=df_yoy['CI_YoY'],
                     mode='lines+markers', line=dict(color='#7c3aed', width=2.5), marker=dict(size=8))
    fig3.add_hline(y=0, line_dash='dash', line_color='#374151', line_width=1)
    base_chart(fig3, 320); fig3.update_layout(barmode='relative', xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">공장별 공헌이익 상세</div><div class="tbl-wrap">', unsafe_allow_html=True)
    html = """<table class="pl-table"><thead>
    <tr><th rowspan="2">공장명</th>
    <th colspan="3">판매단가 (원/㎥)</th><th colspan="3">변동비 (원/㎥)</th><th colspan="3">공헌이익 (원/㎥)</th></tr>
    <tr><th>계획</th><th>실적</th><th>전년</th><th>계획</th><th>실적</th><th>전년</th><th>계획</th><th>실적</th><th>전년</th></tr>
    </thead><tbody>"""
    for _, r in df_rc.iterrows():
        cc = "pos" if (r.get('공헌이익_실적') or 0)>=0 else "neg"
        html += f"""<tr><td>{r['공장명']}</td>
            <td>{f(r.get('판매단가_계획'))}</td><td>{f(r.get('판매단가_실적'))}</td><td>{f(r.get('판매단가_전년'))}</td>
            <td>{f(r.get('변동비_계획'))}</td><td>{f(r.get('변동비_실적'))}</td><td>{f(r.get('변동비_전년'))}</td>
            <td>{f(r.get('공헌이익_계획'))}</td><td class="{cc}">{f(r.get('공헌이익_실적'))}</td><td>{f(r.get('공헌이익_전년'))}</td>
        </tr>"""
    st.markdown(html + "</tbody></table></div></div></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지: 레미콘 공장별
# ══════════════════════════════════════════════════════════════
elif current_page == "레미콘_공장별":
    hero("레미콘 공장별 손익")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    rc_sum = df_all[df_all['공장명'] == '레미콘 계']
    if not rc_sum.empty:
        r = rc_sum.iloc[0]
        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(kpi("매출 실적", f(r['매출_실적']), "백만원", r.get('매출_차이'), "계획"), unsafe_allow_html=True)
        c2.markdown(kpi("영업이익 실적", f(r['영업이익_실적']), "백만원", r.get('영업이익_차이'), "계획",
                        "green" if (r.get('영업이익_실적') or 0)>=0 else "red"), unsafe_allow_html=True)
        c3.markdown(kpi("판매물량 실적", f(r.get('물량_실적'),1), "천㎥", r.get('물량_차이'), "계획", "purple"), unsafe_allow_html=True)
        c4.markdown(kpi("운영 공장", "17", "개", None, "", "amber"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cc1,cc2 = st.columns([2.2,1])
    with cc1:
        st.markdown('<div class="card"><div class="card-title">공장별 영업이익 (백만원)</div>', unsafe_allow_html=True)
        fig = go.Figure()
        for lb,col,clr in [("계획","영업이익_계획",C["계획"]),("실적","영업이익_실적",C["실적"]),("전년","영업이익_전년",C["전년"])]:
            fig.add_bar(name=lb, x=df_rc['공장명'], y=df_rc[col], marker_color=clr)
        base_chart(fig, 380); fig.update_layout(barmode='group', xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">영업이익 순위</div>', unsafe_allow_html=True)
        df_rank = df_rc[['공장명','영업이익_실적']].dropna().sort_values('영업이익_실적', ascending=True)
        cs = [C['pos'] if v>=0 else C['neg'] for v in df_rank['영업이익_실적']]
        fig2 = go.Figure(go.Bar(x=df_rank['영업이익_실적'], y=df_rank['공장명'], orientation='h', marker_color=cs,
                                text=df_rank['영업이익_실적'].apply(lambda x: f(x)), textposition='outside', textfont=dict(size=10)))
        fig2.add_vline(x=0, line_color='#374151', line_width=1.5)
        base_chart(fig2, 380)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 준비중 페이지
# ══════════════════════════════════════════════════════════════
elif current_page in ["건자재_손익","골재_손익","임대_손익"]:
    nm = {"건자재_손익":"건자재","골재_손익":"골재","임대_손익":"임대"}[current_page]
    hero(f"{nm} 손익")
    st.markdown(f"""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:380px;">
        <div style="font-size:3.5em;margin-bottom:20px;opacity:0.35;">🚧</div>
        <div style="font-size:1.3em;font-weight:700;color:#374151;margin-bottom:8px;">{nm} 손익 페이지</div>
        <div style="color:#9ca3af;">준비 중입니다. 곧 업데이트될 예정입니다.</div>
    </div>
    """, unsafe_allow_html=True)
