"""NeuralDoc — Production SaaS RAG Dashboard."""
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
    def export_as_markdown(m, title="Chat"): return "\n".join(f"{x['role']}: {x['content']}" for x in m)
    def record_query(q, lat, ref, model=""): pass
    def get_stats(): return {"total_queries":0,"answered":0,"refused":0,"refusal_rate":0,"avg_latency_ms":0,"recent":[]}

st.set_page_config(page_title="NeuralDoc", page_icon="N", layout="wide",
                   initial_sidebar_state="collapsed")

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("page","landing"),("messages",[]),("tab","chat"),
              ("dark",True),("authed",False),("username","")]:
    if k not in st.session_state:
        st.session_state[k] = v

API_BASE = "http://localhost:8000"
AUTH_KEY = "neural2024"
D = st.session_state.dark

# ══════════════════════════════════════════════════════════════════════════════
# THEME TOKENS — recomputed every rerun
# ══════════════════════════════════════════════════════════════════════════════
if D:
    BG        = "#0b0f1a"
    BG2       = "#0f1420"
    CARD      = "rgba(255,255,255,0.04)"
    CARD_S    = "rgba(255,255,255,0.07)"
    GLASS     = "rgba(255,255,255,0.05)"
    BORDER    = "rgba(255,255,255,0.08)"
    BORDER_A  = "rgba(139,140,245,0.35)"
    T1        = "#e5e7eb"
    T2        = "#9ca3af"
    T3        = "#6b7280"
    ACC       = "#8b8cf5"
    ACC2      = "#6c6de0"
    ACC_S     = "rgba(139,140,245,0.15)"
    GREEN_C   = "#10b981"; GREEN_B = "rgba(16,185,129,0.15)"
    RED_C     = "#ef4444";  RED_B   = "rgba(239,68,68,0.15)"
    YELLOW_C  = "#f59e0b";  YELLOW_B= "rgba(245,158,11,0.15)"
    CYAN_C    = "#06b6d4"
    PINK_C    = "#ec4899"
    NAV_BG    = "rgba(11,15,26,0.92)"
    INP_BG    = "rgba(255,255,255,0.05)"
    SH        = "0 4px 24px rgba(0,0,0,0.4)"
    SH2       = "0 8px 40px rgba(0,0,0,0.6)"
    PILL_BG   = "rgba(139,140,245,0.12)"
    PILL_BD   = "rgba(139,140,245,0.3)"
else:
    BG        = "#f7f7fb"
    BG2       = "#eeeef8"
    CARD      = "#ffffff"
    CARD_S    = "#f3f3fb"
    GLASS     = "rgba(255,255,255,0.8)"
    BORDER    = "rgba(0,0,0,0.07)"
    BORDER_A  = "rgba(124,111,247,0.4)"
    T1        = "#1a1840"
    T2        = "#4a4870"
    T3        = "#9b98b8"
    ACC       = "#7c6ff7"
    ACC2      = "#6459e8"
    ACC_S     = "rgba(124,111,247,0.1)"
    GREEN_C   = "#059669"; GREEN_B = "rgba(5,150,105,0.1)"
    RED_C     = "#dc2626";  RED_B   = "rgba(220,38,38,0.1)"
    YELLOW_C  = "#d97706";  YELLOW_B= "rgba(217,119,6,0.1)"
    CYAN_C    = "#0891b2"
    PINK_C    = "#db2777"
    NAV_BG    = "rgba(247,247,251,0.95)"
    INP_BG    = "#ffffff"
    SH        = "0 4px 16px rgba(124,111,247,0.08)"
    SH2       = "0 8px 32px rgba(124,111,247,0.15)"
    PILL_BG   = "rgba(124,111,247,0.08)"
    PILL_BD   = "rgba(124,111,247,0.25)"

# ── Kill chrome + inject global theme ──────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],#MainMenu,footer {{
    display:none!important; height:0!important; visibility:hidden!important;
}}
[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],.block-container {{
    background:transparent!important; padding:0!important;
    margin:0!important; max-width:100%!important; border:none!important;
}}
[data-testid="stVerticalBlock"]{{gap:0!important;}}
[data-testid="stVerticalBlock"]>div{{margin:0!important;padding:0!important;}}

html,body{{
    font-family:'Inter',sans-serif!important;
    background:{BG}!important; color:{T1}!important;
}}
[data-testid="stAppViewContainer"]{{background:{BG}!important;}}

/* ─── Buttons ─────────────────────────────────────────────────────── */
[data-testid="stButton"]>button{{
    background:{ACC}!important; color:#fff!important;
    border:none!important; border-radius:8px!important;
    font-family:'Inter',sans-serif!important; font-size:13px!important;
    font-weight:600!important; padding:9px 0!important;
    box-shadow:0 0 0 0 transparent!important;
    transition:all 0.2s ease!important; letter-spacing:0.01em!important;
}}
[data-testid="stButton"]>button:hover{{
    background:{ACC2}!important; transform:translateY(-1px)!important;
    box-shadow:0 0 18px {ACC}55!important;
}}
[data-testid="stButton"]>button:active{{transform:scale(0.97)!important;}}

[data-testid="stDownloadButton"]>button{{
    background:transparent!important; color:{ACC}!important;
    border:1px solid {PILL_BD}!important; border-radius:8px!important;
    font-size:13px!important; font-weight:600!important;
    transition:all 0.2s!important;
}}
[data-testid="stDownloadButton"]>button:hover{{
    background:{PILL_BG}!important; transform:translateY(-1px)!important;
}}

/* ─── Inputs ──────────────────────────────────────────────────────── */
.stTextInput input{{
    background:{INP_BG}!important;
    border:1px solid {BORDER}!important;
    border-radius:10px!important; color:{T1}!important;
    font-family:'Inter',sans-serif!important; font-size:14px!important;
    padding:12px 18px!important;
    transition:all 0.2s!important;
}}
.stTextInput input:focus{{
    border-color:{ACC}!important;
    box-shadow:0 0 0 3px {ACC_S}!important; outline:none!important;
}}
.stTextInput input::placeholder{{color:{T3}!important;}}
.stTextInput label,.stFileUploader label{{display:none!important;}}

/* ─── File uploader ───────────────────────────────────────────────── */
[data-testid="stFileUploaderDropzone"]{{
    background:{INP_BG}!important;
    border:2px dashed {PILL_BD}!important;
    border-radius:12px!important; transition:all 0.2s!important;
}}
[data-testid="stFileUploaderDropzone"]:hover{{
    border-color:{ACC}!important; background:{PILL_BG}!important;
}}
[data-testid="stFileUploaderDropzone"] *{{color:{T2}!important;}}
hr{{border-color:{BORDER}!important;}}

