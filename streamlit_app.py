"""NeuralDoc RAG — Pastel Minimal Redesign."""
import requests
import streamlit as st

st.set_page_config(
    page_title="NeuralDoc",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "messages" not in st.session_state:
    st.session_state.messages = []

API_BASE = "http://localhost:8000"

# ── Global reset ──────────────────────────────────────────────────────────────
st.html("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:          #F7F6FF;
  --surface:     #FFFFFF;
  --surface2:    #F0EFF9;
  --border:      rgba(139,92,246,0.1);
  --border-soft: rgba(0,0,0,0.06);

  --violet-50:   #F5F3FF;
  --violet-100:  #EDE9FE;
  --violet-200:  #DDD6FE;
  --violet-400:  #A78BFA;
  --violet-500:  #8B5CF6;
  --violet-600:  #7C3AED;

  --mint-bg:     #ECFDF5;
  --mint-text:   #059669;
  --rose-bg:     #FFF1F2;
  --rose-text:   #E11D48;
  --amber-bg:    #FFFBEB;
  --amber-text:  #D97706;
  --sky-bg:      #F0F9FF;
  --sky-text:    #0284C7;

  --text-1:      #18181B;
  --text-2:      #52525B;
  --text-3:      #A1A1AA;

  --radius-sm:   6px;
  --radius-md:   10px;
  --radius-lg:   16px;
  --radius-xl:   24px;
  --radius-full: 9999px;

  --shadow-sm:  0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md:  0 4px 12px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04);
  --shadow-lg:  0 8px 32px rgba(0,0,0,0.09), 0 4px 8px rgba(0,0,0,0.04);
  --shadow-violet: 0 4px 14px rgba(139,92,246,0.25);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: var(--bg) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Kill all Streamlit chrome */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
#MainMenu, footer { display:none!important; height:0!important; }

[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
  background: transparent!important;
  padding: 0!important;
  margin: 0!important;
  max-width: 100%!important;
  border: none!important;
}

[data-testid="stVerticalBlock"] { gap: 0!important; }
[data-testid="stVerticalBlock"] > div { margin: 0!important; padding: 0!important; }
</style>""")


# ═════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.html("""
    <style>
    body, [data-testid="stAppViewContainer"] { background: var(--bg)!important; }

    /* Subtle background texture */
    .land-root {
      min-height: 100vh;
      background: var(--bg);
      position: relative;
      overflow: hidden;
    }
    .land-root::before {
      content: '';
      position: fixed; inset: 0;
      background:
        radial-gradient(ellipse 60% 50% at 20% 10%, rgba(167,139,250,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 80% 80%, rgba(139,92,246,0.08) 0%, transparent 55%),
        radial-gradient(ellipse 30% 30% at 60% 30%, rgba(196,181,253,0.1) 0%, transparent 50%);
      pointer-events: none; z-index: 0;
    }

    /* Navbar */
    .land-nav {
      position: relative; z-index: 10;
      display: flex; align-items: center; justify-content: space-between;
      max-width: 1100px; margin: 0 auto;
      padding: 28px 40px 0;
      animation: fadeDown 0.5s ease both;
    }
    @keyframes fadeDown { from{opacity:0;transform:translateY(-12px);} to{opacity:1;transform:translateY(0);} }
    .land-logo {
      font-family: 'Instrument Serif', serif;
      font-size: 22px; color: var(--text-1);
      display: flex; align-items: center; gap: 8px;
    }
    .land-logo-dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: var(--violet-500);
    }
    .land-nav-badge {
      font-size: 11px; font-weight: 500; color: var(--violet-600);
      background: var(--violet-100); border: 1px solid var(--violet-200);
      padding: 5px 14px; border-radius: var(--radius-full);
      letter-spacing: 0.3px;
    }

    /* Hero */
    .land-hero {
      position: relative; z-index: 10;
      max-width: 780px; margin: 0 auto;
      padding: 80px 40px 0;
      text-align: center;
      animation: fadeUp 0.6s ease 0.1s both;
    }
    @keyframes fadeUp { from{opacity:0;transform:translateY(20px);} to{opacity:1;transform:translateY(0);} }

    .land-eyebrow {
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 12px; font-weight: 500; color: var(--violet-600);
      background: var(--violet-50); border: 1px solid var(--violet-200);
      padding: 5px 14px; border-radius: var(--radius-full);
      margin-bottom: 28px; letter-spacing: 0.3px;
    }
    .land-eyebrow-dot {
      width: 5px; height: 5px; border-radius: 50%;
      background: var(--violet-500);
      animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.5;transform:scale(0.8);} }

    .land-h1 {
      font-family: 'Instrument Serif', serif;
      font-size: clamp(42px, 6vw, 68px);
      font-weight: 400; color: var(--text-1);
      line-height: 1.1; letter-spacing: -1px;
      margin-bottom: 20px;
    }
    .land-h1 em {
      font-style: italic; color: var(--violet-500);
    }
    .land-sub {
      font-size: 17px; color: var(--text-2);
      line-height: 1.75; max-width: 520px;
      margin: 0 auto 40px; font-weight: 400;
    }
    .land-sub strong { color: var(--text-1); font-weight: 600; }

    /* Stats row */
    .land-stats {
      display: flex; justify-content: center;
      gap: 0; max-width: 600px; margin: 56px auto 0;
      border: 1px solid var(--border-soft);
      border-radius: var(--radius-xl);
      overflow: hidden;
      background: var(--surface);
      box-shadow: var(--shadow-sm);
      animation: fadeUp 0.6s ease 0.3s both;
    }
    .land-stat {
      flex: 1; padding: 24px 16px; text-align: center;
      border-right: 1px solid var(--border-soft);
      transition: background 0.2s;
    }
    .land-stat:last-child { border-right: none; }
    .land-stat:hover { background: var(--violet-50); }
    .land-stat-val {
      font-family: 'Instrument Serif', serif;
      font-size: 32px; color: var(--violet-500);
      line-height: 1; margin-bottom: 4px;
    }
    .land-stat-lbl {
      font-size: 11px; font-weight: 500;
      color: var(--text-3); letter-spacing: 0.5px;
      text-transform: uppercase;
    }

    /* Features */
    .land-features {
      position: relative; z-index: 10;
      max-width: 1100px; margin: 88px auto 0; padding: 0 40px;
      animation: fadeUp 0.6s ease 0.4s both;
    }
    .land-section-label {
      font-size: 11px; font-weight: 600; color: var(--violet-500);
      letter-spacing: 1.5px; text-transform: uppercase;
      margin-bottom: 10px;
    }
    .land-section-title {
      font-family: 'Instrument Serif', serif;
      font-size: 36px; color: var(--text-1);
      margin-bottom: 40px; font-weight: 400;
    }
    .land-section-title em { font-style: italic; color: var(--violet-500); }
    .land-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    .land-card {
      background: var(--surface);
      border: 1px solid var(--border-soft);
      border-radius: var(--radius-xl);
      padding: 28px;
      box-shadow: var(--shadow-sm);
      transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s;
    }
    .land-card:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
      border-color: var(--violet-200);
    }
    .land-card-icon {
      width: 40px; height: 40px; border-radius: var(--radius-md);
      display: flex; align-items: center; justify-content: center;
      font-size: 18px; margin-bottom: 16px;
    }
    .land-card-num {
      font-size: 10px; font-weight: 600; color: var(--text-3);
      letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px;
    }
    .land-card-title {
      font-size: 16px; font-weight: 600; color: var(--text-1); margin-bottom: 8px;
    }
    .land-card-body {
      font-size: 13.5px; color: var(--text-2); line-height: 1.75;
    }
    .land-card-tag {
      display: inline-block; margin-top: 14px;
      font-size: 10px; font-weight: 500;
      padding: 3px 10px; border-radius: var(--radius-full);
      letter-spacing: 0.3px;
    }

    /* Pipeline */
    .land-pipeline {
      position: relative; z-index: 10;
      max-width: 1100px; margin: 88px auto 0; padding: 0 40px;
    }
    .land-pipe-row {
      display: flex; align-items: center; flex-wrap: wrap;
      gap: 0;
      background: var(--surface);
      border: 1px solid var(--border-soft);
      border-radius: var(--radius-xl);
      padding: 32px 40px;
      box-shadow: var(--shadow-sm);
    }
    .land-pipe-step {
      display: flex; flex-direction: column;
      align-items: center; gap: 6px;
      padding: 12px 16px;
      border-radius: var(--radius-lg);
      min-width: 76px;
      transition: all 0.2s;
      cursor: default;
    }
    .land-pipe-step:hover {
      background: var(--violet-50);
      transform: translateY(-2px);
    }
    .land-pipe-icon {
      font-size: 20px; margin-bottom: 2px;
    }
    .land-pipe-lbl {
      font-size: 11px; font-weight: 600;
      color: var(--text-2); letter-spacing: 0.3px;
    }
    .land-pipe-sub {
      font-size: 10px; color: var(--text-3);
    }
    .land-pipe-arrow {
      color: var(--violet-200); font-size: 16px;
      flex-shrink: 0; padding: 0 4px;
      animation: arrowPulse 2.5s ease-in-out infinite;
    }
    .land-pipe-arrow:nth-child(even) { animation-delay: 0.5s; }
    @keyframes arrowPulse { 0%,100%{color:var(--violet-200);} 50%{color:var(--violet-500);} }

    /* Stack tags */
    .land-stack {
      position: relative; z-index: 10;
      max-width: 1100px; margin: 88px auto 0; padding: 0 40px;
    }
    .land-tags { display: flex; flex-wrap: wrap; gap: 10px; }
    .land-tag {
      padding: 7px 16px;
      font-size: 12px; font-weight: 500;
      border-radius: var(--radius-full);
      border: 1px solid;
      transition: transform 0.2s; cursor: default;
    }
    .land-tag:hover { transform: translateY(-2px); }
    .t-violet { color: var(--violet-600); border-color: var(--violet-200); background: var(--violet-50); }
    .t-mint   { color: var(--mint-text); border-color: #A7F3D0; background: var(--mint-bg); }
    .t-rose   { color: var(--rose-text); border-color: #FECDD3; background: var(--rose-bg); }
    .t-amber  { color: var(--amber-text); border-color: #FDE68A; background: var(--amber-bg); }

    /* Footer */
    .land-footer {
      position: relative; z-index: 10;
      max-width: 1100px; margin: 80px auto 0;
      padding: 24px 40px 64px;
      border-top: 1px solid var(--border-soft);
      display: flex; justify-content: space-between;
      align-items: center; flex-wrap: wrap; gap: 12px;
    }
    .land-footer span {
      font-size: 12px; color: var(--text-3); font-weight: 400;
    }
    </style>

    <div class="land-root">
      <nav class="land-nav">
        <div class="land-logo">
          <div class="land-logo-dot"></div>
          NeuralDoc
        </div>
        <div class="land-nav-badge">Production RAG v1.0</div>
      </nav>

      <div class="land-hero">
        <div class="land-eyebrow">
          <span class="land-eyebrow-dot"></span>
          Zero hallucination tolerance
        </div>
        <h1 class="land-h1">
          Ask anything.<br><em>Know everything.</em>
        </h1>
        <p class="land-sub">
          A <strong>production-grade</strong> RAG system that answers questions
          from your documents with <strong>inline citations</strong>,
          hybrid retrieval, and a hard refusal trigger &mdash; no guessing, ever.
        </p>
      </div>

      <div class="land-stats">
        <div class="land-stat">
          <div class="land-stat-val">0%</div>
          <div class="land-stat-lbl">Hallucination rate</div>
        </div>
        <div class="land-stat">
          <div class="land-stat-val">3×</div>
          <div class="land-stat-lbl">Retrieval methods</div>
        </div>
        <div class="land-stat">
          <div class="land-stat-val">100%</div>
          <div class="land-stat-lbl">Local & private</div>
        </div>
        <div class="land-stat">
          <div class="land-stat-val">∞</div>
          <div class="land-stat-lbl">Documents</div>
        </div>
      </div>

      <div class="land-features">
        <div class="land-section-label">Capabilities</div>
        <div class="land-section-title">Six <em>pillars</em> of precision</div>
        <div class="land-cards">
          <div class="land-card">
            <div class="land-card-icon" style="background:var(--mint-bg);">📄</div>
            <div class="land-card-num">01 — Ingestion</div>
            <div class="land-card-title">Smart PDF Parsing</div>
            <div class="land-card-body">Multi-column layouts, embedded tables, complex structures. Headers and footers stripped automatically.</div>
            <span class="land-card-tag" style="color:var(--mint-text);background:var(--mint-bg);border:1px solid #A7F3D0;">pdfplumber</span>
          </div>
          <div class="land-card">
            <div class="land-card-icon" style="background:var(--violet-50);">✂️</div>
            <div class="land-card-num">02 — Chunking</div>
            <div class="land-card-title">Semantic Chunking</div>
            <div class="land-card-body">Header-aware chunks of 500–800 tokens. Every chunk carries source, page, and section breadcrumb.</div>
            <span class="land-card-tag" style="color:var(--violet-600);background:var(--violet-50);border:1px solid var(--violet-200);">tiktoken</span>
          </div>
          <div class="land-card">
            <div class="land-card-icon" style="background:var(--sky-bg);">🔍</div>
            <div class="land-card-num">03 — Retrieval</div>
            <div class="land-card-title">Hybrid Search</div>
            <div class="land-card-body">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion.</div>
            <span class="land-card-tag" style="color:var(--sky-text);background:var(--sky-bg);border:1px solid #BAE6FD;">RRF Fusion</span>
          </div>
          <div class="land-card">
            <div class="land-card-icon" style="background:var(--amber-bg);">⚡</div>
            <div class="land-card-num">04 — Reranking</div>
            <div class="land-card-title">Cross-Encoder Precision</div>
            <div class="land-card-body">Top 20 candidates re-scored. Only the highest-confidence 5 reach the generation layer.</div>
            <span class="land-card-tag" style="color:var(--amber-text);background:var(--amber-bg);border:1px solid #FDE68A;">ms-marco</span>
          </div>
          <div class="land-card">
            <div class="land-card-icon" style="background:#FFF0F9;">✍️</div>
            <div class="land-card-num">05 — Generation</div>
            <div class="land-card-title">Attributed Answers</div>
            <div class="land-card-body">Every claim carries an inline citation [Source, p.X]. Full References section on every response.</div>
            <span class="land-card-tag" style="color:#9333EA;background:#FAF5FF;border:1px solid #E9D5FF;">LangGraph</span>
          </div>
          <div class="land-card">
            <div class="land-card-icon" style="background:var(--rose-bg);">🛡️</div>
            <div class="land-card-num">06 — Safety</div>
            <div class="land-card-title">Hard Refusal Gate</div>
            <div class="land-card-body">Context below confidence threshold triggers a fixed refusal. No speculation, no hallucination.</div>
            <span class="land-card-tag" style="color:var(--rose-text);background:var(--rose-bg);border:1px solid #FECDD3;">Threshold Gate</span>
          </div>
        </div>
      </div>

      <div class="land-pipeline">
        <div class="land-section-label" style="margin-top:0;">Architecture</div>
        <div class="land-section-title">The <em>pipeline</em></div>
        <div class="land-pipe-row">
          <div class="land-pipe-step"><div class="land-pipe-icon">📄</div><div class="land-pipe-lbl">Parse</div><div class="land-pipe-sub">pdfplumber</div></div>
          <div class="land-pipe-arrow">→</div>
          <div class="land-pipe-step"><div class="land-pipe-icon">✂️</div><div class="land-pipe-lbl">Chunk</div><div class="land-pipe-sub">tiktoken</div></div>
          <div class="land-pipe-arrow">→</div>
          <div class="land-pipe-step"><div class="land-pipe-icon">🔢</div><div class="land-pipe-lbl">Embed</div><div class="land-pipe-sub">miniLM</div></div>
          <div class="land-pipe-arrow">→</div>
          <div class="land-pipe-step"><div class="land-pipe-icon">🔤</div><div class="land-pipe-lbl">BM25</div><div class="land-pipe-sub">keyword</div></div>
          <div class="land-pipe-arrow">→</div>
          <div class="land-pipe-step"><div class="land-pipe-icon">🔀</div><div class="land-pipe-lbl">Fuse</div><div class="land-pipe-sub">RRF</div></div>
          <div class="land-pipe-arrow">→</div>
          <div class="land-pipe-step"><div class="land-pipe-icon">📊</div><div class="land-pipe-lbl">Rerank</div><div class="land-pipe-sub">cross-enc</div></div>
          <div class="land-pipe-arrow">→</div>
          <div class="land-pipe-step"><div class="land-pipe-icon">🤖</div><div class="land-pipe-lbl">Generate</div><div class="land-pipe-sub">llama3.1</div></div>
          <div class="land-pipe-arrow">→</div>
          <div class="land-pipe-step"><div class="land-pipe-icon">📌</div><div class="land-pipe-lbl">Cite</div><div class="land-pipe-sub">attributed</div></div>
        </div>
      </div>

      <div class="land-stack">
        <div class="land-section-label" style="margin-top:0;">Stack</div>
        <div class="land-section-title">Built <em>with</em></div>
        <div class="land-tags">
          <span class="land-tag t-mint">pdfplumber</span>
          <span class="land-tag t-mint">ChromaDB</span>
          <span class="land-tag t-mint">sentence-transformers</span>
          <span class="land-tag t-violet">LangGraph</span>
          <span class="land-tag t-violet">langchain-ollama</span>
          <span class="land-tag t-violet">llama3.1:8b</span>
          <span class="land-tag t-rose">BM25 + RRF</span>
          <span class="land-tag t-rose">cross-encoder reranker</span>
          <span class="land-tag t-amber">FastAPI</span>
          <span class="land-tag t-amber">Streamlit</span>
          <span class="land-tag t-amber">Python 3.14</span>
        </div>
      </div>

      <div class="land-footer">
        <span>NeuralDoc — Production RAG System</span>
        <span>Ollama · ChromaDB · LangGraph · FastAPI</span>
      </div>
    </div>
    """)

    # Launch button
    st.html("""<style>
    .launch-wrap {
      position: relative; z-index: 20;
      display: flex; justify-content: center;
      padding: 40px 0 0; margin-top: -20px;
      background: transparent;
    }
    [data-testid="stButton"] > button {
      background: var(--violet-500) !important;
      color: white !important;
      border: none !important;
      border-radius: var(--radius-full) !important;
      font-family: 'Plus Jakarta Sans', sans-serif !important;
      font-size: 15px !important;
      font-weight: 600 !important;
      padding: 14px 40px !important;
      letter-spacing: 0.2px !important;
      box-shadow: var(--shadow-violet) !important;
      transition: all 0.2s ease !important;
      min-width: 200px !important;
    }
    [data-testid="stButton"] > button:hover {
      background: var(--violet-600) !important;
      transform: translateY(-2px) !important;
      box-shadow: 0 8px 20px rgba(139,92,246,0.35) !important;
    }
    [data-testid="stButton"] > button:active {
      transform: scale(0.97) !important;
    }
    </style>""")

    _l, _m, _r = st.columns([3, 2, 3])
    with _m:
        if st.button("Open App →", key="go_chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# CHAT PAGE — Pastel minimal dashboard
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    body, [data-testid="stAppViewContainer"] {
      background: var(--bg) !important;
    }
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .block-container {
      padding: 0 !important;
      background: transparent !important;
      max-width: 100% !important;
    }

    /* Inputs */
    .stTextInput input {
      background: var(--surface) !important;
      border: 1.5px solid var(--border-soft) !important;
      border-radius: var(--radius-md) !important;
      color: var(--text-1) !important;
      font-family: 'Plus Jakarta Sans', sans-serif !important;
      font-size: 14px !important;
      padding: 11px 16px !important;
      box-shadow: var(--shadow-sm) !important;
      transition: border-color 0.15s, box-shadow 0.15s !important;
    }
    .stTextInput input:focus {
      border-color: var(--violet-400) !important;
      box-shadow: 0 0 0 3px var(--violet-100) !important;
      outline: none !important;
    }
    .stTextInput input::placeholder { color: var(--text-3) !important; }
    .stTextInput label, .stFileUploader label { display: none !important; }

    /* Buttons */
    .stButton > button {
      background: var(--violet-500) !important;
      color: white !important;
      border: none !important;
      border-radius: var(--radius-md) !important;
      font-family: 'Plus Jakarta Sans', sans-serif !important;
      font-weight: 600 !important;
      font-size: 13px !important;
      padding: 10px 0 !important;
      box-shadow: 0 2px 8px rgba(139,92,246,0.2) !important;
      transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
      background: var(--violet-600) !important;
      transform: translateY(-1px) !important;
      box-shadow: var(--shadow-violet) !important;
    }
    .stButton > button:active { transform: scale(0.97) !important; }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
      background: var(--surface) !important;
      border: 1.5px dashed var(--violet-200) !important;
      border-radius: var(--radius-lg) !important;
      transition: all 0.2s !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
      border-color: var(--violet-400) !important;
      background: var(--violet-50) !important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: var(--text-2) !important; }

    /* Selectbox */
    .stSelectbox [data-baseweb="select"] > div {
      background: var(--surface) !important;
      border: 1.5px solid var(--border-soft) !important;
      border-radius: var(--radius-md) !important;
      color: var(--text-1) !important;
      font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    hr { border-color: var(--border-soft) !important; }
    </style>""")

    def get_health():
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3).json()
            r["_reachable"] = True
            return r
        except Exception:
            return {"pipeline_ready": False, "total_chunks": 0,
                    "indexed_files": [], "_reachable": False}

    h = get_health()
    api_ok = h.get("_reachable", False)
    ready = h.get("pipeline_ready", False)
    chunks = h.get("total_chunks", 0)
    files = h.get("indexed_files", [])

    # ── Top navigation bar ────────────────────────────────────────────────────
    st.html(f"""<style>
    .app-topbar {{
      display: flex; align-items: center;
      justify-content: space-between;
      padding: 16px 32px;
      background: rgba(255,255,255,0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-soft);
      position: sticky; top: 0; z-index: 100;
    }}
    .app-logo {{
      font-family: 'Instrument Serif', serif;
      font-size: 18px; color: var(--text-1);
      display: flex; align-items: center; gap: 7px;
    }}
    .app-logo-dot {{
      width: 7px; height: 7px; border-radius: 50%;
      background: var(--violet-500);
    }}
    .app-status {{
      display: inline-flex; align-items: center; gap: 6px;
      font-size: 12px; font-weight: 500;
      padding: 5px 12px; border-radius: var(--radius-full);
      border: 1px solid;
    }}
    .app-status-dot {{
      width: 5px; height: 5px; border-radius: 50%;
    }}
    .status-ready   {{ color: var(--mint-text);  background: var(--mint-bg);  border-color: #A7F3D0; }}
    .status-warn    {{ color: var(--amber-text); background: var(--amber-bg); border-color: #FDE68A; }}
    .status-offline {{ color: var(--rose-text);  background: var(--rose-bg);  border-color: #FECDD3; }}
    </style>
    <div class="app-topbar">
      <div class="app-logo">
        <div class="app-logo-dot"></div>
        NeuralDoc
      </div>
      <div class="app-status {'status-ready' if ready else 'status-warn' if api_ok else 'status-offline'}">
        <div class="app-status-dot" style="background:{'var(--mint-text)' if ready else 'var(--amber-text)' if api_ok else 'var(--rose-text)'};"></div>
        {'Ready · ' + str(chunks) + ' chunks indexed' if ready else ('API online · No documents indexed' if api_ok else 'API offline')}
      </div>
    </div>""")

    # Nav buttons row
    nb1, nb2, nb_gap = st.columns([1, 1, 8])
    with nb1:
        st.html('<div style="padding:12px 16px 0;"></div>')
        if st.button("← Home", key="back_home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
    with nb2:
        st.html('<div style="padding:12px 16px 0;"></div>')
        if st.button("Clear Chat", key="clr_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.html('<div style="height:24px;"></div>')

    # ── Main layout ───────────────────────────────────────────────────────────
    col_chat, col_upload = st.columns([3, 2], gap="large")

    # ── RIGHT: Upload panel ───────────────────────────────────────────────────
    with col_upload:
        st.html("""<div style="padding:0 24px 0 0;">""")

        # Panel header
        uh1, uh2 = st.columns([3, 1])
        with uh1:
            st.html("""
            <div style="margin-bottom:16px;">
              <div style="font-size:10px;font-weight:600;color:var(--violet-500);
                letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">
                Knowledge Base
              </div>
              <div style="font-family:'Instrument Serif',serif;font-size:26px;
                color:var(--text-1);line-height:1.1;">
                Upload <em style="font-style:italic;color:var(--violet-500);">documents</em>
              </div>
            </div>""")
        with uh2:
            st.html('<div style="height:32px;"></div>')
            if st.button("Clear", key="clear_idx", use_container_width=True,
                         help="Wipe all indexed documents"):
                try:
                    resp = requests.delete(f"{API_BASE}/index", timeout=15)
                    if resp.status_code == 200:
                        st.success("Index cleared.")
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("API offline.")

        # Upload area hint
        st.html("""
        <div style="background:var(--violet-50);border:1.5px dashed var(--violet-200);
          border-radius:var(--radius-lg);padding:18px 20px;margin-bottom:12px;
          text-align:center;">
          <div style="font-size:20px;margin-bottom:6px;">📎</div>
          <div style="font-size:13px;font-weight:500;color:var(--text-2);margin-bottom:3px;">
            Drop your PDF below
          </div>
          <div style="font-size:11px;color:var(--text-3);">
            Parsed → Chunked → Embedded → Indexed
          </div>
        </div>""")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")

        if uploaded:
            st.html(f"""
            <div style="background:var(--mint-bg);border:1px solid #A7F3D0;
              border-radius:var(--radius-md);padding:10px 14px;margin-bottom:10px;
              display:flex;align-items:center;gap:8px;">
              <span style="font-size:14px;">📄</span>
              <div>
                <div style="font-size:13px;font-weight:500;color:var(--text-1);">{uploaded.name}</div>
                <div style="font-size:11px;color:var(--mint-text);">{uploaded.size//1024} KB</div>
              </div>
            </div>""")
            if st.button("Index Document", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing PDF..."):
                    try:
                        resp = requests.post(f"{API_BASE}/ingest",
                            files={"file": (uploaded.name, uploaded, "application/pdf")},
                            timeout=120)
                        if resp.status_code == 200:
                            d = resp.json()
                            st.success(f"✓ Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                            st.rerun()
                        else:
                            st.error(f"Error: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("API offline. Run: uv run uvicorn api:app --reload --port 8000")
                    except Exception as e:
                        st.error(str(e))

        # Indexed files
        if files:
            st.html("""<div style="font-size:11px;font-weight:600;color:var(--text-3);
              letter-spacing:1px;text-transform:uppercase;margin:16px 0 8px;">
              Indexed files</div>""")
            for f in files:
                fname = f.replace("\\", "/").split("/")[-1]
                st.html(f"""
                <div style="background:var(--surface);border:1px solid var(--border-soft);
                  border-radius:var(--radius-md);padding:10px 14px;margin-bottom:6px;
                  display:flex;align-items:center;gap:8px;box-shadow:var(--shadow-sm);">
                  <span style="font-size:14px;">📄</span>
                  <span style="font-size:13px;font-weight:500;color:var(--text-1);">{fname}</span>
                  <span style="margin-left:auto;font-size:10px;font-weight:600;padding:2px 8px;
                    border-radius:var(--radius-full);color:var(--mint-text);
                    background:var(--mint-bg);border:1px solid #A7F3D0;">indexed</span>
                </div>""")

        # Notes card
        st.html("""
        <div style="margin-top:20px;background:var(--surface);
          border:1px solid var(--border-soft);border-radius:var(--radius-lg);
          padding:18px 20px;box-shadow:var(--shadow-sm);">
          <div style="font-size:11px;font-weight:600;color:var(--text-3);
            letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;">Tips</div>
          <div style="font-size:13px;color:var(--text-2);line-height:1.9;">
            Click <b style="color:var(--text-1);font-weight:600;">Clear</b> before switching documents.<br>
            Ask precise questions for best citation accuracy.<br>
            Every answer includes inline source references.<br>
            Unanswerable queries return a refusal, not a guess.
          </div>
        </div>""")

        st.html("</div>")

    # ── LEFT: Chat panel ──────────────────────────────────────────────────────
    with col_chat:
        st.html("""<div style="padding:0 0 0 24px;">""")

        # Chat header
        st.html(f"""
        <div style="display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:20px;">
          <div>
            <div style="font-size:10px;font-weight:600;color:var(--violet-500);
              letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">
              Document QA
            </div>
            <div style="font-family:'Instrument Serif',serif;font-size:26px;
              color:var(--text-1);line-height:1.1;">
              Ask your <em style="font-style:italic;color:var(--violet-500);">documents</em>
            </div>
          </div>
          <div style="display:flex;gap:8px;align-items:center;padding-bottom:4px;">
            <div style="font-size:11px;font-weight:500;color:var(--text-3);
              background:var(--surface2);padding:4px 10px;border-radius:var(--radius-full);
              border:1px solid var(--border-soft);">{chunks} chunks</div>
            <div style="font-size:11px;font-weight:500;
              padding:4px 10px;border-radius:var(--radius-full);border:1px solid;
              {'color:var(--mint-text);background:var(--mint-bg);border-color:#A7F3D0;' if ready else 'color:var(--rose-text);background:var(--rose-bg);border-color:#FECDD3;'}">
              {'● Ready' if ready else '○ Not ready'}</div>
          </div>
        </div>""")

        # Messages area
        if st.session_state.messages:
            html = ""
            for m in st.session_state.messages:
                if m["role"] == "user":
                    html += f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:16px;">
                      <div style="max-width:75%;padding:12px 16px;
                        background:var(--violet-500);color:white;
                        border-radius:16px 4px 16px 16px;
                        font-size:14px;line-height:1.65;
                        font-family:'Plus Jakarta Sans',sans-serif;
                        box-shadow:0 2px 8px rgba(139,92,246,0.2);">
                        {m['content']}
                      </div>
                    </div>"""
                else:
                    refs = ""
                    if m.get("references"):
                        refs = '<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs += f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:var(--radius-full);color:var(--sky-text);background:var(--sky-bg);border:1px solid #BAE6FD;cursor:default;">📌 {ref}</span>'
                        refs += "</div>"
                    rfsd = '<div style="margin-top:8px;font-size:12px;font-weight:500;color:var(--rose-text);background:var(--rose-bg);border:1px solid #FECDD3;padding:6px 12px;border-radius:var(--radius-md);display:inline-block;">⚠ Insufficient evidence — refusal triggered</div>' if m.get("refused") else ""
                    lat = f'<div style="margin-top:6px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:var(--text-3);">{m.get("latency_ms","")} ms</div>' if m.get("latency_ms") else ""
                    html += f"""
                    <div style="display:flex;margin-bottom:16px;gap:10px;align-items:flex-start;">
                      <div style="width:28px;height:28px;border-radius:var(--radius-md);flex-shrink:0;
                        margin-top:2px;background:var(--violet-100);
                        display:flex;align-items:center;justify-content:center;
                        font-size:13px;border:1px solid var(--violet-200);">✦</div>
                      <div style="max-width:85%;padding:12px 16px;
                        background:var(--surface);border:1px solid var(--border-soft);
                        border-radius:4px 16px 16px 16px;
                        font-size:14px;color:var(--text-1);line-height:1.75;
                        font-family:'Plus Jakarta Sans',sans-serif;
                        box-shadow:var(--shadow-sm);">
                        {m['content']}{refs}{rfsd}{lat}
                      </div>
                    </div>"""
            st.html(f"""
            <div style="max-height:50vh;overflow-y:auto;padding:4px 2px 12px;
              scrollbar-width:thin;scrollbar-color:var(--violet-200) transparent;">
              {html}
            </div>""")
        else:
            st.html("""
            <div style="text-align:center;padding:56px 20px;
              background:linear-gradient(145deg, var(--surface), #FAFAFF);
              border:1px solid var(--border-soft);
              border-radius:var(--radius-xl);margin-bottom:16px;
              box-shadow:var(--shadow-sm);position:relative;overflow:hidden;">
              
              <!-- Subtle colorful background blur -->
              <div style="position:absolute;top:-40px;left:-40px;width:120px;height:120px;background:var(--mint-bg);border-radius:50%;filter:blur(40px);z-index:0;"></div>
              <div style="position:absolute;bottom:-40px;right:-40px;width:120px;height:120px;background:var(--rose-bg);border-radius:50%;filter:blur(40px);z-index:0;"></div>
              
              <div style="position:relative;z-index:1;">
                <div style="width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg, var(--violet-100), var(--sky-bg));
                  display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:28px;
                  color:var(--violet-600);border:1px solid var(--violet-200);box-shadow:var(--shadow-sm);">✦</div>
                <div style="font-family:'Instrument Serif',serif;font-size:26px;
                  color:var(--text-1);margin-bottom:8px;">
                  Ask anything
                </div>
                <div style="font-size:14px;color:var(--text-2);max-width:320px;margin:0 auto;line-height:1.7;">
                  Upload a PDF on the right, then ask questions here. Every answer is <span style="color:var(--mint-text);font-weight:600;">cited</span>.
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:24px;">
                  <span style="font-size:12px;font-weight:600;color:var(--mint-text);background:var(--mint-bg);
                    border:1px solid #A7F3D0;padding:6px 14px;border-radius:var(--radius-full);
                    box-shadow:0 1px 2px rgba(5,150,105,0.05);cursor:default;">What is the main finding?</span>
                  <span style="font-size:12px;font-weight:600;color:var(--sky-text);background:var(--sky-bg);
                    border:1px solid #BAE6FD;padding:6px 14px;border-radius:var(--radius-full);
                    box-shadow:0 1px 2px rgba(2,132,199,0.05);cursor:default;">Summarise section 3</span>
                  <span style="font-size:12px;font-weight:600;color:var(--rose-text);background:var(--rose-bg);
                    border:1px solid #FECDD3;padding:6px 14px;border-radius:var(--radius-full);
                    box-shadow:0 1px 2px rgba(225,29,72,0.05);cursor:default;">What are the key risks?</span>
                </div>
              </div>
            </div>""")

        st.html("<div style='height:8px'></div>")

        # Input styling
        st.html("""
        <style>
        .stTextInput input {
          border: 2px solid transparent !important;
          background-image: linear-gradient(var(--surface), var(--surface)), linear-gradient(135deg, var(--violet-200), var(--sky-text), var(--mint-text)) !important;
          background-origin: border-box !important;
          background-clip: padding-box, border-box !important;
          box-shadow: var(--shadow-md) !important;
          transition: all 0.3s ease !important;
        }
        .stTextInput input:focus {
          background-image: linear-gradient(var(--surface), var(--surface)), linear-gradient(135deg, var(--violet-400), var(--sky-text), var(--mint-text)) !important;
          box-shadow: 0 4px 14px rgba(139,92,246,0.15) !important;
        }
        </style>
        """)

        qc, bc = st.columns([6, 1])
        with qc:
            query = st.text_input(
                "Your question",
                placeholder="Ask anything about your documents...",
                label_visibility="hidden",
                key="q_in"
            )
        with bc:
            ask = st.button("Send →", use_container_width=True)

        if ask and query:
            if not ready:
                st.warning("Upload and index a PDF first.")
            else:
                with st.spinner("Thinking..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/query",
                            json={"query": query},
                            timeout=120
                        )
                        if resp.status_code == 200:
                            d = resp.json()
                            st.session_state.messages.extend([
                                {"role": "user", "content": query},
                                {"role": "assistant", "content": d["answer"],
                                 "references": d["references"],
                                 "refused": d["refused"],
                                 "latency_ms": d["latency_ms"]}
                            ])
                            st.rerun()
                        else:
                            st.error(f"API error: {resp.json().get('detail', resp.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach API. Run: uv run uvicorn api:app --reload --port 8000")

        st.html("</div>")