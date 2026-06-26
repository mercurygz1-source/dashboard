import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import get_available_years, get_available_months, load_factory_data

st.set_page_config(page_title="건재사업본부 손익", page_icon="📊", layout="wide")

# ══════════════════════════════════════════════════════════════
# 로그인
# ══════════════════════════════════════════════════════════════
USERS = st.secrets.get("users", {"tongyang": "6150"})

def login():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif !important; }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a1628 0%, #0f2044 50%, #0a1628 100%) !important;
        min-height: 100vh;
    }
    [data-testid="stHeader"] { display:none; }
    [data-testid="stSidebar"] { display:none; }
    .block-container { padding: 60px 0 0 0 !important; max-width: 100% !important; }
    .login-title {
        text-align: center;
        margin-bottom: 36px;
        padding: 0 20px;
    }
    .stTextInput > label {
        color: rgba(255,255,255,0.55) !important;
        font-size: 0.8em !important;
        font-weight: 600 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase;
    }
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        color: white !important;
        border-radius: 6px !important;
        padding: 14px 16px !important;
        font-size: 0.95em !important;
    }
    .stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.25) !important; }
    .stTextInput > div > div > input:focus {
        border-color: #4a90d9 !important;
        box-shadow: 0 0 0 2px rgba(74,144,217,0.25) !important;
    }
    .stButton > button {
        background: linear-gradient(90deg,#1d4ed8,#2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 0.9em !important;
        height: 52px !important;
        letter-spacing: 3px !important;
        margin-top: 8px !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }
    .login-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 36px 32px 28px;
        backdrop-filter: blur(10px);
    }
    .login-footer {
        text-align: center;
        color: rgba(255,255,255,0.18);
        font-size: 0.72em;
        margin-top: 24px;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 컬럼으로 중앙 정렬
    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        st.markdown("""
        <div class="login-title">
          <div style="color:rgba(255,255,255,0.35);font-size:0.72em;letter-spacing:5px;margin-bottom:12px;font-weight:300;">EUGENE GROUP</div>
          <div style="color:white;font-size:2em;font-weight:900;line-height:1.3;">건재사업본부<br>손익 대시보드</div>
          <div style="width:36px;height:2px;background:#1d4ed8;margin:18px auto 10px;"></div>
          <div style="color:rgba(255,255,255,0.3);font-size:0.78em;letter-spacing:2px;">PROFIT & LOSS DASHBOARD</div>
        </div>
        <div class="login-box">
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
        <div class="login-footer">© 2026 Eugene Group · Confidential</div>
        """, unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# ══════════════════════════════════════════════════════════════
# 전체 CSS (로그인 후)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; box-sizing: border-box; }

[data-testid="stAppViewContainer"] { background: #f0f2f5 !important; padding-top: 70px; }
[data-testid="stHeader"] { display: none; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ─── 상단 네비게이션 ─── */
.top-nav-wrapper {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 70px;
    background: white;
    border-bottom: 1px solid #e8eaed;
    z-index: 9999;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.top-nav-inner {
    max-width: 1500px;
    margin: 0 auto;
    height: 70px;
    display: flex;
    align-items: center;
    padding: 0 32px;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    margin-right: 60px;
    flex-shrink: 0;
    cursor: pointer;
}
.nav-logo-text {
    font-size: 1.15em;
    font-weight: 900;
    color: #0f2044;
    letter-spacing: -0.5px;
    line-height: 1;
}
.nav-logo-sub {
    font-size: 0.62em;
    color: #6b7280;
    font-weight: 400;
    letter-spacing: 0.5px;
    margin-top: 3px;
}
.nav-menu {
    display: flex;
    align-items: center;
    height: 70px;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 0;
}
.nav-item {
    position: relative;
    height: 70px;
    display: flex;
    align-items: center;
}
.nav-link {
    display: flex;
    align-items: center;
    height: 70px;
    padding: 0 26px;
    color: #374151;
    text-decoration: none;
    font-size: 0.93em;
    font-weight: 600;
    border-bottom: 3px solid transparent;
    transition: color 0.2s, border-color 0.2s;
    white-space: nowrap;
    cursor: pointer;
}
.nav-link:hover { color: #1d4ed8; border-bottom-color: #1d4ed8; }
.nav-link.active { color: #1d4ed8; border-bottom-color: #1d4ed8; }

/* 드롭다운 */
.dropdown {
    position: absolute;
    top: 70px;
    left: 0;
    background: white;
    min-width: 180px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    border-top: 3px solid #1d4ed8;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-8px);
    transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
    z-index: 10000;
}
.nav-item:hover .dropdown {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}
.dropdown-link {
    display: block;
    padding: 13px 22px;
    color: #374151;
    text-decoration: none;
    font-size: 0.88em;
    font-weight: 500;
    border-bottom: 1px solid #f3f4f6;
    transition: background 0.15s, color 0.15s, padding-left 0.15s;
}
.dropdown-link:last-child { border-bottom: none; }
.dropdown-link:hover { background: #eff6ff; color: #1d4ed8; padding-left: 28px; }
.dropdown-link.active { background: #eff6ff; color: #1d4ed8; font-weight: 700; border-left: 3px solid #1d4ed8; }

.nav-right {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-left: auto;
    flex-shrink: 0;
}
.nav-user {
    color: #6b7280;
    font-size: 0.85em;
    font-weight: 500;
}

/* 스트림릿 버튼 오버라이드 */
.stButton > button {
    background: none !important;
    border: 1px solid #d1d5db !important;
    color: #6b7280 !important;
    padding: 4px 14px !important;
    border-radius: 4px !important;
    font-size: 0.82em !important;
    font-weight: 500 !important;
    height: auto !important;
    letter-spacing: 0 !important;
}
.stButton > button:hover { border-color: #1d4ed8 !important; color: #1d4ed8 !important; }

/* selectbox 숨기기용 */
[data-testid="stSelectbox"] label { display: none !important; }
[data-testid="stSelectbox"] { margin-top: 0 !important; }

/* ─── 페이지 헤더 ─── */
.page-hero {
    background: linear-gradient(135deg, #0f2044 0%, #1a3a6c 100%);
    padding: 36px 40px;
    color: white;
    position: relative;
    overflow: hidden;
}
.page-hero::before {
    content: '';
    position: absolute;
    right: 80px; top: -60px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
}
.page-hero::after {
    content: '';
    position: absolute;
    right: -20px; bottom: -80px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,255,255,0.02);
}
.page-hero-sub { color: rgba(255,255,255,0.45); font-size:0.78em; letter-spacing:2px; margin-bottom:8px; font-weight:300; }
.page-hero-title { font-size: 1.85em; font-weight: 900; line-height: 1.2; }
.page-hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.12);
    color: rgba(255,255,255,0.85);
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78em;
    margin-top: 12px;
    border: 1px solid rgba(255,255,255,0.2);
    letter-spacing: 0.5px;
}

/* ─── 필터 바 ─── */
.filter-bar {
    background: white;
    border-bottom: 1px solid #e8eaed;
    padding: 8px 32px;
    display: flex;
    align-items: center;
    gap: 0;
}

/* ─── 컨텐츠 ─── */
.content-wrap { padding: 28px 32px; max-width: 1500px; margin: 0 auto; }

/* ─── KPI 카드 ─── */
.kpi-card {
    background: white;
    border-radius: 10px;
    padding: 22px 24px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    border-top: 4px solid #1d4ed8;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.kpi-card.green { border-top-color: #16a34a; }
.kpi-card.red   { border-top-color: #dc2626; }
.kpi-card.amber { border-top-color: #d97706; }
.kpi-card.purple{ border-top-color: #7c3aed; }

.kpi-label { color: #9ca3af; font-size: 0.77em; font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 10px; }
.kpi-value { color: #111827; font-size: 1.85em; font-weight: 900; line-height: 1; margin-bottom: 8px; }
.kpi-unit  { font-size: 0.48em; color: #9ca3af; font-weight: 400; vertical-align: middle; }
.kpi-delta { font-size: 0.82em; font-weight: 600; }
.kpi-delta.pos { color: #16a34a; }
.kpi-delta.neg { color: #dc2626; }
.kpi-delta-sub { color: #d1d5db; font-size: 0.85em; font-weight: 400; margin-left: 3px; }

/* ─── 카드 ─── */
.card {
    background: white;
    border-radius: 10px;
    padding: 24px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}
.card-title {
    font-size: 0.93em;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f3f4f6;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-title::before {
    content: '';
    display: inline-block;
    width: 4px; height: 16px;
    background: #1d4ed8;
    border-radius: 2px;
    flex-shrink: 0;
}

/* ─── 테이블 ─── */
.tbl-wrap { overflow-x: auto; }
table.pl-table { width: 100%; border-collapse: collapse; font-size: 0.86em; }
table.pl-table thead tr th {
    background: #0f2044;
    color: white;
    padding: 11px 14px;
    text-align: center;
    font-weight: 600;
    letter-spacing: 0.3px;
    white-space: nowrap;
}
table.pl-table thead tr:nth-child(2) th { background: #1a3a6c; font-weight: 500; font-size: 0.92em; }
table.pl-table tbody td {
    padding: 10px 14px;
    text-align: right;
    border-bottom: 1px solid #f3f4f6;
    color: #374151;
    white-space: nowrap;
}
table.pl-table tbody td:first-child { text-align: center; font-weight: 700; color: #1f2937; }
table.pl-table tbody tr:hover td { background: #fafbff; }
table.pl-table tbody tr.total td { background: #eff6ff; font-weight: 900; color: #1d4ed8; }
.pos { color: #16a34a !important; font-weight: 700; }
.neg { color: #dc2626 !important; font-weight: 700; }

/* 준비중 */
.coming-soon {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    min-height: 400px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 페이지 상태 (쿼리 파라미터)
# ══════════════════════════════════════════════════════════════
params = st.query_params
current_page = params.get("page", "건재손익_총괄")

NAV_STRUCTURE = {
    "건재손익": ["건재손익_총괄", "건재손익_공장별"],
    "레미콘":   ["레미콘_공헌이익", "레미콘_공장별"],
    "건자재":   ["건자재_손익"],
    "골재":     ["골재_손익"],
    "임대":     ["임대_손익"],
}
PAGE_LABELS = {
    "건재손익_총괄":  "손익 총괄",
    "건재손익_공장별":"공장별 손익",
    "레미콘_공헌이익":"공헌이익 분석",
    "레미콘_공장별":  "공장별 손익",
    "건자재_손익":   "건자재 손익",
    "골재_손익":     "골재 손익",
    "임대_손익":     "임대 손익",
}

def get_parent(page):
    for menu, pages in NAV_STRUCTURE.items():
        if page in pages:
            return menu
    return "건재손익"

active_menu = get_parent(current_page)

# ══════════════════════════════════════════════════════════════
# 네비게이션
# ══════════════════════════════════════════════════════════════
items_html = ""
for menu, pages in NAV_STRUCTURE.items():
    is_active = (menu == active_menu)
    lc = "nav-link active" if is_active else "nav-link"

    if len(pages) > 1:
        dd_items = "".join(
            f'<a class="dropdown-link{"  active" if pg == current_page else ""}" href="?page={pg}">{PAGE_LABELS[pg]}</a>'
            for pg in pages
        )
        dd = f'<div class="dropdown">{dd_items}</div>'
    else:
        dd = ""

    items_html += f'<li class="nav-item"><a class="{lc}" href="?page={pages[0]}">{menu}</a>{dd}</li>'

st.markdown(f"""
<div class="top-nav-wrapper">
  <div class="top-nav-inner">
    <a class="nav-logo" href="?page=건재손익_총괄">
      <div>
        <div class="nav-logo-text">EUGENE</div>
        <div class="nav-logo-sub">건재사업본부</div>
      </div>
    </a>
    <ul class="nav-menu">{items_html}</ul>
    <div class="nav-right">
      <span class="nav-user">👤 {st.session_state['username']}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 필터 + 로그아웃
# ══════════════════════════════════════════════════════════════
fc0, fc1, fc2, fc3 = st.columns([0.06, 0.1, 0.1, 0.74])
with fc0:
    st.markdown('<div style="color:#6b7280;font-size:0.82em;font-weight:600;padding-top:9px;padding-left:32px;">기간</div>', unsafe_allow_html=True)
years = get_available_years()
selected_year = fc1.selectbox("연도", years, label_visibility="collapsed")
months = get_available_months(selected_year)
selected_month = fc2.selectbox("월", months, format_func=lambda x: f"{x}월", label_visibility="collapsed")
with fc3:
    _, btn_col = st.columns([0.88, 0.12])
    with btn_col:
        if st.button("로그아웃"):
            st.session_state["logged_in"] = False
            st.rerun()

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
# 헬퍼
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

def base_chart(fig, title="", h=380):
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color='#1f2937'), x=0),
        height=h, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11), gridcolor='#f3f4f6', linecolor='#e5e7eb'),
        yaxis=dict(tickfont=dict(size=11), gridcolor='#f3f4f6'),
        font=dict(family='Noto Sans KR'),
    )
    return fig

def td_d(val, d=0):
    if val is None or (isinstance(val, float) and pd.isna(val)): return '<td>-</td>'
    cls = "pos" if val>=0 else "neg"
    arr = "▲" if val>=0 else "▼"
    return f'<td class="{cls}">{arr}&nbsp;{f(abs(val),d)}</td>'

def hero(title, badge_text=None):
    badge = badge_text or f"{selected_year}년 {selected_month}월"
    st.markdown(f"""
    <div class="page-hero">
        <div class="page-hero-sub">EUGENE GROUP · 건재사업본부</div>
        <div class="page-hero-title">{title}</div>
        <span class="page-hero-badge">{badge}</span>
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
    st.markdown(html + "</tbody></table></div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
        base_chart(fig, h=400); fig.update_layout(barmode='group', xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cc2:
        st.markdown('<div class="card"><div class="card-title">영업이익 계획대비</div>', unsafe_allow_html=True)
        df_d2 = df_rc[['공장명','영업이익_차이']].dropna()
        cs = [C['pos'] if v>=0 else C['neg'] for v in df_d2['영업이익_차이']]
        fig2 = go.Figure(go.Bar(
            x=df_d2['영업이익_차이'], y=df_d2['공장명'],
            orientation='h', marker_color=cs,
            text=df_d2['영업이익_차이'].apply(lambda x: f(x)),
            textposition='outside', textfont=dict(size=10)
        ))
        fig2.add_vline(x=0, line_color='#374151', line_width=1.5)
        base_chart(fig2, h=400); fig2.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">공장별 손익 상세</div><div class="tbl-wrap">', unsafe_allow_html=True)
    html = """<table class="pl-table"><thead>
    <tr><th rowspan="2">공장명</th>
    <th colspan="3">물량 (천㎥)</th>
    <th colspan="3">매출 (백만원)</th>
    <th colspan="3">영업이익 (백만원)</th></tr>
    <tr><th>계획</th><th>실적</th><th>차이</th>
        <th>계획</th><th>실적</th><th>차이</th>
        <th>계획</th><th>실적</th><th>차이</th></tr>
    </thead><tbody>"""
    for _, r in df_rc.iterrows():
        html += f"""<tr>
            <td>{r['공장명']}</td>
            <td>{f(r.get('물량_계획'),1)}</td><td>{f(r.get('물량_실적'),1)}</td>{td_d(r.get('물량_차이'),1)}
            <td>{f(r.get('매출_계획'))}</td><td>{f(r.get('매출_실적'))}</td>{td_d(r.get('매출_차이'))}
            <td>{f(r.get('영업이익_계획'))}</td><td>{f(r.get('영업이익_실적'))}</td>{td_d(r.get('영업이익_차이'))}
        </tr>"""
    st.markdown(html + "</tbody></table></div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
        base_chart(fig, h=360); fig.update_layout(barmode='group', xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cc2:
        st.markdown('<div class="card"><div class="card-title">공장별 공헌이익 (원/㎥)</div>', unsafe_allow_html=True)
        cs = [C['pos'] if (v or 0)>=0 else C['neg'] for v in df_rc['공헌이익_실적'].fillna(0)]
        fig2 = go.Figure(go.Bar(
            x=df_rc['공장명'], y=df_rc['공헌이익_실적'], marker_color=cs,
            text=df_rc['공헌이익_실적'].apply(lambda x: f(x)),
            textposition='outside', textfont=dict(size=10)
        ))
        fig2.add_hline(y=0, line_dash='dash', line_color='#374151', line_width=1.5)
        base_chart(fig2, h=360); fig2.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">전년 대비 공헌이익 변화 분석</div>', unsafe_allow_html=True)
    df_r2 = df_rc.copy()
    df_r2['CI_YoY'] = df_r2['공헌이익_실적'] - df_r2['공헌이익_전년']
    df_r2['SP_YoY'] = df_r2['판매단가_실적'] - df_r2['판매단가_전년']
    df_r2['VC_YoY'] = df_r2['변동비_실적'] - df_r2['변동비_전년']
    df_yoy = df_r2.dropna(subset=['CI_YoY'])
    fig3 = go.Figure()
    fig3.add_bar(name='판매단가 변화', x=df_yoy['공장명'], y=df_yoy['SP_YoY'], marker_color='#60a5fa')
    fig3.add_bar(name='변동비 변화',   x=df_yoy['공장명'], y=df_yoy['VC_YoY'], marker_color='#f87171')
    fig3.add_scatter(name='공헌이익 변화', x=df_yoy['공장명'], y=df_yoy['CI_YoY'],
                     mode='lines+markers', line=dict(color='#7c3aed', width=2.5), marker=dict(size=8))
    fig3.add_hline(y=0, line_dash='dash', line_color='#374151', line_width=1)
    base_chart(fig3, h=320); fig3.update_layout(barmode='relative', xaxis_tickangle=-30)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">공장별 공헌이익 상세</div><div class="tbl-wrap">', unsafe_allow_html=True)
    html = """<table class="pl-table"><thead>
    <tr><th rowspan="2">공장명</th>
    <th colspan="3">판매단가 (원/㎥)</th>
    <th colspan="3">변동비 (원/㎥)</th>
    <th colspan="3">공헌이익 (원/㎥)</th></tr>
    <tr><th>계획</th><th>실적</th><th>전년</th>
        <th>계획</th><th>실적</th><th>전년</th>
        <th>계획</th><th>실적</th><th>전년</th></tr>
    </thead><tbody>"""
    for _, r in df_rc.iterrows():
        cc = "pos" if (r.get('공헌이익_실적') or 0)>=0 else "neg"
        html += f"""<tr>
            <td>{r['공장명']}</td>
            <td>{f(r.get('판매단가_계획'))}</td><td>{f(r.get('판매단가_실적'))}</td><td>{f(r.get('판매단가_전년'))}</td>
            <td>{f(r.get('변동비_계획'))}</td><td>{f(r.get('변동비_실적'))}</td><td>{f(r.get('변동비_전년'))}</td>
            <td>{f(r.get('공헌이익_계획'))}</td><td class="{cc}">{f(r.get('공헌이익_실적'))}</td><td>{f(r.get('공헌이익_전년'))}</td>
        </tr>"""
    st.markdown(html + "</tbody></table></div></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
        base_chart(fig, h=380); fig.update_layout(barmode='group', xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cc2:
        st.markdown('<div class="card"><div class="card-title">영업이익 순위</div>', unsafe_allow_html=True)
        df_rank = df_rc[['공장명','영업이익_실적']].dropna().sort_values('영업이익_실적', ascending=True)
        cs = [C['pos'] if v>=0 else C['neg'] for v in df_rank['영업이익_실적']]
        fig2 = go.Figure(go.Bar(
            x=df_rank['영업이익_실적'], y=df_rank['공장명'],
            orientation='h', marker_color=cs,
            text=df_rank['영업이익_실적'].apply(lambda x: f(x)),
            textposition='outside', textfont=dict(size=10)
        ))
        fig2.add_vline(x=0, line_color='#374151', line_width=1.5)
        base_chart(fig2, h=380)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 준비중
# ══════════════════════════════════════════════════════════════
elif current_page in ["건자재_손익","골재_손익","임대_손익"]:
    nm = {"건자재_손익":"건자재","골재_손익":"골재","임대_손익":"임대"}[current_page]
    hero(f"{nm} 손익")
    st.markdown(f"""
    <div class="coming-soon">
        <div style="font-size:3.5em;margin-bottom:20px;opacity:0.4;">🚧</div>
        <div style="font-size:1.3em;font-weight:700;color:#374151;margin-bottom:8px;">{nm} 손익 페이지</div>
        <div style="color:#9ca3af;">준비 중입니다. 곧 업데이트될 예정입니다.</div>
    </div>
    """, unsafe_allow_html=True)
