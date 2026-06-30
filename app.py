import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64, os, json, uuid
from data_loader import get_available_years, get_available_months, load_factory_data, load_overview, load_sijangbyul_raw

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
    st.session_state["page"] = "건재손익_요약2"
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
    "건재손익": ["건재손익_요약2", "건재손익_요약", "건재손익_부문별", "건재손익_사업장별"],
    "레미콘":   ["레미콘_손익요약", "레미콘_공장별", "레미콘_공헌이익"],
    "건자재":   ["건자재_손익요약", "건자재_손익"],
    "골재":     ["골재_손익요약", "골재_손익"],
    "임대":     ["임대_손익요약", "임대_손익"],
}
PAGE_LABELS = {
    "건재손익_요약":   "지표 추이",
    "건재손익_요약2":  "요약",
    "건재손익_부문별":  "사업부문별",
    "건재손익_사업장별": "사업장별",
    "건재손익_총괄":   "손익 총괄",
    "건재손익_공장별": "공장별 손익",
    "레미콘_손익요약": "요약",
    "레미콘_공헌이익": "공헌이익 분석",
    "레미콘_공장별":   "공장별 손익",
    "건자재_손익요약": "요약",
    "건자재_손익":    "건자재 손익",
    "골재_손익요약":  "요약",
    "골재_손익":      "골재 손익",
    "임대_손익요약":  "요약",
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
table.pl-table tbody td {{ padding:9px 13px; text-align:right; border-bottom:none; color:#374151; white-space:nowrap; }}
table.pl-table tbody td:first-child {{ text-align:center; font-weight:700; color:#1f2937; }}
table.pl-table tbody tr:hover td {{ background:#fafbff; }}
table.pl-table tbody tr.total td {{ background:#eff6ff; font-weight:900; color:#1d4ed8; }}
.pos {{ color:#16a34a !important; font-weight:700; }}
.neg {{ color:#dc2626 !important; font-weight:700; }}
[data-testid="stSelectbox"] label {{ display:none !important; }}
[data-testid="stSelectbox"] > div > div {{ background:#ffffff !important; border-color:#d1d5db !important; }}
</style>

<div class="top-nav">
    <a class="nav-logo" href="{nav_href('건재손익_요약2')}" target="_self">{logo_html}</a>
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

    _pages_with_own_header = ("건재손익_요약", "건재손익_요약2", "건재손익_부문별", "건재손익_사업장별", "ADMIN_PAGE",
                               "레미콘_손익요약", "건자재_손익요약", "골재_손익요약", "임대_손익요약")
    if current_page not in _pages_with_own_header:
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

def _is_money_unit(unit):
    """% 계열이 아닌 금액/물량 단위 여부."""
    return "%" not in unit

def fmt_money_val(val, unit):
    """음수 금액을 (3) 빨간색 HTML로, 양수는 검정 그대로. % 단위는 변환 안 함."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "-", "#111827"
    if not _is_money_unit(unit):
        return f(val), "#111827"
    if val < 0:
        disp = f"({f(abs(val))})"
        return disp, "#dc2626"
    return f(val), "#111827"

def kpi(label, value, unit, delta=None, dl="계획대비", color=""):
    ds = ""
    if delta is not None and not (isinstance(delta, float) and pd.isna(delta)):
        arrow = "▲" if delta>=0 else "▼"; cls = "pos" if delta>=0 else "neg"
        ds = f'<div class="kpi-delta {cls}">{arrow} {f(abs(delta))}<span class="kpi-delta-sub"> vs {dl}</span></div>'
    return f'<div class="kpi-card {color}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}<span class="kpi-unit"> {unit}</span></div>{ds}</div>'

C = {"계획":"#93c5fd","실적":"#1d4ed8","전년":"#f87171","pos":"#1d4ed8","neg":"#dc2626"}

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
            orientation='h', x=0.5, y=1.12, xanchor='center', yanchor='top',
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

def kpi_spark(col, label, value_str, unit, delta, color, trend_df, pcol, acol, actual_val=None, plan_val=None):
    """KPI 헤더 + 스파크라인을 하나의 카드처럼 렌더링."""
    border = {"amber":"#d97706","green":"#16a34a","red":"#dc2626","purple":"#7c3aed"}.get(color,"#1d4ed8")
    # 음수 금액 표시 변환
    try:
        _sv_num = float(str(value_str).replace(",", ""))
        _sv_disp, _sv_color = fmt_money_val(_sv_num, unit)
    except Exception:
        _sv_disp, _sv_color = value_str, "#111827"
    ds = ""
    if delta is not None and not (isinstance(delta, float) and pd.isna(delta)):
        arrow = "▲" if delta>=0 else "▼"; cls = "pos" if delta>=0 else "neg"
        pct_str = ""
        try:
            if actual_val is not None and plan_val is not None and plan_val != 0 \
               and not pd.isna(actual_val) and not pd.isna(plan_val):
                ratio = actual_val / plan_val * 100
                pct_str = f', {ratio:.1f}%'
        except Exception:
            pass
        ds = f'<span class="kpi-delta {cls}" style="font-size:1.0em;font-weight:700;margin-left:8px;white-space:nowrap;flex-shrink:0;">(계획대비 {arrow} {f(abs(delta))}{pct_str})</span>'
    with col:
        # 상단 숫자 박스
        st.markdown(f"""
        <div style="background:white;border-radius:10px;padding:18px 20px 16px;
                    border-top:4px solid {border};
                    border:1px solid #e5e7eb;border-top:4px solid {border};
                    box-shadow:0 1px 6px rgba(0,0,0,0.06);margin-bottom:8px;">
            <div style="font-size:1.3em;font-weight:900;color:white;background:{border};display:inline-block;padding:3px 12px;border-radius:6px;margin-bottom:12px;letter-spacing:0.02em;">{label}</div>
            <div style="display:flex;align-items:baseline;flex-wrap:nowrap;gap:0;overflow:hidden;">
                <div class="kpi-value" style="flex-shrink:1;min-width:0;color:{_sv_color};">{_sv_disp}<span class="kpi-unit"> {unit}</span></div>
                {ds}
            </div>
        </div>
        """, unsafe_allow_html=True)
        # 하단 그래프 박스
        fig = spark(trend_df, pcol, acol)
        if fig:
            st.markdown("""
            <div style="background:white;border-radius:10px;border:1px solid #e5e7eb;
                        box-shadow:0 1px 6px rgba(0,0,0,0.06);overflow:hidden;padding:4px 0 0;">
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

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

def _page_header(title, show_period=False, period_key="sel_period"):
    """모든 페이지 공통 헤더: 제목(좌) + 연/월(/기간) 필터(우)"""
    _period_sfx = ""
    if show_period:
        _p = st.session_state.get(period_key, "당월")
        _period_sfx = "" if _p == "당월" else " 누계"
    _tc, _rc = st.columns([0.76, 0.24], gap="small")
    with _tc:
        st.markdown(
            '<div style="padding:2px 0 0;display:flex;align-items:center;gap:12px;">'
            '<div style="width:4px;height:24px;background:#1d4ed8;border-radius:2px;flex-shrink:0;"></div>'
            '<span style="font-size:1.7em;font-weight:900;color:#1f2937;">' + title + '</span>'
            '<span style="background:#eff6ff;color:#1d4ed8;padding:4px 16px;border-radius:20px;'
            'font-size:1.7em;font-weight:600;">'
            + str(selected_year) + '년 ' + str(selected_month) + '월' + _period_sfx +
            '</span></div>',
            unsafe_allow_html=True
        )
    with _rc:
        if show_period:
            _cy, _cm, _cp = st.columns([1,1,1], gap="small")
        else:
            _cy, _cm = st.columns([1,1], gap="small")
        with _cy:
            st.markdown('<div style="padding-top:14px;">', unsafe_allow_html=True)
            st.selectbox("연도", years, key="sel_year", format_func=lambda x: f"{x}년", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
        with _cm:
            st.markdown('<div style="padding-top:14px;">', unsafe_allow_html=True)
            _pm = get_available_months(selected_year)
            st.selectbox("월", _pm, format_func=lambda x: f"{x}월", key="sel_month", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
        if show_period:
            with _cp:
                st.markdown('<div style="padding-top:14px;">', unsafe_allow_html=True)
                st.selectbox("기간", ["당월", "누계"], key=period_key, label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)

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
    _page_header("건재사업본부 손익 요약", show_period=True)
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

        # 스파크라인용 억원 단위 컬럼 추가
        if trend_df is not None and not trend_df.empty:
            for col_name in ['매출_계획','매출_실적','영업이익_계획','영업이익_실적']:
                if col_name in trend_df.columns:
                    trend_df[col_name + '_억'] = trend_df[col_name] / 100

        if rc_row_ov is not None:
            kpi_spark(c1, "레미콘 판매량",
                      f(rc_row_ov.get(_ov_col('물량','실적')), 1), "천㎥",
                      rc_row_ov.get(_ov_col('물량','차이')), "amber",
                      trend_df, "판매량_계획", "판매량_실적",
                      actual_val=rc_row_ov.get(_ov_col('물량','실적')),
                      plan_val=rc_row_ov.get(_ov_col('물량','계획')))

        if _kpi_total is not None:
            _매출실적 = _kpi_total.get(_ov_col('매출','실적'))
            _매출차이 = _kpi_total.get(_ov_col('매출','차이'))
            _oi실적   = _kpi_total.get(_ov_col('영업이익','실적'))
            _oi차이   = _kpi_total.get(_ov_col('영업이익','차이'))

            def to억(v):
                if v is None or (isinstance(v, float) and pd.isna(v)): return None
                return v / 100

            kpi_spark(c2, "매출액",
                      f(to억(_매출실적), 1), "억원",
                      to억(_매출차이), "",
                      trend_df, "매출_계획_억", "매출_실적_억")
            kpi_spark(c3, "영업이익",
                      f(to억(_oi실적), 1), "억원",
                      to억(_oi차이),
                      "green" if (_oi실적 or 0)>=0 else "red",
                      trend_df, "영업이익_계획_억", "영업이익_실적_억")

        _rc_detail_kpi = rc_detail
        if _sfx:
            _df_all_누계 = load_factory_data(selected_year, selected_month, period="누계")
            if _df_all_누계 is not None:
                _match = _df_all_누계[_df_all_누계['공장명']=='레미콘 계']
                if not _match.empty:
                    _rc_detail_kpi = _match.iloc[0]

        if _rc_detail_kpi is not None:
            _공헌실적 = _rc_detail_kpi.get('공헌이익_실적')
            _공헌계획 = _rc_detail_kpi.get('공헌이익_계획')
            kpi_spark(c4, "공헌이익",
                      f(_공헌실적), "원/㎥",
                      _공헌실적-_공헌계획 if pd.notna(_공헌계획) and _공헌실적 is not None else None,
                      "green" if (_공헌실적 or 0)>=0 else "red",
                      trend_df, "공헌이익_계획", "공헌이익_실적")


    else:
        st.error("손익총괄 데이터를 불러올 수 없습니다.")

    st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "건재손익_요약2":
    if "sel_period" not in st.session_state:
        st.session_state["sel_period"] = "당월"
    st.markdown("""<style>
    div[data-testid="stColumn"]:has(> div > div > div[data-testid="stSelectbox"]) {
        padding-left: 2px !important; padding-right: 2px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] > div > div > div[data-testid="stSelectbox"]) {
        gap: 4px !important;
    }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    </style>""", unsafe_allow_html=True)

    # ── 헤더 ──
    _page_header("건재사업본부 손익 요약", show_period=True)
    _r2_period = st.session_state.get("sel_period", "당월")
    _r2_sfx = "누계" if _r2_period == "누계" else ""

    @st.cache_data(ttl=600)
    def _get_ov_r2(year, month):
        return load_overview(year, month)

    df_ov2 = _get_ov_r2(selected_year, selected_month)

    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    if df_ov2 is None:
        st.error("데이터를 불러올 수 없습니다.")
    else:
        def _p2(col): return col + ('_누계계획' if _r2_sfx else '_계획')
        def _r2c(col): return col + ('_누계실적' if _r2_sfx else '_실적')
        def _d2(col): return col + ('_누계차이' if _r2_sfx else '_차이')
        def _py2(col): return col + ('_누계전년' if _r2_sfx else '_전년')

        tot2 = df_ov2[df_ov2['구분']=='합계'].iloc[0] if not df_ov2[df_ov2['구분']=='합계'].empty else None
        rc2  = df_ov2[df_ov2['구분']=='레미콘'].iloc[0] if not df_ov2[df_ov2['구분']=='레미콘'].empty else None

        def _v2(row, col):
            if row is None: return None
            v = row.get(col)
            return None if v is None or (isinstance(v, float) and pd.isna(v)) else v

        # ══ 공헌이익 데이터 (레미콘 계) ══
        @st.cache_data(ttl=600)
        def _get_sij_r2(year, month, period):
            return load_sijangbyul_raw(year, month, period)
        _sij_rows = _get_sij_r2(selected_year, selected_month, _r2_period if _r2_period else "당월")
        _rc_sij = next((r for r in _sij_rows if r.get('구분') == '레미콘 계'), None)
        공헌이익실적 = _rc_sij.get('공헌이익_실적') if _rc_sij else None
        공헌이익계획 = _rc_sij.get('공헌이익_계획') if _rc_sij else None
        공헌이익차이 = (공헌이익실적 - 공헌이익계획) if 공헌이익실적 is not None and 공헌이익계획 is not None else None
        공헌이익달성 = (공헌이익실적/공헌이익계획*100) if 공헌이익실적 and 공헌이익계획 else 0

        # ══ 1. 상단 KPI 4개 ══════════════════════════════════════
        매출실적  = _v2(tot2, _r2c('매출'))
        매출계획  = _v2(tot2, _p2('매출'))
        매출차이  = _v2(tot2, _d2('매출'))
        매출전년  = _v2(tot2, _py2('매출'))
        oi실적    = _v2(tot2, _r2c('영업이익'))
        oi계획    = _v2(tot2, _p2('영업이익'))
        oi차이    = _v2(tot2, _d2('영업이익'))
        oi전년    = _v2(tot2, _py2('영업이익'))
        rc물량실적 = _v2(rc2, _r2c('물량'))
        rc물량계획 = _v2(rc2, _p2('물량'))
        rc물량차이 = _v2(rc2, _d2('물량'))

        def _to억(v): return v/100 if v is not None else None
        def _pct(a, b): return f"{a/b*100:.1f}%" if a and b and b!=0 else "-"
        def _diff_badge(val, unit="백만원", per=False):
            if val is None: return ""
            color = "#1d4ed8" if val >= 0 else "#dc2626"
            arrow = "▲" if val >= 0 else "▼"
            disp = f"{abs(val):,.1f}" if per else f"{abs(int(val)):,}"
            return f'<span style="font-size:0.75em;color:{color};font-weight:700;">{arrow} {disp} {unit}</span>'

        oi율실적 = (oi실적/매출실적*100) if oi실적 and 매출실적 else None
        oi율계획 = (oi계획/매출계획*100) if oi계획 and 매출계획 else None
        oi율차이 = (oi율실적 - oi율계획) if oi율실적 is not None and oi율계획 is not None else None

        매출달성 = (매출실적/매출계획*100) if 매출실적 and 매출계획 else None
        oi달성   = (oi실적/oi계획*100) if oi실적 and oi계획 else None

        def _kpi2(title, value_str, unit, sub_html, bar_pct, bar_color, icon):
            pct_clamp = min(max(bar_pct or 0, 0), 100)
            return f"""
            <div style="background:white;border-radius:12px;padding:18px 20px 16px;
                        border-top:4px solid {bar_color};box-shadow:0 2px 10px rgba(0,0,0,0.07);height:100%;">
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <span style="font-size:0.82em;font-weight:700;color:#6b7280;letter-spacing:0.03em;">{title}</span>
                <span style="font-size:1.3em;">{icon}</span>
              </div>
              <div style="font-size:2.0em;font-weight:900;color:#111827;line-height:1.1;margin-bottom:4px;">
                {value_str}<span style="font-size:0.38em;font-weight:500;color:#9ca3af;margin-left:4px;">{unit}</span>
              </div>
              <div style="margin-bottom:10px;min-height:20px;">{sub_html}</div>
              <div style="background:#f3f4f6;border-radius:99px;height:6px;overflow:hidden;">
                <div style="width:{pct_clamp}%;height:100%;background:{bar_color};border-radius:99px;transition:width 0.4s;"></div>
              </div>
              <div style="font-size:0.72em;color:#9ca3af;margin-top:4px;">계획 달성률 {bar_pct:.1f}%</div>
            </div>"""

        # ══ 공통 헬퍼 ═══════════════════════════════════════════
        rc달성  = (rc물량실적/rc물량계획*100) if rc물량실적 and rc물량계획 else 0

        def _ac(pct):
            return "#1d4ed8" if pct >= 100 else "#dc2626"

        def _bw(pct): return str(int(min(max(pct, 0), 100)))

        def _dv(val, unit, per=False):
            """차이 문자열 (HTML)"""
            if val is None: return ""
            c = "#dc2626" if val < 0 else "#1d4ed8"
            a = "▲" if val >= 0 else "▼"
            s = f"{abs(int(round(val))):,}" + " " + unit
            return '<span style="font-size:0.78em;font-weight:600;color:#9ca3af;">계획대비 </span><span style="font-size:0.78em;font-weight:600;color:' + c + ';">' + a + " " + s + '</span>'

        # ══ 1-A. KPI 4개 — 한 줄 HTML 블록 ══════════════════════
        _DIVS = ['레미콘','골재','건자재','기타']
        _DIV_COLORS = {'레미콘':'#1d4ed8','골재':'#0891b2','건자재':'#059669','기타':'#7c3aed'}
        df_div2 = df_ov2[df_ov2['구분'].isin(_DIVS)].set_index('구분')

        _oir_pct = min((oi율실적/(oi율계획)*100) if oi율실적 and oi율계획 else 0, 150)

        def _kpi_card(col, label, val_str, unit, diff_html, pct):
            ac = _ac(pct); bw = _bw(pct)
            # 마이너스 금액: (3) 빨간색 / % 단위는 원본 유지
            try:
                _num = float(val_str.replace(",", ""))
                _disp, _val_color = fmt_money_val(_num, unit)
            except Exception:
                _disp, _val_color = val_str, "#111827"
            with col:
                st.markdown(
                    '<div style="background:white;border-radius:12px;border:1px solid #e8eaed;'
                    'box-shadow:0 1px 4px rgba(0,0,0,0.06);overflow:hidden;">'
                    '<div style="background:#f8fafc;border-bottom:1px solid #e8eaed;'
                    'padding:14px 20px;text-align:center;">'
                    '<span style="font-size:1.25em;font-weight:700;color:#374151;">' + label + '</span>'
                    '</div>'
                    '<div style="padding:18px 20px 18px;text-align:left;">'
                    '<div style="display:flex;align-items:baseline;flex-wrap:wrap;gap:6px;">'
                    '<span style="font-size:2.3em;font-weight:900;color:' + _val_color + ';line-height:1.1;">' + _disp
                    + '<span style="font-size:0.32em;font-weight:500;color:#9ca3af;margin-left:6px;">' + unit + '</span></span>'
                    + ('<span style="font-size:1.1em;font-weight:600;color:#6b7280;">(' + diff_html + ')</span>' if diff_html else '')
                    + '</div>'
                    '<div style="margin-top:12px;background:#f3f4f6;border-radius:99px;height:5px;">'
                    '<div style="width:' + bw + '%;height:100%;background:' + ac + ';border-radius:99px;"></div></div>'
                    '<div style="font-size:0.9em;color:' + ac + ';font-weight:600;margin-top:5px;">달성률 ' + f'{pct:.1f}%' + '</div>'
                    '</div></div>',
                    unsafe_allow_html=True
                )

        st.markdown("""<style>
        div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(5)) {
            gap: 2px !important;
        }
        </style>""", unsafe_allow_html=True)
        _kc1, _kc2, _kc3, _kc4, _kc5 = st.columns([1.25, 1.1, 1.1, 1.1, 1.35], gap="small")
        _kpi_card(_kc1, "레미콘 판매량",
                  f"{rc물량실적:,.0f}" if rc물량실적 else "-", "천㎥",
                  _dv(rc물량차이, "천㎥"), rc달성)
        _kpi_card(_kc2, "매출액",
                  f"{_to억(매출실적):,.0f}" if 매출실적 else "-", "억원",
                  _dv(_to억(매출차이), "억원"), 매출달성 or 0)
        _kpi_card(_kc3, "영업이익",
                  f"{_to억(oi실적):,.0f}" if oi실적 is not None else "-", "억원",
                  _dv(_to억(oi차이), "억원"), oi달성 or 0)
        _kpi_card(_kc4, "영업이익률",
                  f"{oi율실적:.0f}" if oi율실적 is not None else "-", "%",
                  _dv(oi율차이, "%p"), _oir_pct)
        _kpi_card(_kc5, "공헌이익 (레미콘)",
                  f"{공헌이익실적:,.0f}" if 공헌이익실적 is not None else "-", "원/㎥",
                  _dv(공헌이익차이, "원/㎥"), 공헌이익달성)
        st.markdown('<div style="margin-bottom:48px;"></div>', unsafe_allow_html=True)

        # ══ 2. 레미콘 판매량 (권역별) + 부문별 매출/영업이익 ══════════
        left_col, right_col = st.columns([1, 1.6], gap="medium")

        # ── 좌: 레미콘 판매량 권역별 계획 vs 실적 ──────────────────────
        with left_col:
            st.markdown(
                '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
                '<div style="display:flex;align-items:center;gap:8px;">'
                '<div style="width:4px;height:16px;background:#1d4ed8;border-radius:2px;"></div>'
                '<span style="font-size:1.3em;font-weight:700;color:#1f2937;">권역별 판매량</span>'
                '</div>'
                '<span style="font-size:0.85em;color:#9ca3af;">(단위 : 천㎥)</span>'
                '</div>', unsafe_allow_html=True)

            _REGIONS = ['수도권', '영남권', '중부권']
            _rg_plans, _rg_actuals, _rg_diffs, _rg_pcts = [], [], [], []
            for _rg in _REGIONS:
                _rg_row = next((r for r in _sij_rows if r.get('구분') == _rg), None)
                _rp = (_rg_row.get('물량_계획') or 0) if _rg_row else 0
                _rr = (_rg_row.get('물량_실적') or 0) if _rg_row else 0
                _rg_plans.append(_rp)
                _rg_actuals.append(_rr)
                _rg_diffs.append(_rr - _rp)
                _rg_pcts.append((_rr/_rp*100) if _rp else 0)

            _actual_colors = ['#dc2626' if p < 100 else '#1d4ed8' for p in _rg_pcts]
            _diff_texts = [
                f"{'▲' if d>=0 else '▼'} {abs(int(round(d))):,} 천㎥  ({p:.1f}%)"
                for d, p in zip(_rg_diffs, _rg_pcts)
            ]

            _fig_rg = go.Figure()
            _fig_rg.add_trace(go.Bar(
                name='계획', x=_REGIONS, y=_rg_plans,
                marker_color='#bfdbfe', marker_line_width=0,
                text=[f"{int(round(v)):,}" for v in _rg_plans],
                textposition='outside', textfont=dict(size=14, color='#6b7280'),
                hovertemplate='계획: <b>%{y:,}</b> 천㎥<extra></extra>',
            ))
            _fig_rg.add_trace(go.Bar(
                name='실적', x=_REGIONS, y=_rg_actuals,
                marker_color=_actual_colors, marker_line_width=0,
                text=["" for _ in _rg_actuals],
                customdata=_diff_texts,
                hovertemplate='실적: <b>%{y:,}</b> 천㎥<br>%{customdata}<extra></extra>',
            ))
            _fig_rg.update_layout(
                barmode='group', bargap=0.35, bargroupgap=0.08,
                yaxis=dict(showgrid=True, gridcolor='#f3f4f6', zeroline=False,
                           tickfont=dict(size=11), title='', showticklabels=False),
                xaxis=dict(showgrid=False, tickfont=dict(size=14, family='Noto Sans KR')),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5, font=dict(size=14)),
                margin=dict(t=36, b=8, l=8, r=8), height=300,
                paper_bgcolor='white', plot_bgcolor='white',
                font=dict(family='Noto Sans KR'),
            )
            # 실적 숫자 — 연한 배경 + 중앙 정렬 annotation
            # grouped bar(2개)에서 실적(오른쪽) 막대 중심 = 카테고리 index + ~0.175
            # bargap=0.35, bargroupgap=0.08 기준 계산값
            _actual_x_offsets = [i + 0.175 for i in range(len(_REGIONS))]
            for _xi, _rr, _ac, _pct in zip(_actual_x_offsets, _rg_actuals, _actual_colors, _rg_pcts):
                _bg = '#fecaca' if _ac == '#dc2626' else '#bfdbfe'
                _fc = '#dc2626' if _ac == '#dc2626' else '#1d4ed8'
                # % 라벨 — 배경 없음
                _fig_rg.add_annotation(
                    x=_xi, y=_rr, xref='x', yref='y',
                    xshift=0, yshift=44,
                    xanchor='center',
                    text=f"({_pct:.0f}%)",
                    showarrow=False,
                    font=dict(size=12, color=_fc, family='Noto Sans KR'),
                    bgcolor='rgba(0,0,0,0)', borderpad=2, borderwidth=0,
                    opacity=1,
                )
                # 실적 숫자 — 연한 배경
                _fig_rg.add_annotation(
                    x=_xi, y=_rr, xref='x', yref='y',
                    xshift=0, yshift=16,
                    xanchor='center',
                    text=f"<b>{int(round(_rr)):,}</b>",
                    showarrow=False,
                    font=dict(size=17, color=_fc, family='Noto Sans KR'),
                    bgcolor=_bg, borderpad=4, borderwidth=0,
                    opacity=1,
                )
            st.markdown('<div style="background:white;border-radius:10px;border:1px solid #e8eaed;box-shadow:0 1px 4px rgba(0,0,0,0.05);padding:4px 0 0;">', unsafe_allow_html=True)
            st.plotly_chart(_fig_rg, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 우: 부문별 매출액 / 영업이익 차이 ────────────────────────────
        with right_col:
            st.markdown(
                '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">'
                '<div style="display:flex;align-items:center;gap:8px;">'
                '<div style="width:4px;height:16px;background:#7c3aed;border-radius:2px;"></div>'
                '<span style="font-size:1.3em;font-weight:700;color:#1f2937;">부문별 손익</span>'
                '</div>'
                '<span style="font-size:0.85em;color:#9ca3af;">(단위 : 백만원)</span>'
                '</div>', unsafe_allow_html=True)

            _DIVS2 = ['레미콘', '건자재', '골재', '임대', '기타']
            _DIV_C2 = {'레미콘':'#1d4ed8','건자재':'#059669','골재':'#0891b2','임대':'#d97706','기타':'#7c3aed'}

            _df_div3 = df_ov2[df_ov2['구분'].isin(_DIVS2)].set_index('구분') if df_ov2 is not None else None

            if _df_div3 is not None:
                _s_pcts, _o_pcts, _s_diffs, _o_diffs = [], [], [], []
                _valid_divs = []
                for _dn in _DIVS2:
                    if _dn not in _df_div3.index:
                        continue
                    _row3 = _df_div3.loc[_dn]
                    _sp3 = _row3.get(_p2('매출')) or 0
                    _sr3 = _row3.get(_r2c('매출')) or 0
                    _op3 = _row3.get(_p2('영업이익')) or 0
                    _or3 = _row3.get(_r2c('영업이익'))
                    _s_pcts.append((_sr3/_sp3*100) if _sp3 else 0)
                    _s_diffs.append(_sr3 - _sp3)
                    _o_pcts.append((_or3/_op3*100) if _op3 and _or3 is not None else 0)
                    _o_diffs.append((_or3 - _op3) if _or3 is not None else 0)
                    _valid_divs.append(_dn)

                def _make_hbar(divs, pcts, diffs, title):
                    colors = ['#1d4ed8' if p >= 100 else '#dc2626' for p in pcts]
                    diff_texts = [
                        f"{'▲' if d>=0 else '▼'} {abs(int(round(d))):,}  <b>{p:.0f}%</b>"
                        for d, p in zip(diffs, pcts)
                    ]
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=pcts, y=divs, orientation='h',
                        marker_color=colors, marker_line_width=0,
                        text=[f"  {p:.0f}%" for p in pcts],
                        textposition='outside',
                        textfont=dict(size=13, family='Noto Sans KR'),
                        customdata=diff_texts,
                        hovertemplate='%{customdata}<extra></extra>',
                    ))
                    fig.add_vline(x=100, line_color='#9ca3af', line_width=1.5, line_dash='dash')
                    fig.update_layout(
                        title=dict(text=title, font=dict(size=13, color='#6b7280', family='Noto Sans KR'), x=0.5, xanchor='center'),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, max(max(pcts)*1.25, 120)]),
                        yaxis=dict(showgrid=False, tickfont=dict(size=13, family='Noto Sans KR', color='#374151'), autorange='reversed'),
                        margin=dict(t=36, b=8, l=8, r=48), height=220,
                        paper_bgcolor='white', plot_bgcolor='white',
                        showlegend=False,
                        font=dict(family='Noto Sans KR'),
                    )
                    return fig

                _ch1, _ch2 = st.columns(2, gap="small")
                with _ch1:
                    st.markdown(
                        '<div style="background:white;border-radius:12px;border:1px solid #e8eaed;'
                        'box-shadow:0 1px 4px rgba(0,0,0,0.06);overflow:hidden;">'
                        '<div style="background:#f8fafc;border-bottom:1px solid #e8eaed;'
                        'padding:12px 20px;text-align:center;">'
                        '<span style="font-size:1.1em;font-weight:700;color:#374151;">매출액 달성률</span>'
                        '</div>', unsafe_allow_html=True)
                    st.plotly_chart(_make_hbar(_valid_divs, _s_pcts, _s_diffs, ''),
                                    use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)
                with _ch2:
                    st.markdown(
                        '<div style="background:white;border-radius:12px;border:1px solid #e8eaed;'
                        'box-shadow:0 1px 4px rgba(0,0,0,0.06);overflow:hidden;">'
                        '<div style="background:#f8fafc;border-bottom:1px solid #e8eaed;'
                        'padding:12px 20px;text-align:center;">'
                        '<span style="font-size:1.1em;font-weight:700;color:#374151;">영업이익 달성률</span>'
                        '</div>', unsafe_allow_html=True)
                    st.plotly_chart(_make_hbar(_valid_divs, _o_pcts, _o_diffs, ''),
                                    use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="margin-bottom:40px;"></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "건재손익_부문별":
    if "sel_period" not in st.session_state:
        st.session_state["sel_period"] = "당월"
    st.markdown("""<style>
    div[data-testid="stColumn"]:has(> div > div > div[data-testid="stSelectbox"]) {
        padding-left: 2px !important; padding-right: 2px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] > div > div > div[data-testid="stSelectbox"]) {
        gap: 4px !important;
    }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    </style>""", unsafe_allow_html=True)
    _page_header("사업부문별 손익", show_period=True)
    _bm_period = st.session_state.get("sel_period", "당월")
    _bm_sfx = "누계" if _bm_period == "누계" else ""
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    @st.cache_data(ttl=600)
    def _get_overview_bm(year, month):
        return load_overview(year, month)

    df_ov_bm = _get_overview_bm(selected_year, selected_month)

    if df_ov_bm is not None:
        _sfx = _bm_sfx
        _p   = lambda col: col + ('_누계계획' if _sfx else '_계획')
        _r   = lambda col: col + ('_누계실적' if _sfx else '_실적')
        _d   = lambda col: col + ('_누계차이' if _sfx else '_차이')

        _divisions   = ['레미콘', '골재', '건자재', '기타']
        _div_colors  = {'레미콘': '#1d4ed8', '골재': '#0891b2', '건자재': '#059669', '기타': '#7c3aed'}
        _df_div = df_ov_bm[df_ov_bm['구분'].isin(_divisions)].set_index('구분')

        # ── 1. KPI 카드 ──────────────────────────────────────────
        _kpi_cols = st.columns(4, gap="small")
        for _i, _dname in enumerate(_divisions):
            if _dname not in _df_div.index:
                continue
            _row = _df_div.loc[_dname]
            _sp = _row.get(_p('매출')); _sr = _row.get(_r('매출'))
            _op = _row.get(_p('영업이익')); _or = _row.get(_r('영업이익'))
            _clr = _div_colors[_dname]

            _ach_val = (_sr / _sp * 100) if (_sp and _sr and _sp != 0) else None
            _ach_str = f"{_ach_val:.0f}%" if _ach_val is not None else "-"
            _ach_clr = "#1d4ed8" if (_ach_val and _ach_val >= 100) else "#dc2626"

            _oi_rate = f"{_or/_sr*100:.1f}%" if (_sr and _or and _sr != 0) else "-"
            _oi_diff = (_or - _op) if (_or is not None and _op is not None) else None
            _oi_diff_str = (f"+{int(_oi_diff):,}" if _oi_diff >= 0 else f"{int(_oi_diff):,}") if _oi_diff is not None else "-"
            _oi_diff_clr = "#1d4ed8" if (_oi_diff is not None and _oi_diff >= 0) else "#dc2626"

            with _kpi_cols[_i]:
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:18px 16px 14px;border-top:4px solid {_clr};box-shadow:0 1px 6px rgba(0,0,0,0.08);height:100%;">
                  <div style="font-size:1.05em;font-weight:800;color:{_clr};margin-bottom:10px;">{_dname}</div>
                  <div style="font-size:0.72em;color:#9ca3af;margin-bottom:2px;">매출 실적</div>
                  <div style="font-size:1.45em;font-weight:800;color:#1f2937;line-height:1.2;">{f"{int(_sr):,}" if _sr else "-"}<span style="font-size:0.45em;font-weight:400;color:#9ca3af;"> 백만원</span></div>
                  <div style="font-size:0.8em;color:{_ach_clr};font-weight:600;margin-bottom:10px;">계획대비 {_ach_str}</div>
                  <div style="height:1px;background:#f3f4f6;margin:8px 0;"></div>
                  <div style="font-size:0.72em;color:#9ca3af;margin-bottom:2px;">영업이익</div>
                  <div style="font-size:1.15em;font-weight:700;color:#1f2937;">{f"{int(_or):,}" if _or is not None else "-"}<span style="font-size:0.45em;font-weight:400;color:#9ca3af;"> 백만원</span></div>
                  <div style="font-size:0.78em;color:{_oi_diff_clr};font-weight:600;">차이 {_oi_diff_str}</div>
                  <div style="font-size:0.72em;color:#9ca3af;">이익률 {_oi_rate}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── 2. 차트 ──────────────────────────────────────────────
        _col_l, _col_r = st.columns([1, 1], gap="small")

        with _col_l:
            _pie_vals, _pie_labels, _pie_colors = [], [], []
            for _dn in _divisions:
                if _dn in _df_div.index:
                    _v = _df_div.loc[_dn, _r('매출')]
                    if _v and _v > 0:
                        _pie_vals.append(_v)
                        _pie_labels.append(_dn)
                        _pie_colors.append(_div_colors[_dn])
            if _pie_vals:
                _fig_pie = go.Figure(go.Pie(
                    labels=_pie_labels, values=_pie_vals, hole=0.58,
                    marker=dict(colors=_pie_colors, line=dict(color='white', width=2)),
                    textinfo='label+percent',
                    textfont=dict(size=13),
                    hovertemplate='<b>%{label}</b><br>%{value:,.0f} 백만원<br>%{percent}<extra></extra>',
                ))
                _fig_pie.update_layout(
                    title=dict(text="매출 구성 비중", font=dict(size=14, color='#1f2937'), x=0.5, xanchor='center'),
                    showlegend=True,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.18, xanchor='center', x=0.5, font=dict(size=12)),
                    margin=dict(t=40, b=50, l=10, r=10), height=300,
                    paper_bgcolor='white', plot_bgcolor='white',
                    annotations=[dict(text=f"매출<br><b>{int(sum(_pie_vals)):,}</b>", x=0.5, y=0.5, font_size=12, showarrow=False, font_color='#374151')]
                )
                st.markdown('<div style="background:white;border-radius:12px;padding:8px 8px 0;box-shadow:0 1px 6px rgba(0,0,0,0.08);">', unsafe_allow_html=True)
                st.plotly_chart(_fig_pie, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)

        with _col_r:
            _bar_names, _bar_plan, _bar_real = [], [], []
            for _dn in _divisions:
                if _dn in _df_div.index:
                    _op2 = _df_div.loc[_dn, _p('영업이익')]
                    _or2 = _df_div.loc[_dn, _r('영업이익')]
                    if _op2 is not None or _or2 is not None:
                        _bar_names.append(_dn)
                        _bar_plan.append(_op2 or 0)
                        _bar_real.append(_or2 or 0)
            if _bar_names:
                _fig_bar = go.Figure()
                _fig_bar.add_trace(go.Bar(
                    name='계획', y=_bar_names, x=_bar_plan, orientation='h',
                    marker_color='#bfdbfe', marker_line_width=0,
                    hovertemplate='계획: <b>%{x:,.0f}</b> 백만원<extra></extra>',
                    text=[f"{int(v):,}" for v in _bar_plan], textposition='inside',
                    textfont=dict(color='#1d4ed8', size=11),
                ))
                _fig_bar.add_trace(go.Bar(
                    name='실적', y=_bar_names, x=_bar_real, orientation='h',
                    marker_color=['#16a34a' if v >= 0 else '#dc2626' for v in _bar_real],
                    marker_line_width=0,
                    hovertemplate='실적: <b>%{x:,.0f}</b> 백만원<extra></extra>',
                    text=[f"{int(v):,}" for v in _bar_real], textposition='inside',
                    textfont=dict(color='white', size=11),
                ))
                _fig_bar.update_layout(
                    title=dict(text="영업이익 계획 vs 실적 (백만원)", font=dict(size=14, color='#1f2937'), x=0.5, xanchor='center'),
                    barmode='group', bargap=0.3, bargroupgap=0.1,
                    xaxis=dict(showgrid=True, gridcolor='#f3f4f6', zeroline=True, zerolinecolor='#9ca3af'),
                    yaxis=dict(showgrid=False),
                    legend=dict(orientation='h', yanchor='bottom', y=-0.18, xanchor='center', x=0.5, font=dict(size=12)),
                    margin=dict(t=40, b=50, l=10, r=20), height=300,
                    paper_bgcolor='white', plot_bgcolor='white',
                )
                st.markdown('<div style="background:white;border-radius:12px;padding:8px 8px 0;box-shadow:0 1px 6px rgba(0,0,0,0.08);">', unsafe_allow_html=True)
                st.plotly_chart(_fig_bar, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── 3. 상세 테이블 ────────────────────────────────────────
        def _oir_bm(sale, oi):
            try:
                return f"{float(oi)/float(sale)*100:.1f}%"
            except:
                return "-"

        def _build_overview_table_bm(df_src, sfx=""):
            _p2 = lambda col: col + ('_누계계획' if sfx else '_계획')
            _r2 = lambda col: col + ('_누계실적' if sfx else '_실적')
            _d2 = lambda col: col + ('_누계차이' if sfx else '_차이')
            html = """<table class="pl-table"><thead>
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
                m_p = row.get(_p2('물량')); m_r = row.get(_r2('물량')); m_d = row.get(_d2('물량'))
                s_p = row.get(_p2('매출')); s_r = row.get(_r2('매출')); s_d = row.get(_d2('매출'))
                o_p = row.get(_p2('영업이익')); o_r = row.get(_r2('영업이익')); o_d = row.get(_d2('영업이익'))
                html += f"""<tr{tc}>
                  <td>{name}</td>
                  <td>{f(m_p,1)}</td><td>{f(m_r,1)}</td>{td_d(m_d,1)}
                  <td>{f(s_p)}</td><td>{f(s_r)}</td>{td_d(s_d)}
                  <td>{f(o_p)}</td><td>{f(o_r)}</td>{td_d(o_d)}
                  <td>{_oir_bm(s_p,o_p)}</td><td>{_oir_bm(s_r,o_r)}</td>
                </tr>"""
            html += "</tbody></table>"
            return html

        st.markdown(_build_overview_table_bm(df_ov_bm, _bm_sfx), unsafe_allow_html=True)
    else:
        st.error("손익총괄 데이터를 불러올 수 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "건재손익_사업장별":
    if "sel_period" not in st.session_state:
        st.session_state["sel_period"] = "당월"
    st.markdown("""<style>
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    </style>""", unsafe_allow_html=True)
    _page_header("사업장별 손익실적", show_period=True)
    _sjb_period = st.session_state.get("sel_period", "당월")
    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    @st.cache_data(ttl=600)
    def _get_sjb_v2(year, month, period):
        return load_sijangbyul_raw(year, month, period)

    _sjb_rows = _get_sjb_v2(selected_year, selected_month, _sjb_period)

    if not _sjb_rows:
        st.warning("데이터를 불러올 수 없습니다.")
    else:
        # ── 행 그룹 정의 ────────────────────────────────────────────
        REMICON_FACTORIES = ['안양','인천','파주','김포','부산','서부산','김해',
                             '정관','양산','창원','대구','울산','아산','전주',
                             '군산','원주','제주']
        REGION_ROWS  = ['수도권','영남권','중부권']
        GOLCHAE_ROWS = ['부산모래장','서부산CR','부산CR']
        GITA_ROWS    = ['레미콘임대','임대','공통비','OPC 소급분','OPC소급분',
                        '대손','미운영 공장','퇴직위로금','기타']

        SUBTOTAL_ROWS  = {'레미콘 계','골재 계','기타 계'}
        TOTAL_ROWS     = {'합계'}
        BOLD_ROWS      = SUBTOTAL_ROWS | TOTAL_ROWS | {'건자재'}

        # 데이터를 dict로 변환 (이름→행, 순서 유지)
        # 합계가 두 번 나올 수 있어 리스트로 유지
        _sjb_by_name = {}
        for r in _sjb_rows:
            nm = r['구분']
            if nm not in _sjb_by_name:
                _sjb_by_name[nm] = r
            else:
                # 두 번째 합계 = 건자재 포함 전체합계 → 별도 키로 저장
                _sjb_by_name[nm + '_전체'] = r

        def _get(name):
            return _sjb_by_name.get(name) or _sjb_by_name.get(name + '_전체') or {}

        # ── HTML 테이블 빌드 ─────────────────────────────────────────
        def _td(v, fmt='int', bold=False, red_neg=True):
            """숫자 셀 반환"""
            if v is None:
                return '<td class="sjb-num"></td>'
            try:
                fv = float(v)
            except Exception:
                return f'<td class="sjb-num"></td>'
            neg = fv < 0
            if fmt == 'int':
                s = f"{abs(int(round(fv))):,}"
            elif fmt == 'dec1':
                s = f"{abs(fv):,.1f}"
            else:
                s = f"{abs(int(round(fv))):,}"
            display = f"({s})" if neg else s
            color = 'color:#dc2626;' if (neg and red_neg) else ''
            fw = 'font-weight:700;' if bold else ''
            return f'<td class="sjb-num" style="{color}{fw}">{display}</td>'

        def _tdiff(v, bold=False):
            return _td(v, 'int', bold, red_neg=True)

        _DIVIDER_ROWS = {'김포', '울산', '제주'}

        def _ge(cell):
            """그룹 마지막 셀에 우측 구분선 추가"""
            return cell.replace('class="sjb-num"', 'class="sjb-num sjb-ge"', 1)

        def _row_html(label, d, style='normal', section_td=''):
            is_bold = style in ('subtotal', 'total', 'grand_total')
            is_divider = label in _DIVIDER_ROWS
            tr_classes = []
            if is_divider:   tr_classes.append('sjb-divider')
            if style == 'region':     tr_classes.append('sjb-region')
            elif style == 'subtotal': tr_classes.append('sjb-subtotal')
            elif style == 'total':    tr_classes.append('sjb-total')
            elif style == 'grand_total': tr_classes.append('sjb-grand')
            tr_cls = f' class="{" ".join(tr_classes)}"' if tr_classes else ''
            fw = 'font-weight:600;' if is_bold else ''
            label_td = f'<td class="sjb-label" style="{fw}">{label}</td>'
            return (
                f'<tr{tr_cls}>'
                + section_td
                + label_td
                + _td(d.get('물량_계획'),    'int', is_bold)
                + _td(d.get('물량_실적'),    'int', is_bold)
                + _tdiff(d.get('물량_차이'), is_bold)
                + _td(d.get('물량_전년'),    'int', is_bold)
                + _ge(_tdiff(d.get('물량_전년차이'), is_bold))
                + _td(d.get('매출_계획'),    'int', is_bold)
                + _td(d.get('매출_실적'),    'int', is_bold)
                + _tdiff(d.get('매출_차이'), is_bold)
                + _td(d.get('매출_전년'),    'int', is_bold)
                + _ge(_tdiff(d.get('매출_전년차이'), is_bold))
                + _td(d.get('영업이익_계획'),'int', is_bold)
                + _td(d.get('영업이익_실적'),'int', is_bold)
                + _tdiff(d.get('영업이익_차이'), is_bold)
                + _td(d.get('영업이익_전년'),'int', is_bold)
                + _ge(_tdiff(d.get('영업이익_전년차이'), is_bold))
                + _td(d.get('판매단가_계획'),'int', is_bold, False)
                + _td(d.get('판매단가_실적'),'int', is_bold, False)
                + _ge(_td(d.get('판매단가_전년'),'int', is_bold, False))
                + _td(d.get('변동비_계획'),  'int', is_bold, False)
                + _td(d.get('변동비_실적'),  'int', is_bold, False)
                + _ge(_td(d.get('변동비_전년'),  'int', is_bold, False))
                + _td(d.get('공헌이익_계획'),'int', is_bold)
                + _td(d.get('공헌이익_실적'),'int', is_bold)
                + _td(d.get('공헌이익_전년'), 'int', is_bold)
                + '</tr>'
            )

        # 섹션 셀 (rowspan)
        remicon_count = len(REMICON_FACTORIES) + len(REGION_ROWS) + 1  # +1 for 레미콘 계
        golchae_count = len([r for r in _sjb_rows if r['구분'] in set(GOLCHAE_ROWS) or r['구분'] == '골재 계'])
        gita_count    = len([r for r in _sjb_rows if r['구분'] in set(GITA_ROWS) | {'기타 계'}])

        rows_html = []

        # 레미콘 섹션
        first = True
        for i, nm in enumerate(REMICON_FACTORIES):
            d = _get(nm)
            if first:
                sec_td = f'<td class="sjb-sec" rowspan="{remicon_count}" style="color:#1d4ed8;font-weight:700;">레미콘</td>'
                first = False
            else:
                sec_td = ''
            rows_html.append(_row_html(nm, d, 'normal', sec_td))

        for nm in REGION_ROWS:
            d = _get(nm)
            rows_html.append(_row_html(nm, d, 'region', ''))

        d = _get('레미콘 계')
        rows_html.append(_row_html('레미콘 계', d, 'subtotal', ''))

        # 골재 섹션
        golchae_names_found = [r['구분'] for r in _sjb_rows if r['구분'] in set(GOLCHAE_ROWS) | {'골재 계'}]
        for i, nm in enumerate(golchae_names_found):
            d = _get(nm)
            sec_td = f'<td class="sjb-sec" rowspan="{len(golchae_names_found)}" style="color:#16a34a;font-weight:700;">골재</td>' if i == 0 else ''
            style = 'subtotal' if nm == '골재 계' else 'normal'
            rows_html.append(_row_html(nm, d, style, sec_td))

        if not golchae_names_found:
            d = _get('골재 계')
            rows_html.append(_row_html('골재 계', d, 'subtotal',
                '<td class="sjb-sec" style="color:#16a34a;font-weight:700;">골재</td>'))

        # 기타 섹션
        gita_names_found = [r['구분'] for r in _sjb_rows if r['구분'] in set(GITA_ROWS) | {'기타 계'}]
        for i, nm in enumerate(gita_names_found):
            d = _get(nm)
            sec_td = f'<td class="sjb-sec" rowspan="{len(gita_names_found)}" style="color:#7c3aed;font-weight:700;">기타</td>' if i == 0 else ''
            style = 'subtotal' if nm == '기타 계' else 'normal'
            rows_html.append(_row_html(nm, d, style, sec_td))

        # 합계 (레미콘+골재+기타)
        d_tot = _sjb_by_name.get('합계') or {}
        rows_html.append(_row_html('합계', d_tot, 'total',
            '<td class="sjb-sec" style="font-weight:700;"></td>'))

        # 건자재
        d_jc = _get('건자재')
        rows_html.append(_row_html('건자재', d_jc, 'normal',
            '<td class="sjb-sec" style="color:#c2410c;font-weight:700;">건자재</td>'))

        # 전체 합계
        d_all = _sjb_by_name.get('합계_전체') or _sjb_by_name.get('합계') or {}
        rows_html.append(_row_html('합계', d_all, 'grand_total',
            '<td class="sjb-sec" style="font-weight:700;"></td>'))

        html = f"""
<style>
/* ── 사업장별 테이블 ── */
.sjb-wrap {{ overflow-x: auto; margin-top: 4px; }}
.sjb-tbl {{
    border-collapse: collapse;
    font-size: 0.72em;
    white-space: nowrap;
    font-family: 'Segoe UI', Arial, sans-serif;
    width: 100%;
}}

/* 헤더 1행 – 그룹명 */
.sjb-tbl thead tr:first-child th {{
    background: #1e293b;
    padding: 7px 8px 6px;
    text-align: center;
    font-weight: 700;
    font-size: 1.0em;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    border-right: 1px solid rgba(255,255,255,0.12);
    color: #fff;
    letter-spacing: 0.03em;
}}
/* 헤더 그룹 색상 – 모두 동일 다크 */
.sjb-tbl th.th-hdr,
.sjb-tbl th.th-vol,
.sjb-tbl th.th-sale,
.sjb-tbl th.th-oi,
.sjb-tbl th.th-uprc,
.sjb-tbl th.th-vc,
.sjb-tbl th.th-cm {{ background: #1e293b; }}

/* 헤더 2행 – 서브 컬럼 */
.sjb-tbl thead tr:last-child th {{
    background: #334155;
    padding: 4px 6px;
    text-align: center;
    font-size: 0.88em;
    font-weight: 500;
    color: rgba(255,255,255,0.82);
    border-right: 1px solid rgba(255,255,255,0.1);
}}
.sjb-tbl th.ts-vol,
.sjb-tbl th.ts-sale,
.sjb-tbl th.ts-oi,
.sjb-tbl th.ts-uprc,
.sjb-tbl th.ts-vc,
.sjb-tbl th.ts-cm  {{ background: #334155; }}

/* 데이터 셀 공통 */
.sjb-tbl td {{
    border: none !important;
    border-right: 1px solid #e2e8f0 !important;
    border-bottom: none !important;
    padding: 3px 7px;
    background: #fff;
    color: #1e293b;
    vertical-align: middle;
}}
/* 그룹 마지막 셀 구분선 */
.sjb-tbl td.sjb-ge {{ border-right: 2px solid #94a3b8 !important; }}

/* 지브라 */
.sjb-tbl tbody tr:nth-child(even) td {{ background: #f8fafc; }}
.sjb-tbl tbody tr:nth-child(even) td.sjb-ge {{ background: #f8fafc; }}

/* 구분 & 이름 셀 */
.sjb-sec {{
    text-align: center;
    font-size: 0.82em;
    font-weight: 700;
    min-width: 34px;
    border-right: 2px solid #cbd5e1 !important;
    letter-spacing: 0.05em;
}}
.sjb-label {{
    text-align: left;
    padding-left: 10px;
    min-width: 70px;
    border-right: 2px solid #e2e8f0 !important;
    color: #334155;
}}

/* 숫자 셀 */
.sjb-num {{ text-align: right; min-width: 50px; }}

/* 행 타입별 */
.sjb-tbl tr.sjb-region td {{
    background: #f1f5f9 !important;
    color: #475569;
}}
.sjb-tbl tr.sjb-subtotal td {{
    background: #f1f5f9 !important;
    font-weight: 700;
    border-top: 1px solid #cbd5e1;
    border-bottom: 1px solid #cbd5e1;
    color: #1e293b;
}}
.sjb-tbl tr.sjb-total td {{
    background: #e2e8f0 !important;
    font-weight: 700;
    border-top: 1.5px solid #94a3b8;
    border-bottom: 1.5px solid #94a3b8;
    color: #0f172a;
}}
.sjb-tbl tr.sjb-grand td {{
    background: #cbd5e1 !important;
    font-weight: 800;
    border-top: 2px solid #64748b;
    border-bottom: 2px solid #64748b;
    color: #0f172a;
}}
/* 권역 구분선 */
.sjb-tbl tr.sjb-divider td {{ border-bottom: 2px solid #475569 !important; }}

/* 호버 */
.sjb-tbl tbody tr:hover td {{ background: #dbeafe !important; transition: background 0.1s; }}

/* 단위 */
.sjb-unit {{ text-align:right; color:#94a3b8; font-size:0.76em; margin-bottom:3px; }}
</style>
<div class="sjb-unit">[단위 : 천㎥, 백만원]</div>
<div class="sjb-wrap">
<table class="sjb-tbl">
<thead>
<tr>
  <th class="th-hdr" rowspan="2" colspan="2" style="min-width:104px;">구분</th>
  <th class="th-vol"  colspan="5">물량</th>
  <th class="th-sale" colspan="5">매출</th>
  <th class="th-oi"   colspan="5">영업이익 (공통비 배부전)</th>
  <th class="th-uprc" colspan="3">판매단가</th>
  <th class="th-vc"   colspan="3">변동비</th>
  <th class="th-cm"   colspan="3">공헌이익</th>
</tr>
<tr>
  <th class="ts-vol">계획</th><th class="ts-vol">실적</th><th class="ts-vol">차이</th><th class="ts-vol">전년</th><th class="ts-vol">차이</th>
  <th class="ts-sale">계획</th><th class="ts-sale">실적</th><th class="ts-sale">차이</th><th class="ts-sale">전년</th><th class="ts-sale">차이</th>
  <th class="ts-oi">계획</th><th class="ts-oi">실적</th><th class="ts-oi">차이</th><th class="ts-oi">전년</th><th class="ts-oi">차이</th>
  <th class="ts-uprc">계획</th><th class="ts-uprc">실적</th><th class="ts-uprc">전년</th>
  <th class="ts-vc">계획</th><th class="ts-vc">실적</th><th class="ts-vc">전년</th>
  <th class="ts-cm">계획</th><th class="ts-cm">실적</th><th class="ts-cm">전년</th>
</tr>
</thead>
<tbody>
{''.join(rows_html)}
</tbody>
</table>
</div>
"""
        st.markdown(html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif current_page == "건재손익_공장별":
    _page_header("공장별 손익")
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
    _page_header("레미콘 공헌이익 분석")
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
    _page_header("레미콘 공장별 손익")
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

elif current_page in ["레미콘_손익요약","건자재_손익요약","골재_손익요약","임대_손익요약"]:
    nm={"레미콘_손익요약":"레미콘","건자재_손익요약":"건자재","골재_손익요약":"골재","임대_손익요약":"임대"}[current_page]
    if "sel_period" not in st.session_state:
        st.session_state["sel_period"] = "당월"
    st.markdown("""<style>
    div[data-testid="stColumn"]:has(> div > div > div[data-testid="stSelectbox"]) {
        padding-left: 2px !important; padding-right: 2px !important;
    }
    div[data-testid="stHorizontalBlock"]:has(> div[data-testid="stColumn"] > div > div > div[data-testid="stSelectbox"]) {
        gap: 4px !important;
    }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    </style>""", unsafe_allow_html=True)
    _page_header(nm + " 손익 요약", show_period=True)
    _sec_period = st.session_state.get("sel_period", "당월")
    _sec_sfx = "누계" if _sec_period == "누계" else ""

    @st.cache_data(ttl=600)
    def get_sec_overview(year, month):
        return load_overview(year, month)

    @st.cache_data(ttl=600)
    def get_sec_factory(year, month, period="당월"):
        return load_factory_data(year, month, period=period)

    @st.cache_data(ttl=600)
    def get_monthly_trend(year, up_to_month, ov_key, fa_key_name):
        months = [m for m in get_available_months(year) if m <= up_to_month]
        rows = []
        for m in months:
            dov = load_overview(year, m)
            dfa = load_factory_data(year, m)
            r = {'월': m}
            if dov is not None:
                ov_row = dov[dov['구분']==ov_key]
                ov_row = ov_row.iloc[0] if not ov_row.empty else None
                for base in ['물량','매출','영업이익']:
                    r[f'{base}_계획'] = ov_row.get(f'{base}_계획') if ov_row is not None else None
                    r[f'{base}_실적'] = ov_row.get(f'{base}_실적') if ov_row is not None else None
            if dfa is not None and fa_key_name:
                fa_row = dfa[dfa['공장명']==fa_key_name]
                fa_row = fa_row.iloc[0] if not fa_row.empty else None
                if fa_row is not None:
                    r['공헌이익_계획'] = fa_row.get('공헌이익_계획')
                    r['공헌이익_실적'] = fa_row.get('공헌이익_실적')
            rows.append(r)
        return pd.DataFrame(rows) if rows else None

    def to억(v):
        if v is None or (isinstance(v, float) and pd.isna(v)): return None
        return v / 100

    ov_section = {'레미콘_손익요약':'레미콘','건자재_손익요약':'건자재','골재_손익요약':'골재','임대_손익요약':'기타'}[current_page]
    fa_name    = {'레미콘_손익요약':'레미콘 계','건자재_손익요약':'건자재','골재_손익요약':'골재 계','임대_손익요약':'임대'}[current_page]

    df_sec_ov = get_sec_overview(selected_year, selected_month)
    df_sec_fa = get_sec_factory(selected_year, selected_month, period=_sec_sfx if _sec_sfx else "당월")

    row_ov = df_sec_ov[df_sec_ov['구분']==ov_section].iloc[0] if df_sec_ov is not None and not df_sec_ov[df_sec_ov['구분']==ov_section].empty else None
    row_fa = df_sec_fa[df_sec_fa['공장명']==fa_name].iloc[0] if df_sec_fa is not None and not df_sec_fa[df_sec_fa['공장명']==fa_name].empty else None

    def _ov(base, kind):
        col = f'{base}_누계{kind}' if _sec_sfx else f'{base}_{kind}'
        return row_ov.get(col) if row_ov is not None else None

    trend_df2 = get_monthly_trend(selected_year, selected_month, ov_section, fa_name)

    def _safe(v, d=1):
        if v is None or (isinstance(v, float) and pd.isna(v)): return None
        return round(float(v), d)

    def _pct(actual, plan):
        try:
            if actual is None or plan is None or plan == 0: return None
            return round(actual / plan * 100, 1)
        except: return None

    def _달성색(pct):
        if pct is None: return '#6b7280'
        return '#1d4ed8' if pct >= 100 else '#dc2626'

    def _delta_html(val, unit='백만원', positive_good=True):
        if val is None or (isinstance(val, float) and pd.isna(val)): return ''
        good = val >= 0 if positive_good else val <= 0
        color = '#1d4ed8' if good else '#dc2626'
        arrow = '▲' if val >= 0 else '▼'
        return f'<span style="color:{color};font-size:0.85em;font-weight:700;">{arrow} {f(abs(val))} {unit}</span>'

    st.markdown('<div class="content-wrap">', unsafe_allow_html=True)

    # ════════════════════════════════
    # 레미콘 요약: 달성률 게이지 + 지역별 바차트 + 공헌이익 바차트
    # ════════════════════════════════
    if current_page == "레미콘_손익요약":
        m_r=_safe(_ov('물량','실적')); m_p=_safe(_ov('물량','계획'))
        s_r=_safe(_ov('매출','실적')); s_p=_safe(_ov('매출','계획'))
        o_r=_safe(_ov('영업이익','실적')); o_p=_safe(_ov('영업이익','계획'))
        m_pct=_pct(m_r,m_p); s_pct=_pct(s_r,s_p); o_pct=_pct(o_r,o_p)

        # ── 상단: 3개 달성률 게이지 카드 ──
        def gauge_card(label, actual, plan, unit, pct, color_theme):
            bar_w = min(max(pct or 0, 0), 150) / 150 * 100
            bar_color = _달성색(pct)
            diff = (actual - plan) if (actual is not None and plan is not None) else None
            diff_html = _delta_html(diff, unit)
            return f"""
            <div style="background:white;border-radius:12px;padding:22px 24px;border:1px solid #e5e7eb;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06);border-left:5px solid {color_theme};">
              <div style="font-size:0.85em;font-weight:700;color:#6b7280;letter-spacing:0.05em;margin-bottom:6px;">{label}</div>
              <div style="display:flex;align-items:baseline;gap:6px;margin-bottom:14px;">
                <span style="font-size:2.2em;font-weight:900;color:{fmt_money_val(actual,unit)[1] if actual is not None else '#111827'};">{fmt_money_val(actual,unit)[0] if actual is not None else '-'}</span>
                <span style="font-size:1em;color:#6b7280;font-weight:500;">{unit}</span>
              </div>
              <div style="background:#f3f4f6;border-radius:6px;height:8px;margin-bottom:8px;">
                <div style="background:{bar_color};width:{bar_w:.1f}%;height:8px;border-radius:6px;transition:width 0.3s;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:0.8em;color:#9ca3af;">계획 {f(plan,1)} {unit}</span>
                <span style="font-size:1.05em;font-weight:800;color:{bar_color};">계획 {pct:.1f}%</span>
              </div>
              <div style="margin-top:6px;">{diff_html}</div>
            </div>"""

        col1, col2, col3 = st.columns(3)
        col1.markdown(gauge_card("판매량", m_r, m_p, "천㎥", m_pct, "#d97706"), unsafe_allow_html=True)
        col2.markdown(gauge_card("매출액", to억(s_r*100 if s_r else None), to억(s_p*100 if s_p else None), "억원",
                                  s_pct, "#1d4ed8"), unsafe_allow_html=True)
        _oi_color = "#1d4ed8" if (o_r or 0) >= 0 else "#dc2626"
        col3.markdown(gauge_card("영업이익", to억(o_r*100 if o_r else None), to억(o_p*100 if o_p else None), "억원",
                                  o_pct, _oi_color), unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── 중단: 지역별 실적 바차트 + 공헌이익 월별 바차트 ──
        ch_left, ch_right = st.columns([1, 1])

        with ch_left:
            st.markdown('<div class="card"><div class="card-title">지역별 판매 실적 (천㎥)</div>', unsafe_allow_html=True)
            region_rows = []
            for rname in ['수도권','영남권','중부권']:
                match = df_sec_fa[df_sec_fa['공장명']==rname] if df_sec_fa is not None else pd.DataFrame()
                if not match.empty:
                    r2 = match.iloc[0]
                    region_rows.append({'지역': rname,
                                        '계획': r2.get('물량_계획'), '실적': r2.get('물량_실적')})
            if region_rows:
                df_reg = pd.DataFrame(region_rows)
                fig_reg = go.Figure()
                fig_reg.add_trace(go.Bar(name='계획', x=df_reg['지역'], y=df_reg['계획'],
                                         marker_color='#bfdbfe', text=df_reg['계획'].apply(lambda v: f"{v:,.1f}" if v else ""),
                                         textposition='outside', textfont=dict(size=11)))
                fig_reg.add_trace(go.Bar(name='실적', x=df_reg['지역'], y=df_reg['실적'],
                                         marker_color='#1d4ed8', text=df_reg['실적'].apply(lambda v: f"{v:,.1f}" if v else ""),
                                         textposition='outside', textfont=dict(size=11)))
                fig_reg.update_layout(barmode='group', height=280, plot_bgcolor='white', paper_bgcolor='white',
                    margin=dict(l=0,r=0,t=10,b=10),
                    legend=dict(orientation='h',x=0.5,xanchor='center',y=1.12,font=dict(size=12)),
                    xaxis=dict(tickfont=dict(size=13,color='#374151'), showgrid=False),
                    yaxis=dict(showticklabels=False, showgrid=False),
                    font=dict(family='Noto Sans KR'))
                st.plotly_chart(fig_reg, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("지역별 데이터 없음")
            st.markdown('</div>', unsafe_allow_html=True)

        with ch_right:
            st.markdown('<div class="card"><div class="card-title">월별 공헌이익 추이 (원/㎥)</div>', unsafe_allow_html=True)
            if trend_df2 is not None and '공헌이익_실적' in trend_df2.columns:
                mlabels = [f"{int(m)}월" for m in trend_df2['월']]
                ch_vals = list(trend_df2['공헌이익_실적'].fillna(0))
                ch_plan = list(trend_df2.get('공헌이익_계획', pd.Series([None]*len(mlabels))).fillna(0))
                colors = ['#16a34a' if v >= 0 else '#dc2626' for v in ch_vals]
                fig_ch = go.Figure()
                fig_ch.add_trace(go.Scatter(x=mlabels, y=ch_plan, name='계획',
                    line=dict(color='#93c5fd', width=2, dash='dot'), mode='lines+markers',
                    marker=dict(size=6)))
                fig_ch.add_trace(go.Bar(x=mlabels, y=ch_vals, name='실적',
                    marker_color=colors,
                    text=[f"{v:,.0f}" for v in ch_vals], textposition='outside', textfont=dict(size=10)))
                fig_ch.update_layout(barmode='overlay', height=280, plot_bgcolor='white', paper_bgcolor='white',
                    margin=dict(l=0,r=0,t=10,b=10),
                    legend=dict(orientation='h',x=0.5,xanchor='center',y=1.12,font=dict(size=12)),
                    xaxis=dict(tickfont=dict(size=12), showgrid=False),
                    yaxis=dict(showticklabels=False, showgrid=True, gridcolor='#f3f4f6'),
                    font=dict(family='Noto Sans KR'))
                st.plotly_chart(fig_ch, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════
    # 건자재 요약: 좌측 빅넘버 KPI + 우측 월별 매출/이익 바차트
    # ════════════════════════════════
    elif current_page == "건자재_손익요약":
        s_r=_ov('매출','실적'); s_p=_ov('매출','계획'); s_d=_ov('매출','차이')
        o_r=_ov('영업이익','실적'); o_p=_ov('영업이익','계획'); o_d=_ov('영업이익','차이')
        ir_r = (o_r/s_r*100) if (s_r and s_r!=0 and o_r is not None) else None
        ir_p = (o_p/s_p*100) if (s_p and s_p!=0 and o_p is not None) else None
        s_pct = _pct(s_r, s_p)
        o_pct = _pct(o_r, o_p)

        left_col, right_col = st.columns([1, 1.6])

        with left_col:
            def big_kpi(label, actual_억, plan_억, unit, pct, border_color, is_profit=False):
                pct_color = _달성색(pct)
                bar_w = min(max(pct or 0, 0), 150) / 150 * 100
                diff_억 = (actual_억 - plan_억) if (actual_억 is not None and plan_억 is not None) else None
                diff_html = ''
                if diff_억 is not None:
                    good = diff_억 >= 0
                    c = '#1d4ed8' if good else '#dc2626'
                    arrow = '▲' if diff_억 >= 0 else '▼'
                    diff_html = f'<span style="color:{c};font-weight:700;">{arrow} {f(abs(diff_억),1)} {unit} vs 계획</span>'
                return f"""
                <div style="background:white;border-radius:12px;padding:26px 28px;border:1px solid #e5e7eb;
                            box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:14px;
                            border-top:5px solid {border_color};">
                  <div style="font-size:0.82em;font-weight:700;color:{border_color};letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">{label}</div>
                  <div style="font-size:2.8em;font-weight:900;color:{fmt_money_val(actual_억,unit)[1] if actual_억 is not None else '#111827'};line-height:1;">{fmt_money_val(actual_억,unit)[0] if actual_억 is not None else '-'}</div>
                  <div style="font-size:1em;color:#6b7280;margin-bottom:14px;">{unit}</div>
                  <div style="background:#f3f4f6;border-radius:6px;height:6px;margin-bottom:10px;">
                    <div style="background:{pct_color};width:{bar_w:.1f}%;height:6px;border-radius:6px;"></div>
                  </div>
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                    <span style="font-size:0.78em;color:#9ca3af;">계획 {f(plan_억,1)} {unit}</span>
                    <span style="font-size:1em;font-weight:800;color:{pct_color};">{pct:.1f}% 달성</span>
                  </div>
                  <div style="font-size:0.85em;">{diff_html}</div>
                </div>"""

            st.markdown(big_kpi("매출액", to억(s_r), to억(s_p), "억원", s_pct, "#059669"), unsafe_allow_html=True)

            _oi_border = "#1d4ed8" if (o_r or 0) >= 0 else "#dc2626"
            st.markdown(big_kpi("영업이익", to억(o_r), to억(o_p), "억원", o_pct, _oi_border, True), unsafe_allow_html=True)

            ir_diff = (ir_r - ir_p) if (ir_r is not None and ir_p is not None) else None
            ir_color = '#1d4ed8' if (ir_r or 0) >= 0 else '#dc2626'
            ir_arrow = '▲' if (ir_diff or 0) >= 0 else '▼'
            ir_diff_html = f'<span style="color:{ir_color}">{ir_arrow} {abs(ir_diff):.2f}%p vs 계획</span>' if ir_diff is not None else ''
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:20px 28px;border:1px solid #e5e7eb;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06);display:flex;justify-content:space-between;align-items:center;">
              <div>
                <div style="font-size:0.82em;font-weight:700;color:#6b7280;margin-bottom:4px;">영업이익률</div>
                <div style="font-size:2em;font-weight:900;color:{ir_color};">{f(ir_r,1) if ir_r is not None else '-'}%</div>
                <div style="font-size:0.82em;margin-top:4px;">{ir_diff_html}</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:0.78em;color:#9ca3af;">계획</div>
                <div style="font-size:1.4em;font-weight:700;color:#9ca3af;">{f(ir_p,1) if ir_p is not None else '-'}%</div>
              </div>
            </div>""", unsafe_allow_html=True)

        with right_col:
            st.markdown('<div class="card"><div class="card-title">월별 매출 / 영업이익 추이 (억원)</div>', unsafe_allow_html=True)
            if trend_df2 is not None and not trend_df2.empty:
                mlabels = [f"{int(m)}월" for m in trend_df2['월']]
                s_vals = [to억(v) for v in trend_df2.get('매출_실적', [])]
                o_vals = [to억(v) for v in trend_df2.get('영업이익_실적', [])]
                s_plan = [to억(v) for v in trend_df2.get('매출_계획', [])]
                fig_jc = go.Figure()
                fig_jc.add_trace(go.Bar(name='매출 실적', x=mlabels, y=s_vals,
                    marker_color='#6ee7b7', text=[f"{v:.1f}" if v else "" for v in s_vals],
                    textposition='outside', textfont=dict(size=10), yaxis='y'))
                fig_jc.add_trace(go.Scatter(name='매출 계획', x=mlabels, y=s_plan,
                    line=dict(color='#059669', width=2, dash='dot'), mode='lines+markers',
                    marker=dict(size=6), yaxis='y'))
                oi_colors = ['#1d4ed8' if (v or 0) >= 0 else '#dc2626' for v in o_vals]
                fig_jc.add_trace(go.Bar(name='영업이익', x=mlabels, y=o_vals,
                    marker_color=oi_colors,
                    text=[f"{v:.1f}" if v else "" for v in o_vals],
                    textposition='outside', textfont=dict(size=10), yaxis='y2'))
                fig_jc.update_layout(
                    barmode='group', height=380,
                    plot_bgcolor='white', paper_bgcolor='white',
                    margin=dict(l=0,r=40,t=10,b=10),
                    legend=dict(orientation='h',x=0.5,xanchor='center',y=1.08,font=dict(size=11)),
                    xaxis=dict(tickfont=dict(size=12), showgrid=False),
                    yaxis=dict(title='매출 (억원)', showgrid=True, gridcolor='#f3f4f6', tickfont=dict(size=10)),
                    yaxis2=dict(title='영업이익 (억원)', overlaying='y', side='right', showgrid=False, tickfont=dict(size=10)),
                    font=dict(family='Noto Sans KR'))
                st.plotly_chart(fig_jc, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════
    # 골재 요약: 달성률 프로그레스 배지 + 이중축 (물량 바 + 이익률 꺾은선)
    # ════════════════════════════════
    elif current_page == "골재_손익요약":
        m_r=_ov('물량','실적'); m_p=_ov('물량','계획'); m_d=_ov('물량','차이')
        s_r=_ov('매출','실적'); s_p=_ov('매출','계획'); s_d=_ov('매출','차이')
        o_r=_ov('영업이익','실적'); o_p=_ov('영업이익','계획'); o_d=_ov('영업이익','차이')
        ir_r = (o_r/s_r*100) if (s_r and s_r!=0 and o_r is not None) else None

        # ── 상단: 수평 달성률 배지 3개 ──
        def progress_badge(label, actual, plan, unit, actual_display=None):
            pct = _pct(actual, plan)
            bar_color = _달성색(pct)
            bar_w = min(max(pct or 0, 0), 150) / 150 * 100
            diff = (actual - plan) if (actual is not None and plan is not None) else None
            diff_str = ''
            if diff is not None:
                arrow = '▲' if diff >= 0 else '▼'
                diff_color = '#1d4ed8' if diff >= 0 else '#dc2626'
                diff_str = f'<span style="color:{diff_color};font-weight:700;margin-left:8px;">{arrow} {f(abs(diff),1)}</span>'
            if actual_display is not None:
                _disp_color = fmt_money_val(actual, unit)[1] if actual is not None else "#1f2937"
                disp = actual_display
            elif actual is not None:
                _d, _disp_color = fmt_money_val(actual, unit); disp = _d
            else:
                disp = '-'; _disp_color = "#1f2937"
            return f"""
            <div style="background:white;border-radius:12px;padding:20px 24px;border:1px solid #e5e7eb;
                        box-shadow:0 2px 8px rgba(0,0,0,0.06);">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;">
                <div>
                  <div style="font-size:0.8em;font-weight:700;color:#0891b2;margin-bottom:4px;">{label}</div>
                  <div style="font-size:2.4em;font-weight:900;color:{_disp_color};line-height:1.1;">{disp}
                    <span style="font-size:0.4em;color:#6b7280;font-weight:500;">{unit}</span>
                  </div>
                  <div style="font-size:0.82em;color:#6b7280;margin-top:4px;">계획 {f(plan,1) if plan else '-'} {unit}{diff_str}</div>
                </div>
                <div style="background:{bar_color}15;border-radius:50%;width:60px;height:60px;
                            display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                  <span style="font-size:1.05em;font-weight:900;color:{bar_color};">{pct:.0f}%</span>
                </div>
              </div>
              <div style="background:#f3f4f6;border-radius:6px;height:8px;">
                <div style="background:{bar_color};width:{bar_w:.1f}%;height:8px;border-radius:6px;"></div>
              </div>
            </div>"""

        pb1, pb2, pb3 = st.columns(3)
        pb1.markdown(progress_badge("판매량", m_r, m_p, "천㎥"), unsafe_allow_html=True)
        pb2.markdown(progress_badge("매출액", s_r, s_p, "백만원",
                                     f(to억(s_r), 1)+"억원" if s_r else '-'), unsafe_allow_html=True)
        pb3.markdown(progress_badge("영업이익", o_r, o_p, "백만원",
                                     f(to억(o_r), 1)+"억원" if o_r else '-'), unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── 하단: 물량 바 + 이익률 꺾은선 이중축 ──
        st.markdown('<div class="card"><div class="card-title">월별 판매량 (천㎥) · 영업이익률 (%)</div>', unsafe_allow_html=True)
        if trend_df2 is not None and not trend_df2.empty:
            mlabels = [f"{int(m)}월" for m in trend_df2['월']]
            vol_plan = list(trend_df2.get('물량_계획', pd.Series()))
            vol_act  = list(trend_df2.get('물량_실적', pd.Series()))
            s_vals2  = list(trend_df2.get('매출_실적', pd.Series()))
            o_vals2  = list(trend_df2.get('영업이익_실적', pd.Series()))
            ir_vals  = [(_safe(o/s*100) if s and s!=0 and o is not None else None) for o,s in zip(o_vals2, s_vals2)]

            fig_gr = go.Figure()
            fig_gr.add_trace(go.Bar(name='계획 물량', x=mlabels, y=vol_plan,
                marker_color='#cffafe', text=[f"{v:.0f}" if v else "" for v in vol_plan],
                textposition='outside', textfont=dict(size=9), yaxis='y'))
            fig_gr.add_trace(go.Bar(name='실적 물량', x=mlabels, y=vol_act,
                marker_color='#0891b2', text=[f"{v:.0f}" if v else "" for v in vol_act],
                textposition='outside', textfont=dict(size=9), yaxis='y'))
            fig_gr.add_trace(go.Scatter(name='이익률', x=mlabels, y=ir_vals,
                mode='lines+markers+text',
                line=dict(color='#dc2626', width=3),
                marker=dict(size=10, color='#dc2626'),
                text=[f"{v:.1f}%" if v is not None else "" for v in ir_vals],
                textposition='top center', textfont=dict(size=11, color='#dc2626'),
                yaxis='y2'))
            fig_gr.update_layout(
                barmode='group', height=320,
                plot_bgcolor='white', paper_bgcolor='white',
                margin=dict(l=0,r=40,t=10,b=10),
                legend=dict(orientation='h',x=0.5,xanchor='center',y=1.1,font=dict(size=11)),
                xaxis=dict(tickfont=dict(size=12), showgrid=False),
                yaxis=dict(title='물량 (천㎥)', showgrid=True, gridcolor='#f3f4f6', tickfont=dict(size=10)),
                yaxis2=dict(title='이익률 (%)', overlaying='y', side='right', showgrid=False,
                            tickfont=dict(size=10), ticksuffix='%'),
                font=dict(family='Noto Sans KR'))
            st.plotly_chart(fig_gr, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════
    # 임대 요약: 빅넘버 2개 + 월별 가로 바차트
    # ════════════════════════════════
    elif current_page == "임대_손익요약":
        s_r=_ov('매출','실적'); s_p=_ov('매출','계획'); s_d=_ov('매출','차이')
        o_r=_ov('영업이익','실적'); o_p=_ov('영업이익','계획'); o_d=_ov('영업이익','차이')
        ir_r = (o_r/s_r*100) if (s_r and s_r!=0 and o_r is not None) else None
        s_pct = _pct(s_r, s_p)
        o_pct = _pct(o_r, o_p)

        # ── 상단: 빅넘버 2+1 레이아웃 ──
        bn1, bn2, bn3 = st.columns([1.2, 1.2, 0.9])
        def big_number(label, val_억, plan_억, unit, pct, color, col):
            bar_w = min(max(pct or 0, 0), 150) / 150 * 100
            pc = _달성색(pct)
            diff = (val_억 - plan_억) if (val_억 is not None and plan_억 is not None) else None
            diff_html = ''
            if diff is not None:
                arrow = '▲' if diff >= 0 else '▼'
                c = '#1d4ed8' if diff >= 0 else '#dc2626'
                diff_html = f'<span style="color:{c};font-size:0.9em;font-weight:700;">{arrow} {f(abs(diff),1)} {unit} vs 계획</span>'
            col.markdown(f"""
            <div style="background:white;border-radius:14px;padding:28px 30px;border:1px solid #e5e7eb;
                        box-shadow:0 3px 12px rgba(0,0,0,0.07);border-bottom:5px solid {color};">
              <div style="font-size:0.82em;font-weight:700;color:{color};margin-bottom:10px;letter-spacing:0.06em;">{label}</div>
              <div style="font-size:3em;font-weight:900;color:#1f2937;line-height:1;">{f(val_억,1) if val_억 is not None else '-'}</div>
              <div style="font-size:1.1em;color:#6b7280;margin-bottom:16px;">{unit}</div>
              <div style="background:#f3f4f6;border-radius:6px;height:8px;margin-bottom:10px;">
                <div style="background:{pc};width:{bar_w:.1f}%;height:8px;border-radius:6px;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-size:0.78em;color:#9ca3af;">계획 {f(plan_억,1) if plan_억 else '-'} {unit}</span>
                <span style="font-size:0.95em;font-weight:800;color:{pc};">{pct:.1f}% 달성</span>
              </div>
              {diff_html}
            </div>""", unsafe_allow_html=True)

        big_number("매출액", to억(s_r), to억(s_p), "억원", s_pct, "#7c3aed", bn1)
        _oi_col = "#1d4ed8" if (o_r or 0) >= 0 else "#dc2626"
        big_number("영업이익", to억(o_r), to억(o_p), "억원", o_pct, _oi_col, bn2)

        ir_color2 = '#1d4ed8' if (ir_r or 0) >= 0 else '#dc2626'
        bn3.markdown(f"""
        <div style="background:white;border-radius:14px;padding:28px 24px;border:1px solid #e5e7eb;
                    box-shadow:0 3px 12px rgba(0,0,0,0.07);height:100%;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;">
          <div style="font-size:0.82em;font-weight:700;color:#6b7280;margin-bottom:12px;">영업이익률</div>
          <div style="font-size:3.5em;font-weight:900;color:{ir_color2};line-height:1;">{f(ir_r,1) if ir_r is not None else '-'}</div>
          <div style="font-size:1.1em;color:#6b7280;margin-bottom:8px;">%</div>
          <div style="font-size:0.82em;color:#9ca3af;">계획 {f((o_p/s_p*100) if (s_p and s_p!=0 and o_p is not None) else None,1)}%</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── 하단: 월별 매출/영업이익 가로 바차트 ──
        st.markdown('<div class="card"><div class="card-title">월별 매출 · 영업이익 (억원)</div>', unsafe_allow_html=True)
        if trend_df2 is not None and not trend_df2.empty:
            mlabels = [f"{int(m)}월" for m in trend_df2['월']]
            s_trend = [to억(v) for v in trend_df2.get('매출_실적', [])]
            o_trend = [to억(v) for v in trend_df2.get('영업이익_실적', [])]
            s_plan_t = [to억(v) for v in trend_df2.get('매출_계획', [])]
            fig_im = go.Figure()
            fig_im.add_trace(go.Bar(name='매출 실적', y=mlabels, x=s_trend,
                orientation='h', marker_color='#c4b5fd',
                text=[f"{v:.1f}" if v else "" for v in s_trend],
                textposition='outside', textfont=dict(size=11)))
            oi_colors2 = ['#7c3aed' if (v or 0) >= 0 else '#dc2626' for v in o_trend]
            fig_im.add_trace(go.Bar(name='영업이익', y=mlabels, x=o_trend,
                orientation='h', marker_color=oi_colors2,
                text=[f"{v:.1f}" if v else "" for v in o_trend],
                textposition='outside', textfont=dict(size=11)))
            fig_im.update_layout(
                barmode='group', height=max(280, len(mlabels)*55),
                plot_bgcolor='white', paper_bgcolor='white',
                margin=dict(l=0,r=60,t=10,b=10),
                legend=dict(orientation='h',x=0.5,xanchor='center',y=1.1,font=dict(size=11)),
                xaxis=dict(title='억원', showgrid=True, gridcolor='#f3f4f6', tickfont=dict(size=10)),
                yaxis=dict(tickfont=dict(size=12), showgrid=False, autorange='reversed'),
                font=dict(family='Noto Sans KR'))
            st.plotly_chart(fig_im, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif current_page in ["건자재_손익","골재_손익","임대_손익"]:
    nm={"건자재_손익":"건자재","골재_손익":"골재","임대_손익":"임대"}[current_page]
    _page_header(nm + " 손익")
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

