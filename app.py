import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64, os, json, uuid
from data_loader import get_available_years, get_available_months, load_factory_data, load_overview

@st.cache_resource
def _token_store():
    """로그인 토큰 저장소 — 서버 메모리에 유지되므로 새로고침 후에도 로그인 유지"""
    return {}  # {token: username}

ADMIN_USER = "tongyang"
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
PENDING_FILE = os.path.join(os.path.dirname(__file__), "pending_users.json")

def load_users():
    """secrets + users.json 병합. users.json이 우선."""
    base = dict(st.secrets.get("users", {"tongyang": "6150"}))
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                base.update(json.load(f))
        except Exception:
            pass
    return base

def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_pending() -> list:
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_pending(pending: list):
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="동양 건재사업본부 손익", page_icon="📊", layout="wide")

TOKEN_STORE = _token_store()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "건재손익_요약"
if "auth_view" not in st.session_state:
    st.session_state["auth_view"] = "login"  # "login" | "signup"

# ── URL 파라미터 처리 ──
_qp = st.query_params.to_dict()

# 로그아웃
if _qp.get("logout") == "1":
    _t = st.session_state.get("auth_token")
    if _t and _t in TOKEN_STORE:
        del TOKEN_STORE[_t]
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()

# 토큰으로 로그인 복원 (새로고침 후에도 유지)
if not st.session_state.get("logged_in"):
    _t = _qp.get("t")
    if _t and _t in TOKEN_STORE:
        st.session_state["logged_in"] = True
        st.session_state["username"] = TOKEN_STORE[_t]
        st.session_state["auth_token"] = _t

# 페이지 이동 (nav + token 파라미터)
if _qp.get("nav") and st.session_state.get("logged_in"):
    _nav_t = _qp.get("t", "")
    if _nav_t and _nav_t in TOKEN_STORE:
        st.session_state["page"] = _qp["nav"]
        st.query_params.clear()
        st.rerun()



if st.session_state.get("do_logout"):
    st.session_state.clear()
    st.rerun()


USERS = load_users()

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
             '<span style="font-size:1.4em;font-weight:900;color:#0f2044;">동양</span>')

# ══════════════════════════════════════════════════════════════
# 로그인
# ══════════════════════════════════════════════════════════════
USERS = load_users()

