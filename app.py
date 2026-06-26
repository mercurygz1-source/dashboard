import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64, os
from data_loader import get_available_years, get_available_months, load_factory_data

st.set_page_config(page_title="?숈뼇 嫄댁옱?ъ뾽蹂몃? ?먯씡", page_icon="?뱤", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "嫄댁옱?먯씡_珥앷큵"

# 濡쒓렇?꾩썐 泥섎━
if st.query_params.get("logout") == "1":
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()


USERS = st.secrets.get("users", {"tongyang": "6150"})

def get_logo_b64():
    for fname in ["logo.png", "tongyang_logo.png", "logo.jpg"]:
        p = os.path.join(os.path.dirname(__file__), fname)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_html = (f'<img src="data:image/png;base64,{logo_b64}" style="height:44px;object-fit:contain;">'
             if logo_b64 else
             '<span style="font-size:1.4em;font-weight:900;color:#0f2044;">?숈뼇</span>')

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# 濡쒓렇??
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
if not st.session_state["logged_in"]:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    * { font-family:'Noto Sans KR',sans-serif !important; }
    [data-testid="stAppViewContainer"] {
        background:linear-gradient(135deg,#0a1628 0%,#0f2044 50%,#0a1628 100%) !important;
    }
    [data-testid="stHeader"] { display:none; }
    [data-testid="stSidebar"] { display:none; }
    .block-container { padding:80px 0 0 0 !important; max-width:100% !important; }
    .stTextInput > label { color:rgba(255,255,255,0.55) !important; font-size:0.8em !important; font-weight:600 !important; letter-spacing:1.5px !important; }
    .stTextInput > div > div > input {
        background:rgba(255,255,255,0.07) !important; border:1px solid rgba(255,255,255,0.2) !important;
        color:white !important; border-radius:6px !important; padding:14px 16px !important;
    }
    .stTextInput > div > div > input:focus { border-color:#4a90d9 !important; }
    .stButton > button {
        background:linear-gradient(90deg,#1d4ed8,#2563eb) !important; color:white !important;
        border:none !important; border-radius:6px !important; font-weight:700 !important;
        height:52px !important; letter-spacing:3px !important; font-size:0.9em !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        if logo_b64:
            st.markdown(f'<div style="text-align:center;margin-bottom:20px;"><img src="data:image/png;base64,{logo_b64}" style="height:65px;object-fit:contain;filter:brightness(0) invert(1);opacity:0.85;"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center;margin-bottom:30px;">
            <div style="color:rgba(255,255,255,0.35);font-size:0.72em;letter-spacing:5px;margin-bottom:10px;">嫄댁옱?ъ뾽蹂몃?</div>
            <div style="color:white;font-size:1.9em;font-weight:900;line-height:1.3;">?먯씡 ??쒕낫??/div>
            <div style="width:36px;height:2px;background:#1d4ed8;margin:16px auto;"></div>
            <div style="color:rgba(255,255,255,0.3);font-size:0.78em;letter-spacing:2px;">PROFIT &amp; LOSS DASHBOARD</div>
        </div>
        <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:36px 32px 28px;">
        """, unsafe_allow_html=True)
        username = st.text_input("ID", placeholder="?꾩씠?붾? ?낅젰?섏꽭??)
        password = st.text_input("PASSWORD", type="password", placeholder="?⑥뒪?뚮뱶瑜??낅젰?섏꽭??)
        if st.button("L O G I N", use_container_width=True):
            if username in USERS and USERS[username] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("?꾩씠???먮뒗 ?⑥뒪?뚮뱶媛 ?щ컮瑜댁? ?딆뒿?덈떎.")
        st.markdown("""
        </div>
        <div style="text-align:center;color:rgba(255,255,255,0.18);font-size:0.72em;margin-top:22px;">
            짤 2026 Tongyang 쨌 Confidential
        </div>""", unsafe_allow_html=True)
    st.stop()

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# ?ㅻ퉬寃뚯씠??援ъ“
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
NAV_STRUCTURE = {
    "嫄댁옱?먯씡": ["嫄댁옱?먯씡_珥앷큵", "嫄댁옱?먯씡_怨듭옣蹂?],
    "?덈?肄?:   ["?덈?肄?怨듯뿄?댁씡", "?덈?肄?怨듭옣蹂?],
    "嫄댁옄??:   ["嫄댁옄???먯씡"],
    "怨⑥옱":     ["怨⑥옱_?먯씡"],
    "?꾨?":     ["?꾨?_?먯씡"],
}
PAGE_LABELS = {
    "嫄댁옱?먯씡_珥앷큵":   "?먯씡 珥앷큵",
    "嫄댁옱?먯씡_怨듭옣蹂?: "怨듭옣蹂??먯씡",
    "?덈?肄?怨듯뿄?댁씡": "怨듯뿄?댁씡 遺꾩꽍",
    "?덈?肄?怨듭옣蹂?:   "怨듭옣蹂??먯씡",
    "嫄댁옄???먯씡":    "嫄댁옄???먯씡",
    "怨⑥옱_?먯씡":      "怨⑥옱 ?먯씡",
    "?꾨?_?먯씡":      "?꾨? ?먯씡",
}
all_pages_flat = [pg for pages in NAV_STRUCTURE.values() for pg in pages]
current_page = st.session_state["page"]

def get_parent(page):
    for menu, pages in NAV_STRUCTURE.items():
        if page in pages:
            return menu
    return "嫄댁옱?먯씡"

active_menu = get_parent(current_page)

# ?④꺼吏??ㅻ퉬 踰꾪듉 (JS?먯꽌 title ?띿꽦?쇰줈 ?대┃)
_nc = st.columns(len(all_pages_flat))
for i, pg in enumerate(all_pages_flat):
    with _nc[i]:
        if st.button("쨌", key=f"_nav_{pg}", help=f"goto:{pg}"):
            st.session_state["page"] = pg
            st.rerun()

# ?? 濡쒓렇?꾩썐 踰꾪듉: ?④릿 而⑦뀒?대꼫 諛붽묑, CSS濡?nav ?곗륫??怨좎젙 ??
if st.button("濡쒓렇?꾩썐", key="logout"):
    st.session_state.clear()
    st.rerun()

# ?쒕∼?ㅼ슫 HTML ?앹꽦
def make_dd(pages):
    items = "".join(
        f'<div class="dd-item{"  active" if pg == current_page else ""}" onclick="navTo(\'{pg}\')">{PAGE_LABELS[pg]}</div>'
        for pg in pages
    )
    return f'<div class="dropdown">{items}</div>'

menu_html = ""
for menu, pages in NAV_STRUCTURE.items():
    ac = " active" if menu == active_menu else ""
    dd = make_dd(pages) if len(pages) > 1 else ""
    menu_html += f'<li class="nav-item"><a class="nav-link{ac}" onclick="navTo(\'{pages[0]}\')">{menu}</a>{dd}</li>'

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
* {{ font-family:'Noto Sans KR',sans-serif !important; box-sizing:border-box; }}
[data-testid="stAppViewContainer"] {{ background:#f0f2f5 !important; padding-top:70px !important; }}
[data-testid="stHeader"] {{ display:none; }}
[data-testid="stSidebar"] {{ display:none; }}
.block-container {{ padding:0 !important; max-width:100% !important; }}

/* ?④꺼吏??ㅻ퉬 踰꾪듉 ??*/
button[title^="goto:"] {{
    position:absolute !important; opacity:0 !important;
    width:1px !important; height:1px !important;
    min-height:0 !important; padding:0 !important; border:none !important;
    overflow:hidden !important; pointer-events:none !important;
}}
.block-container > div:first-child {{
    height:0 !important; overflow:hidden !important;
    padding:0 !important; margin:0 !important;
}}
/* 濡쒓렇?꾩썐 踰꾪듉: nav ?곗륫 怨좎젙 */
.block-container > div:nth-child(2) {{
    position:fixed !important; top:18px !important; right:32px !important;
    z-index:10001 !important; width:auto !important;
    background:transparent !important; padding:0 !important; margin:0 !important;
}}
.block-container > div:nth-child(2) > div {{
    background:transparent !important;
}}
.block-container > div:nth-child(2) button {{
    background:none !important; border:1px solid #d1d5db !important;
    color:#6b7280 !important; border-radius:4px !important;
    font-size:0.85em !important; font-weight:500 !important;
    height:34px !important; padding:0 16px !important; cursor:pointer !important;
    min-height:0 !important;
}}
.block-container > div:nth-child(2) button:hover {{
    border-color:#1d4ed8 !important; color:#1d4ed8 !important;
}}

/* ?곷떒 ?ㅻ퉬 */
.top-nav {{
    position:fixed; top:0; left:0; right:0; height:70px;
    background:white; border-bottom:1px solid #e2e6ea;
    box-shadow:0 2px 10px rgba(0,0,0,0.06); z-index:9999;
    display:flex; align-items:center; padding:0 32px;
}}
.nav-logo {{ flex-shrink:0; cursor:pointer; line-height:1; }}
.nav-menu {{ display:flex; list-style:none; margin:0; padding:0; height:70px; align-items:center; flex:1; justify-content:center; gap:0; }}
.nav-item {{ position:relative; height:70px; display:flex; align-items:center; }}
.nav-link {{
    display:flex; align-items:center; height:70px; padding:0 36px;
    color:#333; font-size:1.15em; font-weight:600;
    cursor:pointer; white-space:nowrap; text-decoration:none !important;
    transition:color 0.18s; user-select:none; border:none !important;
    outline:none; background:none;
}}
.nav-link:hover {{ color:#1d4ed8; text-decoration:none !important; }}
.nav-link.active {{ color:#1d4ed8; font-weight:700; text-decoration:none !important; }}

/* ?쒕∼?ㅼ슫 */
.dropdown {{
    position:absolute; top:70px; left:0; background:white; min-width:168px;
    border-top:3px solid #1d4ed8;
    box-shadow:0 8px 28px rgba(0,0,0,0.12);
    opacity:0; visibility:hidden; transform:translateY(-6px);
    transition:opacity 0.18s,transform 0.18s,visibility 0.18s; z-index:10000;
}}
.nav-item:hover .dropdown {{ opacity:1; visibility:visible; transform:translateY(0); }}
.dd-item {{
    padding:13px 20px; color:#374151; font-size:0.88em; font-weight:500;
    border-bottom:1px solid #f3f4f6; cursor:pointer;
    transition:background 0.13s,color 0.13s,padding-left 0.13s;
}}
.dd-item:last-child {{ border-bottom:none; }}
.dd-item:hover {{ background:#eff6ff; color:#1d4ed8; padding-left:26px; }}
.dd-item.active {{ background:#eff6ff; color:#1d4ed8; font-weight:700; border-left:3px solid #1d4ed8; }}

.nav-right {{ margin-left:auto; display:flex; align-items:center; gap:14px; flex-shrink:0; }}
.nav-user {{ color:#6b7280; font-size:0.85em; font-weight:500; }}

.nav-right {{ margin-left:auto; display:flex; align-items:center; gap:14px; flex-shrink:0; }}
.nav-user {{ color:#6b7280; font-size:0.85em; font-weight:500; }}
.nav-logout-btn {{
    background:none; border:1px solid #d1d5db; color:#6b7280;
    padding:0 16px; border-radius:4px; font-size:0.85em; cursor:pointer;
    font-weight:500; height:34px; transition:all 0.15s;
    font-family:'Noto Sans KR',sans-serif;
}}
.nav-logout-btn:hover {{ border-color:#1d4ed8; color:#1d4ed8; }}

/* 而⑦뀗痢?*/
.content-wrap {{ padding:24px 32px; max-width:1500px; margin:0 auto; }}

/* KPI 移대뱶 */
.kpi-card {{ background:white; border-radius:10px; padding:20px 22px; box-shadow:0 1px 6px rgba(0,0,0,0.06); border-top:4px solid #1d4ed8; height:100%; }}
.kpi-card.green  {{ border-top-color:#16a34a; }}
.kpi-card.red    {{ border-top-color:#dc2626; }}
.kpi-card.amber  {{ border-top-color:#d97706; }}
.kpi-card.purple {{ border-top-color:#7c3aed; }}
.kpi-label {{ color:#9ca3af; font-size:0.77em; font-weight:600; letter-spacing:0.8px; text-transform:uppercase; margin-bottom:8px; }}
.kpi-value {{ color:#111827; font-size:1.8em; font-weight:900; line-height:1; margin-bottom:6px; }}
.kpi-unit  {{ font-size:0.46em; color:#9ca3af; font-weight:400; vertical-align:middle; }}
.kpi-delta {{ font-size:0.82em; font-weight:600; }}
.kpi-delta.pos {{ color:#16a34a; }}
.kpi-delta.neg {{ color:#dc2626; }}
.kpi-delta-sub {{ color:#d1d5db; font-size:0.85em; font-weight:400; margin-left:3px; }}
.card {{ background:white; border-radius:10px; padding:22px; box-shadow:0 1px 6px rgba(0,0,0,0.06); margin-bottom:18px; }}
.card-title {{ font-size:0.92em; font-weight:700; color:#1f2937; margin-bottom:16px; padding-bottom:10px; border-bottom:1px solid #f3f4f6; display:flex; align-items:center; gap:8px; }}
.card-title::before {{ content:''; display:inline-block; width:4px; height:15px; background:#1d4ed8; border-radius:2px; flex-shrink:0; }}
.tbl-wrap {{ overflow-x:auto; }}
table.pl-table {{ width:100%; border-collapse:collapse; font-size:0.86em; }}
table.pl-table thead tr th {{ background:#0f2044; color:white; padding:10px 13px; text-align:center; font-weight:600; white-space:nowrap; }}
table.pl-table thead tr:nth-child(2) th {{ background:#1a3a6c; font-size:0.9em; }}
table.pl-table tbody td {{ padding:9px 13px; text-align:right; border-bottom:1px solid #f3f4f6; color:#374151; white-space:nowrap; }}
table.pl-table tbody td:first-child {{ text-align:center; font-weight:700; color:#1f2937; }}
table.pl-table tbody tr:hover td {{ background:#fafbff; }}
table.pl-table tbody tr.total td {{ background:#eff6ff; font-weight:900; color:#1d4ed8; }}
.pos {{ color:#16a34a !important; font-weight:700; }}
.neg {{ color:#dc2626 !important; font-weight:700; }}
[data-testid="stSelectbox"] label {{ display:none !important; }}
</style>

<div class="top-nav">
    <div class="nav-logo" onclick="navTo('嫄댁옱?먯씡_珥앷큵')">{logo_html}</div>
    <ul class="nav-menu">{menu_html}</ul>
    <div class="nav-right">
        <span class="nav-user">?뫀 {st.session_state.get('username','')}</span>
    </div>
</div>

<script>
function navTo(page) {{
    var doc = (window.parent && window.parent.document) ? window.parent.document : document;
    var btn = doc.querySelector('button[title="goto:' + page + '"]');
    if (btn) {{ btn.click(); return; }}
    var all = doc.querySelectorAll('button');
    for (var i=0;i<all.length;i++) {{
        if (all[i].getAttribute('title')==='goto:'+page) {{ all[i].click(); return; }}
    }}
}}
</script>
""", unsafe_allow_html=True)

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# ?????꾪꽣 (?곗륫 ?곷떒)
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
years = get_available_years()
if not years:
    st.error("?곗씠???대뜑???곕룄 ?대뜑媛 ?놁뒿?덈떎.")
    st.stop()

_s, _y, _m, _lo = st.columns([0.73, 0.09, 0.09, 0.09])
with _y:
    selected_year = st.selectbox("?곕룄", years, label_visibility="collapsed")
with _m:
    months = get_available_months(selected_year)
    selected_month = st.selectbox("??, months, format_func=lambda x: f"{x}??, label_visibility="collapsed")

st.markdown('<hr style="margin:0;border:none;border-top:1px solid #e8eaed;">', unsafe_allow_html=True)

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# ?곗씠??
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
REMICON_FACTORIES = ['?덉뼇','?몄쿇','?뚯＜','源??,'遺??,'?쒕???,'源??,
                     '?뺢?','?묒궛','李쎌썝','?援?,'?몄궛','?꾩궛','?꾩＜','援곗궛','?먯＜','?쒖＜']

@st.cache_data
def get_data(year, month):
    return load_factory_data(year, month)

df_all = get_data(selected_year, selected_month)
if df_all is None:
    st.error(f"{selected_year}??{selected_month}???곗씠?곕? 李얠쓣 ???놁뒿?덈떎.")
    st.stop()

df_rc      = df_all[df_all['怨듭옣紐?].isin(REMICON_FACTORIES)].copy()
df_summary = df_all[df_all['怨듭옣紐?].isin(['?덈?肄?怨?,'嫄댁옄??,'怨⑥옱 怨?,'湲고?','?⑷퀎'])].copy()

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# ?ы띁
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
def f(val, d=0):
    if val is None or (isinstance(val, float) and pd.isna(val)): return "-"
    return f"{{:,.{d}f}}".format(val)

def kpi(label, value, unit, delta=None, dl="怨꾪쉷?鍮?, color=""):
    ds = ""
    if delta is not None and not (isinstance(delta, float) and pd.isna(delta)):
        arrow = "?? if delta>=0 else "??; cls = "pos" if delta>=0 else "neg"
        ds = f'<div class="kpi-delta {cls}">{arrow} {f(abs(delta))}<span class="kpi-delta-sub"> vs {dl}</span></div>'
    return f'<div class="kpi-card {color}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}<span class="kpi-unit"> {unit}</span></div>{ds}</div>'

C = {"怨꾪쉷":"#93c5fd","?ㅼ쟻":"#1d4ed8","?꾨뀈":"#f87171","pos":"#16a34a","neg":"#dc2626"}

def bc(fig, h=370):
    fig.update_layout(height=h, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10,r=10,t=36,b=10),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,font=dict(size=11)),
        xaxis=dict(tickfont=dict(size=11),gridcolor='#f3f4f6',linecolor='#e5e7eb'),
        yaxis=dict(tickfont=dict(size=11),gridcolor='#f3f4f6'),
        font=dict(family='Noto Sans KR'))
    return fig

def td_d(val, d=0):
    if val is None or (isinstance(val, float) and pd.isna(val)): return '<td>-</td>'
    cls = "pos" if val>=0 else "neg"; arr = "?? if val>=0 else "??
    return f'<td class="{cls}">{arr}&nbsp;{f(abs(val),d)}</td>'

def stitle(title):
    st.markdown(f"""
    <div style="padding:18px 32px 0;display:flex;align-items:center;gap:12px;">
        <div style="width:4px;height:22px;background:#1d4ed8;border-radius:2px;flex-shrink:0;"></div>
        <span style="font-size:1.15em;font-weight:900;color:#1f2937;">{title}</span>
        <span style="background:#eff6ff;color:#1d4ed8;padding:3px 12px;border-radius:20px;font-size:0.78em;font-weight:600;">{selected_year}??{selected_month}??/span>
    </div>""", unsafe_allow_html=True)

# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
# 嫄댁옱?먯씡 珥앷큵
# ?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧?먥븧
if current_page == "嫄댁옱?먯씡_珥앷큵":
    stitle("?먯씡 珥앷큵")
    total = df_summary[df_summary['怨듭옣紐?]=='?⑷퀎']
    rc_row = df_summary[df_summary['怨듭옣紐?]=='?덈?肄?怨?]
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    if not total.empty:
        r = total.iloc[0]
        c1.markdown(kpi("留ㅼ텧 ?ㅼ쟻",f(r['留ㅼ텧_?ㅼ쟻']),"諛깅쭔??,r.get('留ㅼ텧_李⑥씠'),"怨꾪쉷"), unsafe_allow_html=True)
        c2.markdown(kpi("?곸뾽?댁씡 ?ㅼ쟻",f(r['?곸뾽?댁씡_?ㅼ쟻']),"諛깅쭔??,r.get('?곸뾽?댁씡_李⑥씠'),"怨꾪쉷","green" if (r.get('?곸뾽?댁씡_?ㅼ쟻') or 0)>=0 else "red"), unsafe_allow_html=True)
        c3.markdown(kpi("留ㅼ텧 ?꾨뀈?ㅼ쟻",f(r.get('留ㅼ텧_?꾨뀈')),"諛깅쭔??,r['留ㅼ텧_?ㅼ쟻']-r['留ㅼ텧_?꾨뀈'] if pd.notna(r.get('留ㅼ텧_?꾨뀈')) else None,"?꾨뀈"), unsafe_allow_html=True)
        c4.markdown(kpi("?곸뾽?댁씡 ?꾨뀈?ㅼ쟻",f(r.get('?곸뾽?댁씡_?꾨뀈')),"諛깅쭔??,r['?곸뾽?댁씡_?ㅼ쟻']-r['?곸뾽?댁씡_?꾨뀈'] if pd.notna(r.get('?곸뾽?댁씡_?꾨뀈')) else None,"?꾨뀈","purple"), unsafe_allow_html=True)
    if not rc_row.empty:
        rr = rc_row.iloc[0]
        c5.markdown(kpi("?덈?肄?臾쇰웾",f(rr.get('臾쇰웾_?ㅼ쟻'),1),"泥쒌렏",rr.get('臾쇰웾_李⑥씠'),"怨꾪쉷","amber"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    dn=['?덈?肄?怨?,'嫄댁옄??,'怨⑥옱 怨?,'湲고?']; nm={'?덈?肄?怨?:'?덈?肄?,'怨⑥옱 怨?:'怨⑥옱'}
    df_d = df_summary[df_summary['怨듭옣紐?].isin(dn)].copy()
    df_d['怨듭옣紐?] = df_d['怨듭옣紐?].map(lambda x: nm.get(x,x))
    cc1,cc2 = st.columns(2)
    with cc1:
        st.markdown('<div class="card"><div class="card-title">?ъ뾽遺臾몃퀎 留ㅼ텧??(諛깅쭔??</div>', unsafe_allow_html=True)
        fig=go.Figure()
        for lb,col,clr in [("怨꾪쉷","留ㅼ텧_怨꾪쉷",C["怨꾪쉷"]),("?ㅼ쟻","留ㅼ텧_?ㅼ쟻",C["?ㅼ쟻"]),("?꾨뀈","留ㅼ텧_?꾨뀈",C["?꾨뀈"])]:
            fig.add_bar(name=lb,x=df_d['怨듭옣紐?],y=df_d[col],marker_color=clr,text=df_d[col].apply(lambda x:f(x)),textposition='outside',textfont=dict(size=10))
        bc(fig); fig.update_layout(barmode='group'); st.plotly_chart(fig,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">?ъ뾽遺臾몃퀎 ?곸뾽?댁씡 (諛깅쭔??</div>', unsafe_allow_html=True)
        fig2=go.Figure()
        for lb,col,clr in [("怨꾪쉷","?곸뾽?댁씡_怨꾪쉷",C["怨꾪쉷"]),("?ㅼ쟻","?곸뾽?댁씡_?ㅼ쟻",C["?ㅼ쟻"]),("?꾨뀈","?곸뾽?댁씡_?꾨뀈",C["?꾨뀈"])]:
            fig2.add_bar(name=lb,x=df_d['怨듭옣紐?],y=df_d[col],marker_color=clr)
        bc(fig2); fig2.update_layout(barmode='group'); st.plotly_chart(fig2,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">?ъ뾽遺臾몃퀎 ?먯씡 ?곸꽭</div><div class="tbl-wrap">', unsafe_allow_html=True)
    rs=df_summary[df_summary['怨듭옣紐?].isin(dn+['?⑷퀎'])].copy(); rs['怨듭옣紐?]=rs['怨듭옣紐?].map(lambda x:nm.get(x,x))
    html="""<table class="pl-table"><thead><tr><th rowspan="2">援щ텇</th><th colspan="4">留ㅼ텧??諛깅쭔??</th><th colspan="4">?곸뾽?댁씡(諛깅쭔??</th></tr>
    <tr><th>怨꾪쉷</th><th>?ㅼ쟻</th><th>李⑥씠</th><th>?꾨뀈</th><th>怨꾪쉷</th><th>?ㅼ쟻</th><th>李⑥씠</th><th>?꾨뀈</th></tr></thead><tbody>"""
    for _,r in rs.iterrows():
        tc=' class="total"' if r['怨듭옣紐?]=='?⑷퀎' else ''
        html+=f'<tr{tc}><td>{r["怨듭옣紐?]}</td><td>{f(r.get("留ㅼ텧_怨꾪쉷"))}</td><td>{f(r.get("留ㅼ텧_?ㅼ쟻"))}</td>{td_d(r.get("留ㅼ텧_李⑥씠"))}<td>{f(r.get("留ㅼ텧_?꾨뀈"))}</td><td>{f(r.get("?곸뾽?댁씡_怨꾪쉷"))}</td><td>{f(r.get("?곸뾽?댁씡_?ㅼ쟻"))}</td>{td_d(r.get("?곸뾽?댁씡_李⑥씠"))}<td>{f(r.get("?곸뾽?댁씡_?꾨뀈"))}</td></tr>'
    st.markdown(html+"</tbody></table></div></div></div>", unsafe_allow_html=True)

elif current_page == "嫄댁옱?먯씡_怨듭옣蹂?:
    stitle("怨듭옣蹂??먯씡")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    metric=st.selectbox("吏??,['留ㅼ텧','?곸뾽?댁씡','臾쇰웾'],format_func=lambda x:{'留ㅼ텧':'留ㅼ텧??諛깅쭔??','?곸뾽?댁씡':'?곸뾽?댁씡(諛깅쭔??','臾쇰웾':'?먮ℓ臾쇰웾(泥쒌렏)'}[x])
    cc1,cc2=st.columns([2.2,1])
    with cc1:
        st.markdown('<div class="card"><div class="card-title">怨듭옣蹂??ㅼ쟻 鍮꾧탳</div>', unsafe_allow_html=True)
        fig=go.Figure()
        for lb,col,clr in [("怨꾪쉷",f"{metric}_怨꾪쉷",C["怨꾪쉷"]),("?ㅼ쟻",f"{metric}_?ㅼ쟻",C["?ㅼ쟻"]),("?꾨뀈",f"{metric}_?꾨뀈",C["?꾨뀈"])]:
            fig.add_bar(name=lb,x=df_rc['怨듭옣紐?],y=df_rc[col],marker_color=clr)
        bc(fig,400); fig.update_layout(barmode='group',xaxis_tickangle=-30); st.plotly_chart(fig,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">?곸뾽?댁씡 怨꾪쉷?鍮?/div>', unsafe_allow_html=True)
        df_d2=df_rc[['怨듭옣紐?,'?곸뾽?댁씡_李⑥씠']].dropna(); cs=[C['pos'] if v>=0 else C['neg'] for v in df_d2['?곸뾽?댁씡_李⑥씠']]
        fig2=go.Figure(go.Bar(x=df_d2['?곸뾽?댁씡_李⑥씠'],y=df_d2['怨듭옣紐?],orientation='h',marker_color=cs,text=df_d2['?곸뾽?댁씡_李⑥씠'].apply(lambda x:f(x)),textposition='outside',textfont=dict(size=10)))
        fig2.add_vline(x=0,line_color='#374151',line_width=1.5); bc(fig2,400); fig2.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig2,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">怨듭옣蹂??먯씡 ?곸꽭</div><div class="tbl-wrap">', unsafe_allow_html=True)
    html="""<table class="pl-table"><thead><tr><th rowspan="2">怨듭옣紐?/th><th colspan="3">臾쇰웾(泥쒌렏)</th><th colspan="3">留ㅼ텧(諛깅쭔??</th><th colspan="3">?곸뾽?댁씡(諛깅쭔??</th></tr>
    <tr><th>怨꾪쉷</th><th>?ㅼ쟻</th><th>李⑥씠</th><th>怨꾪쉷</th><th>?ㅼ쟻</th><th>李⑥씠</th><th>怨꾪쉷</th><th>?ㅼ쟻</th><th>李⑥씠</th></tr></thead><tbody>"""
    for _,r in df_rc.iterrows():
        html+=f'<tr><td>{r["怨듭옣紐?]}</td><td>{f(r.get("臾쇰웾_怨꾪쉷"),1)}</td><td>{f(r.get("臾쇰웾_?ㅼ쟻"),1)}</td>{td_d(r.get("臾쇰웾_李⑥씠"),1)}<td>{f(r.get("留ㅼ텧_怨꾪쉷"))}</td><td>{f(r.get("留ㅼ텧_?ㅼ쟻"))}</td>{td_d(r.get("留ㅼ텧_李⑥씠"))}<td>{f(r.get("?곸뾽?댁씡_怨꾪쉷"))}</td><td>{f(r.get("?곸뾽?댁씡_?ㅼ쟻"))}</td>{td_d(r.get("?곸뾽?댁씡_李⑥씠"))}</tr>'
    st.markdown(html+"</tbody></table></div></div></div>", unsafe_allow_html=True)

elif current_page == "?덈?肄?怨듯뿄?댁씡":
    stitle("?덈?肄?怨듯뿄?댁씡 遺꾩꽍")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    rc_sum=df_all[df_all['怨듭옣紐?]=='?덈?肄?怨?]
    if not rc_sum.empty:
        r=rc_sum.iloc[0]; c1,c2,c3,c4=st.columns(4)
        c1.markdown(kpi("?먮ℓ?④? ?ㅼ쟻",f(r['?먮ℓ?④?_?ㅼ쟻']),"????,r['?먮ℓ?④?_?ㅼ쟻']-r['?먮ℓ?④?_?꾨뀈'] if pd.notna(r.get('?먮ℓ?④?_?꾨뀈')) else None,"?꾨뀈"), unsafe_allow_html=True)
        c2.markdown(kpi("蹂?숇퉬 ?ㅼ쟻",f(r['蹂?숇퉬_?ㅼ쟻']),"????,r['蹂?숇퉬_?ㅼ쟻']-r['蹂?숇퉬_?꾨뀈'] if pd.notna(r.get('蹂?숇퉬_?꾨뀈')) else None,"?꾨뀈","red"), unsafe_allow_html=True)
        c3.markdown(kpi("怨듯뿄?댁씡 ?ㅼ쟻",f(r['怨듯뿄?댁씡_?ㅼ쟻']),"????,r['怨듯뿄?댁씡_?ㅼ쟻']-r['怨듯뿄?댁씡_?꾨뀈'] if pd.notna(r.get('怨듯뿄?댁씡_?꾨뀈')) else None,"?꾨뀈","green" if (r.get('怨듯뿄?댁씡_?ㅼ쟻') or 0)>=0 else "red"), unsafe_allow_html=True)
        c4.markdown(kpi("怨듯뿄?댁씡 怨꾪쉷?鍮?,f(r.get('怨듯뿄?댁씡_怨꾪쉷')),"????,r['怨듯뿄?댁씡_?ㅼ쟻']-r['怨듯뿄?댁씡_怨꾪쉷'] if pd.notna(r.get('怨듯뿄?댁씡_怨꾪쉷')) else None,"怨꾪쉷","purple"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    cc1,cc2=st.columns(2)
    with cc1:
        st.markdown('<div class="card"><div class="card-title">怨듭옣蹂??먮ℓ?④? vs 蹂?숇퉬 (????</div>', unsafe_allow_html=True)
        fig=go.Figure(); fig.add_bar(name='?먮ℓ?④?',x=df_rc['怨듭옣紐?],y=df_rc['?먮ℓ?④?_?ㅼ쟻'],marker_color=C['?ㅼ쟻']); fig.add_bar(name='蹂?숇퉬',x=df_rc['怨듭옣紐?],y=df_rc['蹂?숇퉬_?ㅼ쟻'],marker_color=C['?꾨뀈'])
        bc(fig,360); fig.update_layout(barmode='group',xaxis_tickangle=-30); st.plotly_chart(fig,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">怨듭옣蹂?怨듯뿄?댁씡 (????</div>', unsafe_allow_html=True)
        cs=[C['pos'] if (v or 0)>=0 else C['neg'] for v in df_rc['怨듯뿄?댁씡_?ㅼ쟻'].fillna(0)]
        fig2=go.Figure(go.Bar(x=df_rc['怨듭옣紐?],y=df_rc['怨듯뿄?댁씡_?ㅼ쟻'],marker_color=cs,text=df_rc['怨듯뿄?댁씡_?ㅼ쟻'].apply(lambda x:f(x)),textposition='outside',textfont=dict(size=10)))
        fig2.add_hline(y=0,line_dash='dash',line_color='#374151',line_width=1.5); bc(fig2,360); fig2.update_layout(xaxis_tickangle=-30); st.plotly_chart(fig2,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">怨듭옣蹂?怨듯뿄?댁씡 ?곸꽭</div><div class="tbl-wrap">', unsafe_allow_html=True)
    html="""<table class="pl-table"><thead><tr><th rowspan="2">怨듭옣紐?/th><th colspan="3">?먮ℓ?④?(????</th><th colspan="3">蹂?숇퉬(????</th><th colspan="3">怨듯뿄?댁씡(????</th></tr>
    <tr><th>怨꾪쉷</th><th>?ㅼ쟻</th><th>?꾨뀈</th><th>怨꾪쉷</th><th>?ㅼ쟻</th><th>?꾨뀈</th><th>怨꾪쉷</th><th>?ㅼ쟻</th><th>?꾨뀈</th></tr></thead><tbody>"""
    for _,r in df_rc.iterrows():
        cc="pos" if (r.get('怨듯뿄?댁씡_?ㅼ쟻') or 0)>=0 else "neg"
        html+=f'<tr><td>{r["怨듭옣紐?]}</td><td>{f(r.get("?먮ℓ?④?_怨꾪쉷"))}</td><td>{f(r.get("?먮ℓ?④?_?ㅼ쟻"))}</td><td>{f(r.get("?먮ℓ?④?_?꾨뀈"))}</td><td>{f(r.get("蹂?숇퉬_怨꾪쉷"))}</td><td>{f(r.get("蹂?숇퉬_?ㅼ쟻"))}</td><td>{f(r.get("蹂?숇퉬_?꾨뀈"))}</td><td>{f(r.get("怨듯뿄?댁씡_怨꾪쉷"))}</td><td class="{cc}">{f(r.get("怨듯뿄?댁씡_?ㅼ쟻"))}</td><td>{f(r.get("怨듯뿄?댁씡_?꾨뀈"))}</td></tr>'
    st.markdown(html+"</tbody></table></div></div></div>", unsafe_allow_html=True)

elif current_page == "?덈?肄?怨듭옣蹂?:
    stitle("?덈?肄?怨듭옣蹂??먯씡")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    rc_sum=df_all[df_all['怨듭옣紐?]=='?덈?肄?怨?]
    if not rc_sum.empty:
        r=rc_sum.iloc[0]; c1,c2,c3,c4=st.columns(4)
        c1.markdown(kpi("留ㅼ텧 ?ㅼ쟻",f(r['留ㅼ텧_?ㅼ쟻']),"諛깅쭔??,r.get('留ㅼ텧_李⑥씠'),"怨꾪쉷"), unsafe_allow_html=True)
        c2.markdown(kpi("?곸뾽?댁씡 ?ㅼ쟻",f(r['?곸뾽?댁씡_?ㅼ쟻']),"諛깅쭔??,r.get('?곸뾽?댁씡_李⑥씠'),"怨꾪쉷","green" if (r.get('?곸뾽?댁씡_?ㅼ쟻') or 0)>=0 else "red"), unsafe_allow_html=True)
        c3.markdown(kpi("?먮ℓ臾쇰웾 ?ㅼ쟻",f(r.get('臾쇰웾_?ㅼ쟻'),1),"泥쒌렏",r.get('臾쇰웾_李⑥씠'),"怨꾪쉷","purple"), unsafe_allow_html=True)
        c4.markdown(kpi("?댁쁺 怨듭옣","17","媛?,None,"","amber"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    cc1,cc2=st.columns([2.2,1])
    with cc1:
        st.markdown('<div class="card"><div class="card-title">怨듭옣蹂??곸뾽?댁씡 (諛깅쭔??</div>', unsafe_allow_html=True)
        fig=go.Figure()
        for lb,col,clr in [("怨꾪쉷","?곸뾽?댁씡_怨꾪쉷",C["怨꾪쉷"]),("?ㅼ쟻","?곸뾽?댁씡_?ㅼ쟻",C["?ㅼ쟻"]),("?꾨뀈","?곸뾽?댁씡_?꾨뀈",C["?꾨뀈"])]:
            fig.add_bar(name=lb,x=df_rc['怨듭옣紐?],y=df_rc[col],marker_color=clr)
        bc(fig,380); fig.update_layout(barmode='group',xaxis_tickangle=-30); st.plotly_chart(fig,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">?곸뾽?댁씡 ?쒖쐞</div>', unsafe_allow_html=True)
        df_rank=df_rc[['怨듭옣紐?,'?곸뾽?댁씡_?ㅼ쟻']].dropna().sort_values('?곸뾽?댁씡_?ㅼ쟻',ascending=True)
        cs=[C['pos'] if v>=0 else C['neg'] for v in df_rank['?곸뾽?댁씡_?ㅼ쟻']]
        fig2=go.Figure(go.Bar(x=df_rank['?곸뾽?댁씡_?ㅼ쟻'],y=df_rank['怨듭옣紐?],orientation='h',marker_color=cs,text=df_rank['?곸뾽?댁씡_?ㅼ쟻'].apply(lambda x:f(x)),textposition='outside',textfont=dict(size=10)))
        fig2.add_vline(x=0,line_color='#374151',line_width=1.5); bc(fig2,380); st.plotly_chart(fig2,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif current_page in ["嫄댁옄???먯씡","怨⑥옱_?먯씡","?꾨?_?먯씡"]:
    nm={"嫄댁옄???먯씡":"嫄댁옄??,"怨⑥옱_?먯씡":"怨⑥옱","?꾨?_?먯씡":"?꾨?"}[current_page]
    stitle(f"{nm} ?먯씡")
    st.markdown(f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:380px;"><div style="font-size:3.5em;margin-bottom:20px;opacity:0.35;">?슙</div><div style="font-size:1.3em;font-weight:700;color:#374151;margin-bottom:8px;">{nm} ?먯씡 ?섏씠吏</div><div style="color:#9ca3af;">以鍮?以묒엯?덈떎.</div></div>', unsafe_allow_html=True)

