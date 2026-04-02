"""NeuralDoc RAG — Minimal pastel SaaS UI. Clean rewrite."""
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
    def export_as_markdown(m, title="Chat"): return "\n".join(
        f"{x['role']}: {x['content']}" for x in m)
    def record_query(q, lat, ref, model=""): pass
    def get_stats(): return {
        "total_queries": 0, "answered": 0, "refused": 0,
        "refusal_rate": 0, "avg_latency_ms": 0, "recent": []}

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuralDoc",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [
    ("page",     "landing"),
    ("messages", []),
    ("tab",      "chat"),
    ("dark",     False),
    ("authed",   False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

API_BASE = "http://localhost:8000"
AUTH_KEY = "neural2024"
D        = st.session_state.dark   # shorthand

# ══════════════════════════════════════════════════════════════════════════════
# THEME — full re-injection every rerun so dark/light always correct
# ══════════════════════════════════════════════════════════════════════════════
if D:
    BG      = "#0E1117"
    CARD    = "#1C1F26"
    CARD2   = "#23272F"
    BORDER  = "rgba(139,139,245,0.18)"
    BORDER2 = "rgba(255,255,255,0.07)"
    T1      = "#F1F0FF"
    T2      = "#A09DC0"
    T3      = "#5E5A80"
    ACCENT  = "#8B8BF5"
    ACCENT2 = "#6B6BDB"
    PILL_BG = "#2A2760"
    PILL_BD = "#4A47A3"
    INP_BG  = "#1C1F26"
    NAV_BG  = "rgba(14,17,23,0.95)"
    NAV_BD  = "rgba(139,139,245,0.15)"
    SH      = "0 1px 3px rgba(0,0,0,0.4), 0 4px 14px rgba(0,0,0,0.3)"
    SH2     = "0 6px 32px rgba(0,0,0,0.5)"
    MESH1   = "rgba(107,107,219,0.18)"
    MESH2   = "rgba(0,200,180,0.07)"
else:
    BG      = "#F7F7FB"
    CARD    = "#FFFFFF"
    CARD2   = "#F0EFF9"
    BORDER  = "rgba(139,139,245,0.20)"
    BORDER2 = "rgba(0,0,0,0.07)"
    T1      = "#1A1840"
    T2      = "#4A4870"
    T3      = "#9B98B8"
    ACCENT  = "#7C6FF7"
    ACCENT2 = "#6459E8"
    PILL_BG = "#EDEDFF"
    PILL_BD = "#C7C4FF"
    INP_BG  = "#FFFFFF"
    NAV_BG  = "rgba(255,255,255,0.95)"
    NAV_BD  = "rgba(139,139,245,0.15)"
    SH      = "0 1px 3px rgba(139,139,245,0.08), 0 4px 14px rgba(139,139,245,0.07)"
    SH2     = "0 6px 32px rgba(139,139,245,0.16)"
    MESH1   = "rgba(180,170,255,0.16)"
    MESH2   = "rgba(6,182,212,0.07)"

# ── Global CSS ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital,wght@0,400;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="stDecoration"],[data-testid="stStatusWidget"],
[data-testid="collapsedControl"],section[data-testid="stSidebar"],
#MainMenu,footer{{display:none!important;height:0!important;}}

[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],.block-container{{
  background:transparent!important;padding:0!important;
  margin:0!important;max-width:100%!important;border:none!important;}}

[data-testid="stVerticalBlock"]{{gap:0!important;}}
[data-testid="stVerticalBlock"]>div{{margin:0!important;padding:0!important;}}

html,body{{
  font-family:'Inter',sans-serif!important;
  background:{BG}!important;color:{T1}!important;}}
[data-testid="stAppViewContainer"]{{background:{BG}!important;}}

/* Buttons */
[data-testid="stButton"]>button{{
  background:{ACCENT}!important;color:#fff!important;border:none!important;
  border-radius:10px!important;font-family:'Inter',sans-serif!important;
  font-size:13px!important;font-weight:600!important;padding:10px 0!important;
  box-shadow:0 2px 8px rgba(124,111,247,0.25)!important;
  transition:all 0.18s!important;letter-spacing:0.01em!important;}}
[data-testid="stButton"]>button:hover{{
  background:{ACCENT2}!important;transform:translateY(-1px)!important;
  box-shadow:0 4px 16px rgba(124,111,247,0.35)!important;}}
[data-testid="stButton"]>button:active{{transform:scale(0.97)!important;}}

/* Download button */
[data-testid="stDownloadButton"]>button{{
  background:{CARD}!important;color:{ACCENT}!important;
  border:1.5px solid {PILL_BD}!important;border-radius:10px!important;
  font-family:'Inter',sans-serif!important;font-size:13px!important;
  font-weight:600!important;box-shadow:none!important;transition:all 0.18s!important;}}
[data-testid="stDownloadButton"]>button:hover{{
  background:{PILL_BG}!important;transform:translateY(-1px)!important;}}

/* Text input */
.stTextInput input{{
  background:{INP_BG}!important;border:1.5px solid {BORDER}!important;
  border-radius:10px!important;color:{T1}!important;
  font-family:'Inter',sans-serif!important;font-size:14px!important;
  padding:13px 18px!important;box-shadow:{SH}!important;transition:all 0.18s!important;}}
.stTextInput input:focus{{
  border-color:{ACCENT}!important;
  box-shadow:0 0 0 3px rgba(124,111,247,0.12)!important;outline:none!important;}}
.stTextInput input::placeholder{{color:{T3}!important;}}
.stTextInput label,.stFileUploader label{{display:none!important;}}

/* File uploader */
[data-testid="stFileUploaderDropzone"]{{
  background:{INP_BG}!important;border:2px dashed {PILL_BD}!important;
  border-radius:14px!important;transition:all 0.18s!important;}}
[data-testid="stFileUploaderDropzone"]:hover{{
  border-color:{ACCENT}!important;background:{PILL_BG}!important;}}
[data-testid="stFileUploaderDropzone"] *{{color:{T2}!important;}}
hr{{border-color:{BORDER2}!important;}}

/* Animations */
@keyframes fadeUp{{
  from{{opacity:0;transform:translateY(14px);}}
  to{{opacity:1;transform:translateY(0);}}}}
@keyframes fadeIn{{from{{opacity:0;}}to{{opacity:1;}}}}
@keyframes pulse{{
  0%,100%{{box-shadow:0 0 0 0 rgba(124,111,247,0.25);}}
  50%{{box-shadow:0 0 0 5px rgba(124,111,247,0);}}}}
@keyframes float{{
  0%,100%{{transform:translateY(0);}}50%{{transform:translateY(-5px);}}}}
@keyframes countIn{{
  from{{opacity:0;transform:scale(0.85);}}to{{opacity:1;transform:scale(1);}}}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def lbl(text):
    return (f'<div style="font-size:10px;font-weight:700;color:{ACCENT};'
            f'letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;">{text}</div>')


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "auth":

    st.markdown(f"""
    <div style="min-height:100vh;background:{BG};position:relative;">
      <div style="position:fixed;inset:0;pointer-events:none;
        background:radial-gradient(ellipse 60% 55% at 30% 30%,{MESH1},transparent 60%),
                  radial-gradient(ellipse 45% 50% at 70% 70%,{MESH2},transparent 55%);"></div>
      <div style="position:relative;z-index:1;max-width:400px;margin:0 auto;
        padding:80px 24px 0;animation:fadeUp 0.5s ease both;">
        <div style="text-align:center;margin-bottom:24px;">
          <div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:10px;">
            <div style="width:8px;height:8px;border-radius:50%;background:{ACCENT};
              animation:pulse 2s ease-in-out infinite;"></div>
            <span style="font-family:'Instrument Serif',serif;font-size:20px;color:{T1};">
              NeuralDoc</span>
          </div>
          <div style="font-family:'Instrument Serif',serif;font-size:28px;color:{T1};
            margin-bottom:6px;">Sign in</div>
          <div style="font-size:14px;color:{T3};">Enter your access key to continue</div>
        </div>
        <div style="background:{CARD};border:1px solid {BORDER2};border-radius:18px;
          padding:28px;box-shadow:{SH2};">
    """, unsafe_allow_html=True)

    pwd = st.text_input("Key", type="password",
                        placeholder="Access key...",
                        label_visibility="hidden", key="auth_key")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sign In", use_container_width=True, key="signin"):
            if pwd == AUTH_KEY:
                st.session_state.authed = True
                st.session_state.page = "chat"
                st.rerun()
            else:
                st.error("Incorrect key.")
    with c2:
        if st.button("Back", use_container_width=True, key="auth_back"):
            st.session_state.page = "landing"
            st.rerun()

    st.markdown(f"""
        </div>
        <div style="text-align:center;margin-top:14px;font-size:12px;color:{T3};">
          Demo key:&nbsp;
          <code style="background:{PILL_BG};color:{ACCENT};padding:2px 8px;
            border-radius:6px;font-size:11px;">neural2024</code>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "landing":

    # ── Navbar ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{NAV_BG};backdrop-filter:blur(14px);
      border-bottom:1px solid {NAV_BD};height:58px;
      display:flex;align-items:center;justify-content:space-between;
      padding:0 52px;position:sticky;top:0;z-index:200;
      animation:fadeIn 0.4s ease both;">
      <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:8px;height:8px;border-radius:50%;background:{ACCENT};
          animation:pulse 2.5s ease-in-out infinite;"></div>
        <span style="font-family:'Instrument Serif',serif;font-size:19px;color:{T1};">
          NeuralDoc</span>
      </div>
      <div style="font-size:11px;font-weight:600;color:{ACCENT};
        text-transform:uppercase;letter-spacing:0.08em;
        background:{PILL_BG};border:1px solid {PILL_BD};
        padding:5px 14px;border-radius:9999px;">Production RAG v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    # Dark mode toggle — standalone row
    _l, _dm, _r = st.columns([5, 1, 5])
    with _dm:
        if st.button("☀ Light" if D else "☽ Dark", key="dm_land",
                     use_container_width=True):
            st.session_state.dark = not D
            st.rerun()

    # ── Mesh background ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="position:fixed;inset:0;pointer-events:none;z-index:0;
      background:radial-gradient(ellipse 55% 50% at 15% 10%,{MESH1},transparent 60%),
                radial-gradient(ellipse 45% 45% at 85% 85%,{MESH2},transparent 55%);
      opacity:0.9;"></div>
    """, unsafe_allow_html=True)

    # ── Hero ─────────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="position:relative;z-index:1;max-width:800px;margin:0 auto;
      padding:60px 48px 0;text-align:center;animation:fadeUp 0.6s ease 0.1s both;">
      <div style="display:inline-flex;align-items:center;gap:6px;margin-bottom:22px;
        font-size:12px;font-weight:600;color:{ACCENT};
        background:{PILL_BG};border:1px solid {PILL_BD};
        padding:5px 16px;border-radius:9999px;">
        <div style="width:5px;height:5px;border-radius:50%;background:{ACCENT};
          animation:pulse 1.8s ease-in-out infinite;"></div>
        Zero hallucination tolerance
      </div>
      <div style="font-family:'Instrument Serif',serif;
        font-size:clamp(40px,5.5vw,62px);color:{T1};
        line-height:1.06;letter-spacing:-0.8px;margin-bottom:6px;">Ask anything.</div>
      <div style="font-family:'Instrument Serif',serif;
        font-size:clamp(40px,5.5vw,62px);font-style:italic;color:{ACCENT};
        line-height:1.06;letter-spacing:-0.8px;margin-bottom:22px;">Know everything.</div>
      <div style="font-size:16px;color:{T2};line-height:1.8;
        max-width:500px;margin:0 auto 36px;">
        A <strong style="color:{T1};">production-grade</strong> RAG system with
        <strong style="color:{T1};">inline citations</strong>, hybrid retrieval,
        persistent history, and live analytics.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA button
    _l2, _btn, _r2 = st.columns([3, 2, 3])
    with _btn:
        st.markdown(f"""<style>
        button[data-testid="baseButton-secondary"]{{
          height:50px!important;font-size:15px!important;
          border-radius:9999px!important;}}
        </style>""", unsafe_allow_html=True)
        if st.button("Open App  →", key="launch_btn", use_container_width=True):
            st.session_state.page = "auth"
            st.rerun()

    # Stats
    stat_items = [("0%","Hallucination"),("3×","Retrieval Methods"),
                  ("100%","Local & Private"),("∞","Documents")]
    stats_html = ""
    for i, (v, l) in enumerate(stat_items):
        br = f"border-right:1px solid {BORDER2};" if i < 3 else ""
        stats_html += (
            f'<div style="flex:1;padding:22px 10px;text-align:center;{br}'
            f'transition:background 0.16s;cursor:default;"'
            f'onmouseover="this.style.background=\'{PILL_BG}\'"'
            f'onmouseout="this.style.background=\'\'">'
            f'<div style="font-family:\'Instrument Serif\',serif;font-size:30px;'
            f'color:{ACCENT};margin-bottom:4px;'
            f'animation:countIn 0.6s ease {0.3+i*0.1:.1f}s both;">{v}</div>'
            f'<div style="font-size:10px;font-weight:700;color:{T3};'
            f'letter-spacing:0.1em;text-transform:uppercase;">{l}</div></div>'
        )
    st.markdown(f"""
    <div style="position:relative;z-index:1;display:flex;max-width:720px;
      margin:40px auto 0;background:{CARD};border:1px solid {BORDER2};
      border-radius:20px;overflow:hidden;box-shadow:{SH};
      animation:fadeUp 0.6s ease 0.25s both;">
      {stats_html}
    </div>
    """, unsafe_allow_html=True)

    # Features + Pillars + Pipeline — all wrapped in one relative z-index div
    feats = [
        ("Persistent Chat History",
         "Every conversation auto-saved. Load any past session in one click.",
         "chat_history.py", ACCENT, PILL_BD),
        ("Export as Markdown",
         "Download any conversation with citations as a .md file.",
         "Export MD", "#06B6D4", "rgba(6,182,212,0.3)"),
        ("Live Query Analytics",
         "Real-time: refusal rate, avg latency, pipeline health.",
         "analytics.py", "#EC4899", "rgba(236,72,153,0.3)"),
    ]
    feats_html = "".join([
        f'<div style="background:linear-gradient(135deg,{PILL_BG},{CARD2});'
        f'border:1px solid {PILL_BD};border-radius:14px;padding:22px;'
        f'transition:transform 0.18s,box-shadow 0.18s;"'
        f'onmouseover="this.style.transform=\'translateY(-4px)\';this.style.boxShadow=\'{SH2}\'"'
        f'onmouseout="this.style.transform=\'\';this.style.boxShadow=\'\'">'
        f'<div style="font-size:14px;font-weight:700;color:{T1};margin-bottom:6px;">{t}</div>'
        f'<div style="font-size:12px;color:{T2};line-height:1.7;">{b}</div>'
        f'<span style="display:inline-block;margin-top:10px;font-size:10px;font-weight:700;'
        f'color:{bc};background:{CARD};border:1px solid {bd};'
        f'padding:3px 10px;border-radius:9999px;">{tag}</span></div>'
        for t, b, tag, bc, bd in feats
    ])

    pillars = [
        ("01","Ingestion","Smart PDF Parsing","Multi-column layouts, tables, complex structures.","pdfplumber","#059669","rgba(5,150,105,0.3)","rgba(5,150,105,0.08)"),
        ("02","Chunking","Semantic Chunking","Header-aware 500-800 token chunks with metadata.","tiktoken",ACCENT,PILL_BD,PILL_BG),
        ("03","Retrieval","Hybrid Search","BM25 + dense vector search via Reciprocal Rank Fusion.","RRF Fusion","#06B6D4","rgba(6,182,212,0.3)","rgba(6,182,212,0.08)"),
        ("04","Reranking","Cross-Encoder Precision","Top 20 re-scored — only the best 5 reach generation.","ms-marco","#F59E0B","rgba(245,158,11,0.3)","rgba(245,158,11,0.08)"),
        ("05","Generation","Attributed Answers","Every claim has [Source, p.X]. References appended.","LangGraph",ACCENT,PILL_BD,PILL_BG),
        ("06","Safety","Hard Refusal Gate","Below threshold = fixed refusal. No hallucination.","Threshold Gate","#EC4899","rgba(236,72,153,0.3)","rgba(236,72,153,0.08)"),
    ]
    pillars_html = "".join([
        f'<div style="background:{CARD};border:1px solid {BORDER2};border-radius:14px;'
        f'padding:22px;box-shadow:{SH};transition:transform 0.2s,box-shadow 0.2s,border-color 0.2s;"'
        f'onmouseover="this.style.transform=\'translateY(-4px)\';this.style.boxShadow=\'{SH2}\';this.style.borderColor=\'{PILL_BD}\'"'
        f'onmouseout="this.style.transform=\'\';this.style.boxShadow=\'{SH}\';this.style.borderColor=\'{BORDER2}\'">'
        f'<div style="font-size:10px;font-weight:700;color:{T3};letter-spacing:0.1em;'
        f'text-transform:uppercase;margin-bottom:7px;">{num} — {cat}</div>'
        f'<div style="font-size:14px;font-weight:700;color:{T1};margin-bottom:6px;">{t}</div>'
        f'<div style="font-size:12px;color:{T2};line-height:1.7;">{b}</div>'
        f'<span style="display:inline-block;margin-top:10px;font-size:10px;font-weight:700;'
        f'padding:3px 10px;border-radius:9999px;color:{tc};'
        f'background:{tbg};border:1px solid {tbd};">{tag}</span></div>'
        for num, cat, t, b, tag, tc, tbd, tbg in pillars
    ])

    steps = [("Parse","pdfplumber"),("Chunk","tiktoken"),("Embed","miniLM"),
             ("BM25","keyword"),("Fuse","RRF"),("Rerank","cross-enc"),
             ("Generate","llama3.1"),("Cite","attributed")]
    pipe_html = ""
    for i, (s, sub) in enumerate(steps):
        pipe_html += (
            f'<div style="display:flex;flex-direction:column;align-items:center;'
            f'gap:4px;flex:1;padding:7px 3px;border-radius:8px;'
            f'transition:all 0.16s;cursor:default;"'
            f'onmouseover="this.style.background=\'{PILL_BG}\';this.style.transform=\'translateY(-2px)\'"'
            f'onmouseout="this.style.background=\'\';this.style.transform=\'\'">'
            f'<div style="font-size:11px;font-weight:700;color:{T1};">{s}</div>'
            f'<div style="font-size:10px;color:{T3};">{sub}</div></div>'
        )
        if i < 7:
            pipe_html += (
                f'<div style="color:{PILL_BD};font-size:13px;flex-shrink:0;">'
                f'&rarr;</div>'
            )

    stack_tags = [
        ("pdfplumber","#059669","rgba(5,150,105,0.3)","rgba(5,150,105,0.08)"),
        ("ChromaDB","#059669","rgba(5,150,105,0.3)","rgba(5,150,105,0.08)"),
        ("sentence-transformers","#059669","rgba(5,150,105,0.3)","rgba(5,150,105,0.08)"),
        ("LangGraph",ACCENT,PILL_BD,PILL_BG),
        ("langchain-ollama",ACCENT,PILL_BD,PILL_BG),
        ("llama3.1:8b",ACCENT,PILL_BD,PILL_BG),
        ("BM25 + RRF","#06B6D4","rgba(6,182,212,0.3)","rgba(6,182,212,0.08)"),
        ("cross-encoder","#06B6D4","rgba(6,182,212,0.3)","rgba(6,182,212,0.08)"),
        ("FastAPI","#EC4899","rgba(236,72,153,0.3)","rgba(236,72,153,0.08)"),
        ("Streamlit","#EC4899","rgba(236,72,153,0.3)","rgba(236,72,153,0.08)"),
        ("Python 3.14","#F59E0B","rgba(245,158,11,0.3)","rgba(245,158,11,0.08)"),
    ]
    stack_html = "".join([
        f'<span style="display:inline-block;padding:6px 13px;font-size:11px;font-weight:600;'
        f'border-radius:9999px;color:{c};border:1px solid {bd};background:{bg};'
        f'transition:transform 0.15s;cursor:default;"'
        f'onmouseover="this.style.transform=\'translateY(-2px)\'"'
        f'onmouseout="this.style.transform=\'\'">{t}</span>'
        for t, c, bd, bg in stack_tags
    ])

    def sec(tag_text, title_html, body_html, delay=0.3):
        return f"""
        <div style="position:relative;z-index:1;max-width:1100px;margin:72px auto 0;
          padding:0 48px;animation:fadeUp 0.6s ease {delay}s both;">
          <div style="font-size:10px;font-weight:700;color:{ACCENT};
            letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">
            {tag_text}</div>
          <div style="font-family:'Instrument Serif',serif;font-size:30px;color:{T1};
            margin-bottom:24px;">{title_html}</div>
          {body_html}
        </div>"""

    st.markdown(
        sec("New in v1.0",
            f'Three <em style="font-style:italic;color:{ACCENT};">new</em> features',
            f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">'
            f'{feats_html}</div>', 0.3)
        + sec("Capabilities",
              f'Six <em style="font-style:italic;color:{ACCENT};">pillars</em> of precision',
              f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">'
              f'{pillars_html}</div>', 0.35)
        + sec("Architecture",
              f'The <em style="font-style:italic;color:{ACCENT};">pipeline</em>',
              f'<div style="display:flex;align-items:center;justify-content:space-between;'
              f'background:{CARD};border:1px solid {BORDER2};border-radius:14px;'
              f'padding:22px 26px;box-shadow:{SH};">{pipe_html}</div>', 0.4)
        + sec("Stack",
              f'Built <em style="font-style:italic;color:{ACCENT};">with</em>',
              f'<div style="display:flex;flex-wrap:wrap;gap:8px;">{stack_html}</div>', 0.45)
        + f"""
        <div style="position:relative;z-index:1;max-width:1100px;margin:64px auto 0;
          padding:20px 48px 56px;border-top:1px solid {BORDER2};
          display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
          <span style="font-size:12px;color:{T3};">NeuralDoc &mdash; Production RAG System</span>
          <span style="font-size:12px;color:{T3};">Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
        </div>""",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHAT / ANALYTICS PAGE
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "chat":

    def get_health():
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3).json()
            r["_reachable"] = True
            return r
        except Exception:
            return {"pipeline_ready": False, "total_chunks": 0,
                    "indexed_files": [], "_reachable": False}

    h      = get_health()
    api_ok = h.get("_reachable", False)
    ready  = h.get("pipeline_ready", False)
    chunks = h.get("total_chunks", 0)
    files  = h.get("indexed_files", [])

    if ready:
        api_c="color:#059669"; api_bg="background:rgba(5,150,105,0.09)"
        api_bd="border:1px solid rgba(5,150,105,0.28)"; api_t=f"Ready · {chunks} chunks"
    elif api_ok:
        api_c="color:#D97706"; api_bg="background:rgba(217,119,6,0.09)"
        api_bd="border:1px solid rgba(217,119,6,0.28)"; api_t="API online · No docs"
    else:
        api_c="color:#DC2626"; api_bg="background:rgba(220,38,38,0.09)"
        api_bd="border:1px solid rgba(220,38,38,0.28)"; api_t="API offline"

    # Tab pill styles
    def tab_style(active):
        if active:
            return (f"background:{ACCENT};color:#fff;"
                    f"box-shadow:0 2px 8px rgba(124,111,247,0.3);")
        return f"color:{T2};background:transparent;"

    # ── TOPBAR ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:{NAV_BG};backdrop-filter:blur(14px);
      border-bottom:1px solid {NAV_BD};height:58px;
      display:flex;align-items:center;justify-content:space-between;
      padding:0 36px;position:sticky;top:0;z-index:200;
      animation:fadeIn 0.4s ease both;">
      <div style="display:flex;align-items:center;gap:8px;min-width:130px;">
        <div style="width:8px;height:8px;border-radius:50%;background:{ACCENT};
          animation:pulse 2.5s ease-in-out infinite;"></div>
        <span style="font-family:'Instrument Serif',serif;font-size:18px;color:{T1};">
          NeuralDoc</span>
      </div>
      <div style="display:flex;gap:3px;background:{CARD2};
        border:1px solid {BORDER2};border-radius:10px;padding:3px;">
        <div style="padding:6px 18px;border-radius:8px;font-size:13px;font-weight:600;
          {tab_style(st.session_state.tab=='chat')} transition:all 0.16s;">Chat</div>
        <div style="padding:6px 18px;border-radius:8px;font-size:13px;font-weight:600;
          {tab_style(st.session_state.tab=='analytics')} transition:all 0.16s;">Analytics</div>
      </div>
      <div style="display:flex;align-items:center;gap:8px;min-width:130px;justify-content:flex-end;">
        <div style="display:inline-flex;align-items:center;gap:5px;font-size:12px;
          font-weight:600;padding:5px 12px;border-radius:9999px;
          {api_c};{api_bg};{api_bd};">
          <div style="width:5px;height:5px;border-radius:50%;
            {'animation:pulse 1.5s ease-in-out infinite;' if ready else ''}
            background:currentColor;"></div>
          {api_t}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ACTION BUTTONS ROW ───────────────────────────────────────────────────────
    st.markdown(f'<div style="padding:14px 36px 0;">', unsafe_allow_html=True)
    b = st.columns([1, 1, 1, 1, 1, 0.7, 4])
    with b[0]:
        if st.button("← Home", key="home_btn", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.page = "landing"
            st.rerun()
    with b[1]:
        if st.button("Clear Chat", key="clr_btn", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.messages = []
            st.rerun()
    with b[2]:
        switch_label = "Analytics →" if st.session_state.tab == "chat" else "← Chat"
        if st.button(switch_label, key="tab_switch", use_container_width=True):
            st.session_state.tab = "analytics" if st.session_state.tab == "chat" else "chat"
            st.rerun()
    with b[3]:
        dm_label = "☀ Light" if D else "☽ Dark"
        if st.button(dm_label, key="dm_chat", use_container_width=True):
            st.session_state.dark = not D
            st.rerun()
    with b[4]:
        if st.session_state.messages:
            md = export_as_markdown(st.session_state.messages, "NeuralDoc Chat")
            st.download_button(
                "Export .md", data=md,
                file_name=f"neuraldoc_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown", use_container_width=True, key="exp_md",
            )
        else:
            st.markdown('<div style="height:44px;"></div>', unsafe_allow_html=True)
    st.markdown('</div><div style="height:16px;"></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ANALYTICS TAB
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.tab == "analytics":
        stats = get_stats()

        recent_rows = ""
        for q in stats["recent"]:
            icon = "x" if q["refused"] else "ok"
            ic   = "#DC2626" if q["refused"] else "#059669"
            qt   = q["query"][:80]
            lt   = q["latency_ms"]
            recent_rows += (
                f'<div style="display:flex;align-items:center;gap:10px;'
                f'padding:11px 14px;border-radius:8px;margin-bottom:5px;'
                f'background:{BG};border:1px solid {BORDER2};transition:all 0.15s;"'
                f'onmouseover="this.style.borderColor=\'{PILL_BD}\';'
                f'this.style.transform=\'translateX(2px)\'"'
                f'onmouseout="this.style.borderColor=\'{BORDER2}\';'
                f'this.style.transform=\'\'">'
                f'<div style="width:20px;height:20px;border-radius:50%;flex-shrink:0;'
                f'background:{ic}15;border:1.5px solid {ic}40;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-size:9px;font-weight:700;color:{ic};">{icon}</div>'
                f'<span style="flex:1;font-size:13px;color:{T1};">{qt}</span>'
                f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;'
                f'color:{T3};background:{PILL_BG};padding:2px 8px;'
                f'border-radius:9999px;">{lt}ms</span></div>'
            )

        ans_pct = round((stats["answered"]/stats["total_queries"]*100)
                        if stats["total_queries"] else 0)
        ref_pct = round((stats["refused"]/stats["total_queries"]*100)
                        if stats["total_queries"] else 0)

        kpi_items = [
            (stats["total_queries"], "Total Queries",   ACCENT,    "0.05"),
            (stats["answered"],      "Answered",        "#059669", "0.10"),
            (stats["refused"],       "Refused",         "#DC2626", "0.15"),
            (f"{stats['refusal_rate']}%", "Refusal Rate","#D97706","0.20"),
            (f"{int(stats['avg_latency_ms'])}ms","Avg Latency","#06B6D4","0.25"),
        ]
        kpi_html = ""
        for val, lbl_text, col, delay in kpi_items:
            extra = ""
            if lbl_text == "Answered":
                extra = (f'<div style="height:3px;background:{col}22;border-radius:3px;'
                         f'overflow:hidden;margin-top:8px;">'
                         f'<div style="height:100%;width:{ans_pct}%;background:{col};'
                         f'border-radius:3px;"></div></div>')
            elif lbl_text == "Refused":
                extra = (f'<div style="height:3px;background:{col}22;border-radius:3px;'
                         f'overflow:hidden;margin-top:8px;">'
                         f'<div style="height:100%;width:{ref_pct}%;background:{col};'
                         f'border-radius:3px;"></div></div>')
            elif lbl_text == "Refusal Rate":
                note = "Good" if stats["refusal_rate"] < 20 else "Review threshold"
                extra = f'<div style="font-size:10px;color:{T3};margin-top:6px;">{note}</div>'
            elif lbl_text == "Avg Latency":
                note = "Fast" if stats["avg_latency_ms"] < 3000 else "Consider GPU"
                extra = f'<div style="font-size:10px;color:{T3};margin-top:6px;">{note}</div>'

            kpi_html += (
                f'<div style="background:{CARD};border:1px solid {BORDER2};'
                f'border-radius:14px;padding:20px 14px;box-shadow:{SH};text-align:center;'
                f'animation:fadeUp 0.4s ease {delay}s both;'
                f'transition:transform 0.2s,box-shadow 0.2s;"'
                f'onmouseover="this.style.transform=\'translateY(-4px)\';'
                f'this.style.boxShadow=\'{SH2}\'"'
                f'onmouseout="this.style.transform=\'\';'
                f'this.style.boxShadow=\'{SH}\'">'
                f'<div style="font-family:\'Instrument Serif\',serif;font-size:34px;'
                f'color:{col};line-height:1;margin-bottom:5px;'
                f'animation:countIn 0.6s ease {float(delay)+0.2:.1f}s both;">{val}</div>'
                f'<div style="font-size:10px;font-weight:700;color:{T3};'
                f'letter-spacing:0.1em;text-transform:uppercase;">{lbl_text}</div>'
                f'{extra}</div>'
            )

        sys_rows = ""
        for sl, sv, ok, warn in [
            ("FastAPI", "Online" if api_ok else "Offline", api_ok, False),
            ("RAG Pipeline", "Ready" if ready else "No docs",
             ready, not ready and api_ok),
            ("Indexed chunks", str(chunks), True, False),
            ("Indexed files",  str(len(files)), True, False),
        ]:
            if ok:
                sc="color:#059669"; sbg="background:rgba(5,150,105,0.09)"
                sbd="border:1px solid rgba(5,150,105,0.28)"
            elif warn:
                sc="color:#D97706"; sbg="background:rgba(217,119,6,0.09)"
                sbd="border:1px solid rgba(217,119,6,0.28)"
            else:
                sc="color:#DC2626"; sbg="background:rgba(220,38,38,0.09)"
                sbd="border:1px solid rgba(220,38,38,0.28)"
            sys_rows += (
                f'<div style="display:flex;align-items:center;'
                f'justify-content:space-between;margin-bottom:8px;">'
                f'<span style="font-size:13px;color:{T2};">{sl}</span>'
                f'<span style="font-size:10px;font-weight:700;padding:2px 9px;'
                f'border-radius:9999px;{sc};{sbg};{sbd};">{sv}</span></div>'
            )

        empty_q = (
            f'<div style="text-align:center;padding:24px;font-size:13px;color:{T3};">'
            f'No queries yet.</div>'
        )

        st.markdown(f"""
        <div style="padding:0 36px 48px;">
          <div style="margin-bottom:22px;animation:fadeUp 0.4s ease both;">
            <div style="font-size:10px;font-weight:700;color:{ACCENT};
              letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;">
              Live Observability</div>
            <div style="font-family:'Instrument Serif',serif;font-size:28px;color:{T1};">
              Query <em style="font-style:italic;color:{ACCENT};">Analytics</em></div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(5,1fr);
            gap:12px;margin-bottom:16px;">{kpi_html}</div>
          <div style="display:grid;grid-template-columns:2fr 1fr;gap:14px;">
            <div style="background:{CARD};border:1px solid {BORDER2};
              border-radius:14px;padding:22px 24px;box-shadow:{SH};
              animation:fadeUp 0.4s ease 0.3s both;">
              <div style="display:flex;align-items:center;justify-content:space-between;
                margin-bottom:14px;">
                <div style="font-size:13px;font-weight:700;color:{T1};">Recent Queries</div>
                <div style="font-size:11px;color:{T3};background:{PILL_BG};
                  padding:3px 10px;border-radius:9999px;border:1px solid {PILL_BD};">
                  {len(stats["recent"])} of {stats["total_queries"]} total</div>
              </div>
              {recent_rows if stats["recent"] else empty_q}
            </div>
            <div style="display:flex;flex-direction:column;gap:12px;">
              <div style="background:{CARD};border:1px solid {BORDER2};
                border-radius:14px;padding:18px 20px;box-shadow:{SH};
                animation:fadeUp 0.4s ease 0.35s both;">
                <div style="font-size:10px;font-weight:700;color:{T3};
                  letter-spacing:0.08em;text-transform:uppercase;margin-bottom:12px;">
                  System Status</div>
                {sys_rows}
              </div>
              <div style="background:linear-gradient(135deg,{PILL_BG},{CARD2});
                border:1px solid {PILL_BD};border-radius:14px;
                padding:18px 20px;flex:1;
                animation:fadeUp 0.4s ease 0.4s both;">
                <div style="font-size:10px;font-weight:700;color:{ACCENT};
                  letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px;">
                  MLOps Notes</div>
                <div style="font-size:12px;color:{T2};line-height:1.85;">
                  Refusal &gt;25%: threshold too strict.<br>
                  Latency &gt;5s: try GPU or GPT-4o-mini.<br>
                  Rolling window: last 200 queries.
                </div>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # CHAT TAB
    # ══════════════════════════════════════════════════════════════════════════
    else:
        st.markdown(f'<div style="padding:0 36px 48px;">', unsafe_allow_html=True)
        col_chat, col_right = st.columns([3, 2], gap="large")

        # ── RIGHT ───────────────────────────────────────────────────────────────
        with col_right:
            # Upload card open
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER2};
              border-radius:16px;padding:24px;box-shadow:{SH};
              margin-bottom:14px;animation:fadeUp 0.5s ease 0.1s both;
              transition:box-shadow 0.2s,border-color 0.2s;"
              onmouseover="this.style.boxShadow='{SH2}';
                this.style.borderColor='{PILL_BD}'"
              onmouseout="this.style.boxShadow='{SH}';
                this.style.borderColor='{BORDER2}'">
            """, unsafe_allow_html=True)

            uh1, uh2 = st.columns([3, 1])
            with uh1:
                st.markdown(
                    f'<div style="margin-bottom:14px;">'
                    f'{lbl("Knowledge Base")}'
                    f'<div style="font-family:\'Instrument Serif\',serif;'
                    f'font-size:20px;color:{T1};">Upload '
                    f'<em style="font-style:italic;color:{ACCENT};">documents</em>'
                    f'</div></div>',
                    unsafe_allow_html=True)
            with uh2:
                st.markdown('<div style="height:24px;"></div>', unsafe_allow_html=True)
                if st.button("Clear", key="clear_idx", use_container_width=True):
                    try:
                        r = requests.delete(f"{API_BASE}/index", timeout=15)
                        if r.status_code == 200:
                            st.success("Index cleared.")
                            st.rerun()
                        else:
                            st.error(f"Error: {r.text}")
                    except Exception:
                        st.error("API offline.")

            st.markdown(f"""
            <div style="background:{PILL_BG};border:2px dashed {PILL_BD};
              border-radius:12px;padding:15px;margin-bottom:10px;text-align:center;
              transition:all 0.18s;"
              onmouseover="this.style.borderColor='{ACCENT}';
                this.style.background='{CARD2}';this.style.transform='scale(1.01)'"
              onmouseout="this.style.borderColor='{PILL_BD}';
                this.style.background='{PILL_BG}';this.style.transform=''">
              <div style="font-size:13px;font-weight:500;color:{T1};margin-bottom:3px;">
                Drop your PDF below</div>
              <div style="font-size:11px;color:{T3};">
                Parsed &rarr; Chunked &rarr; Embedded &rarr; Indexed</div>
            </div>
            """, unsafe_allow_html=True)

            uploaded = st.file_uploader("PDF", type=["pdf"], label_visibility="hidden")
            if uploaded:
                st.markdown(f"""
                <div style="background:rgba(5,150,105,0.08);
                  border:1px solid rgba(5,150,105,0.25);border-radius:8px;
                  padding:9px 13px;margin-bottom:9px;">
                  <div style="font-size:13px;font-weight:600;color:{T1};">{uploaded.name}</div>
                  <div style="font-size:11px;color:#059669;margin-top:1px;">
                    {uploaded.size//1024} KB</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Index Document", use_container_width=True, key="idx_btn"):
                    with st.spinner("Processing PDF..."):
                        try:
                            resp = requests.post(
                                f"{API_BASE}/ingest",
                                files={"file": (uploaded.name, uploaded, "application/pdf")},
                                timeout=120,
                            )
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
                st.markdown(
                    f'<div style="font-size:10px;font-weight:700;color:{T3};'
                    f'letter-spacing:0.08em;text-transform:uppercase;'
                    f'margin:12px 0 7px;">Indexed files</div>',
                    unsafe_allow_html=True)
                for f in files:
                    fname = f.replace("\\", "/").split("/")[-1]
                    st.markdown(f"""
                    <div style="background:{BG};border:1px solid {BORDER2};
                      border-radius:8px;padding:7px 12px;margin-bottom:4px;
                      display:flex;align-items:center;transition:all 0.15s;"
                      onmouseover="this.style.borderColor='{PILL_BD}';
                        this.style.transform='translateX(2px)'"
                      onmouseout="this.style.borderColor='{BORDER2}';
                        this.style.transform=''">
                      <span style="font-size:12px;font-weight:500;
                        color:{T1};flex:1;">{fname}</span>
                      <span style="font-size:10px;font-weight:700;padding:2px 8px;
                        border-radius:9999px;color:#059669;
                        background:rgba(5,150,105,0.09);
                        border:1px solid rgba(5,150,105,0.28);">indexed</span>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="margin-top:12px;background:{BG};border:1px solid {BORDER2};
              border-radius:9px;padding:13px 14px;">
              <div style="font-size:10px;font-weight:700;color:{T3};
                letter-spacing:0.08em;text-transform:uppercase;margin-bottom:7px;">Tips</div>
              <div style="font-size:12px;color:{T2};line-height:1.9;">
                Click <b style="color:{ACCENT};">Clear</b> before switching documents.<br>
                Ask precise questions for best citation accuracy.<br>
                Every answer includes inline source references.<br>
                Unanswerable queries return a refusal, not a guess.
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Chat history
            convs = load_all_conversations()
            if convs:
                st.markdown(f"""
                <div style="background:{CARD};border:1px solid {BORDER2};
                  border-radius:16px;padding:20px 20px 14px;box-shadow:{SH};
                  animation:fadeUp 0.5s ease 0.2s both;">
                  <div style="font-size:10px;font-weight:700;color:{ACCENT};
                    letter-spacing:0.1em;text-transform:uppercase;
                    margin-bottom:12px;">Chat History</div>
                """, unsafe_allow_html=True)
                for i, conv in enumerate(convs[:5]):
                    ts  = conv["timestamp"][:10]
                    ttl = conv["title"][:34] + ("…" if len(conv["title"]) > 34 else "")
                    n   = len([m for m in conv["messages"] if m["role"]=="user"])
                    hc1, hc2 = st.columns([4, 1])
                    with hc1:
                        st.markdown(f"""
                        <div style="padding:7px 10px;border-radius:8px;
                          border:1px solid {BORDER2};margin-bottom:4px;
                          transition:all 0.15s;cursor:default;"
                          onmouseover="this.style.borderColor='{PILL_BD}';
                            this.style.background='{PILL_BG}';
                            this.style.transform='translateX(2px)'"
                          onmouseout="this.style.borderColor='{BORDER2}';
                            this.style.background='';
                            this.style.transform=''">
                          <div style="font-size:12px;font-weight:500;
                            color:{T1};">{ttl}</div>
                          <div style="font-size:10px;color:{T3};margin-top:1px;">
                            {ts} · {n} {'query' if n==1 else 'queries'}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with hc2:
                        if st.button("Load", key=f"ld_{conv['id']}_{i}",
                                     use_container_width=True):
                            st.session_state.messages = load_conversation(conv["id"])
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── LEFT: Chat ───────────────────────────────────────────────────────────
        with col_chat:
            st.markdown(f"""
            <div style="background:{CARD};border:1px solid {BORDER2};
              border-radius:16px;padding:24px 24px 20px;box-shadow:{SH};
              animation:fadeUp 0.5s ease both;">
              <div style="display:flex;align-items:flex-start;
                justify-content:space-between;margin-bottom:18px;">
                <div>
                  {lbl("Document QA")}
                  <div style="font-family:'Instrument Serif',serif;
                    font-size:24px;color:{T1};">
                    Ask your
                    <em style="font-style:italic;color:{ACCENT};">documents</em>
                  </div>
                </div>
                <div style="display:flex;gap:7px;padding-top:14px;flex-shrink:0;">
                  <span style="font-size:11px;font-weight:600;color:{ACCENT};
                    background:{PILL_BG};border:1px solid {PILL_BD};
                    padding:4px 11px;border-radius:9999px;">{chunks} chunks</span>
                  <span style="font-size:11px;font-weight:700;padding:4px 11px;
                    border-radius:9999px;border:1.5px solid;
                    {'color:#059669;background:rgba(5,150,105,0.09);border-color:rgba(5,150,105,0.28);' if ready else 'color:#DC2626;background:rgba(220,38,38,0.09);border-color:rgba(220,38,38,0.28);'}">
                    {'Ready' if ready else 'Not ready'}</span>
                </div>
              </div>
            """, unsafe_allow_html=True)

            if st.session_state.messages:
                msgs_html = ""
                for idx, m in enumerate(st.session_state.messages):
                    delay = min(idx * 0.04, 0.24)
                    if m["role"] == "user":
                        msgs_html += f"""
                        <div style="display:flex;justify-content:flex-end;
                          margin-bottom:12px;animation:fadeUp 0.3s ease {delay:.2f}s both;">
                          <div style="max-width:74%;padding:12px 16px;
                            background:{ACCENT};color:#fff;
                            border-radius:14px 3px 14px 14px;font-size:14px;
                            line-height:1.6;box-shadow:0 2px 10px rgba(124,111,247,0.22);">
                            {m['content']}</div>
                        </div>"""
                    else:
                        refs = ""
                        if m.get("references"):
                            refs = '<div style="margin-top:9px;display:flex;flex-wrap:wrap;gap:5px;">'
                            for ref in m["references"]:
                                refs += (
                                    f'<span style="font-family:JetBrains Mono,monospace;'
                                    f'font-size:10px;padding:2px 9px;border-radius:9999px;'
                                    f'color:#06B6D4;background:rgba(6,182,212,0.09);'
                                    f'border:1px solid rgba(6,182,212,0.25);">{ref}</span>'
                                )
                            refs += "</div>"
                        rfsd = ""
                        if m.get("refused"):
                            rfsd = (
                                f'<div style="margin-top:7px;font-size:12px;font-weight:600;'
                                f'color:#DC2626;background:rgba(220,38,38,0.09);'
                                f'border:1px solid rgba(220,38,38,0.25);padding:5px 11px;'
                                f'border-radius:8px;display:inline-block;">'
                                f'Insufficient evidence &mdash; refusal triggered</div>'
                            )
                        lat = ""
                        if m.get("latency_ms"):
                            lat = (
                                f'<div style="margin-top:4px;font-family:JetBrains Mono,'
                                f'monospace;font-size:10px;color:{T3};">'
                                f'{m["latency_ms"]} ms</div>'
                            )
                        msgs_html += f"""
                        <div style="display:flex;margin-bottom:12px;gap:9px;
                          align-items:flex-start;
                          animation:fadeUp 0.3s ease {delay:.2f}s both;">
                          <div style="width:26px;height:26px;border-radius:8px;
                            flex-shrink:0;margin-top:2px;
                            background:linear-gradient(135deg,{PILL_BG},{CARD2});
                            display:flex;align-items:center;justify-content:center;
                            font-family:'Instrument Serif',serif;font-size:12px;
                            color:{ACCENT};border:1px solid {PILL_BD};
                            animation:float 4s ease-in-out {delay:.2f}s infinite;">N</div>
                          <div style="max-width:86%;padding:12px 16px;
                            background:{BG};border:1px solid {BORDER2};
                            border-radius:3px 14px 14px 14px;
                            font-size:14px;color:{T1};line-height:1.75;
                            box-shadow:{SH};transition:border-color 0.15s;"
                            onmouseover="this.style.borderColor='{PILL_BD}'"
                            onmouseout="this.style.borderColor='{BORDER2}'">
                            {m['content']}{refs}{rfsd}{lat}</div>
                        </div>"""

                st.markdown(f"""
                <div style="max-height:50vh;overflow-y:auto;margin-bottom:14px;
                  padding:2px;scrollbar-width:thin;
                  scrollbar-color:{PILL_BD} transparent;">
                  {msgs_html}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align:center;padding:46px 20px 36px;
                  background:{BG};border:1px solid {BORDER2};
                  border-radius:14px;margin-bottom:14px;
                  animation:fadeUp 0.4s ease both;">
                  <div style="width:40px;height:40px;border-radius:10px;
                    background:linear-gradient(135deg,{PILL_BG},{CARD2});
                    border:1px solid {PILL_BD};
                    display:flex;align-items:center;justify-content:center;
                    margin:0 auto 13px;font-family:'Instrument Serif',serif;
                    font-size:16px;color:{ACCENT};box-shadow:{SH};
                    animation:float 4s ease-in-out infinite;">N</div>
                  <div style="font-family:'Instrument Serif',serif;font-size:20px;
                    color:{T1};margin-bottom:7px;">Ask anything</div>
                  <div style="font-size:13px;color:{T3};max-width:280px;
                    margin:0 auto 18px;line-height:1.7;">
                    Upload a PDF on the right, then ask questions.
                    Every answer is cited.</div>
                  <div style="display:flex;flex-wrap:wrap;gap:7px;justify-content:center;">
                    {"".join([
                        f'<span style="font-size:12px;font-weight:500;color:{ACCENT};'
                        f'background:{PILL_BG};border:1px solid {PILL_BD};'
                        f'padding:6px 13px;border-radius:9999px;cursor:default;'
                        f'transition:all 0.15s;"'
                        f'onmouseover="this.style.background=\'{CARD2}\';'
                        f'this.style.transform=\'translateY(-1px)\'"'
                        f'onmouseout="this.style.background=\'{PILL_BG}\';'
                        f'this.style.transform=\'\'">{q}</span>'
                        for q in ["What is the main finding?",
                                  "Summarise section 3",
                                  "What are the key risks?"]
                    ])}
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Input row
            qc, bc = st.columns([6, 1])
            with qc:
                query = st.text_input(
                    "Q", placeholder="Ask anything about your documents...",
                    label_visibility="hidden", key="q_in")
            with bc:
                ask = st.button("Send", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)  # close chat card

            if ask and query:
                if not ready:
                    st.warning("Upload and index a PDF first.")
                else:
                    with st.spinner("Thinking..."):
                        try:
                            resp = requests.post(
                                f"{API_BASE}/query",
                                json={"query": query}, timeout=120,
                            )
                            if resp.status_code == 200:
                                d = resp.json()
                                st.session_state.messages.extend([
                                    {"role": "user",      "content": query},
                                    {"role": "assistant", "content": d["answer"],
                                     "references": d["references"],
                                     "refused":    d["refused"],
                                     "latency_ms": d["latency_ms"]},
                                ])
                                record_query(query=query,
                                             latency_ms=d["latency_ms"],
                                             refused=d["refused"])
                                st.rerun()
                            else:
                                st.error(
                                    f"API error: {resp.json().get('detail', resp.text)}")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot reach API. Run: "
                                     "uv run uvicorn api:app --reload --port 8000")

        st.markdown('</div>', unsafe_allow_html=True)