if not st.session_state["logged_in"]:
    logo_src = f'data:image/png;base64,{logo_b64}' if logo_b64 else ""
    logo_tag = (f'<img src="{logo_src}" style="height:44px;object-fit:contain;">') if logo_b64 else \
               '<span style="font-size:1.2em;font-weight:900;color:#1a2340;letter-spacing:0.08em;">동양</span>'

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&display=swap');
    html, body, * {{ font-family:'Noto Sans KR',sans-serif !important; }}

    [data-testid="stAppViewContainer"] {{ background:#eef0f4 !important; }}
    [data-testid="stHeader"] {{ display:none !important; }}
    [data-testid="stSidebar"] {{ display:none !important; }}

    .block-container {{
        padding: 36px 32px 28px !important;
        max-width: 420px !important;
        width: 100% !important;
        margin: calc(50vh - 300px) auto 0 !important;
        background: white !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 24px rgba(0,0,0,0.10) !important;
    }}

    .stTextInput > label {{ display:none !important; }}
    .stTextInput > div > div > input {{
        background: #f7f8fa !important;
        border: 1.5px solid #dde2ea !important;
        color: #1a2340 !important;
        border-radius: 6px !important;
        font-size: 0.9em !important;
        height: 42px !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: #1a3a6e !important;
        box-shadow: 0 0 0 2px rgba(26,58,110,0.12) !important;
        background: white !important;
    }}
    .stTextInput > div > div > input::placeholder {{ color: #b0b8c8 !important; }}

    .stButton > button {{
        background: #1a3a6e !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        height: 44px !important;
        font-size: 0.95em !important;
        letter-spacing: 0.03em !important;
    }}
    .stButton > button:hover {{ background: #142d56 !important; }}
    .btn-outline > button {{
        background: white !important;
        color: #1a3a6e !important;
        border: 1.5px solid #1a3a6e !important;
    }}
    .btn-outline > button:hover {{ background: #eef0f4 !important; }}
    [data-testid="stAlert"] {{ border-radius: 6px !important; font-size: 0.85em !important; }}
    </style>

    <div style="position:fixed;top:0;left:0;right:0;z-index:9999;
                background:white;height:70px;display:flex;align-items:center;
                padding:0 32px;box-shadow:0 2px 8px rgba(0,0,0,0.08);border-bottom:1px solid #e8eaf0;">
        {logo_tag}
        <span style="color:rgba(0,0,0,0.2);margin:0 16px;font-size:1.1em;">|</span>
        <span style="color:#4a5568;font-size:1.05em;font-weight:500;
                     letter-spacing:0.04em;">건재사업본부 손익 관리 시스템</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 로그인 뷰 ──
    if st.session_state["auth_view"] == "login":
        st.markdown("""
        <div style="text-align:center;margin-bottom:26px;">
            <div style="display:inline-flex;align-items:center;justify-content:center;
                        width:50px;height:50px;background:#e8eef7;border-radius:50%;
                        margin-bottom:12px;font-size:1.5em;color:#1a3a6e;">&#128100;</div>
            <div style="font-size:1.1em;font-weight:700;color:#1a2340;margin-bottom:3px;">로그인</div>
            <div style="font-size:0.78em;color:#8a95a8;">계정 정보를 입력하세요</div>
        </div>
        <div style="font-size:0.78em;font-weight:600;color:#4a5568;
                    margin-bottom:4px;letter-spacing:0.02em;">아이디</div>
        """, unsafe_allow_html=True)

        username = st.text_input("uid", placeholder="아이디를 입력하세요",
                                 label_visibility="collapsed")

        st.markdown('<div style="font-size:0.78em;font-weight:600;color:#4a5568;'
                    'margin-top:10px;margin-bottom:4px;letter-spacing:0.02em;">패스워드</div>',
                    unsafe_allow_html=True)
        password = st.text_input("pwd", type="password", placeholder="패스워드를 입력하세요",
                                 label_visibility="collapsed")

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

        if st.button("로그인", use_container_width=True):
            if username in USERS and USERS[username] == password:
                _new_token = str(uuid.uuid4())
                TOKEN_STORE[_new_token] = username
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["auth_token"] = _new_token
                st.rerun()
            else:
                st.error("아이디 또는 패스워드가 올바르지 않습니다.")

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("회원가입", use_container_width=True):
            st.session_state["auth_view"] = "signup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="border-top:1px solid #edf0f5;margin:20px 0 0;
                    padding:14px 0 0;text-align:center;">
            <span style="font-size:0.72em;color:#b0b8c8;">
                &copy; 동양 건재사업본부 &nbsp;|&nbsp; 내부 전용 시스템
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── 회원가입 뷰 ──
    else:
        st.markdown("""
        <div style="text-align:center;margin-bottom:26px;">
            <div style="display:inline-flex;align-items:center;justify-content:center;
                        width:50px;height:50px;background:#e8eef7;border-radius:50%;
                        margin-bottom:12px;font-size:1.5em;color:#1a3a6e;">&#9997;&#65039;</div>
            <div style="font-size:1.1em;font-weight:700;color:#1a2340;margin-bottom:3px;">회원가입</div>
            <div style="font-size:0.78em;color:#8a95a8;">가입 신청 후 운영자 승인이 필요합니다</div>
        </div>
        """, unsafe_allow_html=True)

        def _field(label):
            st.markdown(f'<div style="font-size:0.78em;font-weight:600;color:#4a5568;'
                        f'margin-top:10px;margin-bottom:4px;letter-spacing:0.02em;">{label}</div>',
                        unsafe_allow_html=True)

        _field("소속")
        sg_dept = st.text_input("sg_dept", placeholder="소속 부서를 입력하세요",
                                label_visibility="collapsed")
        _field("성함")
        sg_name = st.text_input("sg_name", placeholder="성함을 입력하세요",
                                label_visibility="collapsed")
        _field("아이디")
        sg_uid = st.text_input("sg_uid", placeholder="사용할 아이디를 입력하세요",
                               label_visibility="collapsed")
        _field("패스워드")
        sg_pw = st.text_input("sg_pw", type="password", placeholder="패스워드를 입력하세요",
                              label_visibility="collapsed")
        _field("패스워드 확인")
        sg_pw2 = st.text_input("sg_pw2", type="password", placeholder="패스워드를 다시 입력하세요",
                               label_visibility="collapsed")

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

        if st.button("가입 신청", use_container_width=True):
            current_users = load_users()
            pending = load_pending()
            pending_ids = [p["username"] for p in pending]
            ok = True
            if not sg_dept.strip():
                st.warning("소속을 입력하세요.")
                ok = False
            elif not sg_name.strip():
                st.warning("성함을 입력하세요.")
                ok = False
            elif not sg_uid.strip():
                st.warning("아이디를 입력하세요.")
                ok = False
            elif sg_uid in current_users:
                st.warning("이미 사용 중인 아이디입니다.")
                ok = False
            elif sg_uid in pending_ids:
                st.warning("이미 가입 신청 중인 아이디입니다.")
                ok = False
            elif not sg_pw.strip():
                st.warning("패스워드를 입력하세요.")
                ok = False
            elif sg_pw != sg_pw2:
                st.warning("패스워드가 일치하지 않습니다.")
                ok = False
            if ok:
                pending.append({
                    "id": str(uuid.uuid4()),
                    "department": sg_dept.strip(),
                    "name": sg_name.strip(),
                    "username": sg_uid.strip(),
                    "password": sg_pw,
                })
                save_pending(pending)
                st.success("가입 신청이 완료되었습니다. 운영자 승인 후 로그인할 수 있습니다.")

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("로그인으로 돌아가기", use_container_width=True):
            st.session_state["auth_view"] = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="border-top:1px solid #edf0f5;margin:20px 0 0;
                    padding:14px 0 0;text-align:center;">
            <span style="font-size:0.72em;color:#b0b8c8;">
                &copy; 동양 건재사업본부 &nbsp;|&nbsp; 내부 전용 시스템
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════════════════════
# 네비게이션 구조
# ══════════════════════════════════════════════════════════════
NAV_STRUCTURE = {
    "건재손익": ["건재손익_요약", "건재손익_부문별"],
    "레미콘":   ["레미콘_공헌이익", "레미콘_공장별"],
    "건자재":   ["건자재_손익"],
    "골재":     ["골재_손익"],
    "임대":     ["임대_손익"],
}
PAGE_LABELS = {
    "건재손익_요약":   "요약",
    "건재손익_부문별": "부문별",
    "건재손익_총괄":   "손익 총괄",
    "건재손익_공장별": "공장별 손익",
    "레미콘_공헌이익": "공헌이익 분석",
    "레미콘_공장별":   "공장별 손익",
    "건자재_손익":    "건자재 손익",
    "골재_손익":      "골재 손익",
    "임대_손익":      "임대 손익",
}
all_pages_flat = [pg for pages in NAV_STRUCTURE.values() for pg in pages]

current_page = st.session_state["page"]

def get_parent(page):
    for menu, pages in NAV_STRUCTURE.items():
        if page in pages:
            return menu
    return "건재손익"

active_menu = get_parent(current_page)


_tok = st.session_state.get("auth_token", "")

NAV_LABELS = {
    "건재손익": "건재 손익",
    "레미콘":   "레미콘",
    "건자재":   "건자재",
    "골재":     "골재",
    "임대":     "임대",
}

def nav_href(page):
    return f"?nav={page}&t={_tok}"

def make_dd(pages):
    items = "".join(
        f'<a class="dd-item{"  active" if pg == current_page else ""}" href="{nav_href(pg)}" target="_self">{PAGE_LABELS[pg]}</a>'
        for pg in pages
    )
    return f'<div class="dropdown">{items}</div>'

menu_html = ""
for menu, pages in NAV_STRUCTURE.items():
    ac = " active" if menu == active_menu else ""
    dd = make_dd(pages) if len(pages) > 1 else ""
    label = NAV_LABELS.get(menu, menu)
    menu_html += f'<li class="nav-item"><a class="nav-link{ac}" href="{nav_href(pages[0])}" target="_self">{label}</a>{dd}</li>'

admin_btn_html = f'<a class="nav-admin-btn" href="{nav_href("ADMIN_PAGE")}" target="_self" title="관리자 설정"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg></a>' if st.session_state.get("username") == ADMIN_USER else ""

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
* {{ font-family:'Noto Sans KR',sans-serif !important; box-sizing:border-box; }}
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {{ background:#f0f2f5 !important; }}
[data-testid="stHeader"] {{ display:none; }}
[data-testid="stSidebar"] {{ display:none; }}
.block-container {{ padding-top:100px !important; padding-left:56px !important; padding-right:56px !important; padding-bottom:0 !important; max-width:100% !important; }}

/* 상단 네비 */
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
    display:flex; align-items:center; height:70px; padding:10px 72px 0 72px;
    color:#333; font-size:1.35em; font-weight:600;
    cursor:pointer; white-space:nowrap; text-decoration:none !important;
    transition:color 0.18s; user-select:none; border:none !important;
    outline:none; background:none;
}}
.nav-link:hover {{ color:#1d4ed8; text-decoration:none !important; }}
.nav-link.active {{
    color:#1d4ed8; font-weight:700; text-decoration:none !important;
    background: linear-gradient(180deg, transparent 30%, #dbeafe 100%);
    border-bottom: 3px solid #1d4ed8;
    padding-bottom: 0;
    padding-left: 28px; padding-right: 28px;
}}

/* 드롭다운 */
.dropdown {{
    position:absolute; top:70px; left:50%; background:white; min-width:120px;
    border-top:3px solid #1d4ed8;
    box-shadow:0 8px 28px rgba(0,0,0,0.12);
    opacity:0; visibility:hidden; transform:translateX(-50%) translateY(-6px);
    transition:opacity 0.18s,transform 0.18s,visibility 0.18s; z-index:10000;
}}
.nav-item:hover .dropdown {{ opacity:1; visibility:visible; transform:translateX(-50%) translateY(0); }}
.dd-item {{
    display:block; padding:13px 14px; color:#374151; font-size:1.0em; font-weight:500; text-align:center;
    border-bottom:1px solid #f3f4f6; cursor:pointer; text-decoration:none !important;
    transition:background 0.13s,color 0.13s;
}}
.dd-item:last-child {{ border-bottom:none; }}
.dd-item:hover {{ background:#eff6ff; color:#1d4ed8; }}
.dd-item.active {{ background:#eff6ff; color:#1d4ed8; font-weight:700; }}

.nav-right {{ margin-left:auto; display:flex; align-items:center; gap:14px; flex-shrink:0; }}
.nav-user {{ color:#6b7280; font-size:0.85em; font-weight:500; }}

.nav-right {{ margin-left:auto; display:flex; align-items:center; gap:14px; flex-shrink:0; }}
.nav-user {{ color:#6b7280; font-size:0.85em; font-weight:500; }}
.nav-logout-btn {{
    background:none; border:1px solid #d1d5db; color:#6b7280 !important;
    padding:0 16px; border-radius:4px; font-size:0.85em; cursor:pointer;
    font-weight:500; height:34px; transition:all 0.15s;
    font-family:'Noto Sans KR',sans-serif;
    text-decoration:none !important; display:inline-flex; align-items:center;
}}
.nav-logout-btn:visited {{ color:#6b7280 !important; text-decoration:none !important; }}
.nav-logout-btn:hover {{ border-color:#1d4ed8; color:#1d4ed8 !important; text-decoration:none !important; }}
.nav-admin-btn {{
    background:none; border:1px solid #d1d5db; border-radius:4px;
    height:34px; width:34px; padding:0; color:#6b7280 !important;
    flex-shrink:0; transition:all 0.15s; display:inline-flex;
    align-items:center; justify-content:center; text-decoration:none !important;
    cursor:pointer; line-height:1;
}}
.nav-admin-btn:hover {{ border-color:#1d4ed8 !important; background:#eff6ff !important; color:#1d4ed8 !important; text-decoration:none !important; }}
.nav-admin-btn:visited {{ color:#6b7280 !important; text-decoration:none !important; }}

/* 페이지 전환 페이드인 */
@keyframes fadeIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
[data-testid="stAppViewContainer"] {{ animation: fadeIn 0.3s ease-in; }}

/* 컨텐츠 */
.content-wrap {{ padding:2px 0; max-width:1500px; margin:0 auto; }}

/* KPI 카드 */
.kpi-card {{ background:white; border-radius:10px; padding:20px 22px; box-shadow:0 1px 6px rgba(0,0,0,0.06); border-top:4px solid #1d4ed8; height:100%; }}
.kpi-card.green  {{ border-top-color:#16a34a; }}
.kpi-card.red    {{ border-top-color:#dc2626; }}
.kpi-card.amber  {{ border-top-color:#d97706; }}
.kpi-card.purple {{ border-top-color:#7c3aed; }}
.kpi-label {{ color:#374151; font-size:1.05em; font-weight:700; letter-spacing:0.3px; margin-bottom:10px; }}
.kpi-value {{ color:#111827; font-size:2.4em; font-weight:900; line-height:1; margin-bottom:0; }}
.kpi-unit  {{ font-size:0.42em; color:#6b7280; font-weight:500; vertical-align:middle; }}
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
[data-testid="stSelectbox"] > div > div {{ background:#ffffff !important; border-color:#d1d5db !important; }}
</style>

<div class="top-nav">
    <a class="nav-logo" href="{nav_href('건재손익_요약')}" target="_self">{logo_html}</a>
    <ul class="nav-menu">{menu_html}</ul>
    <div class="nav-right"><span class="nav-user">👤 <span style="font-family:Arial,sans-serif;">{st.session_state.get('username','')}</span></span>{admin_btn_html}<a class="nav-logout-btn" href="?logout=1" target="_self">로그아웃</a></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 연/월 필터 (우측 상단)
# ══════════════════════════════════════════════════════════════
if current_page == "ADMIN_PAGE":
    years = []
    selected_year = None
    selected_month = None
    df_all = df_rc = df_summary = None
else:
    years = get_available_years()
    if not years:
        st.error("데이터 폴더에 연도 폴더가 없습니다.")
        st.stop()

    if "sel_year" not in st.session_state:
        st.session_state["sel_year"] = years[0]
    if st.session_state["sel_year"] not in years:
        st.session_state["sel_year"] = years[0]
    selected_year = st.session_state["sel_year"]
    _init_months = get_available_months(selected_year)
    if "sel_month" not in st.session_state or st.session_state["sel_month"] not in _init_months:
        st.session_state["sel_month"] = _init_months[-1] if _init_months else 1
    selected_month = st.session_state["sel_month"]

    if current_page not in ("건재손익_요약", "건재손익_부문별"):
        _s, _y, _m = st.columns([0.82, 0.09, 0.09])
        with _y:
            st.selectbox("연도", years, key="sel_year", format_func=lambda x: f"{x}년", label_visibility="collapsed")
        with _m:
            _pm = get_available_months(selected_year)
            st.selectbox("월", _pm, format_func=lambda x: f"{x}월", key="sel_month", label_visibility="collapsed")
        st.markdown('<hr style="margin:0;border:none;border-top:1px solid #e8eaed;">', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # 데이터
    # ══════════════════════════════════════════════════════════════
    REMICON_FACTORIES = ['안양','인천','파주','김포','부산','서부산','김해',
                         '정관','양산','창원','대구','울산','아산','전주','군산','원주','제주']

    @st.cache_data(ttl=600)
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

def kpi(label, value, unit, delta=None, dl="계획대비", color=""):
    ds = ""
    if delta is not None and not (isinstance(delta, float) and pd.isna(delta)):
        arrow = "▲" if delta>=0 else "▼"; cls = "pos" if delta>=0 else "neg"
        ds = f'<div class="kpi-delta {cls}">{arrow} {f(abs(delta))}<span class="kpi-delta-sub"> vs {dl}</span></div>'
    return f'<div class="kpi-card {color}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}<span class="kpi-unit"> {unit}</span></div>{ds}</div>'

C = {"계획":"#93c5fd","실적":"#1d4ed8","전년":"#f87171","pos":"#16a34a","neg":"#dc2626"}

@st.cache_data(ttl=600)
def get_kpi_trend(year, up_to_month):
    """1월~up_to_month 각 월의 KPI 당월값을 모아 트렌드 DataFrame 반환."""
    months = [m for m in get_available_months(year) if m <= up_to_month]
    rows = []
    for m in months:
        dov = load_overview(year, m)
        dfa = load_factory_data(year, m)
        if dov is None:
            continue
        rc  = dov[dov['구분']=='레미콘'].iloc[0] if not dov[dov['구분']=='레미콘'].empty else None
        tot = dov[dov['구분']=='합계'].iloc[0]   if not dov[dov['구분']=='합계'].empty   else None
        rcd = dfa[dfa['공장명']=='레미콘 계'].iloc[0] if dfa is not None and not dfa[dfa['공장명']=='레미콘 계'].empty else None
        rows.append({
            '월': m,
            '판매량_계획':  rc.get('물량_계획')      if rc  is not None else None,
            '판매량_실적':  rc.get('물량_실적')      if rc  is not None else None,
            '매출_계획':    tot.get('매출_계획')     if tot is not None else None,
            '매출_실적':    tot.get('매출_실적')     if tot is not None else None,
            '영업이익_계획': tot.get('영업이익_계획') if tot is not None else None,
            '영업이익_실적': tot.get('영업이익_실적') if tot is not None else None,
            '공헌이익_계획': rcd.get('공헌이익_계획') if rcd is not None else None,
            '공헌이익_실적': rcd.get('공헌이익_실적') if rcd is not None else None,
        })
    return pd.DataFrame(rows) if rows else None

def spark(df, pcol, acol, height=420):
    """계획/실적 선 그래프 스파크라인."""
    if df is None or df.empty:
        return None
    mlabels = [f"{int(m)}월" for m in df['월']]
    fig = go.Figure()
    if pcol in df.columns:
        fig.add_trace(go.Scatter(
            x=mlabels, y=df[pcol], mode='lines+markers', name='계획',
            line=dict(color='#93c5fd', width=3, dash='dot'),
            marker=dict(size=9, color='#93c5fd'),
        ))
    if acol in df.columns:
        yvals = list(df[acol])
        textvals = [f"{v:,.0f}" if v is not None and not (isinstance(v, float) and pd.isna(v)) else "" for v in yvals]

        # 각 포인트 위/아래 자동 배치: 직전보다 높으면 위, 낮으면 아래
        # 단, 인접 포인트와 너무 가까우면 반대쪽으로
        def smart_pos(vals):
            n = len(vals)
            pos = []
            for i in range(n):
                prev = vals[i-1] if i > 0 else None
                nxt  = vals[i+1] if i < n-1 else None
                cur  = vals[i]
                if cur is None or (isinstance(cur, float) and pd.isna(cur)):
                    pos.append('top center')
                    continue
                # 로컬 최대 → 위, 로컬 최소 → 아래
                is_max = (prev is None or cur >= prev) and (nxt is None or cur >= nxt)
                is_min = (prev is None or cur <= prev) and (nxt is None or cur <= nxt)
                if is_max:
                    pos.append('top center')
                elif is_min:
                    pos.append('bottom center')
                else:
                    # 방향: 올라가는 중이면 위, 내려가는 중이면 아래
                    pos.append('top center' if (prev is not None and cur > prev) else 'bottom center')
            return pos

        text_positions = smart_pos(yvals)
        fig.add_trace(go.Scatter(
            x=mlabels, y=yvals, mode='lines+markers+text', name='실적',
            line=dict(color='#1d4ed8', width=4),
            marker=dict(size=10, color='#1d4ed8'),
            text=textvals,
            textposition=text_positions,
            textfont=dict(size=16, color='#1d4ed8', family='Noto Sans KR'),
        ))
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=50, b=30),
        plot_bgcolor='white', paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation='h', x=1, y=1.18, xanchor='right', yanchor='top',
            font=dict(size=14, color='#6b7280'), bgcolor='rgba(0,0,0,0)',
            itemwidth=30, traceorder='normal',
        ),
        xaxis=dict(
            showgrid=False, tickfont=dict(size=14, color='#4b5563'),
            linecolor='#e5e7eb', showline=True, tickangle=0,
        ),
        yaxis=dict(
            showgrid=True, showticklabels=False, gridcolor='#f3f4f6',
        ),
        font=dict(family='Noto Sans KR'),
        hoverlabel=dict(font_size=13, font_family='Noto Sans KR'),
    )
    return fig

def kpi_spark(col, label, value_str, unit, delta, color, trend_df, pcol, acol, plan_val=None):
    """KPI 헤더 + 스파크라인을 하나의 카드처럼 렌더링."""
    border = {"amber":"#d97706","green":"#16a34a","red":"#dc2626","purple":"#7c3aed"}.get(color,"#1d4ed8")
    ds = ""
    if delta is not None and not (isinstance(delta, float) and pd.isna(delta)):
        arrow = "▲" if delta>=0 else "▼"; cls = "pos" if delta>=0 else "neg"
        pct_str = ""
        if plan_val is not None and plan_val != 0 and not (isinstance(plan_val, float) and pd.isna(plan_val)):
            pct = delta / plan_val * 100
            pct_arrow = "▲" if pct>=0 else "▼"
            pct_str = f' {pct_arrow}{abs(pct):.1f}%'
        ds = f'<span class="kpi-delta {cls}" style="font-size:1.0em;font-weight:700;margin-left:8px;white-space:nowrap;flex-shrink:0;">(계획대비 {arrow} {f(abs(delta))}{pct_str})</span>'
    with col:
        st.markdown(f"""
        <div style="background:white;border-radius:10px 10px 0 0;padding:18px 20px 12px;
                    border-top:4px solid {border};
                    box-shadow:0 1px 0 rgba(0,0,0,0.04);
                    border-left:1px solid #eef0f4;border-right:1px solid #eef0f4;">
            <div style="font-size:1.15em;font-weight:800;color:#1f2937;margin-bottom:10px;letter-spacing:0.01em;">{label}</div>
            <div style="display:flex;align-items:baseline;flex-wrap:nowrap;gap:0;overflow:hidden;">
                <div class="kpi-value" style="flex-shrink:1;min-width:0;">{value_str}<span class="kpi-unit"> {unit}</span></div>
                {ds}
            </div>
        </div>
        """, unsafe_allow_html=True)
        fig = spark(trend_df, pcol, acol)
        if fig:
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("""
            <div style="background:white;border-radius:0 0 10px 10px;height:10px;
                        border-left:1px solid #eef0f4;border-right:1px solid #eef0f4;
                        border-bottom:1px solid #eef0f4;margin-top:-18px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.05);"></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:white;border-radius:0 0 10px 10px;
                        border-left:1px solid #eef0f4;border-right:1px solid #eef0f4;
                        border-bottom:1px solid #eef0f4;height:16px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.05);"></div>
            """, unsafe_allow_html=True)

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
    cls = "pos" if val>=0 else "neg"; arr = "▲" if val>=0 else "▼"
    return f'<td class="{cls}">{arr}&nbsp;{f(abs(val),d)}</td>'

def stitle(title):
    st.markdown(f"""
    <div style="padding:18px 32px 0;display:flex;align-items:center;gap:12px;">
        <div style="width:4px;height:22px;background:#1d4ed8;border-radius:2px;flex-shrink:0;"></div>
        <span style="font-size:1.15em;font-weight:900;color:#1f2937;">{title}</span>
        <span style="background:#eff6ff;color:#1d4ed8;padding:3px 12px;border-radius:20px;font-size:0.78em;font-weight:600;">{selected_year}년 {selected_month}월</span>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 건재손익 요약
# ══════════════════════════════════════════════════════════════
if current_page == "건재손익_요약":
    if "sel_period" not in st.session_state:
        st.session_state["sel_period"] = "당월"
    st.markdown("""<style>
    /* 드롭다운만 있는 컬럼 패딩 제거 */
    div[data-testid="stColumn"]:has(> div > div > div[data-testid="stSelectbox"]) {
        padding-left: 2px !important;
        padding-right: 2px !important;
    }
    /* 드롭다운 컬럼들이 속한 행의 gap 최소화 */
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] > div > div > div[data-testid="stSelectbox"]) {
        gap: 4px !important;
    }
    /* 요약 페이지 제목 행~KPI 카드 사이 여백 */
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    </style>""", unsafe_allow_html=True)
    _tc, _rc = st.columns([0.76, 0.24], gap="small")
    with _tc:
        st.markdown(f"""
        <div style="padding:2px 0 0;display:flex;align-items:center;gap:12px;">
            <div style="width:4px;height:22px;background:#1d4ed8;border-radius:2px;flex-shrink:0;"></div>
            <span style="font-size:1.6em;font-weight:900;color:#1f2937;">요약</span>
            <span style="background:#eff6ff;color:#1d4ed8;padding:4px 16px;border-radius:20px;font-size:1.05em;font-weight:600;">{selected_year}년 {selected_month}월</span>
        </div>""", unsafe_allow_html=True)
    with _rc:
        _cy, _cm, _cp = st.columns([1,1,1], gap="small")
        with _cy:
            st.markdown('<div style="padding-top:14px;">', unsafe_allow_html=True)
            st.selectbox("연도", years, key="sel_year", format_func=lambda x: f"{x}년", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
        with _cm:
            st.markdown('<div style="padding-top:14px;">', unsafe_allow_html=True)
            _months = get_available_months(selected_year)
            st.selectbox("월", _months, format_func=lambda x: f"{x}월", key="sel_month", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
        with _cp:
            st.markdown('<div style="padding-top:14px;">', unsafe_allow_html=True)
            st.selectbox("기간", ["당월", "누계"], key="sel_period", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
    selected_period = st.session_state["sel_period"]
    _sfx = "누계" if selected_period == "누계" else ""
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    @st.cache_data(ttl=600)
    def get_overview(year, month):
        return load_overview(year, month)

    df_ov = get_overview(selected_year, selected_month)

    def oir(sale, oi):
        try:
            v = float(oi) / float(sale) * 100
            return f"{v:.1f}%"
        except:
            return "-"

    def build_overview_table(df_src, sfx=""):
        """sfx='' → 당월, sfx='누계' → 누계"""
        p = lambda col: col + (f'_누계계획' if sfx else '_계획')
        r_col = lambda col: col + (f'_누계실적' if sfx else '_실적')
        d_col = lambda col: col + (f'_누계차이' if sfx else '_차이')
        html = """<table class="pl-table">
        <thead>
        <tr>
          <th rowspan="2">구분</th>
          <th colspan="3">물량 (천㎥)</th>
          <th colspan="3">매출액 (백만원)</th>
          <th colspan="3">영업이익 (백만원)</th>
          <th colspan="2">영업이익률</th>
        </tr>
        <tr>
          <th>계획</th><th>실적</th><th>차이</th>
          <th>계획</th><th>실적</th><th>차이</th>
          <th>계획</th><th>실적</th><th>차이</th>
          <th>계획</th><th>실적</th>
        </tr></thead><tbody>"""
        for _, row in df_src.iterrows():
            name = row['구분']
            tc = ' class="total"' if name == '합계' else ''
            m_p = row.get(p('물량')); m_r = row.get(r_col('물량')); m_d = row.get(d_col('물량'))
            s_p = row.get(p('매출')); s_r = row.get(r_col('매출')); s_d = row.get(d_col('매출'))
            o_p = row.get(p('영업이익')); o_r = row.get(r_col('영업이익')); o_d = row.get(d_col('영업이익'))
            html += f"""<tr{tc}>
              <td>{name}</td>
              <td>{f(m_p,1)}</td><td>{f(m_r,1)}</td>{td_d(m_d,1)}
              <td>{f(s_p)}</td><td>{f(s_r)}</td>{td_d(s_d)}
              <td>{f(o_p)}</td><td>{f(o_r)}</td>{td_d(o_d)}
              <td>{oir(s_p,o_p)}</td><td>{oir(s_r,o_r)}</td>
            </tr>"""
        html += "</tbody></table>"
        return html

    if df_ov is not None:
        total_row = df_ov[df_ov['구분']=='합계'].iloc[0] if not df_ov[df_ov['구분']=='합계'].empty else None
        rc_row_ov = df_ov[df_ov['구분']=='레미콘'].iloc[0] if not df_ov[df_ov['구분']=='레미콘'].empty else None

        # ── KPI 카드 ──
        def _ov_col(base, kind):
            # kind: '실적','차이','계획'
            return f'{base}_누계{kind}' if _sfx else f'{base}_{kind}'
        rc_detail   = df_all[df_all['공장명']=='레미콘 계'].iloc[0] if not df_all[df_all['공장명']=='레미콘 계'].empty else None
        total_all   = df_all[df_all['공장명']=='합계'].iloc[0]       if not df_all[df_all['공장명']=='합계'].empty       else None

        # 월별 트렌드 데이터 (스파크라인용)
        trend_df = get_kpi_trend(selected_year, selected_month)

        # 스파크라인 plotly 요소와 markdown 사이 gap 제거용 CSS
        st.markdown("""
        <style>
        /* KPI 스파크라인 카드: 헤더와 차트 사이 gap 제거 */
        [data-testid="stColumn"] [data-testid="stVerticalBlock"]
            > [data-testid="element-container"]:has(+ [data-testid="element-container"] [data-testid="stPlotlyChart"]) {
            margin-bottom: 0 !important;
        }
        [data-testid="stColumn"] [data-testid="stVerticalBlock"]
            > [data-testid="element-container"]:has([data-testid="stPlotlyChart"]) {
            margin-top: -10px !important;
            background: white;
        }
        [data-testid="stColumn"] [data-testid="stVerticalBlock"]
            > [data-testid="element-container"] [data-testid="stPlotlyChart"] {
            background: white;
        }
        </style>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        _kpi_total = total_row if _sfx else (total_all if total_all is not None else total_row)

        if rc_row_ov is not None:
            kpi_spark(c1, "레미콘 판매량",
                      f(rc_row_ov.get(_ov_col('물량','실적')), 1), "천㎥",
                      rc_row_ov.get(_ov_col('물량','차이')), "amber",
                      trend_df, "판매량_계획", "판매량_실적",
                      plan_val=rc_row_ov.get(_ov_col('물량','계획')))

        if _kpi_total is not None:
            _매출실적 = _kpi_total.get(_ov_col('매출','실적'))
            _oi실적   = _kpi_total.get(_ov_col('영업이익','실적'))
            kpi_spark(c2, "매출액",
                      f(_매출실적), "백만원",
                      _kpi_total.get(_ov_col('매출','차이')), "",
                      trend_df, "매출_계획", "매출_실적")
            kpi_spark(c3, "영업이익",
                      f(_oi실적), "백만원",
                      _kpi_total.get(_ov_col('영업이익','차이')),
                      "green" if (_oi실적 or 0)>=0 else "red",
                      trend_df, "영업이익_계획", "영업이익_실적")

        if rc_detail is not None:
            _공헌실적 = rc_detail.get('공헌이익_실적')
            _공헌계획 = rc_detail.get('공헌이익_계획')
            kpi_spark(c4, "공헌이익",
                      f(_공헌실적), "원/㎥",
                      _공헌실적-_공헌계획 if pd.notna(_공헌계획) and _공헌실적 is not None else None,
                      "green" if (_공헌실적 or 0)>=0 else "red",
                      trend_df, "공헌이익_계획", "공헌이익_실적")


    else:
        st.error("손익총괄 데이터를 불러올 수 없습니다.")

    st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "건재손익_부문별":
    stitle("건재 부문별 손익")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    if "sel_period" not in st.session_state:
        st.session_state["sel_period"] = "당월"
    _bm_period = st.session_state.get("sel_period", "당월")
    _bm_sfx = "누계" if _bm_period == "누계" else ""

    @st.cache_data(ttl=600)
    def _get_overview_bm(year, month):
        return load_overview(year, month)

    df_ov_bm = _get_overview_bm(selected_year, selected_month)

    def _oir_bm(sale, oi):
        try:
            return f"{float(oi)/float(sale)*100:.1f}%"
        except:
            return "-"

    def _build_overview_table_bm(df_src, sfx=""):
        p = lambda col: col + ('_누계계획' if sfx else '_계획')
        r_col = lambda col: col + ('_누계실적' if sfx else '_실적')
        d_col = lambda col: col + ('_누계차이' if sfx else '_차이')
        html = """<table class="pl-table">
        <thead>
        <tr>
          <th rowspan="2">구분</th>
          <th colspan="3">물량 (천㎥)</th>
          <th colspan="3">매출액 (백만원)</th>
          <th colspan="3">영업이익 (백만원)</th>
          <th colspan="2">영업이익률</th>
        </tr>
        <tr>
          <th>계획</th><th>실적</th><th>차이</th>
          <th>계획</th><th>실적</th><th>차이</th>
          <th>계획</th><th>실적</th><th>차이</th>
          <th>계획</th><th>실적</th>
        </tr></thead><tbody>"""
        for _, row in df_src.iterrows():
            name = row['구분']
            tc = ' class="total"' if name == '합계' else ''
            m_p = row.get(p('물량')); m_r = row.get(r_col('물량')); m_d = row.get(d_col('물량'))
            s_p = row.get(p('매출')); s_r = row.get(r_col('매출')); s_d = row.get(d_col('매출'))
            o_p = row.get(p('영업이익')); o_r = row.get(r_col('영업이익')); o_d = row.get(d_col('영업이익'))
            html += f"""<tr{tc}>
              <td>{name}</td>
              <td>{f(m_p,1)}</td><td>{f(m_r,1)}</td>{td_d(m_d,1)}
              <td>{f(s_p)}</td><td>{f(s_r)}</td>{td_d(s_d)}
              <td>{f(o_p)}</td><td>{f(o_r)}</td>{td_d(o_d)}
              <td>{_oir_bm(s_p,o_p)}</td><td>{_oir_bm(s_r,o_r)}</td>
            </tr>"""
        html += "</tbody></table>"
        return html

    if df_ov_bm is not None:
        st.markdown(f'<div class="card"><div class="card-title">사업부문별 손익 상세 — {_bm_period}</div><div class="tbl-wrap">', unsafe_allow_html=True)
        st.markdown(_build_overview_table_bm(df_ov_bm, _bm_sfx) + "</div></div>", unsafe_allow_html=True)
    else:
        st.error("손익총괄 데이터를 불러올 수 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "건재손익_공장별":
    stitle("공장별 손익")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    metric=st.selectbox("지표",['매출','영업이익','물량'],format_func=lambda x:{'매출':'매출액(백만원)','영업이익':'영업이익(백만원)','물량':'판매물량(천㎥)'}[x])
    cc1,cc2=st.columns([2.2,1])
    with cc1:
        st.markdown('<div class="card"><div class="card-title">공장별 실적 비교</div>', unsafe_allow_html=True)
        fig=go.Figure()
        for lb,col,clr in [("계획",f"{metric}_계획",C["계획"]),("실적",f"{metric}_실적",C["실적"]),("전년",f"{metric}_전년",C["전년"])]:
            fig.add_bar(name=lb,x=df_rc['공장명'],y=df_rc[col],marker_color=clr)
        bc(fig,400); fig.update_layout(barmode='group',xaxis_tickangle=-30); st.plotly_chart(fig,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">영업이익 계획대비</div>', unsafe_allow_html=True)
        df_d2=df_rc[['공장명','영업이익_차이']].dropna(); cs=[C['pos'] if v>=0 else C['neg'] for v in df_d2['영업이익_차이']]
        fig2=go.Figure(go.Bar(x=df_d2['영업이익_차이'],y=df_d2['공장명'],orientation='h',marker_color=cs,text=df_d2['영업이익_차이'].apply(lambda x:f(x)),textposition='outside',textfont=dict(size=10)))
        fig2.add_vline(x=0,line_color='#374151',line_width=1.5); bc(fig2,400); fig2.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig2,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">공장별 손익 상세</div><div class="tbl-wrap">', unsafe_allow_html=True)
    html="""<table class="pl-table"><thead><tr><th rowspan="2">공장명</th><th colspan="3">물량(천㎥)</th><th colspan="3">매출(백만원)</th><th colspan="3">영업이익(백만원)</th></tr>
    <tr><th>계획</th><th>실적</th><th>차이</th><th>계획</th><th>실적</th><th>차이</th><th>계획</th><th>실적</th><th>차이</th></tr></thead><tbody>"""
    for _,r in df_rc.iterrows():
        html+=f'<tr><td>{r["공장명"]}</td><td>{f(r.get("물량_계획"),1)}</td><td>{f(r.get("물량_실적"),1)}</td>{td_d(r.get("물량_차이"),1)}<td>{f(r.get("매출_계획"))}</td><td>{f(r.get("매출_실적"))}</td>{td_d(r.get("매출_차이"))}<td>{f(r.get("영업이익_계획"))}</td><td>{f(r.get("영업이익_실적"))}</td>{td_d(r.get("영업이익_차이"))}</tr>'
    st.markdown(html+"</tbody></table></div></div></div>", unsafe_allow_html=True)

elif current_page == "레미콘_공헌이익":
    stitle("레미콘 공헌이익 분석")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    rc_sum=df_all[df_all['공장명']=='레미콘 계']
    if not rc_sum.empty:
        r=rc_sum.iloc[0]; c1,c2,c3,c4=st.columns(4)
        c1.markdown(kpi("판매단가 실적",f(r['판매단가_실적']),"원/㎥",r['판매단가_실적']-r['판매단가_전년'] if pd.notna(r.get('판매단가_전년')) else None,"전년"), unsafe_allow_html=True)
        c2.markdown(kpi("변동비 실적",f(r['변동비_실적']),"원/㎥",r['변동비_실적']-r['변동비_전년'] if pd.notna(r.get('변동비_전년')) else None,"전년","red"), unsafe_allow_html=True)
        c3.markdown(kpi("공헌이익 실적",f(r['공헌이익_실적']),"원/㎥",r['공헌이익_실적']-r['공헌이익_전년'] if pd.notna(r.get('공헌이익_전년')) else None,"전년","green" if (r.get('공헌이익_실적') or 0)>=0 else "red"), unsafe_allow_html=True)
        c4.markdown(kpi("공헌이익 계획대비",f(r.get('공헌이익_계획')),"원/㎥",r['공헌이익_실적']-r['공헌이익_계획'] if pd.notna(r.get('공헌이익_계획')) else None,"계획","purple"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    cc1,cc2=st.columns(2)
    with cc1:
        st.markdown('<div class="card"><div class="card-title">공장별 판매단가 vs 변동비 (원/㎥)</div>', unsafe_allow_html=True)
        fig=go.Figure(); fig.add_bar(name='판매단가',x=df_rc['공장명'],y=df_rc['판매단가_실적'],marker_color=C['실적']); fig.add_bar(name='변동비',x=df_rc['공장명'],y=df_rc['변동비_실적'],marker_color=C['전년'])
        bc(fig,360); fig.update_layout(barmode='group',xaxis_tickangle=-30); st.plotly_chart(fig,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">공장별 공헌이익 (원/㎥)</div>', unsafe_allow_html=True)
        cs=[C['pos'] if (v or 0)>=0 else C['neg'] for v in df_rc['공헌이익_실적'].fillna(0)]
        fig2=go.Figure(go.Bar(x=df_rc['공장명'],y=df_rc['공헌이익_실적'],marker_color=cs,text=df_rc['공헌이익_실적'].apply(lambda x:f(x)),textposition='outside',textfont=dict(size=10)))
        fig2.add_hline(y=0,line_dash='dash',line_color='#374151',line_width=1.5); bc(fig2,360); fig2.update_layout(xaxis_tickangle=-30); st.plotly_chart(fig2,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="card-title">공장별 공헌이익 상세</div><div class="tbl-wrap">', unsafe_allow_html=True)
    html="""<table class="pl-table"><thead><tr><th rowspan="2">공장명</th><th colspan="3">판매단가(원/㎥)</th><th colspan="3">변동비(원/㎥)</th><th colspan="3">공헌이익(원/㎥)</th></tr>
    <tr><th>계획</th><th>실적</th><th>전년</th><th>계획</th><th>실적</th><th>전년</th><th>계획</th><th>실적</th><th>전년</th></tr></thead><tbody>"""
    for _,r in df_rc.iterrows():
        cc="pos" if (r.get('공헌이익_실적') or 0)>=0 else "neg"
        html+=f'<tr><td>{r["공장명"]}</td><td>{f(r.get("판매단가_계획"))}</td><td>{f(r.get("판매단가_실적"))}</td><td>{f(r.get("판매단가_전년"))}</td><td>{f(r.get("변동비_계획"))}</td><td>{f(r.get("변동비_실적"))}</td><td>{f(r.get("변동비_전년"))}</td><td>{f(r.get("공헌이익_계획"))}</td><td class="{cc}">{f(r.get("공헌이익_실적"))}</td><td>{f(r.get("공헌이익_전년"))}</td></tr>'
    st.markdown(html+"</tbody></table></div></div></div>", unsafe_allow_html=True)

elif current_page == "레미콘_공장별":
    stitle("레미콘 공장별 손익")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)
    rc_sum=df_all[df_all['공장명']=='레미콘 계']
    if not rc_sum.empty:
        r=rc_sum.iloc[0]; c1,c2,c3,c4=st.columns(4)
        c1.markdown(kpi("매출 실적",f(r['매출_실적']),"백만원",r.get('매출_차이'),"계획"), unsafe_allow_html=True)
        c2.markdown(kpi("영업이익 실적",f(r['영업이익_실적']),"백만원",r.get('영업이익_차이'),"계획","green" if (r.get('영업이익_실적') or 0)>=0 else "red"), unsafe_allow_html=True)
        c3.markdown(kpi("판매물량 실적",f(r.get('물량_실적'),1),"천㎥",r.get('물량_차이'),"계획","purple"), unsafe_allow_html=True)
        c4.markdown(kpi("운영 공장","17","개",None,"","amber"), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    cc1,cc2=st.columns([2.2,1])
    with cc1:
        st.markdown('<div class="card"><div class="card-title">공장별 영업이익 (백만원)</div>', unsafe_allow_html=True)
        fig=go.Figure()
        for lb,col,clr in [("계획","영업이익_계획",C["계획"]),("실적","영업이익_실적",C["실적"]),("전년","영업이익_전년",C["전년"])]:
            fig.add_bar(name=lb,x=df_rc['공장명'],y=df_rc[col],marker_color=clr)
        bc(fig,380); fig.update_layout(barmode='group',xaxis_tickangle=-30); st.plotly_chart(fig,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown('<div class="card"><div class="card-title">영업이익 순위</div>', unsafe_allow_html=True)
        df_rank=df_rc[['공장명','영업이익_실적']].dropna().sort_values('영업이익_실적',ascending=True)
        cs=[C['pos'] if v>=0 else C['neg'] for v in df_rank['영업이익_실적']]
        fig2=go.Figure(go.Bar(x=df_rank['영업이익_실적'],y=df_rank['공장명'],orientation='h',marker_color=cs,text=df_rank['영업이익_실적'].apply(lambda x:f(x)),textposition='outside',textfont=dict(size=10)))
        fig2.add_vline(x=0,line_color='#374151',line_width=1.5); bc(fig2,380); st.plotly_chart(fig2,use_container_width=True); st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif current_page in ["건자재_손익","골재_손익","임대_손익"]:
    nm={"건자재_손익":"건자재","골재_손익":"골재","임대_손익":"임대"}[current_page]
    stitle(f"{nm} 손익")
    st.markdown(f'<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:380px;"><div style="font-size:3.5em;margin-bottom:20px;opacity:0.35;">🚧</div><div style="font-size:1.3em;font-weight:700;color:#374151;margin-bottom:8px;">{nm} 손익 페이지</div><div style="color:#9ca3af;">준비 중입니다.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 통합관리시스템
# ══════════════════════════════════════════════════════════════
elif current_page == "ADMIN_PAGE":
    if st.session_state.get("username") != ADMIN_USER:
        st.error("접근 권한이 없습니다.")
        st.stop()

    st.markdown("""
    <style>
    .admin-wrap { max-width:760px; margin:0 auto; padding:24px 0; }
    .admin-section { background:white; border-radius:10px; padding:28px 32px;
                     box-shadow:0 1px 6px rgba(0,0,0,0.07); margin-bottom:22px; }
    .admin-title { font-size:1.05em; font-weight:700; color:#1f2937; margin-bottom:18px;
                   padding-bottom:12px; border-bottom:1px solid #f3f4f6;
                   display:flex; align-items:center; gap:8px; }
    .admin-title::before { content:''; display:inline-block; width:4px; height:15px;
                            background:#1d4ed8; border-radius:2px; flex-shrink:0; }
    .user-row { display:flex; align-items:center; justify-content:space-between;
                padding:10px 0; border-bottom:1px solid #f9fafb; font-size:0.9em; }
    .user-row:last-child { border-bottom:none; }
    .user-id { font-weight:600; color:#1f2937; }
    .user-badge { background:#eff6ff; color:#1d4ed8; font-size:0.75em;
                  padding:2px 8px; border-radius:12px; font-weight:600; margin-left:8px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="admin-wrap">', unsafe_allow_html=True)

    # ── 가입 승인 대기 섹션 ──
    pending = load_pending()
    if pending:
        st.markdown(f'<div class="admin-section"><div class="admin-title">🔔 가입 승인 대기 ({len(pending)}건)</div>', unsafe_allow_html=True)
        st.markdown("""
        <style>
        .pending-row { display:flex; align-items:center; gap:8px; padding:10px 0;
                       border-bottom:1px solid #f3f4f6; font-size:0.88em; }
        .pending-row:last-child { border-bottom:none; }
        .pending-info { flex:1; }
        .pending-name { font-weight:700; color:#1f2937; }
        .pending-meta { color:#6b7280; font-size:0.85em; margin-top:2px; }
        .pending-uid { display:inline-block; background:#f3f4f6; border-radius:4px;
                       padding:1px 7px; font-size:0.9em; font-family:monospace; color:#374151; }
        </style>
        """, unsafe_allow_html=True)

        approved_ids = []
        rejected_ids = []
        for req in pending:
            cols = st.columns([4, 1, 1])
            cols[0].markdown(
                f'<div class="pending-info">'
                f'<span class="pending-name">{req["name"]}</span>'
                f' <span class="pending-meta">| {req["department"]}</span>'
                f'<div style="margin-top:4px;"><span class="pending-uid">{req["username"]}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if cols[1].button("승인", key=f"approve_{req['id']}", type="primary"):
                approved_ids.append(req["id"])
            if cols[2].button("거절", key=f"reject_{req['id']}", type="secondary"):
                rejected_ids.append(req["id"])

        if approved_ids:
            current_users_now = load_users()
            secrets_users = dict(st.secrets.get("users", {}))
            new_pending = []
            for req in pending:
                if req["id"] in approved_ids:
                    current_users_now[req["username"]] = req["password"]
                else:
                    new_pending.append(req)
            override = {k: v for k, v in current_users_now.items()
                        if k not in secrets_users or secrets_users[k] != v}
            save_users(override)
            save_pending(new_pending)
            st.success("승인 처리되었습니다.")
            st.rerun()

        if rejected_ids:
            new_pending = [req for req in pending if req["id"] not in rejected_ids]
            save_pending(new_pending)
            st.warning("거절 처리되었습니다.")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="admin-section"><div class="admin-title">⚙️ 통합관리시스템 — 계정 관리</div>', unsafe_allow_html=True)

    current_users = load_users()

    # 사용자 목록
    st.markdown("**현재 등록된 계정**")
    for uid, pw in current_users.items():
        cols = st.columns([3, 1])
        badge = '<span class="user-badge">관리자</span>' if uid == ADMIN_USER else ''
        cols[0].markdown(f'<div class="user-id">{uid}{badge}</div>', unsafe_allow_html=True)
        if uid != ADMIN_USER:
            if cols[1].button("삭제", key=f"del_{uid}", type="secondary"):
                del current_users[uid]
                save_users({k: v for k, v in current_users.items()
                            if k not in dict(st.secrets.get("users", {}))})
                st.success(f"'{uid}' 계정이 삭제되었습니다.")
                st.rerun()
        else:
            cols[1].markdown('<span style="color:#9ca3af;font-size:0.8em;">삭제 불가</span>', unsafe_allow_html=True)

    st.markdown("---")

    # 새 계정 추가
    st.markdown("**새 계정 추가**")
    c1, c2, c3 = st.columns([2, 2, 1])
    new_id = c1.text_input("아이디", placeholder="새 아이디", label_visibility="collapsed", key="new_uid")
    new_pw = c2.text_input("패스워드", placeholder="패스워드", label_visibility="collapsed",
                           type="password", key="new_pw")
    if c3.button("추가", type="primary", use_container_width=True):
        if not new_id.strip():
            st.warning("아이디를 입력하세요.")
        elif new_id in current_users:
            st.warning(f"'{new_id}' 아이디가 이미 존재합니다.")
        elif not new_pw.strip():
            st.warning("패스워드를 입력하세요.")
        else:
            current_users[new_id] = new_pw
            secrets_users = dict(st.secrets.get("users", {}))
            override = {k: v for k, v in current_users.items() if k not in secrets_users or secrets_users[k] != v}
            save_users(override)
            st.success(f"'{new_id}' 계정이 추가되었습니다.")
            st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

