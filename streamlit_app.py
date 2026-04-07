import requests
import streamlit as st
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from chat_history import (save_conversation, load_all_conversations,
                               load_conversation, export_as_markdown)
    from analytics import record_query, get_stats
except ImportError:
    def save_conversation(m, t=None): return ""
    def load_all_conversations(): return []
    def load_conversation(cid): return []
    def export_as_markdown(m, title=""): return "\n".join(f"{x['role']}: {x['content']}" for x in m)
    def record_query(q, lat, ref, model=""): pass
    def get_stats(): return {"total_queries":0,"answered":0,"refused":0,"refusal_rate":0,"avg_latency_ms":0,"recent":[]}

st.set_page_config(page_title="NeuralDoc", page_icon="N", layout="wide",
                   initial_sidebar_state="collapsed")

for k, v in [("page","landing"),("messages",[]),("active_tab","chat"),
             ("show_analytics",False),("dark_mode",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

API_BASE = "http://localhost:8000"

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

# Theme CSS 
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
      --bg:#F6F5FF;--s:#FFFFFF;--s2:#F0EEFF;--s3:#EAE7FF;
      --v:#7C3AED;--v2:#6D28D9;--v3:#8B5CF6;
      --v-10:rgba(124,58,237,0.10);--v-15:rgba(124,58,237,0.15);
      --v-20:rgba(124,58,237,0.20);--vp:#EDE9FE;--vpb:#DDD6FE;
      --cyan:#06B6D4;--pink:#EC4899;--green:#10B981;--amber:#F59E0B;
      --t1:#1E1B4B;--t2:#4C4888;--t3:#9CA3AF;
      --bd:rgba(124,58,237,0.12);--bd2:rgba(0,0,0,0.06);
      --sh:0 1px 3px rgba(124,58,237,0.08),0 4px 16px rgba(124,58,237,0.06);
      --sh2:0 8px 40px rgba(124,58,237,0.14),0 2px 8px rgba(0,0,0,0.04);
      --r:10px;--r2:18px;--r3:24px;--rf:9999px;
      --navbar-bg:rgba(255,255,255,0.88);--navbar-bd:rgba(124,58,237,0.1);
    """

# Global CSS
st.html(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital,wght@0,400;1,400&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[data-testid="stAppViewContainer"]{{{css_vars()}}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{font-family:'Plus Jakarta Sans',sans-serif!important;
  background:var(--bg)!important;color:var(--t1)!important;}}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],#MainMenu,footer{{display:none!important;height:0!important;}}
[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],.block-container{{
  background:transparent!important;padding:0!important;
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
/* ── File uploader ── */
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
/* ── Animations ── */
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


# ══════════════════════════════════════════════════════════════
# HEALTH CHECK (top-level — needed for navbar badge + all pages)
# ══════════════════════════════════════════════════════════════
def get_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3).json()
        r["_reachable"] = True
        return r
    except Exception:
        return {"pipeline_ready":False,"total_chunks":0,"indexed_files":[],"_reachable":False}

h = get_health()
api_ok = h.get("_reachable", False)
ready  = h.get("pipeline_ready", False)
chunks = h.get("total_chunks", 0)
files  = h.get("indexed_files", [])

if ready:
    _bs = "color:#059669;background:rgba(5,150,105,0.08);border:1.5px solid rgba(5,150,105,0.3);"
    _bd = "#059669"; _bt = f"Ready &middot; {chunks} chunks"
elif api_ok:
    _bs = "color:#D97706;background:rgba(217,119,6,0.08);border:1.5px solid rgba(217,119,6,0.3);"
    _bd = "#D97706"; _bt = "API online &mdash; No docs indexed"
else:
    _bs = "color:#DC2626;background:rgba(220,38,38,0.08);border:1.5px solid rgba(220,38,38,0.3);"
    _bd = "#DC2626"; _bt = "API offline"


# ══════════════════════════════════════════════════════════════
# NAVBAR (all pages) — native Streamlit buttons, CSS styled
# ══════════════════════════════════════════════════════════════
dm = st.session_state.dark_mode
dm_icon = "☀" if dm else "☽"
dm_label = f"{dm_icon} {'Light' if dm else 'Dark'}"

st.html(f"""<style>
/* ── Navbar row styling ── */
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

# Navbar row
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

# Highlight active nav button via JS
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


# ══════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    # ── Single st.html block: styles + full page content + HTML form CTA ──
    # Using HTML <form> with ?launch=1 avoids breaking the layout with Streamlit
    # widget containers (which create white strips and blank gaps).
    st.html("""
    <style>
    .land{min-height:calc(100vh - 56px);background:var(--bg);position:relative;overflow:hidden;}
    .land::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
      background:
        radial-gradient(ellipse 55% 50% at 15% 10%,rgba(167,139,250,0.18),transparent 60%),
        radial-gradient(ellipse 45% 45% at 85% 85%,rgba(6,182,212,0.10),transparent 55%),
        radial-gradient(ellipse 35% 35% at 50% 50%,rgba(236,72,153,0.06),transparent 55%);}
    .hero{position:relative;z-index:10;max-width:820px;margin:0 auto;
      padding:48px 56px 0;text-align:center;animation:fU .8s cubic-bezier(0.16,1,0.3,1) .15s both;}
    .h-eyebrow{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;
      color:var(--v);border:1px solid var(--vpb);background:var(--vp);
      padding:5px 16px;border-radius:var(--rf);margin-bottom:28px;letter-spacing:0.04em;
      animation:fU .6s cubic-bezier(0.16,1,0.3,1) .25s both;}
    .h-dot{width:5px;height:5px;border-radius:50%;background:var(--v);
      animation:dp 1.8s ease-in-out infinite;}
    .h1{font-family:'Instrument Serif',serif;font-size:clamp(44px,6vw,68px);font-weight:400;
      color:var(--t1);line-height:1.06;letter-spacing:-1px;margin-bottom:8px;
      animation:fU .8s cubic-bezier(0.16,1,0.3,1) .4s both;}
    .h1 em{font-style:italic;color:var(--v);}
    .h-sub{font-size:17px;color:var(--t2);line-height:1.8;max-width:560px;
      margin:0 auto 44px;font-weight:400;
      animation:fU .7s cubic-bezier(0.16,1,0.3,1) .55s both;}
    .h-sub b{color:var(--t1);font-weight:600;}
    .cta-wrap{display:flex;justify-content:center;margin-bottom:0;
      animation:fU .6s cubic-bezier(0.16,1,0.3,1) .7s both;}
    .btn-lnd{display:inline-flex;align-items:center;justify-content:center;gap:8px;
      height:52px;padding:0 48px;background:var(--v);color:#fff;border:none;
      border-radius:var(--rf);font-family:'Plus Jakarta Sans',sans-serif;
      font-size:16px;font-weight:600;cursor:pointer;
      box-shadow:0 4px 20px rgba(124,58,237,0.32);
      transition:background 0.18s,transform 0.15s,box-shadow 0.18s;}
    .btn-lnd:hover{background:var(--v2);transform:translateY(-2px);
      box-shadow:0 8px 28px rgba(124,58,237,0.42);}
    .btn-lnd:active{transform:scale(0.97);}
    .stats{position:relative;z-index:10;display:flex;max-width:780px;
      margin:52px auto 0;background:var(--s);border:1px solid var(--bd2);
      border-radius:var(--r3);overflow:hidden;box-shadow:var(--sh);
      animation:fU .7s ease .85s both;}
    .stat{flex:1;padding:26px 12px;text-align:center;border-right:1px solid var(--bd2);
      transition:background 0.18s;}
    .stat:last-child{border-right:none;}.stat:hover{background:var(--vp);}
    .sv{font-family:'Instrument Serif',serif;font-size:32px;color:var(--v);
      line-height:1;margin-bottom:5px;}
    .sl{font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.1em;text-transform:uppercase;}
    .sec{position:relative;z-index:10;max-width:1200px;margin:88px auto 0;padding:0 56px;}
    .sec-lbl{font-size:11px;font-weight:700;color:var(--v);letter-spacing:0.12em;
      text-transform:uppercase;margin-bottom:10px;}
    .sec-ttl{font-family:'Instrument Serif',serif;font-size:38px;color:var(--t1);
      margin-bottom:36px;font-weight:400;}
    .sec-ttl em{font-style:italic;color:var(--v);}
    .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
    .card{background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
      padding:26px;box-shadow:var(--sh);
      transition:transform 0.22s,box-shadow 0.22s,border-color 0.22s;}
    .card:hover{transform:translateY(-5px);box-shadow:var(--sh2);border-color:var(--vpb);}
    .c-num{font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.12em;
      text-transform:uppercase;margin-bottom:10px;}
    .c-ttl{font-size:15px;font-weight:700;color:var(--t1);margin-bottom:7px;}
    .c-bdy{font-size:13px;color:var(--t2);line-height:1.75;}
    .c-tag{display:inline-block;margin-top:13px;font-size:10px;font-weight:700;
      padding:3px 10px;border-radius:var(--rf);border:1px solid;}
    .tg{color:#059669;border-color:rgba(5,150,105,0.3);background:rgba(5,150,105,0.08);}
    .tv{color:var(--v);border-color:var(--vpb);background:var(--vp);}
    .tc{color:var(--cyan);border-color:rgba(6,182,212,0.3);background:rgba(6,182,212,0.08);}
    .tp{color:var(--pink);border-color:rgba(236,72,153,0.3);background:rgba(236,72,153,0.08);}
    .tam{color:var(--amber);border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.08);}
    .feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
    .feat{background:linear-gradient(135deg,var(--vp),var(--s2));
      border:1px solid var(--vpb);border-radius:var(--r2);padding:24px;
      transition:transform 0.2s,box-shadow 0.2s;}
    .feat:hover{transform:translateY(-3px);box-shadow:var(--sh2);}
    .feat-ttl{font-size:14px;font-weight:700;color:var(--t1);margin-bottom:6px;}
    .feat-bdy{font-size:12px;color:var(--t2);line-height:1.7;}
    .feat-badge{display:inline-block;margin-top:10px;font-size:10px;font-weight:700;
      color:var(--v);background:var(--s);border:1px solid var(--vpb);
      padding:3px 10px;border-radius:var(--rf);}
    .pipe-row{display:flex;align-items:center;justify-content:space-between;
      background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
      padding:28px 36px;box-shadow:var(--sh);}
    .p-step{display:flex;flex-direction:column;align-items:center;gap:5px;
      flex:1;padding:8px 4px;border-radius:var(--r);transition:all 0.18s;cursor:default;}
    .p-step:hover{background:var(--vp);transform:translateY(-2px);}
    .p-lbl{font-size:11px;font-weight:700;color:var(--t1);letter-spacing:0.04em;}
    .p-sub{font-size:10px;color:var(--t3);}
    .p-arr{color:var(--vpb);font-size:14px;flex-shrink:0;
      animation:aP 2.5s ease-in-out infinite;}
    .tags{display:flex;flex-wrap:wrap;gap:9px;}
    .tag{padding:6px 14px;font-size:11px;font-weight:600;border-radius:var(--rf);
      border:1px solid;transition:transform 0.15s;cursor:default;}
    .tag:hover{transform:translateY(-2px);}
    .foot{position:relative;z-index:10;max-width:1200px;margin:72px auto 0;
      padding:22px 56px 64px;border-top:1px solid var(--bd2);
      display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
    .foot span{font-size:12px;color:var(--t3);}
    </style>

    <div class="land">
    <div style="position:relative;z-index:1;">

      <section class="hero">
        <div class="h-eyebrow"><span class="h-dot"></span>Zero hallucination tolerance</div>
        <h1 class="h1">Ask anything.<br><em>Know everything.</em></h1>
        <p class="h-sub">
          A <b>production-grade</b> RAG system with <b>inline citations</b>,
          persistent chat history, live analytics, and a hard refusal trigger — no guessing, ever.
        </p>
        <div class="cta-wrap">
          <form method="get" action="" style="margin:0;">
            <input type="hidden" name="launch" value="1">
            <button type="submit" class="btn-lnd">Open App &nbsp;&#8594;</button>
          </form>
        </div>
      </section>

      <div class="stats">
        <div class="stat"><div class="sv">0%</div><div class="sl">Hallucination Rate</div></div>
        <div class="stat"><div class="sv">3&times;</div><div class="sl">Retrieval Methods</div></div>
        <div class="stat"><div class="sv">100%</div><div class="sl">Local &amp; Private</div></div>
        <div class="stat"><div class="sv">&infin;</div><div class="sl">Documents</div></div>
      </div>

      <div class="sec">
        <div class="sec-lbl">New in v1.0</div>
        <div class="sec-ttl">Three <em>new</em> features</div>
        <div class="feat-grid">
          <div class="feat">
            <div class="feat-ttl">Persistent Chat History</div>
            <div class="feat-bdy">Every conversation auto-saved to disk. Load any past chat in one click.</div>
            <span class="feat-badge">chat_history.py</span>
          </div>
          <div class="feat">
            <div class="feat-ttl">Export as Markdown</div>
            <div class="feat-bdy">Download any conversation as a clean .md file with all citations included.</div>
            <span class="feat-badge" style="color:var(--cyan);border-color:rgba(6,182,212,0.3);background:rgba(6,182,212,0.08);">Export MD</span>
          </div>
          <div class="feat">
            <div class="feat-ttl">Live Query Analytics</div>
            <div class="feat-bdy">Real-time dashboard: total queries, refusal rate, avg latency. MLOps observability.</div>
            <span class="feat-badge" style="color:var(--pink);border-color:rgba(236,72,153,0.3);background:rgba(236,72,153,0.08);">analytics.py</span>
          </div>
        </div>
      </div>

      <div class="sec">
        <div class="sec-lbl">Capabilities</div>
        <div class="sec-ttl">Six <em>pillars</em> of precision</div>
        <div class="cards">
          <div class="card"><div class="c-num">01 &mdash; Ingestion</div><div class="c-ttl">Smart PDF Parsing</div><div class="c-bdy">Multi-column layouts, embedded tables, complex structures. Headers and footers stripped automatically.</div><span class="c-tag tg">pdfplumber</span></div>
          <div class="card"><div class="c-num">02 &mdash; Chunking</div><div class="c-ttl">Semantic Chunking</div><div class="c-bdy">Header-aware 500–800 token chunks. Source, page, and section breadcrumb on every chunk.</div><span class="c-tag tv">tiktoken</span></div>
          <div class="card"><div class="c-num">03 &mdash; Retrieval</div><div class="c-ttl">Hybrid Search</div><div class="c-bdy">BM25 fused with dense vector search via Reciprocal Rank Fusion. Catches what either alone misses.</div><span class="c-tag tc">RRF Fusion</span></div>
          <div class="card"><div class="c-num">04 &mdash; Reranking</div><div class="c-ttl">Cross-Encoder Precision</div><div class="c-bdy">Top 20 re-scored. Only the highest-confidence 5 reach the generation layer.</div><span class="c-tag tam">ms-marco</span></div>
          <div class="card"><div class="c-num">05 &mdash; Generation</div><div class="c-ttl">Attributed Answers</div><div class="c-bdy">Every claim carries an inline citation [Source, p.X]. Full References section appended.</div><span class="c-tag tv">LangGraph</span></div>
          <div class="card"><div class="c-num">06 &mdash; Safety</div><div class="c-ttl">Hard Refusal Gate</div><div class="c-bdy">Context below confidence threshold triggers a fixed refusal. No speculation, no hallucination.</div><span class="c-tag tp">Threshold Gate</span></div>
        </div>
      </div>

      <div class="sec">
        <div class="sec-lbl">Architecture</div>
        <div class="sec-ttl">The <em>pipeline</em></div>
        <div class="pipe-row">
          <div class="p-step"><div class="p-lbl">Parse</div><div class="p-sub">pdfplumber</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">Chunk</div><div class="p-sub">tiktoken</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">Embed</div><div class="p-sub">miniLM</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">BM25</div><div class="p-sub">keyword</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">Fuse</div><div class="p-sub">RRF</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">Rerank</div><div class="p-sub">cross-enc</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">Generate</div><div class="p-sub">llama3.1</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">Cite</div><div class="p-sub">attributed</div></div>
        </div>
      </div>

      <div class="sec">
        <div class="sec-lbl">Stack</div>
        <div class="sec-ttl">Built <em>with</em></div>
        <div class="tags">
          <span class="tag tg">pdfplumber</span><span class="tag tg">ChromaDB</span>
          <span class="tag tg">sentence-transformers</span><span class="tag tv">LangGraph</span>
          <span class="tag tv">langchain-ollama</span><span class="tag tv">llama3.1:8b</span>
          <span class="tag tc">BM25 + RRF</span><span class="tag tc">cross-encoder</span>
          <span class="tag tp">FastAPI</span><span class="tag tp">Streamlit</span>
          <span class="tag tam">Python 3.14</span>
        </div>
      </div>

      <div class="foot">
        <span>NeuralDoc &mdash; Production RAG System</span>
        <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
      </div>
    </div>
    </div>""")


# ══════════════════════════════════════════════════════════════
# CHAT / APP PAGE — premium animated redesign
# ══════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    [data-testid="stAppViewContainer"]{background:var(--bg)!important;}
    [data-testid="stAppViewContainer"]::before{
      content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
      background:
        radial-gradient(ellipse 55% 45% at 10% 5%,  rgba(167,139,250,0.14),transparent 55%),
        radial-gradient(ellipse 40% 40% at 90% 90%,  rgba(6,182,212,0.08),transparent 50%),
        radial-gradient(ellipse 30% 30% at 50% 50%,  rgba(236,72,153,0.05),transparent 50%);
      animation:meshMove 20s ease-in-out infinite alternate;
    }
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container{
      padding:0!important;background:transparent!important;max-width:100%!important;}
    @keyframes slideUp{from{opacity:0;transform:translateY(16px);}to{opacity:1;transform:translateY(0);}}
    @keyframes fadeIn{from{opacity:0;}to{opacity:1;}}
    @keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(124,58,237,0.15);}50%{box-shadow:0 0 0 6px rgba(124,58,237,0);}}
    @keyframes counterUp{from{opacity:0;transform:scale(0.8);}to{opacity:1;transform:scale(1);}}
    @keyframes borderGlow{0%,100%{border-color:rgba(124,58,237,0.12);}50%{border-color:rgba(124,58,237,0.35);}}
    </style>""")

    # ── ACTION ROW ────────────────────────────────────────────────────────────
    st.html('<div style="padding:10px 52px 0;display:flex;gap:12px;align-items:center;'
            'animation:slideUp 0.5s ease .1s both;position:relative;z-index:10;">')
    a1, a2, _ = st.columns([1, 1, 8])
    with a1:
        if st.button("Clear Chat", key="clr_btn", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.messages = []
            st.rerun()
    with a2:
        if st.session_state.messages:
            md = export_as_markdown(st.session_state.messages, "NeuralDoc Chat")
            st.download_button("Export .md", data=md,
                file_name=f"neuraldoc_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown", use_container_width=True, key="exp_md")
        else:
            st.html('<div style="height:44px;"></div>')
    st.html('</div>')

    # ══════════════════════════════════════════════════════════
    # ANALYTICS TAB
    # ══════════════════════════════════════════════════════════
    if st.session_state.active_tab == "analytics":
        stats = get_stats()

        recent_rows = ""
        for q in stats["recent"]:
            icon = "✕" if q["refused"] else "✓"
            icon_color = "#DC2626" if q["refused"] else "#059669"
            q_text = q["query"][:80]
            lat = q["latency_ms"]
            recent_rows += (
                f'<div style="display:flex;align-items:center;gap:12px;'
                f'padding:12px 16px;border-radius:var(--r);margin-bottom:6px;'
                f'background:var(--bg);border:1px solid var(--bd2);'
                f'transition:border-color 0.15s,transform 0.15s;'
                f'animation:slideUp 0.4s ease both;"'
                f'onmouseover="this.style.borderColor=\'rgba(124,58,237,0.25)\';this.style.transform=\'translateX(3px)\'"'
                f'onmouseout="this.style.borderColor=\'var(--bd2)\';this.style.transform=\'\'">',
                f'<div style="width:20px;height:20px;border-radius:50%;flex-shrink:0;'
                f'background:{icon_color}20;border:1.5px solid {icon_color}40;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:10px;font-weight:700;color:{icon_color};">{icon}</div>'
                f'<span style="flex:1;font-size:13px;color:var(--t1);">{q_text}</span>'
                f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
                f'color:var(--t3);background:var(--vp);padding:2px 8px;'
                f'border-radius:var(--rf);">{lat}ms</span>'
                f'</div>'
            )
        # join tuple parts
        recent_rows = "".join(
            "".join(x) if isinstance(x, tuple) else x
            for x in [
                (
                    f'<div style="display:flex;align-items:center;gap:12px;'
                    f'padding:12px 16px;border-radius:var(--r);margin-bottom:6px;'
                    f'background:var(--bg);border:1px solid var(--bd2);'
                    f'transition:border-color 0.15s,transform 0.15s;'
                    f'animation:slideUp 0.4s ease both;"'
                    f'onmouseover="this.style.borderColor=\'rgba(124,58,237,0.25)\';this.style.transform=\'translateX(3px)\'"'
                    f'onmouseout="this.style.borderColor=\'var(--bd2)\';this.style.transform=\'\'">',
                    f'<div style="width:20px;height:20px;border-radius:50%;flex-shrink:0;'
                    f'background:{q["refused"] and "#DC2626" or "#059669"}20;'
                    f'border:1.5px solid {q["refused"] and "#DC2626" or "#059669"}40;'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-size:10px;font-weight:700;'
                    f'color:{q["refused"] and "#DC2626" or "#059669"};">'
                    f'{"✕" if q["refused"] else "✓"}</div>'
                    f'<span style="flex:1;font-size:13px;color:var(--t1);">{q["query"][:80]}</span>'
                    f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
                    f'color:var(--t3);background:var(--vp);padding:2px 8px;'
                    f'border-radius:var(--rf);">{q["latency_ms"]}ms</span>'
                    f'</div>'
                )
                for q in stats["recent"]
            ]
        ) if stats["recent"] else ""

        # rebuild properly
        recent_rows = ""
        for q in stats["recent"]:
            icon = "✕" if q["refused"] else "✓"
            ic = "#DC2626" if q["refused"] else "#059669"
            recent_rows += (
                f'<div style="display:flex;align-items:center;gap:12px;padding:12px 16px;'
                f'border-radius:var(--r);margin-bottom:6px;background:var(--bg);'
                f'border:1px solid var(--bd2);transition:border-color 0.15s,transform 0.15s;'
                f'animation:slideUp 0.4s ease both;"'
                f' onmouseover="this.style.borderColor=\'rgba(124,58,237,0.25)\';this.style.transform=\'translateX(3px)\'"'
                f' onmouseout="this.style.borderColor=\'var(--bd2)\';this.style.transform=\'\'">'
                f'<div style="width:20px;height:20px;border-radius:50%;flex-shrink:0;'
                f'background:{ic}20;border:1.5px solid {ic}40;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:10px;font-weight:700;color:{ic};">{icon}</div>'
                f'<span style="flex:1;font-size:13px;color:var(--t1);">{q["query"][:80]}</span>'
                f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;'
                f'color:var(--t3);background:var(--vp);padding:2px 8px;'
                f'border-radius:var(--rf);">{q["latency_ms"]}ms</span>'
                f'</div>'
            )

        ans_pct = round((stats['answered']/stats['total_queries']*100) if stats['total_queries'] else 0)
        ref_pct = round((stats['refused']/stats['total_queries']*100) if stats['total_queries'] else 0)

        st.html(f"""
        <div style="padding:16px 52px 48px;position:relative;z-index:10;">

          <div style="margin-bottom:20px;animation:slideUp 0.4s ease both;">
            <div style="font-size:11px;font-weight:700;color:var(--v);
              letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">Live Observability</div>
            <div style="font-family:'Instrument Serif',serif;font-size:30px;color:var(--t1);">
              Query <em style="font-style:italic;color:var(--v);">Analytics</em></div>
          </div>

          <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:24px;">
            <div style="background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
              padding:22px 18px;box-shadow:var(--sh);text-align:center;
              animation:slideUp 0.4s ease .05s both;
              transition:transform 0.2s,box-shadow 0.2s,border-color 0.2s;"
              onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='var(--sh2)';this.style.borderColor='var(--vpb)'"
              onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)';this.style.borderColor='var(--bd2)'">
              <div style="font-family:'Instrument Serif',serif;font-size:36px;color:var(--v);
                line-height:1;margin-bottom:6px;animation:counterUp 0.6s ease .3s both;">
                {stats['total_queries']}</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);
                letter-spacing:0.1em;text-transform:uppercase;">Total Queries</div>
            </div>
            <div style="background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
              padding:22px 18px;box-shadow:var(--sh);text-align:center;
              animation:slideUp 0.4s ease .1s both;
              transition:transform 0.2s,box-shadow 0.2s,border-color 0.2s;"
              onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='var(--sh2)';this.style.borderColor='rgba(5,150,105,0.3)'"
              onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)';this.style.borderColor='var(--bd2)'">
              <div style="font-family:'Instrument Serif',serif;font-size:36px;color:#059669;
                line-height:1;margin-bottom:6px;animation:counterUp 0.6s ease .35s both;">
                {stats['answered']}</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);
                letter-spacing:0.1em;text-transform:uppercase;">Answered</div>
              <div style="margin-top:8px;height:3px;border-radius:4px;background:var(--s2);overflow:hidden;">
                <div style="height:100%;background:#059669;border-radius:4px;width:{ans_pct}%;
                  transition:width 1s ease;"></div></div>
            </div>
            <div style="background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
              padding:22px 18px;box-shadow:var(--sh);text-align:center;
              animation:slideUp 0.4s ease .15s both;
              transition:transform 0.2s,box-shadow 0.2s,border-color 0.2s;"
              onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='var(--sh2)';this.style.borderColor='rgba(220,38,38,0.3)'"
              onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)';this.style.borderColor='var(--bd2)'">
              <div style="font-family:'Instrument Serif',serif;font-size:36px;color:#DC2626;
                line-height:1;margin-bottom:6px;animation:counterUp 0.6s ease .4s both;">
                {stats['refused']}</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);
                letter-spacing:0.1em;text-transform:uppercase;">Refused</div>
              <div style="margin-top:8px;height:3px;border-radius:4px;background:var(--s2);overflow:hidden;">
                <div style="height:100%;background:#DC2626;border-radius:4px;width:{ref_pct}%;
                  transition:width 1s ease;"></div></div>
            </div>
            <div style="background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
              padding:22px 18px;box-shadow:var(--sh);text-align:center;
              animation:slideUp 0.4s ease .2s both;
              transition:transform 0.2s,box-shadow 0.2s,border-color 0.2s;"
              onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='var(--sh2)';this.style.borderColor='rgba(217,119,6,0.3)'"
              onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)';this.style.borderColor='var(--bd2)'">
              <div style="font-family:'Instrument Serif',serif;font-size:36px;color:#D97706;
                line-height:1;margin-bottom:6px;animation:counterUp 0.6s ease .45s both;">
                {stats['refusal_rate']}%</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);
                letter-spacing:0.1em;text-transform:uppercase;">Refusal Rate</div>
              <div style="margin-top:8px;font-size:11px;color:var(--t3);">
                {'Good' if stats['refusal_rate'] < 20 else 'High — check threshold'}</div>
            </div>
            <div style="background:linear-gradient(135deg,var(--vp),var(--s));
              border:1px solid var(--vpb);border-radius:var(--r2);
              padding:22px 18px;box-shadow:var(--sh);text-align:center;
              animation:borderGlow 3s ease-in-out infinite;
              transition:transform 0.2s,box-shadow 0.2s;"
              onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='var(--sh2)'"
              onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)'">
              <div style="font-family:'Instrument Serif',serif;font-size:36px;color:var(--cyan);
                line-height:1;margin-bottom:6px;animation:counterUp 0.6s ease .5s both;">
                {int(stats['avg_latency_ms'])}ms</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);
                letter-spacing:0.1em;text-transform:uppercase;">Avg Latency</div>
              <div style="margin-top:8px;font-size:11px;color:var(--t3);">
                {'Fast' if stats['avg_latency_ms'] < 3000 else 'Consider GPU'}</div>
            </div>
          </div>

          <div style="background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
            padding:24px 28px;box-shadow:var(--sh);animation:slideUp 0.4s ease .3s both;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;">
              <div style="font-size:13px;font-weight:700;color:var(--t1);">Recent Queries</div>
              <div style="font-size:11px;color:var(--t3);background:var(--vp);
                padding:3px 10px;border-radius:var(--rf);border:1px solid var(--vpb);">
                Last {len(stats['recent'])} of {stats['total_queries']} total</div>
            </div>
            {'<div style="text-align:center;padding:32px;color:var(--t3);font-size:13px;">No queries recorded yet. Send a message to start tracking.</div>' if not stats['recent'] else recent_rows}
          </div>

          <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:14px;">
            <div style="background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
              padding:20px 24px;box-shadow:var(--sh);animation:slideUp 0.4s ease .35s both;">
              <div style="font-size:11px;font-weight:700;color:var(--t3);
                letter-spacing:0.08em;text-transform:uppercase;margin-bottom:14px;">System Status</div>
              <div style="display:flex;gap:10px;flex-direction:column;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                  <span style="font-size:13px;color:var(--t2);">FastAPI Backend</span>
                  <span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:var(--rf);
                    {'color:#059669;background:rgba(5,150,105,0.08);border:1px solid rgba(5,150,105,0.3);' if api_ok else 'color:#DC2626;background:rgba(220,38,38,0.08);border:1px solid rgba(220,38,38,0.3);'}">
                    {'Online' if api_ok else 'Offline'}</span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;">
                  <span style="font-size:13px;color:var(--t2);">RAG Pipeline</span>
                  <span style="font-size:11px;font-weight:700;padding:3px 10px;border-radius:var(--rf);
                    {'color:#059669;background:rgba(5,150,105,0.08);border:1px solid rgba(5,150,105,0.3);' if ready else 'color:#D97706;background:rgba(217,119,6,0.08);border:1px solid rgba(217,119,6,0.3);'}">
                    {'Ready' if ready else 'No docs'}</span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;">
                  <span style="font-size:13px;color:var(--t2);">Indexed Chunks</span>
                  <span style="font-size:11px;font-weight:700;color:var(--v);
                    background:var(--vp);padding:3px 10px;border-radius:var(--rf);
                    border:1px solid var(--vpb);">{chunks}</span>
                </div>
                <div style="display:flex;align-items:center;justify-content:space-between;">
                  <span style="font-size:13px;color:var(--t2);">Indexed Files</span>
                  <span style="font-size:11px;font-weight:700;color:var(--v);
                    background:var(--vp);padding:3px 10px;border-radius:var(--rf);
                    border:1px solid var(--vpb);">{len(files)}</span>
                </div>
              </div>
            </div>
            <div style="background:linear-gradient(135deg,var(--vp),var(--s2));
              border:1px solid var(--vpb);border-radius:var(--r2);
              padding:20px 24px;box-shadow:var(--sh);animation:slideUp 0.4s ease .4s both;">
              <div style="font-size:11px;font-weight:700;color:var(--v);
                letter-spacing:0.08em;text-transform:uppercase;margin-bottom:14px;">MLOps Notes</div>
              <div style="font-size:13px;color:var(--t2);line-height:1.8;">
                This observability layer tracks refusal rate and latency — the two key RAG quality KPIs.
                Refusal rate above 25% may indicate your threshold is too strict.
                Avg latency above 5s suggests a GPU upgrade or model swap to llama3.3:70b.
              </div>
              <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;">
                <span style="font-size:10px;font-weight:700;color:var(--v);
                  background:var(--s);padding:3px 10px;border-radius:var(--rf);
                  border:1px solid var(--vpb);">analytics.json</span>
                <span style="font-size:10px;font-weight:700;color:var(--cyan);
                  background:rgba(6,182,212,0.08);padding:3px 10px;border-radius:var(--rf);
                  border:1px solid rgba(6,182,212,0.25);">200 query rolling window</span>
              </div>
            </div>
          </div>

        </div>""")

    # ══════════════════════════════════════════════════════════
    # CHAT TAB
    # ══════════════════════════════════════════════════════════
    else:
        # ── CSS-only layout: no open/close wrapper divs (each st.html is isolated) ──
        st.html("""<style>
        /* Page padding via CSS — not a wrapper div */
        [data-testid="stMainBlockContainer"] .block-container {
          padding-left: 0 !important; padding-right: 0 !important;
        }
        /* Suppress default Streamlit column/block white backgrounds and borders */
        [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
          background: transparent !important;
        }
        /* ── RIGHT column — upload card ── */
        .upload-card {
          background: var(--s);
          border: 1px solid var(--bd2);
          border-radius: var(--r2);
          padding: 20px 20px 18px;
          box-shadow: var(--sh);
          margin-bottom: 14px;
          animation: slideUp 0.5s ease .1s both;
          transition: box-shadow 0.2s, border-color 0.2s;
        }
        .upload-card:hover { box-shadow: var(--sh2); border-color: var(--vpb); }
        /* ── LEFT column — chat card ── */
        .chat-card {
          background: var(--s);
          border: 1px solid var(--bd2);
          border-radius: var(--r2);
          padding: 20px 22px 18px;
          box-shadow: var(--sh);
          animation: slideUp 0.5s ease both;
        }
        /* ── History card ── */
        .history-card {
          background: var(--s);
          border: 1px solid var(--bd2);
          border-radius: var(--r2);
          padding: 18px 20px 12px;
          box-shadow: var(--sh);
          animation: slideUp 0.5s ease .2s both;
        }
        /* Suppress Streamlit's own column gap rendering artifacts */
        [data-testid="stHorizontalBlock"] { gap: 0 !important; }
        </style>""")

        # ── Outer padding wrapper (pure visual spacer, no widgets inside) ──
        st.html('<div style="height:6px;"></div>')

        col_chat, col_right = st.columns([3, 2], gap="large")

        # ── RIGHT COLUMN ─────────────────────────────────────────────────────
        with col_right:
            # Upload card header (self-contained — no open/close)
            st.html("""<div class="upload-card">
              <div style="display:flex;align-items:center;justify-content:space-between;
                margin-bottom:14px;">
                <div>
                  <div style="font-size:10px;font-weight:700;color:var(--v);
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:5px;">
                    Knowledge Base</div>
                  <div style="font-family:'Instrument Serif',serif;font-size:20px;color:var(--t1);">
                    Upload <em style="font-style:italic;color:var(--v);">documents</em></div>
                </div>
              </div>
              <div style="background:var(--vp);border:2px dashed var(--vpb);
                border-radius:var(--r2);padding:14px;margin-bottom:10px;text-align:center;
                transition:all 0.2s ease;"
                onmouseover="this.style.borderColor='var(--v)';this.style.background='var(--s3)';this.style.transform='scale(1.01)'"
                onmouseout="this.style.borderColor='var(--vpb)';this.style.background='var(--vp)';this.style.transform=''">
                <div style="font-size:13px;font-weight:500;color:var(--t1);margin-bottom:4px;">
                  Drop your PDF below</div>
                <div style="font-size:11px;color:var(--t3);">
                  Parsed &#8594; Chunked &#8594; Embedded &#8594; Indexed</div>
              </div>
            </div>""")

            # Widgets sit OUTSIDE the decorative div — that's fine; they get card bg via CSS
            if st.button("Clear Index", key="clear_idx", use_container_width=False):
                try:
                    r = requests.delete(f"{API_BASE}/index", timeout=15)
                    if r.status_code == 200:
                        st.success("Index cleared.")
                        st.rerun()
                    else:
                        st.error(f"Error: {r.text}")
                except Exception:
                    st.error("API offline.")

            uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")
            if uploaded:
                st.html(f"""<div style="background:rgba(5,150,105,0.07);
                  border:1px solid rgba(5,150,105,0.25);border-radius:var(--r);
                  padding:10px 14px;margin-bottom:10px;animation:slideUp 0.3s ease both;">
                  <div style="font-size:13px;font-weight:600;color:var(--t1);">{uploaded.name}</div>
                  <div style="font-size:11px;color:#059669;margin-top:2px;">{uploaded.size//1024} KB ready</div>
                </div>""")
                if st.button("Index Document", use_container_width=True, key="idx_btn"):
                    with st.spinner("Processing PDF..."):
                        try:
                            resp = requests.post(f"{API_BASE}/ingest",
                                files={"file":(uploaded.name,uploaded,"application/pdf")},
                                timeout=120)
                            if resp.status_code == 200:
                                d = resp.json()
                                st.success(f"Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                                st.rerun()
                            else:
                                st.error(f"Error: {resp.text}")
                        except requests.exceptions.ConnectionError:
                            st.error("API offline. Run: uv run uvicorn api:app --reload --port 8000")
                        except Exception as e:
                            st.error(str(e))

            if files:
                st.html("""<div style="font-size:10px;font-weight:700;color:var(--t3);
                  letter-spacing:0.08em;text-transform:uppercase;margin:10px 0 6px;">
                  Indexed files</div>""")
                for f in files:
                    fname = f.replace("\\","/").split("/")[-1]
                    st.html(f"""<div style="background:var(--bg);border:1px solid var(--bd2);
                      border-radius:var(--r);padding:8px 13px;margin-bottom:5px;
                      display:flex;align-items:center;transition:border-color 0.15s,transform 0.15s;"
                      onmouseover="this.style.borderColor='var(--vpb)';this.style.transform='translateX(2px)'"
                      onmouseout="this.style.borderColor='var(--bd2)';this.style.transform=''">
                      <span style="font-size:12px;font-weight:500;color:var(--t1);flex:1;">{fname}</span>
                      <span style="font-size:10px;font-weight:700;padding:2px 8px;
                        border-radius:var(--rf);color:#059669;background:rgba(5,150,105,0.08);
                        border:1px solid rgba(5,150,105,0.3);">indexed</span>
                    </div>""")

            st.html("""<div style="margin-top:10px;background:var(--bg);border:1px solid var(--bd2);
              border-radius:var(--r);padding:12px 14px;">
              <div style="font-size:10px;font-weight:700;color:var(--t3);
                letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;">Tips</div>
              <div style="font-size:12px;color:var(--t2);line-height:1.8;">
                Click <b style="color:var(--v);">Clear Index</b> before switching documents.<br>
                Ask precise questions for best citation accuracy.<br>
                Every answer includes inline source references.<br>
                Unanswerable queries return a refusal, not a guess.
              </div></div>""")

            # Chat History
            convs = load_all_conversations()
            if convs:
                st.html("""<div class="history-card">
                  <div style="font-size:10px;font-weight:700;color:var(--v);
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:12px;">
                    Chat History</div>""")
                for i, conv in enumerate(convs[:5]):
                    ts = conv["timestamp"][:10]
                    title = conv["title"][:34] + ("…" if len(conv["title"]) > 34 else "")
                    n = len([m for m in conv["messages"] if m["role"]=="user"])
                    hc1, hc2 = st.columns([4, 1])
                    with hc1:
                        st.html(f"""<div style="padding:8px 10px;border-radius:var(--r);
                          border:1px solid var(--bd2);margin-bottom:5px;cursor:pointer;transition:all 0.15s;"
                          onmouseover="this.style.borderColor='var(--vpb)';this.style.background='var(--vp)';this.style.transform='translateX(2px)'"
                          onmouseout="this.style.borderColor='var(--bd2)';this.style.background='';this.style.transform=''">
                          <div style="font-size:12px;font-weight:500;color:var(--t1);">{title}</div>
                          <div style="font-size:10px;color:var(--t3);margin-top:2px;">
                            {ts} &middot; {n} {'query' if n==1 else 'queries'}</div>
                        </div>""")
                    with hc2:
                        if st.button("Load", key=f"ld_{conv['id']}_{i}", use_container_width=True):
                            st.session_state.messages = load_conversation(conv["id"])
                            st.rerun()
                st.html('</div>')

        # ── LEFT COLUMN: Chat ─────────────────────────────────────────────────
        with col_chat:
            # Chat card header + status (self-contained)
            st.html(f"""<div class="chat-card">
              <div style="display:flex;align-items:flex-start;
                justify-content:space-between;margin-bottom:18px;">
                <div>
                  <div style="font-size:10px;font-weight:700;color:var(--v);
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:5px;">Document QA</div>
                  <div style="font-family:'Instrument Serif',serif;font-size:26px;
                    color:var(--t1);line-height:1.1;">
                    Ask your <em style="font-style:italic;color:var(--v);">documents</em></div>
                </div>
                <div style="display:flex;gap:7px;align-items:center;padding-top:12px;flex-shrink:0;">
                  <span style="font-size:12px;font-weight:600;color:var(--v);
                    background:var(--vp);border:1px solid var(--vpb);
                    padding:4px 12px;border-radius:var(--rf);">{chunks} chunks</span>
                  <span style="font-size:12px;font-weight:700;padding:4px 12px;
                    border-radius:var(--rf);border:1.5px solid;
                    {'color:#059669;background:rgba(5,150,105,0.08);border-color:rgba(5,150,105,0.3);' if ready else 'color:#DC2626;background:rgba(220,38,38,0.08);border-color:rgba(220,38,38,0.3);'} ">
                    {'Ready' if ready else 'Not ready'}</span>
                </div>
              </div>
            </div>""")

            if st.session_state.messages:
                html = ""
                for idx, m in enumerate(st.session_state.messages):
                    delay = f"{idx * 0.05:.2f}s"
                    if m["role"] == "user":
                        html += f"""
                        <div style="display:flex;justify-content:flex-end;margin-bottom:14px;
                          animation:slideUp 0.3s ease {delay} both;">
                          <div style="max-width:74%;padding:13px 17px;
                            background:linear-gradient(135deg,var(--v),var(--v3));
                            color:#fff;border-radius:16px 3px 16px 16px;
                            font-size:14px;line-height:1.65;
                            font-family:'Plus Jakarta Sans',sans-serif;
                            box-shadow:0 3px 12px rgba(124,58,237,0.25);">
                            {m['content']}</div></div>"""
                    else:
                        refs = ""
                        if m.get("references"):
                            refs = '<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:5px;">'
                            for ref in m["references"]:
                                refs += (
                                    f'<span style="font-family:\'JetBrains Mono\',monospace;' 
                                    f'font-size:10px;padding:2px 9px;border-radius:var(--rf);' 
                                    f'color:var(--cyan);background:rgba(6,182,212,0.08);' 
                                    f'border:1px solid rgba(6,182,212,0.25);">{ref}</span>'
                                )
                            refs += "</div>"
                        rfsd = ""
                        if m.get("refused"):
                            rfsd = (
                                '<div style="margin-top:8px;font-size:12px;font-weight:600;'
                                'color:#DC2626;background:rgba(220,38,38,0.08);border:1px solid rgba(220,38,38,0.3);'
                                'padding:5px 12px;border-radius:var(--r);display:inline-block;">'
                                'Insufficient evidence — refusal triggered</div>'
                            )
                        lat = ""
                        if m.get("latency_ms"):
                            lat = (
                                f'<div style="margin-top:5px;font-family:\'JetBrains Mono\','
                                f'monospace;font-size:10px;color:var(--t3);">'
                                f'{m["latency_ms"]} ms</div>'
                            )
                        html += f"""
                        <div style="display:flex;margin-bottom:14px;gap:10px;align-items:flex-start;
                          animation:slideUp 0.3s ease {delay} both;">
                          <div style="width:28px;height:28px;border-radius:8px;flex-shrink:0;
                            margin-top:2px;background:linear-gradient(135deg,var(--vp),var(--s2));
                            display:flex;align-items:center;justify-content:center;
                            font-family:'Instrument Serif',serif;font-size:13px;
                            color:var(--v);border:1px solid var(--vpb);">N</div>
                          <div style="max-width:86%;padding:13px 17px;
                            background:var(--bg);border:1px solid var(--bd2);
                            border-radius:3px 16px 16px 16px;
                            font-size:14px;color:var(--t1);line-height:1.75;
                            font-family:'Plus Jakarta Sans',sans-serif;
                            box-shadow:var(--sh);transition:border-color 0.15s;"
                            onmouseover="this.style.borderColor='var(--vpb)'"
                            onmouseout="this.style.borderColor='var(--bd2)'">
                            {m['content']}{refs}{rfsd}{lat}</div></div>"""
                st.html(f"""<div style="max-height:50vh;overflow-y:auto;margin-bottom:14px;
                  padding:2px;scrollbar-width:thin;
                  scrollbar-color:var(--vpb) transparent;">{html}</div>""")
            else:
                st.html("""
                <div style="text-align:center;padding:44px 24px 36px;
                  background:var(--bg);border:1px solid var(--bd2);
                  border-radius:var(--r2);margin-bottom:14px;animation:fadeIn 0.5s ease both;">
                  <div style="width:44px;height:44px;border-radius:12px;
                    background:linear-gradient(135deg,var(--vp),var(--s2));
                    border:1px solid var(--vpb);display:flex;align-items:center;
                    justify-content:center;margin:0 auto 12px;
                    font-family:'Instrument Serif',serif;font-size:18px;color:var(--v);
                    box-shadow:var(--sh);">N</div>
                  <div style="font-family:'Instrument Serif',serif;font-size:22px;
                    color:var(--t1);margin-bottom:8px;">Ask anything</div>
                  <div style="font-size:13px;color:var(--t3);
                    max-width:280px;margin:0 auto 20px;line-height:1.7;">
                    Upload a PDF on the right, then ask questions here.
                    Every answer is cited.</div>
                  <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
                    <span style="font-size:12px;font-weight:500;color:var(--v);
                      background:var(--vp);border:1px solid var(--vpb);
                      padding:6px 14px;border-radius:var(--rf);cursor:default;transition:all 0.15s;"
                      onmouseover="this.style.background='var(--s3)';this.style.transform='translateY(-1px)'"
                      onmouseout="this.style.background='var(--vp)';this.style.transform=''">
                      What is the main finding?</span>
                    <span style="font-size:12px;font-weight:500;color:var(--v);
                      background:var(--vp);border:1px solid var(--vpb);
                      padding:6px 14px;border-radius:var(--rf);cursor:default;transition:all 0.15s;"
                      onmouseover="this.style.background='var(--s3)';this.style.transform='translateY(-1px)'"
                      onmouseout="this.style.background='var(--vp)';this.style.transform=''">
                      Summarise section 3</span>
                    <span style="font-size:12px;font-weight:500;color:var(--v);
                      background:var(--vp);border:1px solid var(--vpb);
                      padding:6px 14px;border-radius:var(--rf);cursor:default;transition:all 0.15s;"
                      onmouseover="this.style.background='var(--s3)';this.style.transform='translateY(-1px)'"
                      onmouseout="this.style.background='var(--vp)';this.style.transform=''">
                      What are the key risks?</span>
                  </div>
                </div>""")

            # Input bar
            qc, bc = st.columns([6, 1])
            with qc:
                query = st.text_input("Question",
                    placeholder="Ask anything about your documents...",
                    label_visibility="hidden", key="q_in")
            with bc:
                ask = st.button("Send →", use_container_width=True)

            if ask and query:
                if not ready:
                    st.warning("Upload and index a PDF first.")
                else:
                    with st.spinner("Thinking..."):
                        try:
                            resp = requests.post(f"{API_BASE}/query",
                                json={"query":query}, timeout=120)
                            if resp.status_code == 200:
                                d = resp.json()
                                st.session_state.messages.extend([
                                    {"role":"user","content":query},
                                    {"role":"assistant","content":d["answer"],
                                     "references":d["references"],"refused":d["refused"],
                                     "latency_ms":d["latency_ms"]}])
                                record_query(query=query, latency_ms=d["latency_ms"],
                                             refused=d["refused"])
                                st.rerun()
                            else:
                                st.error(f"API error: {resp.json().get('detail',resp.text)}")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot reach API. Run: uv run uvicorn api:app --reload --port 8000")
