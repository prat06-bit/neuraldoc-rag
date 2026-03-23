"""NeuralDoc RAG — Dark neon landing + pastel minimal chat."""
import requests
import streamlit as st

st.set_page_config(
    page_title="NeuralDoc",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "messages" not in st.session_state:
    st.session_state.messages = []

API_BASE = "http://localhost:8000"

# ── Global chrome kill ────────────────────────────────────────────────────────
st.html("""<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  /* Dark neon */
  --black:    #0A0A1A;
  --cyan:     #00FFD0;
  --magenta:  #FF006B;
  --green:    #00FFB0;
  --purple:   #6B1AFF;
  --white:    #FFFFFF;
  --body-txt: #E0E0E0;

  /* Pastel app */
  --bg-app:      #F7F4FF;
  --panel-white: #FFFFFF;
  --panel-lav:   #F4F0FF;
  --v:           #8B5CF6;
  --v-dark:      #7C3AED;
  --v-bg:        #F4F0FF;
  --v-pill:      #E9DFFF;
  --txt1:        #222222;
  --txt2:        #A1A1AA;
  --txt-lbl:     #B0A7C3;
  --bdr:         #E5E7EB;
  --bdr-p:       #E9DFFF;
  --sh:          0 4px 24px rgba(139,92,246,0.08);
  --sh-btn:      0 4px 24px rgba(139,92,246,0.12);
  --r-card:      18px; --r-btn: 12px;
  --r-pill:      16px; --r-full: 9999px;
}

* { box-sizing:border-box; margin:0; padding:0; }
html,body { font-family:'Inter',sans-serif!important; }

[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],#MainMenu,footer {
  display:none!important; height:0!important; }

[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],.block-container {
  background:transparent!important; padding:0!important;
  margin:0!important; max-width:100%!important; border:none!important; }

[data-testid="stVerticalBlock"] { gap:0!important; }
[data-testid="stVerticalBlock"]>div { margin:0!important; padding:0!important; }
</style>""")


# ═════════════════════════════════════════════════════════════════════════════
# LANDING  — dark neon spec
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.html("""<style>
    [data-testid="stAppViewContainer"] { background: var(--black)!important; }

    /* CTA button */
    [data-testid="stButton"]>button {
      background: linear-gradient(90deg,#6B1AFF 0%,#FF006B 50%,#00FFD0 100%)!important;
      background-size: 200% 100%!important;
      color: #fff!important; border: none!important;
      border-radius: 32px!important;
      font-family: 'Inter',sans-serif!important;
      font-size: 19px!important; font-weight: 500!important;
      height: 64px!important; padding: 0!important; width:100%!important;
      box-shadow: 0 4px 32px 0 rgba(0,255,208,0.22)!important;
      letter-spacing: 0.02em!important;
      transition: background-position 0.4s ease, box-shadow 0.3s ease, transform 0.15s!important;
      cursor: pointer!important;
    }
    [data-testid="stButton"]>button:hover {
      background-position: 100% 0!important;
      box-shadow: 0 6px 40px 0 rgba(0,255,208,0.42), 0 2px 16px rgba(255,0,107,0.28)!important;
      transform: translateY(-2px)!important;
    }
    [data-testid="stButton"]>button:active { transform: scale(0.97)!important; }
    </style>""")

    # Full page HTML
    st.html("""
    <style>
    .land {
      min-height: 100vh;
      background:
        radial-gradient(ellipse 70% 60% at 0% 0%,   rgba(107,26,255,0.38) 0%, transparent 60%),
        radial-gradient(ellipse 55% 55% at 100% 100%,rgba(0,255,208,0.22) 0%, transparent 55%),
        radial-gradient(ellipse 45% 45% at 55% 45%,  rgba(255,0,107,0.18) 0%, transparent 50%),
        #0A0A1A;
      position: relative; overflow: hidden;
    }
    /* Grid overlay */
    .land::before {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
      background-image:
        linear-gradient(rgba(255,255,255,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px);
      background-size: 80px 80px;
    }
    /* Animate glows */
    @keyframes floatOrb {
      0%,100%{transform:translate(0,0) scale(1);}
      33%{transform:translate(30px,-40px) scale(1.08);}
      66%{transform:translate(-20px,30px) scale(0.94);}
    }
    .orb {
      position:fixed; border-radius:50%; filter:blur(80px);
      pointer-events:none; z-index:0;
      animation: floatOrb linear infinite;
    }
    .orb1{width:520px;height:520px;background:rgba(107,26,255,.22);top:-180px;left:-180px;animation-duration:22s;}
    .orb2{width:420px;height:420px;background:rgba(0,255,208,.14);bottom:-140px;right:-140px;animation-duration:28s;animation-delay:-10s;}
    .orb3{width:320px;height:320px;background:rgba(255,0,107,.12);top:40%;left:52%;animation-duration:18s;animation-delay:-5s;}

    /* Navbar */
    .nav {
      position:relative; z-index:10;
      display:flex; align-items:center; justify-content:space-between;
      max-width:1100px; margin:0 auto;
      padding:40px 48px 0;
      animation: navIn 0.6s ease both;
    }
    @keyframes navIn{from{opacity:0;transform:translateY(-14px);}to{opacity:1;transform:translateY(0);}}
    .logo {
      font-family:'Montserrat',sans-serif; font-size:26px;
      font-weight:800; letter-spacing:0.1em; text-transform:uppercase;
    }
    .logo-n { color:#00FFD0; }
    .logo-d { color:#FF006B; }
    .nav-badge {
      font-family:'Inter',sans-serif; font-size:14px; font-weight:500;
      color:#00FFD0; text-transform:uppercase; letter-spacing:0.15em;
      border:1.5px solid #00FFD0; border-radius:24px;
      padding:7px 22px; background:transparent;
      transition: box-shadow 0.2s;
    }
    .nav-badge:hover { box-shadow:0 0 14px rgba(0,255,208,0.5); }

    /* Hero */
    .hero {
      position:relative; z-index:10;
      max-width:900px; margin:0 auto;
      padding:80px 48px 0; text-align:center;
    }

    /* Decorative badge */
    .h-badge {
      display:inline-block;
      font-family:'Inter',sans-serif; font-size:14px; font-weight:500;
      color:#FF006B; text-transform:uppercase; letter-spacing:0.15em;
      border:1.5px solid #FF006B; border-radius:24px;
      padding:7px 22px; background:transparent; margin-bottom:48px;
      box-shadow: 0 0 18px rgba(255,0,107,0.28);
      animation: badgeIn 0.7s ease 0.1s both;
    }
    @keyframes badgeIn{from{opacity:0;transform:translateY(-10px);}to{opacity:1;transform:translateY(0);}}

    /* Main heading stacked */
    .h-title {
      font-family:'Montserrat',sans-serif; font-weight:900;
      font-size:clamp(56px,8vw,100px);
      text-transform:uppercase; letter-spacing:-0.02em;
      line-height:0.92; margin-bottom:48px;
      animation: headIn 0.8s ease 0.2s both;
    }
    @keyframes headIn{from{opacity:0;transform:translateY(28px);}to{opacity:1;transform:translateY(0);}}
    .h-neural {
      display:block;
      background: linear-gradient(90deg,#00FFD0 0%,#FF006B 100%);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .h-doc {
      display:block;
      background: linear-gradient(90deg,#00FFD0 0%,#00FFB0 100%);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .h-rag { display:block; color:#FFFFFF; }

    /* Body text */
    .h-body {
      font-family:'Inter',sans-serif; font-size:19px;
      color:#E0E0E0; line-height:1.7;
      max-width:620px; margin:0 auto 52px;
      animation: bodyIn 0.7s ease 0.5s both;
    }
    @keyframes bodyIn{from{opacity:0;}to{opacity:1;}}
    .h-body .hl1 { color:#00FFD0; font-weight:700; }
    .h-body .hl2 { color:#00FFB0; font-weight:700; }

    /* Stats row */
    .stats {
      display:flex; max-width:800px; margin:64px auto 0;
      background:rgba(255,255,255,0.04);
      border:1px solid rgba(255,255,255,0.08);
      border-radius:20px; overflow:hidden;
      animation: bodyIn 0.7s ease 0.8s both;
    }
    .stat {
      flex:1; padding:26px 12px; text-align:center;
      border-right:1px solid rgba(255,255,255,0.07);
      transition: background 0.2s;
    }
    .stat:last-child { border-right:none; }
    .stat:hover { background:rgba(107,26,255,0.12); }
    .stat-v {
      font-family:'Montserrat',sans-serif; font-size:34px; font-weight:800;
      background:linear-gradient(90deg,#00FFD0,#6B1AFF);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
      line-height:1; margin-bottom:6px;
    }
    .stat-l {
      font-family:'Inter',sans-serif; font-size:10px; font-weight:600;
      color:rgba(255,255,255,0.38); letter-spacing:0.12em; text-transform:uppercase;
    }

    /* Capabilities section */
    .caps {
      position:relative; z-index:10;
      max-width:1100px; margin:96px auto 0; padding:0 48px;
      animation: bodyIn 0.7s ease 1s both;
    }
    .caps-tag {
      font-family:'Inter',sans-serif; font-size:11px; font-weight:700;
      color:#00FFD0; letter-spacing:0.15em; text-transform:uppercase; margin-bottom:12px;
    }
    .caps-title {
      font-family:'Montserrat',sans-serif; font-size:38px; font-weight:800;
      color:#fff; margin-bottom:36px; letter-spacing:-0.02em;
      text-transform:uppercase;
    }
    .caps-title em {
      font-style:italic;
      background:linear-gradient(90deg,#00FFD0,#FF006B);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    }
    .cards-grid {
      display:grid; grid-template-columns:repeat(3,1fr); gap:16px;
    }
    .card {
      background:rgba(255,255,255,0.04);
      border:1px solid rgba(255,255,255,0.08);
      border-radius:16px; padding:22px;
      transition:transform 0.22s,border-color 0.22s,box-shadow 0.22s;
    }
    .card:hover {
      transform:translateY(-5px);
      border-color:rgba(0,255,208,0.3);
      box-shadow:0 8px 32px rgba(0,255,208,0.08);
    }
    .card-num { font-size:10px;font-weight:700;color:rgba(255,255,255,0.25);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:9px; }
    .card-title { font-size:15px;font-weight:600;color:#fff;margin-bottom:7px; }
    .card-body { font-size:13px;color:rgba(255,255,255,0.48);line-height:1.7; }
    .card-tag { display:inline-block;margin-top:12px;font-size:10px;font-weight:600;padding:3px 10px;border-radius:var(--r-full);border:1px solid; }

    /* Pipeline */
    .pipe-wrap {
      position:relative; z-index:10;
      max-width:1100px; margin:80px auto 0; padding:0 48px;
    }
    .pipe-row {
      display:flex; align-items:center; flex-wrap:wrap;
      background:rgba(255,255,255,0.04);
      border:1px solid rgba(255,255,255,0.08);
      border-radius:18px; padding:28px 36px; gap:2px;
    }
    .p-step {
      display:flex;flex-direction:column;align-items:center;gap:5px;
      padding:10px 14px;border-radius:12px;min-width:70px;
      transition:all 0.2s; cursor:default;
    }
    .p-step:hover { background:rgba(107,26,255,0.18); transform:translateY(-2px); }
    .p-lbl { font-size:11px;font-weight:700;color:rgba(255,255,255,0.65);letter-spacing:0.05em; }
    .p-sub { font-size:10px;color:rgba(255,255,255,0.3); }
    .p-arr {
      color:rgba(255,255,255,0.12); font-size:14px; padding:0 2px; flex-shrink:0;
      animation:arrP 2.5s ease-in-out infinite;
    }
    .p-arr:nth-child(even){animation-delay:0.5s;}
    @keyframes arrP{0%,100%{color:rgba(255,255,255,0.1);}50%{color:#00FFD0;}}

    /* Stack */
    .stk {
      position:relative;z-index:10;
      max-width:1100px;margin:80px auto 0;padding:0 48px;
    }
    .tags{display:flex;flex-wrap:wrap;gap:10px;}
    .tag{padding:7px 15px;font-family:'Inter',sans-serif;font-size:11px;font-weight:600;
      border-radius:var(--r-full);border:1px solid;letter-spacing:0.05em;transition:transform 0.2s;}
    .tag:hover{transform:translateY(-2px);}
    .tc{color:#00FFD0;border-color:rgba(0,255,208,0.3);background:rgba(0,255,208,0.06);}
    .tv{color:#A78BFA;border-color:rgba(167,139,250,0.3);background:rgba(167,139,250,0.06);}
    .tm{color:#FF006B;border-color:rgba(255,0,107,0.3);background:rgba(255,0,107,0.06);}
    .ta{color:#FFD600;border-color:rgba(255,214,0,0.3);background:rgba(255,214,0,0.06);}

    /* Footer */
    .footer {
      position:relative;z-index:10;
      max-width:1100px;margin:72px auto 0;
      padding:22px 48px 64px;
      border-top:1px solid rgba(255,255,255,0.07);
      display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;
    }
    .footer span{font-family:'Inter',sans-serif;font-size:12px;color:rgba(255,255,255,0.25);}
    </style>

    <div class="land">
      <div class="orb orb1"></div>
      <div class="orb orb2"></div>
      <div class="orb orb3"></div>

      <!-- NAV -->
      <nav class="nav">
        <div class="logo">
          <span class="logo-n">NEURAL</span><span class="logo-d">DOC</span>
        </div>
        <div class="nav-badge">Production RAG v1.0</div>
      </nav>

      <!-- HERO -->
      <section class="hero">
        <div class="h-badge">&#x2022; Zero Hallucination Tolerance</div>

        <h1 class="h-title">
          <span class="h-neural">NEURAL</span>
          <span class="h-doc">DOC</span>
          <span class="h-rag">RAG</span>
        </h1>

        <p class="h-body">
          A <span class="hl1">production-grade</span> RAG system that answers
          questions from your documents with <span class="hl2">inline citations</span>,
          hybrid retrieval, and a hard refusal trigger &mdash; no guessing, ever.
        </p>
      </section>

      <!-- STATS -->
      <div class="stats">
        <div class="stat">
          <div class="stat-v">0%</div>
          <div class="stat-l">Hallucination Rate</div>
        </div>
        <div class="stat">
          <div class="stat-v">3x</div>
          <div class="stat-l">Retrieval Methods</div>
        </div>
        <div class="stat">
          <div class="stat-v">100%</div>
          <div class="stat-l">Local &amp; Private</div>
        </div>
        <div class="stat">
          <div class="stat-v">inf</div>
          <div class="stat-l">Documents</div>
        </div>
      </div>

      <!-- CAPABILITIES -->
      <div class="caps">
        <div class="caps-tag">// Capabilities</div>
        <div class="caps-title">SIX <em>PILLARS</em></div>
        <div class="cards-grid">
          <div class="card">
            <div class="card-num">01 &mdash; Ingestion</div>
            <div class="card-title">Smart PDF Parsing</div>
            <div class="card-body">Multi-column layouts, embedded tables, complex structures. Headers and footers stripped automatically.</div>
            <span class="card-tag tc">pdfplumber</span>
          </div>
          <div class="card">
            <div class="card-num">02 &mdash; Chunking</div>
            <div class="card-title">Semantic Chunking</div>
            <div class="card-body">Header-aware 500–800 token chunks. Source, page, and section breadcrumb on every chunk.</div>
            <span class="card-tag tv">tiktoken</span>
          </div>
          <div class="card">
            <div class="card-num">03 &mdash; Retrieval</div>
            <div class="card-title">Hybrid Search</div>
            <div class="card-body">BM25 keyword fused with dense vector search via Reciprocal Rank Fusion.</div>
            <span class="card-tag tc">RRF Fusion</span>
          </div>
          <div class="card">
            <div class="card-num">04 &mdash; Reranking</div>
            <div class="card-title">Cross-Encoder Precision</div>
            <div class="card-body">Top 20 candidates re-scored. Only the highest-confidence 5 reach the generation layer.</div>
            <span class="card-tag ta">ms-marco</span>
          </div>
          <div class="card">
            <div class="card-num">05 &mdash; Generation</div>
            <div class="card-title">Attributed Answers</div>
            <div class="card-body">Every claim carries an inline citation [Source, p.X]. Full References section appended.</div>
            <span class="card-tag tv">LangGraph</span>
          </div>
          <div class="card">
            <div class="card-num">06 &mdash; Safety</div>
            <div class="card-title">Hard Refusal Gate</div>
            <div class="card-body">Context below confidence threshold triggers a fixed refusal. No speculation, no hallucination.</div>
            <span class="card-tag tm">Threshold Gate</span>
          </div>
        </div>
      </div>

      <!-- PIPELINE -->
      <div class="pipe-wrap">
        <div class="caps-tag">// Architecture</div>
        <div class="caps-title">THE <em>PIPELINE</em></div>
        <div class="pipe-row">
          <div class="p-step"><div class="p-lbl">PARSE</div><div class="p-sub">pdfplumber</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">CHUNK</div><div class="p-sub">tiktoken</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">EMBED</div><div class="p-sub">miniLM</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">BM25</div><div class="p-sub">keyword</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">FUSE</div><div class="p-sub">RRF</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">RERANK</div><div class="p-sub">cross-enc</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">GENERATE</div><div class="p-sub">llama3.1</div></div>
          <div class="p-arr">&#8594;</div>
          <div class="p-step"><div class="p-lbl">CITE</div><div class="p-sub">attributed</div></div>
        </div>
      </div>

      <!-- STACK -->
      <div class="stk">
        <div class="caps-tag">// Stack</div>
        <div class="caps-title">BUILT <em>WITH</em></div>
        <div class="tags">
          <span class="tag tc">pdfplumber</span>
          <span class="tag tc">ChromaDB</span>
          <span class="tag tc">sentence-transformers</span>
          <span class="tag tv">LangGraph</span>
          <span class="tag tv">langchain-ollama</span>
          <span class="tag tv">llama3.1:8b</span>
          <span class="tag tm">BM25 + RRF</span>
          <span class="tag tm">cross-encoder reranker</span>
          <span class="tag ta">FastAPI</span>
          <span class="tag ta">Streamlit</span>
          <span class="tag ta">Python 3.14</span>
        </div>
      </div>

      <!-- FOOTER -->
      <div class="footer">
        <span>NeuralDoc &mdash; Production RAG System</span>
        <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
      </div>

    </div>""")

    # CTA button — Streamlit renders after the hero HTML
    # We center it over the hero section using negative margin trick
    st.html("""<style>
    .cta-wrap {
      position:relative; z-index:20;
      /* Pull the button up into the hero section */
      margin-top: -360px;
      display:flex; justify-content:center;
      padding:0 48px;
      pointer-events:none;
    }
    /* We can't truly overlap with st.columns but we inject a transparent spacer */
    </style>
    <div style="height:1px;position:relative;z-index:20;"></div>""")

    _l, _m, _r = st.columns([2, 2, 2])
    with _m:
        if st.button("Launch App →", key="go_chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

    # Push the stats back into the flow with a negative spacer
    st.html("""<style>
    /* Pull the button to sit just below the hero body text */
    [data-testid="stHorizontalBlock"] {
      position: relative;
      z-index: 20;
      margin-top: -330px!important;
    }
    </style>""")


# ═════════════════════════════════════════════════════════════════════════════
# CHAT PAGE  — pastel spec (doc 4)
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    [data-testid="stAppViewContainer"] { background: var(--bg-app)!important; }
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container {
      padding:0!important; background:transparent!important; max-width:100%!important; }

    .stTextInput input {
      background: var(--panel-white)!important; border:1px solid var(--bdr)!important;
      border-radius: var(--r-btn)!important; color: var(--txt1)!important;
      font-family:'Inter',sans-serif!important; font-size:15px!important;
      padding:16px 20px!important;
      transition:border-color 0.18s,box-shadow 0.18s!important;
    }
    .stTextInput input:focus {
      border-color:var(--v)!important; box-shadow:0 0 0 2px var(--bdr-p)!important; outline:none!important;
    }
    .stTextInput input::placeholder { color:var(--txt2)!important; }
    .stTextInput label, .stFileUploader label { display:none!important; }

    .stButton>button {
      background:var(--v)!important; color:#fff!important;
      border:none!important; border-radius:var(--r-btn)!important;
      font-family:'Inter',sans-serif!important; font-weight:500!important;
      font-size:15px!important; padding:14px 0!important;
      transition:background 0.15s,transform 0.12s,box-shadow 0.15s!important;
    }
    .stButton>button:hover {
      background:var(--v-dark)!important; transform:translateY(-1px)!important;
      box-shadow:var(--sh-btn)!important;
    }
    .stButton>button:active { transform:scale(0.97)!important; }

    [data-testid="stFileUploaderDropzone"] {
      background:var(--panel-white)!important; border:2px dashed var(--bdr-p)!important;
      border-radius:var(--r-pill)!important; transition:all 0.2s!important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
      border-color:var(--v)!important; background:#F7F4FF!important;
    }
    [data-testid="stFileUploaderDropzone"] * { color:var(--txt1)!important; }
    hr { border-color:var(--bdr)!important; }
    </style>""")

    def get_health():
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3).json()
            r["_reachable"] = True
            return r
        except Exception:
            return {"pipeline_ready":False,"total_chunks":0,"indexed_files":[],"_reachable":False}

    h      = get_health()
    api_ok = h.get("_reachable", False)
    ready  = h.get("pipeline_ready", False)
    chunks = h.get("total_chunks", 0)
    files  = h.get("indexed_files", [])

    if ready:
        bdg_s="color:#059669;background:#ECFDF5;border:1px solid #A7F3D0;"
        bdg_dot="#059669"; bdg_txt=f"Ready &middot; {chunks} chunks indexed"
    elif api_ok:
        bdg_s="color:#B45309;background:#FDE68A;border:1px solid #FCD34D;"
        bdg_dot="#B45309"; bdg_txt="API online &mdash; No documents indexed"
    else:
        bdg_s="color:#B91C1C;background:#FCA5A5;border:1px solid #F87171;"
        bdg_dot="#B91C1C"; bdg_txt="API offline"

    # Topbar
    st.html(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
      height:64px;padding:0 40px;
      background:var(--panel-white);border-bottom:1px solid var(--bdr);
      position:sticky;top:0;z-index:100;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:12px;height:12px;border-radius:50%;background:var(--v);"></div>
        <span style="font-family:'Inter',sans-serif;font-size:20px;font-weight:500;color:var(--txt1);">NeuralDoc</span>
      </div>
      <div style="display:inline-flex;align-items:center;gap:7px;
        font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
        padding:6px 18px;border-radius:var(--r-full);{bdg_s}">
        <div style="width:6px;height:6px;border-radius:50%;background:{bdg_dot};flex-shrink:0;"></div>
        {bdg_txt}
      </div>
    </div>""")

    # Action buttons
    st.html('<div style="padding:24px 40px 0;">')
    b1, b2, _ = st.columns([1, 1, 8])
    with b1:
        if st.button("← Home", key="back_home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
    with b2:
        if st.button("Clear Chat", key="clr_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    st.html('</div><div style="height:24px;"></div>')

    # Two-panel layout
    st.html('<div style="padding:0 40px 40px;">')
    col_chat, col_up = st.columns([2, 1], gap="large")

    # ── RIGHT: Knowledge Base ─────────────────────────────────────────────────
    with col_up:
        st.html("""<div style="background:var(--panel-lav);border-radius:var(--r-card);
          padding:32px 32px 24px;box-shadow:var(--sh);">""")

        uh1, uh2 = st.columns([3, 1])
        with uh1:
            st.html("""<div>
              <div style="font-family:'Inter',sans-serif;font-size:12px;font-weight:600;
                color:var(--txt-lbl);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">
                Knowledge Base</div>
              <div style="font-family:'Playfair Display',serif;font-size:24px;
                font-weight:400;color:var(--v);line-height:1.2;margin-bottom:16px;">
                Upload <em>documents</em></div>
            </div>""")
        with uh2:
            st.html('<div style="height:28px;"></div>')
            if st.button("Clear", key="clear_idx", use_container_width=True):
                try:
                    resp = requests.delete(f"{API_BASE}/index", timeout=15)
                    if resp.status_code == 200:
                        st.success("Index cleared.")
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("API offline.")

        st.html("""
        <div style="background:var(--panel-white);border:2px dashed var(--bdr-p);
          border-radius:var(--r-pill);padding:22px;margin-bottom:14px;text-align:center;
          transition:border-color 0.2s,background 0.2s;"
          onmouseover="this.style.borderColor='var(--v)';this.style.background='#F7F4FF'"
          onmouseout="this.style.borderColor='var(--bdr-p)';this.style.background='var(--panel-white)'">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
            stroke="#8B5CF6" stroke-width="1.5" stroke-linecap="round"
            stroke-linejoin="round" style="margin:0 auto 8px;display:block;">
            <polyline points="16 16 12 12 8 16"></polyline>
            <line x1="12" y1="12" x2="12" y2="21"></line>
            <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"></path>
          </svg>
          <div style="font-family:'Inter',sans-serif;font-size:14px;font-weight:500;
            color:var(--txt1);margin-bottom:4px;">Drop your PDF below</div>
          <div style="font-family:'Inter',sans-serif;font-size:12px;color:var(--txt2);">
            Parsed &#8594; Chunked &#8594; Embedded &#8594; Indexed</div>
        </div>""")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")

        if uploaded:
            st.html(f"""<div style="background:var(--panel-white);border:1px solid #A7F3D0;
              border-radius:var(--r-btn);padding:10px 14px;margin-bottom:10px;">
              <div style="font-family:'Inter',sans-serif;font-size:14px;font-weight:600;color:var(--txt1);">{uploaded.name}</div>
              <div style="font-family:'Inter',sans-serif;font-size:11px;color:#059669;margin-top:2px;">{uploaded.size//1024} KB</div>
            </div>""")
            if st.button("Index Document", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing..."):
                    try:
                        resp = requests.post(f"{API_BASE}/ingest",
                            files={"file":(uploaded.name,uploaded,"application/pdf")},timeout=120)
                        if resp.status_code==200:
                            d=resp.json()
                            st.success(f"Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                            st.rerun()
                        else: st.error(f"Error: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("API offline. Run: uv run uvicorn api:app --reload --port 8000")
                    except Exception as e: st.error(str(e))

        if files:
            st.html("""<div style="font-family:'Inter',sans-serif;font-size:10px;font-weight:700;
              color:var(--txt-lbl);letter-spacing:0.08em;text-transform:uppercase;margin:12px 0 7px;">
              Indexed files</div>""")
            for f in files:
                fname=f.replace("\\","/").split("/")[-1]
                st.html(f"""<div style="background:var(--panel-white);border:1px solid var(--bdr);
                  border-radius:var(--r-btn);padding:8px 13px;margin-bottom:5px;
                  display:flex;align-items:center;box-shadow:var(--sh);">
                  <span style="font-size:13px;font-weight:500;color:var(--txt1);flex:1;">{fname}</span>
                  <span style="font-size:10px;font-weight:700;padding:2px 9px;border-radius:var(--r-full);
                    color:#059669;background:#ECFDF5;border:1px solid #A7F3D0;">indexed</span>
                </div>""")

        st.html("""<div style="margin-top:18px;background:var(--panel-white);
          border-radius:var(--r-btn);padding:16px 18px;box-shadow:var(--sh);">
          <div style="font-family:'Inter',sans-serif;font-size:10px;font-weight:700;
            color:var(--txt-lbl);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:9px;">Tips</div>
          <div style="font-family:'Inter',sans-serif;font-size:13px;color:var(--txt1);line-height:1.9;">
            Click <b>Clear</b> before switching documents.<br>
            Ask precise questions for best citation accuracy.<br>
            Every answer includes inline source references.<br>
            Unanswerable queries return a refusal, not a guess.
          </div></div>""")

        st.html('</div>')

    # ── LEFT: Document QA ─────────────────────────────────────────────────────
    with col_chat:
        st.html("""<div style="background:var(--panel-white);border-radius:var(--r-card);
          padding:32px 32px 24px;box-shadow:var(--sh);">""")

        st.html(f"""
        <div style="display:flex;align-items:flex-start;
          justify-content:space-between;margin-bottom:22px;">
          <div>
            <div style="font-family:'Inter',sans-serif;font-size:12px;font-weight:600;
              color:var(--txt-lbl);letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">
              Document QA</div>
            <div style="font-family:'Playfair Display',serif;font-size:34px;
              font-weight:400;font-style:italic;color:var(--v);line-height:1.15;">
              Ask your <em>documents</em></div>
          </div>
          <div style="display:flex;gap:7px;align-items:center;padding-top:20px;flex-shrink:0;">
            <span style="font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
              color:var(--v);background:var(--v-bg);border:1px solid var(--bdr-p);
              padding:5px 13px;border-radius:var(--r-pill);">{chunks} chunks</span>
            <span style="font-family:'Inter',sans-serif;font-size:13px;font-weight:600;
              padding:5px 13px;border-radius:var(--r-pill);border:1px solid;
              {'color:#059669;background:#ECFDF5;border-color:#A7F3D0;' if ready else 'color:#B91C1C;background:#FCA5A5;border-color:#F87171;'}">
              {'Ready' if ready else 'Not ready'}</span>
          </div>
        </div>""")

        if st.session_state.messages:
            html=""
            for m in st.session_state.messages:
                if m["role"]=="user":
                    html+=f"""<div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
                      <div style="max-width:72%;padding:13px 17px;background:var(--v);color:#fff;
                        border-radius:16px 4px 16px 16px;font-family:'Inter',sans-serif;
                        font-size:14px;line-height:1.65;box-shadow:0 2px 8px rgba(139,92,246,0.2);">
                        {m['content']}</div></div>"""
                else:
                    refs=""
                    if m.get("references"):
                        refs='<div style="margin-top:9px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs+=f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:var(--r-full);color:#0284C7;background:#F0F9FF;border:1px solid #BAE6FD;">{ref}</span>'
                        refs+="</div>"
                    rfsd=""
                    if m.get("refused"):
                        rfsd='<div style="margin-top:7px;font-size:12px;font-weight:600;color:#B91C1C;background:#FCA5A5;border:1px solid #F87171;padding:5px 11px;border-radius:var(--r-btn);display:inline-block;">Insufficient evidence — refusal triggered</div>'
                    lat=""
                    if m.get("latency_ms"):
                        lat=f'<div style="margin-top:4px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:var(--txt2);">{m["latency_ms"]} ms</div>'
                    html+=f"""<div style="display:flex;margin-bottom:14px;gap:9px;align-items:flex-start;">
                      <div style="width:26px;height:26px;border-radius:7px;flex-shrink:0;margin-top:2px;
                        background:var(--v-bg);display:flex;align-items:center;justify-content:center;
                        font-size:11px;font-weight:700;color:var(--v);border:1px solid var(--bdr-p);">N</div>
                      <div style="max-width:84%;padding:13px 16px;background:var(--panel-white);
                        border:1px solid var(--bdr);border-radius:4px 16px 16px 16px;
                        font-family:'Inter',sans-serif;font-size:14px;color:var(--txt1);
                        line-height:1.75;box-shadow:var(--sh);">
                        {m['content']}{refs}{rfsd}{lat}</div></div>"""
            st.html(f"""<div style="max-height:46vh;overflow-y:auto;margin-bottom:14px;
              padding:2px;scrollbar-width:thin;scrollbar-color:var(--bdr-p) transparent;">{html}</div>""")
        else:
            st.html("""<div style="text-align:center;padding:48px 20px 36px;
              border:1px solid var(--bdr);border-radius:var(--r-pill);margin-bottom:14px;">
              <div style="font-family:'Playfair Display',serif;font-size:22px;
                color:var(--txt1);margin-bottom:8px;">Ask anything</div>
              <div style="font-family:'Inter',sans-serif;font-size:14px;color:var(--txt2);
                max-width:300px;margin:0 auto 20px;line-height:1.7;">
                Upload a PDF on the right, then ask questions here. Every answer is cited.</div>
              <div style="display:flex;flex-wrap:wrap;gap:9px;justify-content:center;">
                <span style="font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
                  color:var(--v);background:var(--v-bg);border:1px solid var(--bdr-p);
                  padding:7px 15px;border-radius:var(--r-pill);cursor:default;
                  transition:background 0.15s;"
                  onmouseover="this.style.background='#E9DFFF'"
                  onmouseout="this.style.background='var(--v-bg)'">What is the main finding?</span>
                <span style="font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
                  color:var(--v);background:var(--v-bg);border:1px solid var(--bdr-p);
                  padding:7px 15px;border-radius:var(--r-pill);cursor:default;
                  transition:background 0.15s;"
                  onmouseover="this.style.background='#E9DFFF'"
                  onmouseout="this.style.background='var(--v-bg)'">Summarise section 3</span>
                <span style="font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
                  color:var(--v);background:var(--v-bg);border:1px solid var(--bdr-p);
                  padding:7px 15px;border-radius:var(--r-pill);cursor:default;
                  transition:background 0.15s;"
                  onmouseover="this.style.background='#E9DFFF'"
                  onmouseout="this.style.background='var(--v-bg)'">What are the key risks?</span>
              </div></div>""")

        qc, bc = st.columns([6, 1])
        with qc:
            query=st.text_input("Question",placeholder="Ask anything about your documents...",
                                label_visibility="hidden",key="q_in")
        with bc:
            ask=st.button("Send →",use_container_width=True)

        if ask and query:
            if not ready:
                st.warning("Upload and index a PDF first.")
            else:
                with st.spinner("Thinking..."):
                    try:
                        resp=requests.post(f"{API_BASE}/query",json={"query":query},timeout=120)
                        if resp.status_code==200:
                            d=resp.json()
                            st.session_state.messages.extend([
                                {"role":"user","content":query},
                                {"role":"assistant","content":d["answer"],
                                 "references":d["references"],"refused":d["refused"],
                                 "latency_ms":d["latency_ms"]}])
                            st.rerun()
                        else:
                            st.error(f"API error: {resp.json().get('detail',resp.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach API. Run: uv run uvicorn api:app --reload --port 8000")

        st.html('</div>')
    st.html('</div>')