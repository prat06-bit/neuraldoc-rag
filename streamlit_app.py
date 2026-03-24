"""NeuralDoc RAG — Dark neon throughout."""
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

st.html("""<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --black:   #0A0A1A;
  --card-bg: rgba(255,255,255,0.04);
  --card-br: rgba(255,255,255,0.08);
  --cyan:    #00FFD0;
  --magenta: #FF006B;
  --green:   #00FFB0;
  --purple:  #6B1AFF;
  --white:   #FFFFFF;
  --body:    #E0E0E0;
  --dim:     rgba(255,255,255,0.38);
  --r-full:  9999px;
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


# ═══════════════════════════════════════════════════════════════
# LANDING
# ═══════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.html("""<style>
    [data-testid="stAppViewContainer"] { background: var(--black)!important; }

    [data-testid="stButton"]>button {
      background: linear-gradient(90deg,#6B1AFF 0%,#FF006B 50%,#00FFD0 100%)!important;
      background-size: 200% 100%!important;
      color: #fff!important; border: none!important;
      border-radius: 32px!important;
      font-family: 'Inter',sans-serif!important;
      font-size: 18px!important; font-weight: 500!important;
      height: 60px!important; padding: 0!important; width:100%!important;
      box-shadow: 0 4px 32px 0 rgba(0,255,208,0.22)!important;
      transition: background-position 0.4s,box-shadow 0.3s,transform 0.15s!important;
    }
    [data-testid="stButton"]>button:hover {
      background-position: 100% 0!important;
      box-shadow: 0 6px 40px rgba(0,255,208,0.42),0 2px 16px rgba(255,0,107,0.28)!important;
      transform: translateY(-2px)!important;
    }
    [data-testid="stButton"]>button:active { transform:scale(0.97)!important; }

    /* pull columns up to sit inside hero */
    [data-testid="stHorizontalBlock"] {
      position:relative; z-index:20;
      margin-top: -88px!important;
    }
    </style>""")

    st.html("""
    <style>
    .land {
      background:
        radial-gradient(ellipse 70% 60% at 0% 0%,   rgba(107,26,255,0.38),transparent 60%),
        radial-gradient(ellipse 55% 55% at 100% 100%,rgba(0,255,208,0.22),transparent 55%),
        radial-gradient(ellipse 45% 45% at 55% 45%,  rgba(255,0,107,0.18),transparent 50%),
        #0A0A1A;
      min-height:100vh; position:relative; overflow:hidden;
    }
    .land::before {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
      background-image:
        linear-gradient(rgba(255,255,255,0.04) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,0.04) 1px,transparent 1px);
      background-size:80px 80px;
    }
    .orb{position:fixed;border-radius:50%;filter:blur(80px);pointer-events:none;z-index:0;
      animation:floatOrb linear infinite;}
    @keyframes floatOrb{
      0%,100%{transform:translate(0,0) scale(1);}
      33%{transform:translate(30px,-40px) scale(1.08);}
      66%{transform:translate(-20px,30px) scale(0.94);}
    }
    .o1{width:520px;height:520px;background:rgba(107,26,255,.22);top:-180px;left:-180px;animation-duration:22s;}
    .o2{width:420px;height:420px;background:rgba(0,255,208,.14);bottom:-140px;right:-140px;animation-duration:28s;animation-delay:-10s;}
    .o3{width:320px;height:320px;background:rgba(255,0,107,.12);top:40%;left:52%;animation-duration:18s;animation-delay:-5s;}

    /* NAV */
    .nav{position:relative;z-index:10;display:flex;align-items:center;
      justify-content:space-between;max-width:1200px;margin:0 auto;padding:36px 48px 0;}
    .logo{font-family:'Montserrat',sans-serif;font-size:24px;font-weight:800;
      letter-spacing:0.1em;text-transform:uppercase;}
    .logo-n{color:#00FFD0;}.logo-d{color:#FF006B;}
    .nav-badge{font-family:'Inter',sans-serif;font-size:12px;font-weight:500;
      color:#00FFD0;text-transform:uppercase;letter-spacing:0.15em;
      border:1.5px solid #00FFD0;border-radius:24px;padding:7px 20px;
      background:transparent;transition:box-shadow 0.2s;}
    .nav-badge:hover{box-shadow:0 0 14px rgba(0,255,208,0.5);}

    /* HERO */
    .hero{position:relative;z-index:10;max-width:860px;margin:0 auto;
      padding:72px 48px 0;text-align:center;}
    .h-badge{display:inline-block;font-family:'Inter',sans-serif;font-size:13px;
      font-weight:500;color:#FF006B;text-transform:uppercase;letter-spacing:0.15em;
      border:1.5px solid #FF006B;border-radius:24px;padding:6px 20px;
      background:transparent;margin-bottom:40px;
      box-shadow:0 0 18px rgba(255,0,107,0.28);
      animation:bIn 0.7s ease 0.1s both;}
    @keyframes bIn{from{opacity:0;transform:translateY(-10px);}to{opacity:1;transform:translateY(0);}}
    .h-title{font-family:'Montserrat',sans-serif;font-weight:900;
      font-size:clamp(54px,8vw,96px);text-transform:uppercase;
      letter-spacing:-0.02em;line-height:0.9;margin-bottom:36px;
      animation:hIn 0.8s ease 0.2s both;}
    @keyframes hIn{from{opacity:0;transform:translateY(28px);}to{opacity:1;transform:translateY(0);}}
    .h-n{display:block;background:linear-gradient(90deg,#00FFD0,#FF006B);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .h-d{display:block;background:linear-gradient(90deg,#00FFD0,#00FFB0);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .h-r{display:block;color:#fff;}
    .h-body{font-family:'Inter',sans-serif;font-size:18px;color:#E0E0E0;
      line-height:1.75;max-width:600px;margin:0 auto;
      /* leave 88px for the button to float over */
      padding-bottom:104px;
      animation:bdy 0.7s ease 0.5s both;}
    @keyframes bdy{from{opacity:0;}to{opacity:1;}}
    .hl1{color:#00FFD0;font-weight:700;}
    .hl2{color:#00FFB0;font-weight:700;}

    /* STATS */
    .stats{display:flex;max-width:920px;margin:32px auto 0;
      background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
      border-radius:20px;overflow:hidden;position:relative;z-index:10;}
    .stat{flex:1;padding:26px 12px;text-align:center;
      border-right:1px solid rgba(255,255,255,0.07);transition:background 0.2s;}
    .stat:last-child{border-right:none;}
    .stat:hover{background:rgba(107,26,255,0.12);}
    .sv{font-family:'Montserrat',sans-serif;font-size:32px;font-weight:800;
      background:linear-gradient(90deg,#00FFD0,#6B1AFF);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;
      line-height:1;margin-bottom:6px;}
    .sl{font-family:'Inter',sans-serif;font-size:10px;font-weight:600;
      color:rgba(255,255,255,0.38);letter-spacing:0.12em;text-transform:uppercase;}

    /* SECTION LABEL + TITLE */
    .s-tag{font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
      color:#00FFD0;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;}
    .s-title{font-family:'Montserrat',sans-serif;font-size:36px;font-weight:800;
      color:#fff;text-transform:uppercase;letter-spacing:-0.02em;margin-bottom:32px;}
    .s-title em{font-style:italic;
      background:linear-gradient(90deg,#00FFD0,#FF006B);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;}

    /* CAPS GRID */
    .caps{position:relative;z-index:10;max-width:1200px;margin:88px auto 0;padding:0 48px;}
    .cgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}
    .ccard{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
      border-radius:14px;padding:20px;
      transition:transform 0.2s,border-color 0.2s,box-shadow 0.2s;}
    .ccard:hover{transform:translateY(-4px);border-color:rgba(0,255,208,0.28);
      box-shadow:0 8px 28px rgba(0,255,208,0.07);}
    .c-num{font-size:10px;font-weight:700;color:rgba(255,255,255,0.22);
      letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;}
    .c-ttl{font-size:14px;font-weight:600;color:#fff;margin-bottom:6px;}
    .c-bdy{font-size:12px;color:rgba(255,255,255,0.45);line-height:1.7;}
    .c-tag{display:inline-block;margin-top:10px;font-size:10px;font-weight:600;
      padding:3px 10px;border-radius:var(--r-full);border:1px solid;}

    /* PIPELINE — full-width horizontal scroll row */
    .pipe-wrap{position:relative;z-index:10;max-width:1200px;margin:80px auto 0;padding:0 48px;}
    .pipe-row{
      display:flex;align-items:center;justify-content:space-between;
      background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
      border-radius:18px;padding:32px 40px;width:100%;
    }
    .p-step{display:flex;flex-direction:column;align-items:center;gap:5px;
      flex:1;padding:8px 4px;border-radius:10px;transition:all 0.2s;cursor:default;}
    .p-step:hover{background:rgba(107,26,255,0.2);transform:translateY(-3px);}
    .p-lbl{font-family:'Montserrat',sans-serif;font-size:12px;font-weight:800;
      color:rgba(255,255,255,0.72);letter-spacing:0.05em;text-transform:uppercase;}
    .p-sub{font-family:'Inter',sans-serif;font-size:10px;color:rgba(255,255,255,0.3);}
    .p-arr{color:rgba(255,255,255,0.15);font-size:16px;flex-shrink:0;
      animation:aP 2.5s ease-in-out infinite;}
    .p-arr:nth-child(4n){animation-delay:0.5s;}
    .p-arr:nth-child(4n+2){animation-delay:1s;}
    .p-arr:nth-child(4n+3){animation-delay:1.5s;}
    @keyframes aP{0%,100%{color:rgba(255,255,255,0.12);}50%{color:#00FFD0;}}

    /* STACK */
    .stk{position:relative;z-index:10;max-width:1200px;margin:80px auto 0;padding:0 48px;}
    .tags{display:flex;flex-wrap:wrap;gap:10px;}
    .tag{padding:7px 16px;font-family:'Inter',sans-serif;font-size:11px;font-weight:600;
      border-radius:var(--r-full);border:1px solid;letter-spacing:0.04em;transition:transform 0.2s;}
    .tag:hover{transform:translateY(-2px);}
    .tc{color:#00FFD0;border-color:rgba(0,255,208,0.32);background:rgba(0,255,208,0.06);}
    .tv{color:#A78BFA;border-color:rgba(167,139,250,0.32);background:rgba(167,139,250,0.06);}
    .tm{color:#FF006B;border-color:rgba(255,0,107,0.32);background:rgba(255,0,107,0.06);}
    .ta{color:#FFD600;border-color:rgba(255,214,0,0.32);background:rgba(255,214,0,0.06);}

    /* FOOTER */
    .foot{position:relative;z-index:10;max-width:1200px;margin:72px auto 0;
      padding:22px 48px 64px;border-top:1px solid rgba(255,255,255,0.07);
      display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
    .foot span{font-family:'Inter',sans-serif;font-size:12px;color:rgba(255,255,255,0.25);}
    </style>

    <div class="land">
      <div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>

      <nav class="nav">
        <div class="logo"><span class="logo-n">NEURAL</span><span class="logo-d">DOC</span></div>
        <div class="nav-badge">Production RAG v1.0</div>
      </nav>

      <section class="hero">
        <div class="h-badge">&#x25CF;&nbsp; Zero Hallucination Tolerance</div>
        <h1 class="h-title">
          <span class="h-n">NEURAL</span>
          <span class="h-d">DOC</span>
          <span class="h-r">RAG</span>
        </h1>
        <p class="h-body">
          A <span class="hl1">production-grade</span> RAG system that answers
          questions from your documents with <span class="hl2">inline citations</span>,
          hybrid retrieval, and a hard refusal trigger &mdash; no guessing, ever.
        </p>
      </section>
    </div>""")

    # ── Button floated into hero ──────────────────────────────────────────────
    _l, _m, _r = st.columns([2, 2, 2])
    with _m:
        if st.button("Launch App →", key="go_chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

    # ── Rest of landing (stats, caps, pipe, stack, footer) ───────────────────
    st.html("""
    <div style="background:
        radial-gradient(ellipse 70% 60% at 0% 0%,   rgba(107,26,255,0.28),transparent 60%),
        radial-gradient(ellipse 55% 55% at 100% 100%,rgba(0,255,208,0.16),transparent 55%),
        radial-gradient(ellipse 45% 45% at 55% 45%,  rgba(255,0,107,0.12),transparent 50%),
        #0A0A1A;
      padding-top:24px;padding-bottom:88px;position:relative;">

    <div style="position:fixed;inset:0;pointer-events:none;z-index:0;
      background-image:linear-gradient(rgba(255,255,255,0.04) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,0.04) 1px,transparent 1px);
      background-size:80px 80px;"></div>

    <!-- STATS -->
    <div class="stats">
      <div class="stat"><div class="sv">0%</div><div class="sl">Hallucination Rate</div></div>
      <div class="stat"><div class="sv">3x</div><div class="sl">Retrieval Methods</div></div>
      <div class="stat"><div class="sv">100%</div><div class="sl">Local &amp; Private</div></div>
      <div class="stat"><div class="sv">inf</div><div class="sl">Documents</div></div>
    </div>

    <!-- CAPABILITIES -->
    <div class="caps">
      <div class="s-tag">// Capabilities</div>
      <div class="s-title">SIX <em>PILLARS</em></div>
      <div class="cgrid">
        <div class="ccard"><div class="c-num">01 — Ingestion</div><div class="c-ttl">Smart PDF Parsing</div><div class="c-bdy">Multi-column layouts, embedded tables, complex structures. Headers and footers stripped automatically.</div><span class="c-tag tc">pdfplumber</span></div>
        <div class="ccard"><div class="c-num">02 — Chunking</div><div class="c-ttl">Semantic Chunking</div><div class="c-bdy">Header-aware 500–800 token chunks. Source, page, and section breadcrumb on every chunk.</div><span class="c-tag tv">tiktoken</span></div>
        <div class="ccard"><div class="c-num">03 — Retrieval</div><div class="c-ttl">Hybrid Search</div><div class="c-bdy">BM25 keyword fused with dense vector search via Reciprocal Rank Fusion.</div><span class="c-tag tc">RRF Fusion</span></div>
        <div class="ccard"><div class="c-num">04 — Reranking</div><div class="c-ttl">Cross-Encoder Precision</div><div class="c-bdy">Top 20 candidates re-scored. Only the highest-confidence 5 reach the generation layer.</div><span class="c-tag ta">ms-marco</span></div>
        <div class="ccard"><div class="c-num">05 — Generation</div><div class="c-ttl">Attributed Answers</div><div class="c-bdy">Every claim carries an inline citation [Source, p.X]. Full References section appended.</div><span class="c-tag tv">LangGraph</span></div>
        <div class="ccard"><div class="c-num">06 — Safety</div><div class="c-ttl">Hard Refusal Gate</div><div class="c-bdy">Context below confidence threshold triggers a fixed refusal. No speculation, no hallucination.</div><span class="c-tag tm">Threshold Gate</span></div>
      </div>
    </div>

    <!-- PIPELINE — full width, all 8 steps visible -->
    <div class="pipe-wrap">
      <div class="s-tag">// Architecture</div>
      <div class="s-title">THE <em>PIPELINE</em></div>
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
      <div class="s-tag">// Stack</div>
      <div class="s-title">BUILT <em>WITH</em></div>
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

    <div class="foot">
      <span>NeuralDoc — Production RAG System</span>
      <span>Ollama · ChromaDB · LangGraph · FastAPI</span>
    </div>
    </div>""")


# ═══════════════════════════════════════════════════════════════
# CHAT PAGE — dark neon, same aesthetic as landing
# ═══════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    [data-testid="stAppViewContainer"] {
      background:
        radial-gradient(ellipse 65% 50% at 0% 0%,   rgba(107,26,255,0.28),transparent 60%),
        radial-gradient(ellipse 50% 60% at 100% 100%,rgba(0,255,208,0.14),transparent 55%),
        radial-gradient(ellipse 40% 40% at 60% 40%, rgba(255,0,107,0.10),transparent 50%),
        #0A0A1A !important;
    }
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container {
      padding:0!important; background:transparent!important; max-width:100%!important; }

    /* Grid overlay */
    [data-testid="stAppViewContainer"]::before {
      content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
      background-image:
        linear-gradient(rgba(255,255,255,0.035) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,0.035) 1px,transparent 1px);
      background-size:80px 80px;
    }

    /* Text inputs */
    .stTextInput input {
      background: rgba(255,255,255,0.06)!important;
      border: 1px solid rgba(255,255,255,0.12)!important;
      border-radius: 12px!important;
      color: #E0E0E0!important;
      font-family:'Inter',sans-serif!important;
      font-size:15px!important; padding:14px 18px!important;
      transition:border-color 0.18s,box-shadow 0.18s!important;
    }
    .stTextInput input:focus {
      border-color:#00FFD0!important;
      box-shadow:0 0 0 2px rgba(0,255,208,0.15)!important; outline:none!important;
    }
    .stTextInput input::placeholder { color:rgba(255,255,255,0.3)!important; }
    .stTextInput label,.stFileUploader label { display:none!important; }

    /* Buttons */
    .stButton>button {
      background: linear-gradient(90deg,#6B1AFF,#FF006B)!important;
      color:#fff!important; border:none!important; border-radius:12px!important;
      font-family:'Inter',sans-serif!important; font-weight:600!important;
      font-size:14px!important; padding:12px 0!important;
      box-shadow:0 2px 12px rgba(107,26,255,0.3)!important;
      transition:all 0.15s!important;
    }
    .stButton>button:hover {
      box-shadow:0 4px 20px rgba(255,0,107,0.4)!important;
      transform:translateY(-1px)!important;
    }
    .stButton>button:active { transform:scale(0.97)!important; }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
      background:rgba(255,255,255,0.04)!important;
      border:1.5px dashed rgba(0,255,208,0.3)!important;
      border-radius:14px!important; transition:all 0.2s!important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
      border-color:#00FFD0!important; background:rgba(0,255,208,0.04)!important;
    }
    [data-testid="stFileUploaderDropzone"] * { color:rgba(255,255,255,0.6)!important; }
    hr { border-color:rgba(255,255,255,0.08)!important; }
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
        bs="color:#00FFD0;background:rgba(0,255,208,0.1);border:1px solid rgba(0,255,208,0.3);"
        bd="#00FFD0"; bt=f"Ready &middot; {chunks} chunks"
    elif api_ok:
        bs="color:#FFD600;background:rgba(255,214,0,0.1);border:1px solid rgba(255,214,0,0.3);"
        bd="#FFD600"; bt="API online &mdash; No documents indexed"
    else:
        bs="color:#FF006B;background:rgba(255,0,107,0.1);border:1px solid rgba(255,0,107,0.3);"
        bd="#FF006B"; bt="API offline"

    # ── Topbar ────────────────────────────────────────────────────────────────
    st.html(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
      height:60px;padding:0 40px;
      background:rgba(10,10,26,0.85);backdrop-filter:blur(12px);
      border-bottom:1px solid rgba(255,255,255,0.08);
      position:sticky;top:0;z-index:100;">
      <div style="display:flex;align-items:center;gap:9px;">
        <div style="width:10px;height:10px;border-radius:50%;
          background:linear-gradient(135deg,#00FFD0,#6B1AFF);"></div>
        <span style="font-family:'Montserrat',sans-serif;font-size:18px;
          font-weight:800;letter-spacing:0.08em;text-transform:uppercase;">
          <span style="color:#00FFD0;">NEURAL</span><span style="color:#FF006B;">DOC</span>
        </span>
      </div>
      <div style="display:inline-flex;align-items:center;gap:6px;
        font-family:'Inter',sans-serif;font-size:12px;font-weight:500;
        padding:5px 14px;border-radius:var(--r-full);{bs}">
        <div style="width:5px;height:5px;border-radius:50%;
          background:{bd};flex-shrink:0;"></div>
        {bt}
      </div>
    </div>""")

    # ── Action buttons ────────────────────────────────────────────────────────
    st.html('<div style="padding:20px 40px 0;position:relative;z-index:10;">')
    b1, b2, _ = st.columns([1, 1, 8])
    with b1:
        if st.button("← Home", key="back_home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
    with b2:
        if st.button("Clear Chat", key="clr_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    st.html('</div><div style="height:20px;"></div>')

    # ── Two-panel layout ──────────────────────────────────────────────────────
    st.html('<div style="padding:0 40px 40px;position:relative;z-index:10;">')
    col_chat, col_up = st.columns([2, 1], gap="large")

    # ── RIGHT: Knowledge Base (dark card, cyan accent) ────────────────────────
    with col_up:
        st.html("""
        <div style="background:rgba(255,255,255,0.04);
          border:1px solid rgba(255,255,255,0.09);
          border-radius:18px;padding:28px 28px 22px;
          box-shadow:0 4px 24px rgba(0,255,208,0.05);">""")

        uh1, uh2 = st.columns([3, 1])
        with uh1:
            st.html("""<div>
              <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
                color:rgba(255,255,255,0.35);letter-spacing:0.12em;
                text-transform:uppercase;margin-bottom:8px;">Knowledge Base</div>
              <div style="font-family:'Montserrat',sans-serif;font-size:22px;
                font-weight:800;text-transform:uppercase;letter-spacing:0.02em;
                margin-bottom:16px;">
                <span style="color:#fff;">UPLOAD </span>
                <em style="font-style:italic;background:linear-gradient(90deg,#00FFD0,#00FFB0);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;">DOCS</em>
              </div>
            </div>""")
        with uh2:
            st.html('<div style="height:26px;"></div>')
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
        <div style="background:rgba(0,255,208,0.04);
          border:1.5px dashed rgba(0,255,208,0.25);
          border-radius:12px;padding:18px 16px;
          margin-bottom:12px;text-align:center;
          transition:border-color 0.2s,background 0.2s;"
          onmouseover="this.style.borderColor='#00FFD0';this.style.background='rgba(0,255,208,0.07)'"
          onmouseout="this.style.borderColor='rgba(0,255,208,0.25)';this.style.background='rgba(0,255,208,0.04)'">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none"
            stroke="#00FFD0" stroke-width="1.5" stroke-linecap="round"
            stroke-linejoin="round" style="margin:0 auto 8px;display:block;opacity:0.8;">
            <polyline points="16 16 12 12 8 16"></polyline>
            <line x1="12" y1="12" x2="12" y2="21"></line>
            <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"></path>
          </svg>
          <div style="font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
            color:#E0E0E0;margin-bottom:4px;">Drop your PDF below</div>
          <div style="font-family:'Inter',sans-serif;font-size:11px;
            color:rgba(255,255,255,0.3);">
            Parsed &#8594; Chunked &#8594; Embedded &#8594; Indexed</div>
        </div>""")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")

        if uploaded:
            st.html(f"""
            <div style="background:rgba(0,255,208,0.07);
              border:1px solid rgba(0,255,208,0.25);border-radius:10px;
              padding:10px 13px;margin-bottom:10px;">
              <div style="font-size:13px;font-weight:600;color:#E0E0E0;">{uploaded.name}</div>
              <div style="font-size:11px;color:#00FFD0;margin-top:2px;">{uploaded.size//1024} KB</div>
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
            st.html("""<div style="font-size:10px;font-weight:700;
              color:rgba(255,255,255,0.3);letter-spacing:0.1em;
              text-transform:uppercase;margin:12px 0 7px;">Indexed files</div>""")
            for f in files:
                fname=f.replace("\\","/").split("/")[-1]
                st.html(f"""
                <div style="background:rgba(255,255,255,0.04);
                  border:1px solid rgba(255,255,255,0.08);border-radius:10px;
                  padding:8px 12px;margin-bottom:5px;display:flex;align-items:center;">
                  <span style="font-size:13px;font-weight:500;color:#E0E0E0;flex:1;">{fname}</span>
                  <span style="font-size:10px;font-weight:700;padding:2px 9px;
                    border-radius:var(--r-full);
                    color:#00FFD0;background:rgba(0,255,208,0.1);
                    border:1px solid rgba(0,255,208,0.3);">indexed</span>
                </div>""")

        st.html("""
        <div style="margin-top:16px;background:rgba(255,255,255,0.03);
          border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px 16px;">
          <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,0.28);
            letter-spacing:0.12em;text-transform:uppercase;margin-bottom:9px;">Tips</div>
          <div style="font-family:'Inter',sans-serif;font-size:13px;
            color:rgba(255,255,255,0.45);line-height:1.9;">
            Click <b style="color:#00FFD0;">Clear</b> before switching documents.<br>
            Ask precise questions for best citation accuracy.<br>
            Every answer includes inline source references.<br>
            Unanswerable queries return a refusal, not a guess.
          </div>
        </div>""")

        st.html('</div>')

    # ── LEFT: Document QA (dark card) ─────────────────────────────────────────
    with col_chat:
        st.html("""
        <div style="background:rgba(255,255,255,0.04);
          border:1px solid rgba(255,255,255,0.09);
          border-radius:18px;padding:28px 28px 22px;
          box-shadow:0 4px 24px rgba(107,26,255,0.08);">""")

        st.html(f"""
        <div style="display:flex;align-items:flex-start;
          justify-content:space-between;margin-bottom:20px;">
          <div>
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
              color:rgba(255,255,255,0.3);letter-spacing:0.12em;
              text-transform:uppercase;margin-bottom:8px;">Document QA</div>
            <div style="font-family:'Montserrat',sans-serif;font-size:28px;
              font-weight:800;text-transform:uppercase;letter-spacing:0.01em;line-height:1.1;">
              <span style="color:#fff;">ASK YOUR </span>
              <em style="font-style:italic;background:linear-gradient(90deg,#6B1AFF,#FF006B);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">DOCS</em>
            </div>
          </div>
          <div style="display:flex;gap:7px;align-items:center;padding-top:18px;flex-shrink:0;">
            <span style="font-family:'Inter',sans-serif;font-size:12px;font-weight:600;
              color:#A78BFA;background:rgba(167,139,250,0.12);
              border:1px solid rgba(167,139,250,0.3);
              padding:4px 12px;border-radius:var(--r-full);">{chunks} chunks</span>
            <span style="font-family:'Inter',sans-serif;font-size:12px;font-weight:700;
              padding:4px 12px;border-radius:var(--r-full);border:1px solid;
              {'color:#00FFD0;background:rgba(0,255,208,0.1);border-color:rgba(0,255,208,0.3);' if ready else 'color:#FF006B;background:rgba(255,0,107,0.1);border-color:rgba(255,0,107,0.3);'}">
              {'Ready' if ready else 'Not ready'}</span>
          </div>
        </div>""")

        if st.session_state.messages:
            html=""
            for m in st.session_state.messages:
                if m["role"]=="user":
                    html+=f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
                      <div style="max-width:72%;padding:12px 16px;
                        background:linear-gradient(135deg,rgba(107,26,255,0.5),rgba(255,0,107,0.4));
                        color:#fff;border-radius:14px 3px 14px 14px;
                        font-family:'Inter',sans-serif;font-size:14px;line-height:1.65;
                        border:1px solid rgba(255,255,255,0.12);">
                        {m['content']}</div></div>"""
                else:
                    refs=""
                    if m.get("references"):
                        refs='<div style="margin-top:9px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs+=f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:var(--r-full);color:#00FFD0;background:rgba(0,255,208,0.08);border:1px solid rgba(0,255,208,0.25);">{ref}</span>'
                        refs+="</div>"
                    rfsd=""
                    if m.get("refused"):
                        rfsd='<div style="margin-top:7px;font-size:12px;font-weight:600;color:#FF006B;background:rgba(255,0,107,0.1);border:1px solid rgba(255,0,107,0.3);padding:5px 11px;border-radius:10px;display:inline-block;">Insufficient evidence — refusal triggered</div>'
                    lat=""
                    if m.get("latency_ms"):
                        lat=f'<div style="margin-top:4px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,0.25);">{m["latency_ms"]} ms</div>'
                    html+=f"""
                    <div style="display:flex;margin-bottom:14px;gap:9px;align-items:flex-start;">
                      <div style="width:26px;height:26px;border-radius:7px;flex-shrink:0;
                        margin-top:2px;
                        background:linear-gradient(135deg,rgba(107,26,255,0.4),rgba(0,255,208,0.2));
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Montserrat',sans-serif;font-size:11px;font-weight:800;
                        color:#00FFD0;border:1px solid rgba(0,255,208,0.2);">N</div>
                      <div style="max-width:86%;padding:13px 16px;
                        background:rgba(255,255,255,0.05);
                        border:1px solid rgba(255,255,255,0.09);
                        border-radius:3px 14px 14px 14px;
                        font-family:'Inter',sans-serif;font-size:14px;
                        color:#E0E0E0;line-height:1.75;">
                        {m['content']}{refs}{rfsd}{lat}</div></div>"""
            st.html(f"""
            <div style="max-height:46vh;overflow-y:auto;margin-bottom:14px;
              padding:2px;scrollbar-width:thin;
              scrollbar-color:rgba(107,26,255,0.4) transparent;">{html}</div>""")
        else:
            st.html("""
            <div style="text-align:center;padding:48px 20px 36px;
              background:rgba(255,255,255,0.03);
              border:1px solid rgba(255,255,255,0.07);
              border-radius:14px;margin-bottom:14px;">
              <div style="font-family:'Montserrat',sans-serif;font-size:20px;font-weight:800;
                text-transform:uppercase;letter-spacing:0.02em;
                background:linear-gradient(90deg,#6B1AFF,#FF006B,#00FFD0);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:10px;">Ask Anything</div>
              <div style="font-family:'Inter',sans-serif;font-size:13px;
                color:rgba(255,255,255,0.35);max-width:300px;margin:0 auto 20px;line-height:1.7;">
                Upload a PDF on the right, then ask questions here. Every answer is cited.</div>
              <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
                <span style="font-family:'Inter',sans-serif;font-size:12px;font-weight:500;
                  color:#A78BFA;background:rgba(167,139,250,0.1);
                  border:1px solid rgba(167,139,250,0.25);
                  padding:6px 14px;border-radius:var(--r-full);cursor:default;
                  transition:background 0.15s;"
                  onmouseover="this.style.background='rgba(167,139,250,0.18)'"
                  onmouseout="this.style.background='rgba(167,139,250,0.1)'">
                  What is the main finding?</span>
                <span style="font-family:'Inter',sans-serif;font-size:12px;font-weight:500;
                  color:#A78BFA;background:rgba(167,139,250,0.1);
                  border:1px solid rgba(167,139,250,0.25);
                  padding:6px 14px;border-radius:var(--r-full);cursor:default;
                  transition:background 0.15s;"
                  onmouseover="this.style.background='rgba(167,139,250,0.18)'"
                  onmouseout="this.style.background='rgba(167,139,250,0.1)'">
                  Summarise section 3</span>
                <span style="font-family:'Inter',sans-serif;font-size:12px;font-weight:500;
                  color:#A78BFA;background:rgba(167,139,250,0.1);
                  border:1px solid rgba(167,139,250,0.25);
                  padding:6px 14px;border-radius:var(--r-full);cursor:default;
                  transition:background 0.15s;"
                  onmouseover="this.style.background='rgba(167,139,250,0.18)'"
                  onmouseout="this.style.background='rgba(167,139,250,0.1)'">
                  What are the key risks?</span>
              </div>
            </div>""")

        qc, bc = st.columns([6, 1])
        with qc:
            query=st.text_input("Question",
                                placeholder="Ask anything about your documents...",
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