/* ─── Animations ──────────────────────────────────────────────────── */
@keyframes fadeUp{{
    from{{opacity:0;transform:translateY(16px);}}
    to{{opacity:1;transform:translateY(0);}}
}}
@keyframes fadeIn{{from{{opacity:0;}}to{{opacity:1;}}}}
@keyframes pulse{{
    0%,100%{{box-shadow:0 0 0 0 {ACC}44;}}
    50%{{box-shadow:0 0 0 6px transparent;}}
}}
@keyframes float{{
    0%,100%{{transform:translateY(0);}}
    50%{{transform:translateY(-4px);}}
}}
@keyframes shimmer{{
    0%{{background-position:-200% 0;}}
    100%{{background-position:200% 0;}}
}}
@keyframes gradBG{{
    0%{{background-position:0% 50%;}}
    50%{{background-position:100% 50%;}}
    100%{{background-position:0% 50%;}}
}}
</style>
""", unsafe_allow_html=True)


def mdiv(html: str):
    """Shorthand for st.markdown with unsafe_allow_html."""
    st.markdown(html, unsafe_allow_html=True)


def tag(text, color, bg, border):
    return (f'<span style="display:inline-flex;align-items:center;gap:4px;'
            f'font-size:11px;font-weight:600;color:{color};'
            f'background:{bg};border:1px solid {border};'
            f'padding:2px 9px;border-radius:9999px;">{text}</span>')


def sec_label(text):
    return (f'<div style="font-size:10px;font-weight:700;color:{ACC};'
            f'letter-spacing:0.12em;text-transform:uppercase;'
            f'margin-bottom:5px;">{text}</div>')


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "auth":

    mdiv(f"""
    <div style="position:fixed;inset:0;background:{BG};
      background:radial-gradient(ellipse 70% 60% at 30% 20%,
        rgba(139,140,245,0.15),transparent 55%),
        radial-gradient(ellipse 60% 50% at 75% 75%,
        rgba(6,182,212,0.08),transparent 55%),{BG};
      z-index:0;"></div>

    <div style="position:relative;z-index:1;min-height:100vh;
      display:flex;align-items:center;justify-content:center;padding:40px 20px;">
      <div style="width:100%;max-width:400px;animation:fadeUp 0.5s ease both;">

        <!-- Logo -->
        <div style="text-align:center;margin-bottom:32px;">
          <div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:14px;">
            <div style="width:36px;height:36px;border-radius:10px;
              background:linear-gradient(135deg,{ACC},{CYAN_C});
              display:flex;align-items:center;justify-content:center;
              font-family:'Instrument Serif',serif;font-size:18px;
              color:#fff;box-shadow:0 4px 16px {ACC}44;">N</div>
            <span style="font-family:'Instrument Serif',serif;font-size:22px;
              color:{T1};">NeuralDoc</span>
          </div>
          <h2 style="font-family:'Instrument Serif',serif;font-size:26px;
            color:{T1};margin-bottom:6px;font-weight:400;">Welcome back</h2>
          <p style="font-size:14px;color:{T3};">
            Sign in to your workspace</p>
        </div>

        <!-- Card -->
        <div style="background:{CARD};border:1px solid {BORDER};
          border-radius:18px;padding:32px;box-shadow:{SH2};
          backdrop-filter:blur(12px);">
    """)

    username = st.text_input("Username", placeholder="Username...",
                              label_visibility="hidden", key="auth_user")
    mdiv('<div style="height:10px;"></div>')
    pwd = st.text_input("Password", type="password",
                         placeholder="Password or access key...",
                         label_visibility="hidden", key="auth_pwd")
    mdiv('<div style="height:16px;"></div>')

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sign In", use_container_width=True, key="signin_btn"):
            if pwd == AUTH_KEY:
                st.session_state.authed = True
                st.session_state.username = username or "User"
                st.session_state.page = "chat"
                st.rerun()
            else:
                st.error("Incorrect credentials.")
    with c2:
        if st.button("← Back", use_container_width=True, key="auth_back"):
            st.session_state.page = "landing"
            st.rerun()

    mdiv(f"""
        </div>
        <div style="text-align:center;margin-top:18px;">
          <span style="font-size:12px;color:{T3};">Demo credentials: &nbsp;</span>
          <code style="font-size:11px;background:{PILL_BG};color:{ACC};
            padding:3px 10px;border-radius:6px;border:1px solid {PILL_BD};">
            neural2024</code>
        </div>
      </div>
    </div>
    """)


# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "landing":

    # ── Navbar ─────────────────────────────────────────────────────────────────
    mdiv(f"""
    <nav style="position:sticky;top:0;z-index:200;height:52px;
      background:{NAV_BG};backdrop-filter:blur(16px);
      border-bottom:1px solid {BORDER};
      display:flex;align-items:center;justify-content:space-between;
      padding:0 48px;animation:fadeIn 0.4s ease both;">
      <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:26px;height:26px;border-radius:7px;
          background:linear-gradient(135deg,{ACC},{CYAN_C});
          display:flex;align-items:center;justify-content:center;
          font-family:'Instrument Serif',serif;font-size:13px;color:#fff;">N</div>
        <span style="font-family:'Instrument Serif',serif;font-size:17px;
          color:{T1};">NeuralDoc</span>
      </div>
      <div style="font-size:11px;font-weight:600;color:{ACC};
        background:{PILL_BG};border:1px solid {PILL_BD};
        padding:4px 14px;border-radius:9999px;letter-spacing:0.06em;
        text-transform:uppercase;">Production RAG v1.0</div>
    </nav>
    """)

    # Dark mode toggle row (top right, no overlap)
    _sp, _dm = st.columns([10, 1])
    with _dm:
        mdiv('<div style="padding:8px 16px 0 0;display:flex;justify-content:flex-end;">')
        if st.button("☀" if D else "☽", key="dm_land", use_container_width=False):
            st.session_state.dark = not D
            st.rerun()
        mdiv('</div>')

    # Background gradient blobs
    mdiv(f"""
    <div style="position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;">
      <div style="position:absolute;width:600px;height:600px;border-radius:50%;
        background:radial-gradient(circle,{ACC}22,transparent 70%);
        top:-200px;left:-100px;animation:float 12s ease-in-out infinite;"></div>
      <div style="position:absolute;width:500px;height:500px;border-radius:50%;
        background:radial-gradient(circle,{CYAN_C}18,transparent 70%);
        bottom:-150px;right:-100px;animation:float 15s ease-in-out 3s infinite;"></div>
    </div>

    <!-- Hero -->
    <div style="position:relative;z-index:1;max-width:800px;margin:0 auto;
      padding:72px 48px 0;text-align:center;animation:fadeUp 0.6s ease 0.1s both;">
      <div style="display:inline-flex;align-items:center;gap:6px;margin-bottom:24px;
        font-size:12px;font-weight:600;color:{ACC};
        background:{PILL_BG};border:1px solid {PILL_BD};
        padding:5px 16px;border-radius:9999px;">
        <div style="width:6px;height:6px;border-radius:50%;background:{GREEN_C};
          animation:pulse 2s ease-in-out infinite;"></div>
        Zero hallucination tolerance
      </div>
      <h1 style="font-family:'Instrument Serif',serif;
        font-size:clamp(40px,5.5vw,64px);color:{T1};
        line-height:1.06;letter-spacing:-1px;margin-bottom:6px;font-weight:400;">
        Ask anything.
      </h1>
      <h1 style="font-family:'Instrument Serif',serif;
        font-size:clamp(40px,5.5vw,64px);font-style:italic;color:{ACC};
        line-height:1.06;letter-spacing:-1px;margin-bottom:24px;font-weight:400;">
        Know everything.
      </h1>
      <p style="font-size:16px;color:{T2};line-height:1.8;
        max-width:500px;margin:0 auto 36px;">
        A <strong style="color:{T1};">production-grade</strong> RAG system with
        <strong style="color:{T1};">inline citations</strong>, hybrid retrieval,
        persistent history, and live analytics.
      </p>
    </div>
    """)

    # CTA
    _l, _m, _r = st.columns([3, 2, 3])
    with _m:
        mdiv(f"""<style>
        [data-testid="stButton"] button{{
          height:50px!important;font-size:15px!important;
          border-radius:9999px!important;
          background:linear-gradient(135deg,{ACC},{CYAN_C})!important;
          box-shadow:0 4px 24px {ACC}44!important;
        }}
        </style>""")
        if st.button("Open App  →", key="launch_btn", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()

    # Stats bar
    stat_items = [("0%","Hallucination"),("3×","Retrieval Modes"),
                  ("100%","Local & Private"),("∞","Documents")]
    stats_html = ""
    for i,(v,l) in enumerate(stat_items):
        border_r = f"border-right:1px solid {BORDER};" if i<3 else ""
        stats_html += f"""
        <div style="flex:1;padding:20px 12px;text-align:center;{border_r}
          transition:background 0.18s;cursor:default;"
          onmouseover="this.style.background='{PILL_BG}'"
          onmouseout="this.style.background='transparent'">
          <div style="font-family:'Instrument Serif',serif;font-size:28px;
            color:{ACC};line-height:1;margin-bottom:4px;">{v}</div>
          <div style="font-size:10px;font-weight:700;color:{T3};
            letter-spacing:0.1em;text-transform:uppercase;">{l}</div>
        </div>"""

    mdiv(f"""
    <div style="position:relative;z-index:1;display:flex;max-width:700px;
      margin:44px auto 0;background:{CARD};border:1px solid {BORDER};
      border-radius:20px;overflow:hidden;box-shadow:{SH};
      animation:fadeUp 0.6s ease 0.3s both;">
      {stats_html}
    </div>
    """)

    # Pillars grid
    pillars = [
        ("01","Ingestion","Smart PDF Parsing","Multi-column layouts, tables, complex structures.",
         "pdfplumber",GREEN_C,f"rgba(16,185,129,0.2)","rgba(16,185,129,0.08)"),
        ("02","Chunking","Semantic Chunking","Header-aware 500-800 token chunks with metadata.",
         "tiktoken",ACC,PILL_BD,PILL_BG),
        ("03","Retrieval","Hybrid Search","BM25 + dense vector via Reciprocal Rank Fusion.",
         "RRF Fusion",CYAN_C,"rgba(6,182,212,0.3)","rgba(6,182,212,0.08)"),
        ("04","Reranking","Cross-Encoder","Top 20 re-scored — best 5 reach generation.",
         "ms-marco",YELLOW_C,f"rgba(245,158,11,0.3)","rgba(245,158,11,0.08)"),
        ("05","Generation","Attributed Answers","Every claim has [Source, p.X] citation.",
         "LangGraph",ACC,PILL_BD,PILL_BG),
        ("06","Safety","Hard Refusal Gate","Below threshold = fixed refusal. No hallucination.",
         "Threshold Gate",PINK_C,"rgba(236,72,153,0.3)","rgba(236,72,153,0.08)"),
    ]
    cards = "".join([
        f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:14px;'
        f'padding:22px;backdrop-filter:blur(8px);'
        f'transition:transform 0.2s,box-shadow 0.2s,border-color 0.2s;"'
        f'onmouseover="this.style.transform=\'translateY(-4px)\';'
        f'this.style.boxShadow=\'0 8px 32px {tc}33\';'
        f'this.style.borderColor=\'{tc}55\'"'
        f'onmouseout="this.style.transform=\'\';'
        f'this.style.boxShadow=\'\';this.style.borderColor=\'{BORDER}\'">'
        f'<div style="font-size:10px;font-weight:700;color:{T3};letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:6px;">{num} — {cat}</div>'
        f'<div style="font-size:14px;font-weight:700;color:{T1};margin-bottom:5px;">{t}</div>'
        f'<div style="font-size:12px;color:{T2};line-height:1.7;">{b}</div>'
        f'<span style="display:inline-block;margin-top:10px;font-size:10px;font-weight:700;'
        f'padding:2px 9px;border-radius:9999px;color:{tc};'
        f'background:{tbg};border:1px solid {tbd};">{tag_text}</span></div>'
        for num,cat,t,b,tag_text,tc,tbd,tbg in pillars
    ])

    steps = [("Parse","pdfplumber"),("Chunk","tiktoken"),("Embed","miniLM"),
             ("BM25","keyword"),("Fuse","RRF"),("Rerank","cross-enc"),
             ("Generate","llama3.1"),("Cite","attributed")]
    pipe = ""
    for i,(s,sub) in enumerate(steps):
        pipe += (f'<div style="display:flex;flex-direction:column;align-items:center;'
                 f'gap:4px;flex:1;padding:7px 3px;border-radius:8px;transition:all 0.16s;cursor:default;"'
                 f'onmouseover="this.style.background=\'{PILL_BG}\'"'
                 f'onmouseout="this.style.background=\'\'">'
                 f'<div style="font-size:11px;font-weight:700;color:{T1};">{s}</div>'
                 f'<div style="font-size:10px;color:{T3};">{sub}</div></div>')
        if i<7:
            pipe += f'<div style="color:{BORDER_A};font-size:12px;flex-shrink:0;">&rarr;</div>'

    mdiv(f"""
    <div style="position:relative;z-index:1;max-width:1100px;margin:80px auto 0;padding:0 48px;">
      <div style="font-size:10px;font-weight:700;color:{ACC};letter-spacing:0.12em;
        text-transform:uppercase;margin-bottom:8px;">Capabilities</div>
      <div style="font-family:'Instrument Serif',serif;font-size:30px;color:{T1};
        margin-bottom:24px;font-weight:400;">
        Six <em style="font-style:italic;color:{ACC};">pillars</em> of precision</div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">{cards}</div>
    </div>
    <div style="position:relative;z-index:1;max-width:1100px;margin:64px auto 0;padding:0 48px;">
      <div style="font-size:10px;font-weight:700;color:{ACC};letter-spacing:0.12em;
        text-transform:uppercase;margin-bottom:8px;">Architecture</div>
      <div style="font-family:'Instrument Serif',serif;font-size:30px;color:{T1};
        margin-bottom:22px;font-weight:400;">
        The <em style="font-style:italic;color:{ACC};">pipeline</em></div>
      <div style="display:flex;align-items:center;justify-content:space-between;
        background:{CARD};border:1px solid {BORDER};border-radius:14px;
        padding:22px 24px;backdrop-filter:blur(8px);">{pipe}</div>
    </div>
    <div style="max-width:1100px;margin:60px auto 0;padding:20px 48px 64px;
      border-top:1px solid {BORDER};
      display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
      <span style="font-size:12px;color:{T3};">NeuralDoc — Production RAG System</span>
      <span style="font-size:12px;color:{T3};">Ollama · ChromaDB · LangGraph · FastAPI</span>
    </div>
    """)


# ══════════════════════════════════════════════════════════════════════════════
# CHAT / ANALYTICS APP
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":

    def get_health():
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3).json()
            r["_ok"] = True; return r
        except Exception:
            return {"pipeline_ready":False,"total_chunks":0,"indexed_files":[],"_ok":False}

    h      = get_health()
    api_ok = h.get("_ok", False)
    ready  = h.get("pipeline_ready", False)
    chunks = h.get("total_chunks", 0)
    files  = h.get("indexed_files", [])

    # Status pill values (plain Python strings — no HTML injection risk)
    if ready:
        _sc = GREEN_C; _sb = GREEN_B; _sd = GREEN_C
        _st = f"Ready · {chunks} chunks"
    elif api_ok:
        _sc = YELLOW_C; _sb = YELLOW_B; _sd = YELLOW_C
        _st = "API online · No docs"
    else:
        _sc = RED_C; _sb = RED_B; _sd = RED_C
        _st = "API offline"

    tab = st.session_state.tab
    tab_chat_s = (f"background:{ACC};color:#fff;"
                  f"box-shadow:0 2px 10px {ACC}55;" if tab=="chat"
                  else f"color:{T2};background:transparent;")
    tab_anlyt_s = (f"background:{ACC};color:#fff;"
                   f"box-shadow:0 2px 10px {ACC}55;" if tab=="analytics"
                   else f"color:{T2};background:transparent;")

    uname = st.session_state.username or "User"
    initial = uname[0].upper()

    # ── NAVBAR — logo+home | tab pill | dark+user ────────────────────────────
    mdiv(f"""
    <nav style="position:sticky;top:0;z-index:200;height:52px;
      background:{NAV_BG};backdrop-filter:blur(16px);
      border-bottom:1px solid {BORDER};
      display:flex;align-items:center;justify-content:space-between;
      padding:0 32px;animation:fadeIn 0.4s ease both;">

      <!-- LEFT: Logo + Home button placeholder -->
      <div style="display:flex;align-items:center;gap:10px;min-width:160px;">
        <div style="width:26px;height:26px;border-radius:7px;
          background:linear-gradient(135deg,{ACC},{CYAN_C});
          display:flex;align-items:center;justify-content:center;
          font-family:'Instrument Serif',serif;font-size:13px;color:#fff;">N</div>
        <span style="font-family:'Instrument Serif',serif;font-size:16px;
          color:{T1};">NeuralDoc</span>
      </div>

      <!-- CENTER: Tab pill -->
      <div style="display:flex;gap:2px;background:{CARD_S};
        border:1px solid {BORDER};border-radius:9px;padding:3px;">
        <div style="padding:5px 20px;border-radius:7px;font-size:13px;
          font-weight:600;{tab_chat_s}transition:all 0.18s;cursor:default;">Chat</div>
        <div style="padding:5px 20px;border-radius:7px;font-size:13px;
          font-weight:600;{tab_anlyt_s}transition:all 0.18s;cursor:default;">Analytics</div>
      </div>

      <!-- RIGHT: status + dark toggle + avatar -->
      <div style="display:flex;align-items:center;gap:10px;min-width:160px;
        justify-content:flex-end;">
        <div style="display:inline-flex;align-items:center;gap:5px;font-size:12px;
          font-weight:600;padding:4px 12px;border-radius:9999px;
          color:{_sc};background:{_sb};border:1px solid {_sc}44;">
          <div style="width:5px;height:5px;border-radius:50%;background:{_sd};
            {'animation:pulse 1.5s ease-in-out infinite;' if ready else ''}"></div>
          {_st}
        </div>
        <div style="width:28px;height:28px;border-radius:50%;
          background:linear-gradient(135deg,{ACC},{PINK_C});
          display:flex;align-items:center;justify-content:center;
          font-size:12px;font-weight:700;color:#fff;
          box-shadow:0 2px 8px {ACC}44;">{initial}</div>
      </div>
    </nav>
    """)

    # ── Toolbar — minimal, one row ────────────────────────────────────────────
    mdiv(f'<div style="padding:10px 32px;display:flex;align-items:center;gap:8px;">')
    _cols = st.columns([1, 1, 1, 1, 1, 0.8, 0.5, 6])

    with _cols[0]:
        if st.button("⌂ Home", key="home_btn", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.page = "landing"
            st.rerun()
    with _cols[1]:
        if st.button("Clear", key="clr_btn", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.messages = []
            st.rerun()
    with _cols[2]:
        chat_label = "Analytics →" if tab == "chat" else "← Chat"
        if st.button(chat_label, key="tab_switch", use_container_width=True):
            st.session_state.tab = "analytics" if tab=="chat" else "chat"
            st.rerun()
    with _cols[3]:
        if st.button("☀" if D else "☽ Dark", key="dm_chat", use_container_width=True):
            st.session_state.dark = not D
            st.rerun()
    with _cols[4]:
        if st.button("Sign Out", key="logout_btn", use_container_width=True):
            st.session_state.authed = False
            st.session_state.username = ""
            st.session_state.messages = []
            st.session_state.page = "auth"
            st.rerun()
    with _cols[5]:
        if st.session_state.messages:
            md = export_as_markdown(st.session_state.messages, "NeuralDoc Chat")
            st.download_button("Export", data=md,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown", use_container_width=True, key="exp_md")

    mdiv('</div>')

    # ══════════════════════════════════════════════════════════════════════════
    # ANALYTICS TAB
    # ══════════════════════════════════════════════════════════════════════════
    if tab == "analytics":
        stats = get_stats()

        # KPI cards
        ans_pct = round((stats["answered"]/stats["total_queries"]*100) if stats["total_queries"] else 0)
        ref_pct = round((stats["refused"]/stats["total_queries"]*100)  if stats["total_queries"] else 0)

        kpis = [
            ("⬡","Total Queries",   str(stats["total_queries"]),  ACC,    f"rgba(139,140,245,0.12)", ""),
            ("✓","Answered",        str(stats["answered"]),        GREEN_C, GREEN_B,
             f'<div style="height:3px;background:{GREEN_C}22;border-radius:2px;overflow:hidden;margin-top:8px;"><div style="height:100%;width:{ans_pct}%;background:{GREEN_C};border-radius:2px;transition:width 1s;"></div></div>'),
            ("✕","Refused",         str(stats["refused"]),         RED_C,   RED_B,
             f'<div style="height:3px;background:{RED_C}22;border-radius:2px;overflow:hidden;margin-top:8px;"><div style="height:100%;width:{ref_pct}%;background:{RED_C};border-radius:2px;"></div></div>'),
            ("◎","Refusal Rate",    f"{stats['refusal_rate']}%",   YELLOW_C,YELLOW_B,
             f'<div style="font-size:10px;color:{T3};margin-top:6px;">{"Good" if stats["refusal_rate"]<20 else "High — review threshold"}</div>'),
            ("⚡","Avg Latency",     f"{int(stats['avg_latency_ms'])}ms", CYAN_C, f"rgba(6,182,212,0.12)",
             f'<div style="font-size:10px;color:{T3};margin-top:6px;">{"Fast" if stats["avg_latency_ms"]<3000 else "Consider GPU"}</div>'),
        ]

        kpi_html = ""
        for icon, lbl, val, col, bg, extra in kpis:
            kpi_html += f"""
            <div style="background:{bg};border:1px solid {col}33;border-radius:16px;
              padding:22px 18px;text-align:center;backdrop-filter:blur(8px);
              transition:transform 0.2s,box-shadow 0.2s,border-color 0.2s;
              animation:fadeUp 0.4s ease both;"
              onmouseover="this.style.transform='translateY(-5px)';
                this.style.boxShadow='0 8px 32px {col}33';
                this.style.borderColor='{col}55'"
              onmouseout="this.style.transform='';
                this.style.boxShadow='';this.style.borderColor='{col}33'">
              <div style="font-size:18px;color:{col};margin-bottom:6px;">{icon}</div>
              <div style="font-family:'Instrument Serif',serif;font-size:36px;
                color:{col};line-height:1;margin-bottom:5px;">{val}</div>
              <div style="font-size:10px;font-weight:700;color:{T3};
                letter-spacing:0.1em;text-transform:uppercase;">{lbl}</div>
              {extra}
            </div>"""

        # Recent queries
        rows_html = ""
        for q in stats["recent"]:
            ic = RED_C if q["refused"] else GREEN_C
            symbol = "✕" if q["refused"] else "✓"
            rows_html += f"""
            <div style="display:flex;align-items:center;gap:10px;
              padding:10px 14px;border-radius:8px;margin-bottom:4px;
              background:{CARD_S};border:1px solid {BORDER};
              transition:all 0.15s;"
              onmouseover="this.style.borderColor='{BORDER_A}';
                this.style.transform='translateX(2px)'"
              onmouseout="this.style.borderColor='{BORDER}';
                this.style.transform=''">
              <div style="width:20px;height:20px;border-radius:50%;flex-shrink:0;
                background:{ic}20;border:1.5px solid {ic}55;
                display:flex;align-items:center;justify-content:center;
                font-size:9px;font-weight:700;color:{ic};">{symbol}</div>
              <span style="flex:1;font-size:13px;color:{T1};
                overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                {q["query"][:80]}</span>
              <code style="font-family:'JetBrains Mono',monospace;font-size:11px;
                color:{T3};background:{PILL_BG};padding:2px 8px;
                border-radius:6px;">{q["latency_ms"]}ms</code>
            </div>"""

        empty_q = f"""
        <div style="display:flex;flex-direction:column;align-items:center;
          justify-content:center;padding:48px 24px;
          border:2px dashed {BORDER};border-radius:12px;
          background:linear-gradient(135deg,{PILL_BG},transparent);">
          <div style="font-size:36px;margin-bottom:12px;opacity:0.4;">◎</div>
          <div style="font-size:14px;font-weight:600;color:{T2};margin-bottom:4px;">
            No queries yet</div>
          <div style="font-size:12px;color:{T3};text-align:center;max-width:220px;">
            Send a message in the Chat tab to start tracking performance.</div>
        </div>"""

        # System status rows
        sys_items = [
            ("⬡ FastAPI",     "Online" if api_ok else "Offline",
             GREEN_C if api_ok else RED_C, GREEN_B if api_ok else RED_B),
            ("⬡ RAG Pipeline", "Ready" if ready else "No docs",
             GREEN_C if ready else (YELLOW_C if api_ok else RED_C),
             GREEN_B if ready else (YELLOW_B if api_ok else RED_B)),
            ("⬡ Chunks Indexed", str(chunks), ACC, PILL_BG),
            ("⬡ Files Indexed",  str(len(files)), ACC, PILL_BG),
        ]
        sys_html = ""
        for label, val, col, bg in sys_items:
            sys_html += f"""
            <div style="display:flex;align-items:center;
              justify-content:space-between;padding:8px 0;
              border-bottom:1px solid {BORDER};">
              <span style="font-size:13px;color:{T2};">{label}</span>
              <span style="font-size:11px;font-weight:700;padding:2px 10px;
                border-radius:9999px;color:{col};background:{bg};
                border:1px solid {col}44;">{val}</span>
            </div>"""

        mdiv(f"""
        <div style="padding:0 32px 48px;">
          <!-- Header -->
          <div style="margin-bottom:20px;animation:fadeUp 0.4s ease both;">
            <div style="font-size:10px;font-weight:700;color:{ACC};
              letter-spacing:0.12em;text-transform:uppercase;margin-bottom:5px;">
              Live Observability</div>
            <div style="font-family:'Instrument Serif',serif;font-size:28px;color:{T1};">
              Query <em style="font-style:italic;color:{ACC};">Analytics</em></div>
          </div>

          <!-- KPI row -->
          <div style="display:grid;grid-template-columns:repeat(5,1fr);
            gap:12px;margin-bottom:16px;">
            {kpi_html}
          </div>

          <!-- Bottom: Recent + Status + Notes -->
          <div style="display:grid;grid-template-columns:2fr 1fr;gap:14px;">

            <!-- Recent queries -->
            <div style="background:{CARD};border:1px solid {BORDER};
              border-radius:16px;padding:22px;
              backdrop-filter:blur(8px);">
              <div style="display:flex;align-items:center;
                justify-content:space-between;margin-bottom:14px;">
                <div style="font-size:13px;font-weight:700;color:{T1};">
                  Recent Queries</div>
                <span style="font-size:11px;color:{T3};background:{PILL_BG};
                  padding:3px 10px;border-radius:9999px;border:1px solid {PILL_BD};">
                  {len(stats["recent"])} of {stats["total_queries"]}</span>
              </div>
              <div style="max-height:340px;overflow-y:auto;
                scrollbar-width:thin;scrollbar-color:{PILL_BD} transparent;">
                {"".join([rows_html]) if stats["recent"] else empty_q}
              </div>
            </div>

            <!-- Right column: status + notes -->
            <div style="display:flex;flex-direction:column;gap:12px;">

              <!-- System Status -->
              <div style="background:{CARD};border:1px solid {BORDER};
                border-radius:16px;padding:20px;backdrop-filter:blur(8px);">
                <div style="font-size:10px;font-weight:700;color:{T3};
                  letter-spacing:0.1em;text-transform:uppercase;margin-bottom:12px;">
                  System Status</div>
                {sys_html}
              </div>

              <!-- MLOps Notes — styled as info alert -->
              <div style="background:linear-gradient(135deg,{PILL_BG},{CARD});
                border:1px solid {BORDER_A};border-radius:16px;padding:20px;
                flex:1;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                  <div style="width:24px;height:24px;border-radius:6px;
                    background:{ACC};display:flex;align-items:center;
                    justify-content:center;font-size:12px;color:#fff;">ℹ</div>
                  <div style="font-size:12px;font-weight:700;color:{ACC};">
                    MLOps Notes</div>
                </div>
                <div style="font-size:12px;color:{T2};line-height:1.85;">
                  Refusal &gt;25%: threshold too strict.<br>
                  Latency &gt;5s: try GPU or GPT-4o-mini.<br>
                  Rolling window: last 200 queries.
                </div>
                <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:12px;">
                  <code style="font-size:10px;color:{ACC};background:{PILL_BG};
                    padding:2px 8px;border-radius:6px;border:1px solid {PILL_BD};">
                    analytics.json</code>
                  <code style="font-size:10px;color:{CYAN_C};
                    background:rgba(6,182,212,0.08);padding:2px 8px;border-radius:6px;
                    border:1px solid rgba(6,182,212,0.25);">200 query window</code>
                </div>
              </div>

            </div>
          </div>
        </div>
        """)

    # ══════════════════════════════════════════════════════════════════════════
    # CHAT TAB
    # ══════════════════════════════════════════════════════════════════════════
    else:
        mdiv(f'<div style="padding:0 32px 48px;">')
        col_chat, col_right = st.columns([3, 2], gap="large")

        # ── RIGHT: Upload ───────────────────────────────────────────────────────
        with col_right:
            mdiv(f"""
            <div style="background:{CARD};border:1px solid {BORDER};
              border-radius:16px;padding:24px;backdrop-filter:blur(8px);
              margin-bottom:14px;animation:fadeUp 0.5s ease 0.1s both;
              transition:box-shadow 0.2s,border-color 0.2s;"
              onmouseover="this.style.boxShadow='{SH2}';
                this.style.borderColor='{BORDER_A}'"
              onmouseout="this.style.boxShadow='';
                this.style.borderColor='{BORDER}'">
            """)

            uh1, uh2 = st.columns([3, 1])
            with uh1:
                mdiv(f"""<div style="margin-bottom:14px;">
                  {sec_label("Knowledge Base")}
                  <div style="font-family:'Instrument Serif',serif;
                    font-size:20px;color:{T1};">Upload
                    <em style="font-style:italic;color:{ACC};">documents</em></div>
                </div>""")
            with uh2:
                mdiv('<div style="height:24px;"></div>')
                if st.button("Clear KB", key="clear_idx", use_container_width=True):
                    try:
                        r = requests.delete(f"{API_BASE}/index", timeout=15)
                        if r.status_code == 200:
                            st.success("Index cleared.")
                            st.rerun()
                        else:
                            st.error(f"Error {r.status_code}")
                    except Exception:
                        st.error("API offline.")

            mdiv(f"""
            <div style="background:{PILL_BG};border:2px dashed {PILL_BD};
              border-radius:12px;padding:16px;margin-bottom:10px;text-align:center;
              transition:all 0.18s;"
              onmouseover="this.style.borderColor='{ACC}';
                this.style.background='{ACC_S}';this.style.transform='scale(1.01)'"
              onmouseout="this.style.borderColor='{PILL_BD}';
                this.style.background='{PILL_BG}';this.style.transform=''">
              <div style="font-size:24px;margin-bottom:6px;opacity:0.6;">⬆</div>
              <div style="font-size:13px;font-weight:500;color:{T1};margin-bottom:3px;">
                Drop your PDF below</div>
              <div style="font-size:11px;color:{T3};">
                Parsed → Chunked → Embedded → Indexed</div>
            </div>
            """)

            uploaded = st.file_uploader("PDF", type=["pdf"], label_visibility="hidden")
            if uploaded:
                mdiv(f"""
                <div style="background:{GREEN_B};border:1px solid {GREEN_C}44;
                  border-radius:8px;padding:9px 13px;margin-bottom:9px;">
                  <div style="font-size:13px;font-weight:600;color:{T1};">
                    {uploaded.name}</div>
                  <div style="font-size:11px;color:{GREEN_C};margin-top:1px;">
                    {uploaded.size//1024} KB · Ready to index</div>
                </div>""")
                if st.button("Index Document", use_container_width=True, key="idx_btn"):
                    with st.spinner("Processing PDF..."):
                        try:
                            resp = requests.post(
                                f"{API_BASE}/ingest",
                                files={"file":(uploaded.name,uploaded,"application/pdf")},
                                timeout=120)
                            if resp.status_code == 200:
                                d = resp.json()
                                st.success(f"Indexed {d['chunks_indexed']} chunks")
                                st.rerun()
                            else:
                                st.error(f"Error: {resp.text}")
                        except requests.exceptions.ConnectionError:
                            st.error("API offline — run: uv run uvicorn api:app --reload --port 8000")
                        except Exception as e:
                            st.error(str(e))

            if files:
                mdiv(f'<div style="font-size:10px;font-weight:700;color:{T3};'
                     f'letter-spacing:0.08em;text-transform:uppercase;margin:10px 0 6px;">'
                     f'Indexed files</div>')
                for f in files:
                    fname = f.replace("\\","/").split("/")[-1]
                    mdiv(f"""
                    <div style="background:{CARD_S};border:1px solid {BORDER};
                      border-radius:8px;padding:7px 12px;margin-bottom:4px;
                      display:flex;align-items:center;transition:all 0.15s;"
                      onmouseover="this.style.borderColor='{BORDER_A}';
                        this.style.transform='translateX(2px)'"
                      onmouseout="this.style.borderColor='{BORDER}';
                        this.style.transform=''">
                      <span style="font-size:12px;color:{T1};flex:1;">{fname}</span>
                      <span style="font-size:10px;font-weight:700;padding:2px 8px;
                        border-radius:9999px;color:{GREEN_C};background:{GREEN_B};
                        border:1px solid {GREEN_C}44;">indexed</span>
                    </div>""")

            mdiv(f"""
            <div style="margin-top:12px;background:{CARD_S};border:1px solid {BORDER};
              border-radius:10px;padding:13px 14px;">
              <div style="font-size:10px;font-weight:700;color:{T3};
                letter-spacing:0.08em;text-transform:uppercase;margin-bottom:7px;">Tips</div>
              <div style="font-size:12px;color:{T2};line-height:1.9;">
                Click <strong style="color:{ACC};">Clear KB</strong> before switching documents.<br>
                Ask precise questions for best citation accuracy.<br>
                Every answer includes inline source references.<br>
                Unanswerable queries return a refusal, not a guess.
              </div>
            </div>
            """)
            mdiv('</div>')  # close upload card

            # Chat History
            convs = load_all_conversations()
            if convs:
                mdiv(f"""
                <div style="background:{CARD};border:1px solid {BORDER};
                  border-radius:16px;padding:18px 20px 12px;
                  backdrop-filter:blur(8px);animation:fadeUp 0.5s ease 0.2s both;">
                  <div style="font-size:10px;font-weight:700;color:{ACC};
                    letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px;">
                    Chat History</div>
                """)
                for i, conv in enumerate(convs[:5]):
                    ts  = conv["timestamp"][:10]
                    ttl = conv["title"][:32] + ("…" if len(conv["title"])>32 else "")
                    n   = len([m for m in conv["messages"] if m["role"]=="user"])
                    hc1, hc2 = st.columns([4, 1])
                    with hc1:
                        mdiv(f"""
                        <div style="padding:7px 10px;border-radius:8px;
                          border:1px solid {BORDER};margin-bottom:4px;
                          transition:all 0.15s;cursor:default;"
                          onmouseover="this.style.borderColor='{BORDER_A}';
                            this.style.background='{PILL_BG}'"
                          onmouseout="this.style.borderColor='{BORDER}';
                            this.style.background=''">
                          <div style="font-size:12px;font-weight:500;color:{T1};">
                            {ttl}</div>
                          <div style="font-size:10px;color:{T3};margin-top:1px;">
                            {ts} · {n} quer{'y' if n==1 else 'ies'}</div>
                        </div>""")
                    with hc2:
                        if st.button("Load", key=f"ld_{conv['id']}_{i}",
                                     use_container_width=True):
                            st.session_state.messages = load_conversation(conv["id"])
                            st.rerun()
                mdiv('</div>')

        # ── LEFT: Chat ──────────────────────────────────────────────────────────
        with col_chat:
            mdiv(f"""
            <div style="background:{CARD};border:1px solid {BORDER};
              border-radius:16px;padding:22px 24px 20px;
              backdrop-filter:blur(8px);animation:fadeUp 0.5s ease both;">
              <div style="display:flex;align-items:flex-start;
                justify-content:space-between;margin-bottom:18px;">
                <div>
                  {sec_label("Document QA")}
                  <div style="font-family:'Instrument Serif',serif;
                    font-size:24px;color:{T1};">
                    Ask your
                    <em style="font-style:italic;color:{ACC};">documents</em>
                  </div>
                </div>
                <div style="display:flex;gap:6px;padding-top:14px;flex-shrink:0;">
                  <span style="font-size:11px;font-weight:600;color:{ACC};
                    background:{PILL_BG};border:1px solid {PILL_BD};
                    padding:3px 10px;border-radius:9999px;">{chunks} chunks</span>
                  <span style="font-size:11px;font-weight:700;padding:3px 10px;
                    border-radius:9999px;border:1px solid;
                    {'color:'+GREEN_C+';background:'+GREEN_B+';border-color:'+GREEN_C+'44;' if ready
                     else 'color:'+RED_C+';background:'+RED_B+';border-color:'+RED_C+'44;'}">
                    {'Ready' if ready else 'Not ready'}
                  </span>
                </div>
              </div>
            """)

            # Messages
            if st.session_state.messages:
                msgs_html = ""
                for idx, m in enumerate(st.session_state.messages):
                    delay = min(idx * 0.04, 0.24)
                    if m["role"] == "user":
                        msgs_html += f"""
                        <div style="display:flex;justify-content:flex-end;
                          margin-bottom:12px;animation:fadeUp 0.3s ease {delay:.2f}s both;">
                          <div style="max-width:74%;padding:12px 16px;
                            background:linear-gradient(135deg,{ACC},{ACC2});
                            color:#fff;border-radius:14px 3px 14px 14px;
                            font-size:14px;line-height:1.6;
                            box-shadow:0 2px 12px {ACC}44;">
                            {m['content']}</div>
                        </div>"""
                    else:
                        refs = ""
                        if m.get("references"):
                            refs = '<div style="margin-top:9px;display:flex;flex-wrap:wrap;gap:4px;">'
                            for ref in m["references"]:
                                refs += (f'<code style="font-family:JetBrains Mono,monospace;'
                                         f'font-size:10px;padding:2px 8px;border-radius:6px;'
                                         f'color:{CYAN_C};background:rgba(6,182,212,0.08);'
                                         f'border:1px solid rgba(6,182,212,0.2);">{ref}</code>')
                            refs += "</div>"
                        rfsd = ""
                        if m.get("refused"):
                            rfsd = (f'<div style="margin-top:7px;font-size:12px;font-weight:600;'
                                    f'color:{RED_C};background:{RED_B};'
                                    f'border:1px solid {RED_C}44;padding:5px 11px;'
                                    f'border-radius:8px;display:inline-block;">'
                                    f'Insufficient evidence — refusal triggered</div>')
                        lat = ""
                        if m.get("latency_ms"):
                            lat = (f'<div style="margin-top:4px;font-family:JetBrains Mono,'
                                   f'monospace;font-size:10px;color:{T3};">'
                                   f'{m["latency_ms"]} ms</div>')
                        msgs_html += f"""
                        <div style="display:flex;margin-bottom:12px;gap:9px;
                          align-items:flex-start;
                          animation:fadeUp 0.3s ease {delay:.2f}s both;">
                          <div style="width:26px;height:26px;border-radius:8px;
                            flex-shrink:0;margin-top:2px;
                            background:linear-gradient(135deg,{PILL_BG},{CARD_S});
                            display:flex;align-items:center;justify-content:center;
                            font-family:'Instrument Serif',serif;font-size:12px;
                            color:{ACC};border:1px solid {PILL_BD};
                            animation:float 4s ease-in-out {delay:.2f}s infinite;">N</div>
                          <div style="max-width:86%;padding:12px 16px;
                            background:{CARD_S};border:1px solid {BORDER};
                            border-radius:3px 14px 14px 14px;
                            font-size:14px;color:{T1};line-height:1.75;
                            transition:border-color 0.15s;"
                            onmouseover="this.style.borderColor='{BORDER_A}'"
                            onmouseout="this.style.borderColor='{BORDER}'">
                            {m['content']}{refs}{rfsd}{lat}
                          </div>
                        </div>"""

                mdiv(f"""
                <div style="max-height:50vh;overflow-y:auto;margin-bottom:14px;
                  padding:2px;scrollbar-width:thin;
                  scrollbar-color:{BORDER_A} transparent;">
                  {msgs_html}
                </div>""")

            else:
                # Empty state
                mdiv(f"""
                <div style="text-align:center;padding:44px 20px 36px;
                  background:{CARD_S};border:2px dashed {BORDER};
                  border-radius:14px;margin-bottom:14px;
                  animation:fadeUp 0.4s ease both;">
                  <div style="width:42px;height:42px;border-radius:12px;
                    background:linear-gradient(135deg,{PILL_BG},{CARD_S});
                    border:1px solid {PILL_BD};
                    display:flex;align-items:center;justify-content:center;
                    margin:0 auto 13px;font-family:'Instrument Serif',serif;
                    font-size:16px;color:{ACC};
                    animation:float 4s ease-in-out infinite;">N</div>
                  <div style="font-family:'Instrument Serif',serif;font-size:20px;
                    color:{T1};margin-bottom:7px;">Ask anything</div>
                  <div style="font-size:13px;color:{T3};max-width:280px;
                    margin:0 auto 18px;line-height:1.7;">
                    Upload a PDF on the right, then ask questions.
                    Every answer is cited.</div>
                  <div style="display:flex;flex-wrap:wrap;gap:7px;justify-content:center;">
                    {"".join([
                        f'<span style="font-size:12px;font-weight:500;color:{ACC};'
                        f'background:{PILL_BG};border:1px solid {PILL_BD};'
                        f'padding:5px 13px;border-radius:9999px;cursor:default;'
                        f'transition:all 0.15s;"'
                        f'onmouseover="this.style.transform=\'translateY(-2px)\';'
                        f'this.style.boxShadow=\'0 4px 12px {ACC}33\'"'
                        f'onmouseout="this.style.transform=\'\';'
                        f'this.style.boxShadow=\'\'">{q}</span>'
                        for q in ["What is the main finding?",
                                  "Summarise section 3",
                                  "What are the key risks?"]
                    ])}
                  </div>
                </div>""")

            # Input row
            qc, bc = st.columns([6, 1])
            with qc:
                query = st.text_input("Q",
                    placeholder="Ask anything about your documents...",
                    label_visibility="hidden", key="q_in")
            with bc:
                ask = st.button("Send", use_container_width=True)

            mdiv('</div>')  # close chat card

            if ask and query:
                if not ready:
                    st.warning("Upload and index a PDF first.")
                else:
                    with st.spinner("Thinking..."):
                        try:
                            resp = requests.post(
                                f"{API_BASE}/query", json={"query":query}, timeout=120)
                            if resp.status_code == 200:
                                d = resp.json()
                                st.session_state.messages.extend([
                                    {"role":"user","content":query},
                                    {"role":"assistant","content":d["answer"],
                                     "references":d["references"],"refused":d["refused"],
                                     "latency_ms":d["latency_ms"]},
                                ])
                                record_query(query=query,latency_ms=d["latency_ms"],
                                             refused=d["refused"])
                                st.rerun()
                            else:
                                st.error(f"API error: {resp.json().get('detail',resp.text)}")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot reach API. Run: "
                                     "uv run uvicorn api:app --reload --port 8000")

        mdiv('</div>')  # close padding wrapper