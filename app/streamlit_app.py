"""
NeuralDoc — Streamlit entry point.

Run with:
    streamlit run app/streamlit_app.py

This file is intentionally slim — it owns only:
  1. Page config & global CSS
  2. Session-state init
  3. Navbar
  4. Route dispatch → app/pages/{landing, chat, analytics_page}
"""

import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `app.*` resolves to the
# app/ *package* even if a stale `app.py` file still exists at the root.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Load .env file (NVIDIA_API_KEY, OPENAI_API_KEY, etc.)
_env_path = Path(_PROJECT_ROOT) / ".env"
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

import streamlit as st

from app.analytics import get_stats
from app.pages.analytics_page import render_analytics
from app.pages.chat import render_chat
from app.pages.landing import render_landing
from rag.pipeline import Pipeline

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="NeuralDoc", page_icon="N", layout="wide",
                   initial_sidebar_state="collapsed")

for k, v in [("page","landing"),("messages",[]),("active_tab","chat"),
             ("show_analytics",False),("dark_mode",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# Shared pipeline — initialised once, reused across Streamlit reruns
if "pipe" not in st.session_state:
    st.session_state.pipe = Pipeline()

if st.query_params.get("launch") == "1":
    st.query_params.clear()
    st.session_state.page = "app"
    st.session_state.active_tab = "chat"
    st.rerun()

if st.query_params.get("darkmode") == "on":
    st.query_params.clear()
    st.session_state.dark_mode = True

if st.query_params.get("darkmode") == "off":
    st.query_params.clear()
    st.session_state.dark_mode = False

# ── Theme CSS ────────────────────────────────────────────────────────────────

def css_vars():
    if st.session_state.dark_mode:
        return """
          --bg:#0F0D1A;--s:#1A1730;--s2:#221E3A;--s3:#2A2550;
          --v:#7C3AED;--v2:#6D28D9;--v3:#8B5CF6;
          --v-10:rgba(124,58,237,0.10);--v-15:rgba(124,58,237,0.15);
          --v-20:rgba(124,58,237,0.20);--vp:#2D2060;--vpb:#4C3A9E;
          --cyan:#06B6D4;--pink:#EC4899;--green:#10B981;--amber:#F59E0B;
          --t1:#F0EEFF;--t2:#A89EC9;--t3:#6B6490;
          --bd:rgba(167,139,250,0.18);--bd2:rgba(255,255,255,0.07);
          --sh:0 1px 3px rgba(0,0,0,0.3),0 4px 16px rgba(0,0,0,0.2);
          --sh2:0 8px 40px rgba(0,0,0,0.4),0 2px 8px rgba(0,0,0,0.2);
          --r:10px;--r2:18px;--r3:24px;--rf:9999px;
          --navbar-bg:rgba(15,13,26,0.88);--navbar-bd:rgba(167,139,250,0.12);
        """
    return """
      --bg:#FAFAFF;--s:#FFFFFF;--s2:#F4F2FB;--s3:#EEEAFC;
      --v:#7C5CFC;--v2:#6949E0;--v3:#9B85FF;
      --v-10:rgba(124,92,252,0.08);--v-15:rgba(124,92,252,0.12);
      --v-20:rgba(124,92,252,0.16);--vp:#F1EEFE;--vpb:#E4DDFB;
      --cyan:#38B2AC;--pink:#E8699A;--green:#48BB78;--amber:#ED8936;
      --t1:#2D2B55;--t2:#6B6A8A;--t3:#A0A0B8;
      --bd:rgba(124,92,252,0.10);--bd2:rgba(45,43,85,0.06);
      --sh:0 1px 3px rgba(45,43,85,0.04),0 4px 20px rgba(124,92,252,0.05);
      --sh2:0 8px 32px rgba(124,92,252,0.10),0 2px 6px rgba(45,43,85,0.03);
      --r:12px;--r2:20px;--r3:24px;--rf:9999px;
      --navbar-bg:rgba(255,255,255,0.92);--navbar-bd:rgba(124,92,252,0.08);
    """

# ── Global CSS ───────────────────────────────────────────────────────────────

st.html(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital,wght@0,400;1,400&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[data-testid="stAppViewContainer"]{{{css_vars()}}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{font-family:'Plus Jakarta Sans',sans-serif!important;
  background:var(--bg)!important;color:var(--t1)!important;}}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],#MainMenu,footer{{display:none!important;height:0!important;}}
[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],.block-container{{
  background:var(--bg)!important;padding:0!important;
  margin:0!important;max-width:100%!important;border:none!important;}}
[data-testid="stVerticalBlock"]{{gap:0!important;}}
[data-testid="stVerticalBlock"]>div{{margin:0!important;padding:0!important;}}

/*  Inputs */
.stTextInput input{{
  background:var(--s)!important;border:1.5px solid var(--bd)!important;
  border-radius:var(--r)!important;color:var(--t1)!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;font-size:14px!important;
  padding:13px 18px!important;box-shadow:var(--sh)!important;
  transition:all 0.2s cubic-bezier(0.4,0,0.2,1)!important;}}
.stTextInput input:focus{{
  border-color:var(--v)!important;
  box-shadow:0 0 0 3px rgba(124,58,237,0.12),var(--sh)!important;
  outline:none!important;transform:translateY(-1px)!important;}}
.stTextInput input::placeholder{{color:var(--t3)!important;}}
.stTextInput label,.stFileUploader label{{display:none!important;}}

/*  Buttons  */
.stButton>button{{
  background:linear-gradient(135deg,var(--v),var(--v3))!important;
  color:#fff!important;border:none!important;border-radius:var(--r)!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600!important;
  font-size:13px!important;padding:12px 0!important;
  box-shadow:0 2px 10px rgba(124,58,237,0.25)!important;
  transition:all 0.2s cubic-bezier(0.4,0,0.2,1)!important;
  position:relative!important;overflow:hidden!important;}}
.stButton>button:hover{{
  background:linear-gradient(135deg,var(--v2),var(--v))!important;
  transform:translateY(-2px)!important;
  box-shadow:0 6px 20px rgba(124,58,237,0.35)!important;}}
.stButton>button:active{{transform:scale(0.97)!important;}}

/* File uploader  */
[data-testid="stFileUploaderDropzone"]{{
  background:var(--s)!important;border:2px dashed var(--vpb)!important;
  border-radius:var(--r2)!important;
  transition:all 0.2s cubic-bezier(0.4,0,0.2,1)!important;}}
[data-testid="stFileUploaderDropzone"]:hover{{
  border-color:var(--v)!important;background:var(--vp)!important;
  transform:scale(1.01)!important;}}
[data-testid="stFileUploaderDropzone"] *{{color:var(--t2)!important;}}
[data-testid="stDownloadButton"]>button{{
  background:var(--s)!important;color:var(--v)!important;
  border:1.5px solid var(--vpb)!important;border-radius:var(--r)!important;
  font-weight:600!important;font-size:13px!important;box-shadow:none!important;
  transition:all 0.18s!important;}}
[data-testid="stDownloadButton"]>button:hover{{
  background:var(--vp)!important;transform:translateY(-1px)!important;
  box-shadow:var(--sh)!important;}}
hr{{border-color:var(--bd2)!important;}}

/* Streamlit alerts — force dark readable text on all notifications */
[data-testid="stAlert"] {{
  border-radius:var(--r)!important;
  font-family:'Inter','Plus Jakarta Sans',sans-serif!important;
  font-size:13.5px!important;font-weight:500!important;
  padding:12px 18px!important;margin:8px 0!important;
  animation:slideUp 0.3s ease both;
}}
/* Force ALL alert text to dark */
[data-testid="stAlert"] *,
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div,
[role="alert"] *,
.stAlert * {{
  color:#1a1a2e!important;
}}
/* Warning — amber tint */
[data-testid="stAlert"][data-baseweb*="warning"],
div[role="alert"]:has(svg[data-testid="stIconWarning"]) {{
  background:#FFFBEB!important;border:1.5px solid #FDE68A!important;
}}
/* Error — red tint */
[data-testid="stAlert"][data-baseweb*="negative"],
div[role="alert"]:has(svg[data-testid="stIconError"]) {{
  background:#FEF2F2!important;border:1.5px solid #FECACA!important;
}}
/* Success — green tint */
[data-testid="stAlert"][data-baseweb*="positive"],
div[role="alert"]:has(svg[data-testid="stIconSuccess"]) {{
  background:#F0FFF4!important;border:1.5px solid #C6F6D5!important;
}}
/* Info — blue tint */
[data-testid="stAlert"][data-baseweb*="info"],
div[role="alert"]:has(svg[data-testid="stIconInfo"]) {{
  background:#EBF8FF!important;border:1.5px solid #BEE3F8!important;
}}
/* Exception */
.stException {{
  background:#FEF2F2!important;border:1.5px solid #FECACA!important;
  border-radius:var(--r)!important;padding:14px 18px!important;
}}
.stException * {{ color:#991B1B!important; }}

/* Spinner text */
[data-testid="stSpinner"],
[data-testid="stSpinner"] *,
.stSpinner, .stSpinner * {{
  color:#1a1a2e!important;
}}

/* Animations  */
@keyframes slideUp{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes fadeIn{{from{{opacity:0;}}to{{opacity:1;}}}}
@keyframes fD{{from{{opacity:0;transform:translateY(-12px);filter:blur(4px);}}to{{opacity:1;transform:translateY(0);filter:blur(0);}}}}
@keyframes fU{{from{{opacity:0;transform:translateY(22px);filter:blur(4px);}}to{{opacity:1;transform:translateY(0);filter:blur(0);}}}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 0 rgba(124,58,237,0.15);}}50%{{box-shadow:0 0 0 6px rgba(124,58,237,0);}}}}
@keyframes counterUp{{from{{opacity:0;transform:scale(0.8);}}to{{opacity:1;transform:scale(1);}}}}
@keyframes dp{{0%,100%{{opacity:1;}}50%{{opacity:0.2;}}}}
@keyframes borderGlow{{0%,100%{{border-color:rgba(124,58,237,0.12);}}50%{{border-color:rgba(124,58,237,0.35);}}}}
@keyframes aP{{0%,100%{{color:var(--vpb);}}50%{{color:var(--v);}}}}
@keyframes meshMove{{
  0%{{background-position:0% 0%,100% 100%,50% 50%;}}
  100%{{background-position:10% 5%,90% 85%,55% 45%;}}}}
</style>""")

# ── Pipeline status ──────────────────────────────────────────────────────────

pipe: Pipeline = st.session_state.pipe
ready  = pipe.is_ready
chunks = len(pipe.all_chunks)
files  = pipe.indexed_files

if ready:
    _bs = "color:#059669;background:rgba(5,150,105,0.08);border:1.5px solid rgba(5,150,105,0.3);"
    _bd = "#059669"; _bt = f"Ready &middot; {chunks} chunks"
else:
    _bs = "color:#D97706;background:rgba(217,119,6,0.08);border:1.5px solid rgba(217,119,6,0.3);"
    _bd = "#D97706"; _bt = "No docs indexed"

# ── Navbar ───────────────────────────────────────────────────────────────────

dm = st.session_state.dark_mode
dm_icon = "☀" if dm else "☽"
dm_label = f"{dm_icon} {'Light' if dm else 'Dark'}"

st.html(f"""<style>
/*  Navbar row styling  */
div[data-testid="stHorizontalBlock"]:first-of-type {{
  position:sticky!important;top:0!important;z-index:200!important;
  background:var(--navbar-bg)!important;backdrop-filter:blur(16px)!important;
  border-bottom:1px solid var(--navbar-bd)!important;
  padding:8px max(24px, calc((100vw - 1150px)/2 + 24px))!important;
  align-items:center!important;gap:8px!important;
  animation:fD 0.5s ease both;
}}
/* Logo column */
div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child {{
  display:flex!important;align-items:center!important;
}}
/* Nav buttons pill style */
div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button {{
  background:transparent!important;color:var(--t2)!important;
  border:none!important;border-radius:7px!important;
  font-size:12px!important;font-weight:600!important;
  padding:5px 16px!important;height:32px!important;min-height:0!important;
  box-shadow:none!important;transition:all 0.2s!important;
  font-family:'Plus Jakarta Sans',sans-serif!important;
  white-space:nowrap!important;line-height:1!important;
}}
div[data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover {{
  background:var(--vp)!important;color:var(--v)!important;
  transform:none!important;box-shadow:none!important;
}}
/* Dark mode toggle button */
div[data-testid="stHorizontalBlock"]:first-of-type .dm-toggle-col .stButton > button {{
  background:var(--vp)!important;color:var(--v)!important;
  border:1.5px solid var(--vpb)!important;border-radius:9999px!important;
  font-size:12px!important;font-weight:600!important;
  padding:5px 13px!important;height:32px!important;
  box-shadow:none!important;
}}
div[data-testid="stHorizontalBlock"]:first-of-type .dm-toggle-col .stButton > button:hover {{
  background:var(--v-15)!important;transform:none!important;
  box-shadow:none!important;
}}
</style>""")

# Navbar Row
_logo, _home, _chat, _anl, _spacer, _dm_col, _status = st.columns([2, 0.8, 0.8, 1.1, 3, 1, 1.3])

with _logo:
    st.html("""<div style="display:flex;align-items:center;gap:9px;padding:4px 0;">
      <div style="width:8px;height:8px;border-radius:50%;background:var(--v);
        animation:pulse 2.5s ease-in-out infinite;"></div>
      <span style="font-family:'Instrument Serif',serif;font-size:19px;color:var(--t1);
        letter-spacing:-0.3px;white-space:nowrap;">NeuralDoc</span>
    </div>""")

with _home:
    if st.button("Home", key="_nav_home", use_container_width=True):
        st.session_state.page = "landing"; st.rerun()

with _chat:
    if st.button("Chat", key="_nav_chat", use_container_width=True):
        st.session_state.page = "app"
        st.session_state.active_tab = "chat"; st.rerun()

with _anl:
    if st.button("Analytics", key="_nav_analytics", use_container_width=True):
        st.session_state.page = "app"
        st.session_state.active_tab = "analytics"; st.rerun()

with _dm_col:
    if st.button(dm_label, key="_nav_dark", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode; st.rerun()

with _status:
    st.html(f"""<div style="display:inline-flex;align-items:center;gap:5px;
      font-size:11px;font-weight:600;padding:5px 12px;border-radius:var(--rf);{_bs};white-space:nowrap;">
      <div style="width:5px;height:5px;border-radius:50%;background:{_bd};
        {'animation:pulse 1.5s ease-in-out infinite;' if ready else ''}"></div>
      {_bt}</div>""")

if st.session_state.page == "landing":
    _active_label = "Home"
elif st.session_state.get("active_tab") == "analytics":
    _active_label = "Analytics"
else:
    _active_label = "Chat"

st.html(f"""<script>
(function(){{
  var doc = window.parent ? window.parent.document : document;
  var btns = doc.querySelectorAll('button');
  for(var i=0;i<btns.length;i++){{
    var t = btns[i].innerText.trim();
    if(t==='{_active_label}'){{
      btns[i].style.background='var(--v)';
      btns[i].style.color='#fff';
      btns[i].style.boxShadow='0 2px 8px rgba(124,58,237,0.25)';
    }}
  }}
}})();
</script>""")

# ── Route dispatch ───────────────────────────────────────────────────────────

if st.session_state.page == "landing":
    render_landing()
elif st.session_state.active_tab == "analytics":
    stats = get_stats()
    render_analytics(stats=stats, api_ok=True, ready=ready, chunks=chunks, files=files)
else:
    render_chat(pipe=pipe, ready=ready, chunks=chunks, files=files)
