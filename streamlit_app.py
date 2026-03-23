"""NeuralDoc RAG — Pastel Minimal."""
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

# ── Global reset ──────────────────────────────────────────────────────────────
st.html("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:          #F7F6FF;
  --surface:     #FFFFFF;
  --surface2:    #F0EFF9;
  --border:      rgba(139,92,246,0.1);
  --border-soft: rgba(0,0,0,0.07);

  --violet-50:   #F5F3FF;
  --violet-100:  #EDE9FE;
  --violet-200:  #DDD6FE;
  --violet-400:  #A78BFA;
  --violet-500:  #8B5CF6;
  --violet-600:  #7C3AED;

  --mint-bg:   #ECFDF5; --mint-text:  #059669;
  --rose-bg:   #FFF1F2; --rose-text:  #E11D48;
  --amber-bg:  #FFFBEB; --amber-text: #D97706;
  --sky-bg:    #F0F9FF; --sky-text:   #0284C7;

  --text-1: #18181B;
  --text-2: #52525B;
  --text-3: #A1A1AA;

  --r-sm:   6px;  --r-md:  10px; --r-lg: 16px;
  --r-xl:   24px; --r-full: 9999px;

  --sh-sm: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04);
  --sh-md: 0 4px 12px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.04);
  --sh-lg: 0 8px 32px rgba(0,0,0,0.09), 0 4px 8px rgba(0,0,0,0.04);
  --sh-v:  0 4px 14px rgba(139,92,246,0.25);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: var(--bg)!important; font-family: 'Plus Jakarta Sans', sans-serif!important; }

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
# LANDING PAGE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    # Button style — must come before columns
    st.html("""<style>
    [data-testid="stAppViewContainer"] { background: var(--bg)!important; }
    [data-testid="stButton"]>button {
      background: var(--violet-500)!important; color: white!important;
      border: none!important; border-radius: var(--r-full)!important;
      font-family: 'Plus Jakarta Sans', sans-serif!important;
      font-size: 15px!important; font-weight: 600!important;
      padding: 14px 48px!important; letter-spacing: 0.2px!important;
      box-shadow: var(--sh-v)!important; transition: all 0.2s!important;
      min-width: 180px!important;
    }
    [data-testid="stButton"]>button:hover {
      background: var(--violet-600)!important;
      transform: translateY(-2px)!important;
      box-shadow: 0 8px 20px rgba(139,92,246,0.35)!important;
    }
    [data-testid="stButton"]>button:active { transform: scale(0.97)!important; }
    </style>""")

    # Nav
    st.html("""<style>
    .ln { position:relative; z-index:10; display:flex; align-items:center;
      justify-content:space-between; max-width:1100px; margin:0 auto;
      padding:28px 40px 0; animation:fD 0.5s ease both; }
    @keyframes fD{from{opacity:0;transform:translateY(-12px);}to{opacity:1;transform:translateY(0);}}
    .ln-logo { font-family:'Instrument Serif',serif; font-size:20px; color:var(--text-1);
      display:flex; align-items:center; gap:7px; }
    .ln-dot { width:7px; height:7px; border-radius:50%; background:var(--violet-500); }
    .ln-badge { font-size:11px; font-weight:500; color:var(--violet-600);
      background:var(--violet-100); border:1px solid var(--violet-200);
      padding:5px 14px; border-radius:var(--r-full); }
    .land-bg { position:fixed; inset:0; pointer-events:none; z-index:0;
      background:
        radial-gradient(ellipse 60% 50% at 20% 10%, rgba(167,139,250,0.12), transparent 60%),
        radial-gradient(ellipse 40% 40% at 80% 80%, rgba(139,92,246,0.07), transparent 55%); }
    </style>
    <div class="land-bg"></div>
    <nav class="ln">
      <div class="ln-logo"><div class="ln-dot"></div>NeuralDoc</div>
      <div class="ln-badge">Production RAG v1.0</div>
    </nav>""")

    # Hero — button rendered by Streamlit INSIDE the hero container
    st.html("""<style>
    .hero-wrap { position:relative; z-index:10; max-width:720px;
      margin:0 auto; padding:72px 40px 0; text-align:center; animation:fU 0.6s ease 0.1s both; }
    @keyframes fU{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
    .h-pill { display:inline-flex; align-items:center; gap:6px;
      font-size:12px; font-weight:500; color:var(--violet-600);
      background:var(--violet-50); border:1px solid var(--violet-200);
      padding:5px 14px; border-radius:var(--r-full); margin-bottom:24px; }
    .h-dot { width:5px; height:5px; border-radius:50%; background:var(--violet-500);
      animation:dp 2s ease-in-out infinite; }
    @keyframes dp{0%,100%{opacity:1;}50%{opacity:0.3;}}
    .h-title { font-family:'Instrument Serif',serif; font-size:clamp(40px,6vw,64px);
      font-weight:400; color:var(--text-1); line-height:1.08;
      letter-spacing:-1px; margin-bottom:18px; }
    .h-title em { font-style:italic; color:var(--violet-500); }
    .h-sub { font-size:16px; color:var(--text-2); line-height:1.75;
      max-width:480px; margin:0 auto 0; font-weight:400; }
    .h-sub strong { color:var(--text-1); font-weight:600; }
    </style>
    <div class="hero-wrap">
      <div class="h-pill"><span class="h-dot"></span>Zero hallucination tolerance</div>
      <h1 class="h-title">Ask anything.<br><em>Know everything.</em></h1>
      <p class="h-sub">A <strong>production-grade</strong> RAG system that answers
        questions from your documents with <strong>inline citations</strong>,
        hybrid retrieval, and a hard refusal trigger — no guessing, ever.</p>
    </div>""")

    # Button sits directly under hero — inside the page flow, no gap
    st.html('<div style="position:relative;z-index:10;height:36px;"></div>')
    _l, _m, _r = st.columns([3, 2, 3])
    with _m:
        if st.button("Open App", key="go_chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

    # Stats
    st.html("""<style>
    .stats { display:flex; max-width:580px; margin:52px auto 0;
      border:1px solid var(--border-soft); border-radius:var(--r-xl);
      overflow:hidden; background:var(--surface); box-shadow:var(--sh-sm);
      position:relative; z-index:10; }
    .stat { flex:1; padding:22px 12px; text-align:center;
      border-right:1px solid var(--border-soft); transition:background 0.2s; }
    .stat:last-child { border-right:none; }
    .stat:hover { background:var(--violet-50); }
    .s-val { font-family:'Instrument Serif',serif; font-size:30px;
      color:var(--violet-500); line-height:1; margin-bottom:4px; }
    .s-lbl { font-size:10px; font-weight:600; color:var(--text-3);
      letter-spacing:0.8px; text-transform:uppercase; }
    </style>
    <div class="stats">
      <div class="stat"><div class="s-val">0%</div><div class="s-lbl">Hallucination</div></div>
      <div class="stat"><div class="s-val">3x</div><div class="s-lbl">Retrieval methods</div></div>
      <div class="stat"><div class="s-val">100%</div><div class="s-lbl">Local & private</div></div>
      <div class="stat"><div class="s-val">inf</div><div class="s-lbl">Documents</div></div>
    </div>""")

    # Features
    st.html("""<style>
    .sec { position:relative; z-index:10;
      max-width:1100px; margin:80px auto 0; padding:0 40px; }
    .sec-tag { font-size:10px; font-weight:600; color:var(--violet-500);
      letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px; }
    .sec-title { font-family:'Instrument Serif',serif; font-size:34px;
      color:var(--text-1); margin-bottom:36px; font-weight:400; }
    .sec-title em { font-style:italic; color:var(--violet-500); }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); gap:14px; }
    .card { background:var(--surface); border:1px solid var(--border-soft);
      border-radius:var(--r-xl); padding:24px; box-shadow:var(--sh-sm);
      transition:transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s; }
    .card:hover { transform:translateY(-4px); box-shadow:var(--sh-lg); border-color:var(--violet-200); }
    .c-num { font-size:10px; font-weight:600; color:var(--text-3);
      letter-spacing:1.5px; text-transform:uppercase; margin-bottom:10px; }
    .c-title { font-size:15px; font-weight:600; color:var(--text-1); margin-bottom:7px; }
    .c-body { font-size:13px; color:var(--text-2); line-height:1.75; }
    .c-tag { display:inline-block; margin-top:12px; font-size:10px; font-weight:500;
      padding:3px 10px; border-radius:var(--r-full); border:1px solid; }
    </style>
    <div class="sec">
      <div class="sec-tag">Capabilities</div>
      <div class="sec-title">Six <em>pillars</em> of precision</div>
      <div class="grid">
        <div class="card">
          <div class="c-num">01 — Ingestion</div>
          <div class="c-title">Smart PDF Parsing</div>
          <div class="c-body">Multi-column layouts, embedded tables, complex structures. Headers and footers stripped automatically.</div>
          <span class="c-tag" style="color:var(--mint-text);background:var(--mint-bg);border-color:#A7F3D0;">pdfplumber</span>
        </div>
        <div class="card">
          <div class="c-num">02 — Chunking</div>
          <div class="c-title">Semantic Chunking</div>
          <div class="c-body">Header-aware chunks of 500–800 tokens. Every chunk carries source, page, and section breadcrumb.</div>
          <span class="c-tag" style="color:var(--violet-600);background:var(--violet-50);border-color:var(--violet-200);">tiktoken</span>
        </div>
        <div class="card">
          <div class="c-num">03 — Retrieval</div>
          <div class="c-title">Hybrid Search</div>
          <div class="c-body">BM25 keyword fused with dense vector search via Reciprocal Rank Fusion. Catches what either alone misses.</div>
          <span class="c-tag" style="color:var(--sky-text);background:var(--sky-bg);border-color:#BAE6FD;">RRF Fusion</span>
        </div>
        <div class="card">
          <div class="c-num">04 — Reranking</div>
          <div class="c-title">Cross-Encoder Precision</div>
          <div class="c-body">Top 20 candidates re-scored. Only the highest-confidence 5 reach the generation layer.</div>
          <span class="c-tag" style="color:var(--amber-text);background:var(--amber-bg);border-color:#FDE68A;">ms-marco</span>
        </div>
        <div class="card">
          <div class="c-num">05 — Generation</div>
          <div class="c-title">Attributed Answers</div>
          <div class="c-body">Every claim carries an inline citation [Source, p.X]. Full References section on every response.</div>
          <span class="c-tag" style="color:#9333EA;background:#FAF5FF;border-color:#E9D5FF;">LangGraph</span>
        </div>
        <div class="card">
          <div class="c-num">06 — Safety</div>
          <div class="c-title">Hard Refusal Gate</div>
          <div class="c-body">Context below confidence threshold triggers a fixed refusal. No speculation, no hallucination, by design.</div>
          <span class="c-tag" style="color:var(--rose-text);background:var(--rose-bg);border-color:#FECDD3;">Threshold Gate</span>
        </div>
      </div>
    </div>""")

    # Pipeline
    st.html("""<style>
    .pipe { position:relative; z-index:10;
      max-width:1100px; margin:80px auto 0; padding:0 40px; }
    .pipe-row { display:flex; align-items:center; flex-wrap:wrap;
      background:var(--surface); border:1px solid var(--border-soft);
      border-radius:var(--r-xl); padding:28px 36px; box-shadow:var(--sh-sm); gap:2px; }
    .p-step { display:flex; flex-direction:column; align-items:center; gap:5px;
      padding:10px 14px; border-radius:var(--r-lg); min-width:72px;
      transition:all 0.2s; cursor:default; }
    .p-step:hover { background:var(--violet-50); transform:translateY(-2px); }
    .p-label { font-size:12px; font-weight:600; color:var(--text-2); }
    .p-sub   { font-size:10px; color:var(--text-3); }
    .p-arr   { color:var(--violet-200); font-size:14px; padding:0 2px; flex-shrink:0;
      animation:ap 2.5s ease-in-out infinite; }
    .p-arr:nth-child(even) { animation-delay:0.5s; }
    @keyframes ap{0%,100%{color:var(--violet-200);}50%{color:var(--violet-500);}}
    </style>
    <div class="pipe">
      <div class="sec-tag">Architecture</div>
      <div class="sec-title">The <em>pipeline</em></div>
      <div class="pipe-row">
        <div class="p-step"><div class="p-label">Parse</div><div class="p-sub">pdfplumber</div></div>
        <div class="p-arr">&#8594;</div>
        <div class="p-step"><div class="p-label">Chunk</div><div class="p-sub">tiktoken</div></div>
        <div class="p-arr">&#8594;</div>
        <div class="p-step"><div class="p-label">Embed</div><div class="p-sub">miniLM</div></div>
        <div class="p-arr">&#8594;</div>
        <div class="p-step"><div class="p-label">BM25</div><div class="p-sub">keyword</div></div>
        <div class="p-arr">&#8594;</div>
        <div class="p-step"><div class="p-label">Fuse</div><div class="p-sub">RRF</div></div>
        <div class="p-arr">&#8594;</div>
        <div class="p-step"><div class="p-label">Rerank</div><div class="p-sub">cross-enc</div></div>
        <div class="p-arr">&#8594;</div>
        <div class="p-step"><div class="p-label">Generate</div><div class="p-sub">llama3.1</div></div>
        <div class="p-arr">&#8594;</div>
        <div class="p-step"><div class="p-label">Cite</div><div class="p-sub">attributed</div></div>
      </div>
    </div>""")

    # Stack + footer
    st.html("""<style>
    .stk { position:relative; z-index:10;
      max-width:1100px; margin:80px auto 0; padding:0 40px; }
    .tags { display:flex; flex-wrap:wrap; gap:9px; }
    .tag { padding:6px 14px; font-size:11px; font-weight:500;
      border-radius:var(--r-full); border:1px solid; transition:transform 0.2s; cursor:default; }
    .tag:hover { transform:translateY(-2px); }
    .t-v { color:var(--violet-600); border-color:var(--violet-200); background:var(--violet-50); }
    .t-g { color:var(--mint-text); border-color:#A7F3D0; background:var(--mint-bg); }
    .t-r { color:var(--rose-text); border-color:#FECDD3; background:var(--rose-bg); }
    .t-a { color:var(--amber-text); border-color:#FDE68A; background:var(--amber-bg); }
    .footer { position:relative; z-index:10; max-width:1100px;
      margin:72px auto 0; padding:22px 40px 60px;
      border-top:1px solid var(--border-soft);
      display:flex; justify-content:space-between;
      align-items:center; flex-wrap:wrap; gap:10px; }
    .footer span { font-size:12px; color:var(--text-3); }
    </style>
    <div class="stk">
      <div class="sec-tag">Stack</div>
      <div class="sec-title">Built <em>with</em></div>
      <div class="tags">
        <span class="tag t-g">pdfplumber</span>
        <span class="tag t-g">ChromaDB</span>
        <span class="tag t-g">sentence-transformers</span>
        <span class="tag t-v">LangGraph</span>
        <span class="tag t-v">langchain-ollama</span>
        <span class="tag t-v">llama3.1:8b</span>
        <span class="tag t-r">BM25 + RRF</span>
        <span class="tag t-r">cross-encoder reranker</span>
        <span class="tag t-a">FastAPI</span>
        <span class="tag t-a">Streamlit</span>
        <span class="tag t-a">Python 3.14</span>
      </div>
    </div>
    <div class="footer">
      <span>NeuralDoc — Production RAG System</span>
      <span>Ollama · ChromaDB · LangGraph · FastAPI</span>
    </div>""")


# ═════════════════════════════════════════════════════════════════════════════
# CHAT PAGE
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    [data-testid="stAppViewContainer"] { background: var(--bg)!important; }
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container {
      padding: 0!important; background: transparent!important; max-width:100%!important; }

    .stTextInput input {
      background: var(--surface)!important; border: 1.5px solid var(--border-soft)!important;
      border-radius: var(--r-md)!important; color: var(--text-1)!important;
      font-family: 'Plus Jakarta Sans', sans-serif!important; font-size: 14px!important;
      padding: 11px 16px!important; box-shadow: var(--sh-sm)!important;
      transition: border-color 0.15s, box-shadow 0.15s!important;
    }
    .stTextInput input:focus {
      border-color: var(--violet-400)!important;
      box-shadow: 0 0 0 3px var(--violet-100)!important; outline: none!important;
    }
    .stTextInput input::placeholder { color: var(--text-3)!important; }
    .stTextInput label, .stFileUploader label { display: none!important; }

    .stButton>button {
      background: var(--violet-500)!important; color: white!important;
      border: none!important; border-radius: var(--r-md)!important;
      font-family: 'Plus Jakarta Sans', sans-serif!important;
      font-weight: 600!important; font-size: 13px!important; padding: 10px 0!important;
      box-shadow: 0 2px 8px rgba(139,92,246,0.2)!important; transition: all 0.15s!important;
    }
    .stButton>button:hover {
      background: var(--violet-600)!important; transform: translateY(-1px)!important;
      box-shadow: var(--sh-v)!important;
    }
    .stButton>button:active { transform: scale(0.97)!important; }

    [data-testid="stFileUploaderDropzone"] {
      background: var(--surface)!important; border: 1.5px dashed var(--violet-200)!important;
      border-radius: var(--r-lg)!important; transition: all 0.2s!important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
      border-color: var(--violet-400)!important; background: var(--violet-50)!important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: var(--text-2)!important; }
    .stSelectbox [data-baseweb="select"]>div {
      background: var(--surface)!important; border: 1.5px solid var(--border-soft)!important;
      border-radius: var(--r-md)!important; color: var(--text-1)!important;
    }
    hr { border-color: var(--border-soft)!important; }
    </style>""")

    def get_health():
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3).json()
            r["_reachable"] = True
            return r
        except Exception:
            return {"pipeline_ready":False,"total_chunks":0,"indexed_files":[],"_reachable":False}

    h = get_health()
    api_ok   = h.get("_reachable", False)
    ready    = h.get("pipeline_ready", False)
    chunks   = h.get("total_chunks", 0)
    files    = h.get("indexed_files", [])

    # Status pill values
    if ready:
        s_cls  = "s-ready";  s_dot = "var(--mint-text)"
        s_text = f"Ready · {chunks} chunks indexed"
    elif api_ok:
        s_cls  = "s-warn";   s_dot = "var(--amber-text)"
        s_text = "API online · No documents indexed"
    else:
        s_cls  = "s-off";    s_dot = "var(--rose-text)"
        s_text = "API offline"

    # Top bar
    st.html(f"""<style>
    .topbar {{ display:flex; align-items:center; justify-content:space-between;
      padding:14px 32px; background:rgba(255,255,255,0.88);
      backdrop-filter:blur(12px); border-bottom:1px solid var(--border-soft);
      position:sticky; top:0; z-index:100; }}
    .tb-logo {{ font-family:'Instrument Serif',serif; font-size:18px; color:var(--text-1);
      display:flex; align-items:center; gap:7px; }}
    .tb-dot {{ width:7px; height:7px; border-radius:50%; background:var(--violet-500); }}
    .s-pill {{ display:inline-flex; align-items:center; gap:6px;
      font-size:12px; font-weight:500; padding:5px 13px;
      border-radius:var(--r-full); border:1px solid; }}
    .s-ready {{ color:var(--mint-text); background:var(--mint-bg); border-color:#A7F3D0; }}
    .s-warn  {{ color:var(--amber-text);background:var(--amber-bg);border-color:#FDE68A; }}
    .s-off   {{ color:var(--rose-text); background:var(--rose-bg); border-color:#FECDD3; }}
    .s-dot-el{{ width:5px; height:5px; border-radius:50%; }}
    </style>
    <div class="topbar">
      <div class="tb-logo"><div class="tb-dot"></div>NeuralDoc</div>
      <div class="s-pill {s_cls}">
        <div class="s-dot-el" style="background:{s_dot};"></div>
        {s_text}
      </div>
    </div>""")

    # Nav buttons
    st.html('<div style="padding:16px 32px 0;">')
    nb1, nb2, _ = st.columns([1, 1, 8])
    with nb1:
        if st.button("Home", key="back_home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
    with nb2:
        if st.button("Clear Chat", key="clr_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    st.html('</div>')

    st.html('<div style="height:20px;"></div>')

    # Main two-column layout
    col_chat, col_upload = st.columns([3, 2], gap="large")

    # ── RIGHT: Upload ─────────────────────────────────────────────────────────
    with col_upload:
        st.html('<div style="padding:0 24px 0 0;">')

        uh1, uh2 = st.columns([3, 1])
        with uh1:
            st.html("""
            <div style="margin-bottom:14px;">
              <div style="font-size:10px;font-weight:600;color:var(--violet-500);
                letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">
                Knowledge Base
              </div>
              <div style="font-family:'Instrument Serif',serif;font-size:24px;
                color:var(--text-1);line-height:1.1;">
                Upload <em style="font-style:italic;color:var(--violet-500);">documents</em>
              </div>
            </div>""")
        with uh2:
            st.html('<div style="height:30px;"></div>')
            if st.button("Clear", key="clear_idx", use_container_width=True,
                         help="Wipe all indexed documents before uploading a new PDF."):
                try:
                    resp = requests.delete(f"{API_BASE}/index", timeout=15)
                    if resp.status_code == 200:
                        st.success("Index cleared.")
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("API offline.")

        # Drop hint
        st.html("""
        <div style="background:var(--violet-50);border:1.5px dashed var(--violet-200);
          border-radius:var(--r-lg);padding:18px 20px;margin-bottom:12px;text-align:center;">
          <div style="font-size:13px;font-weight:500;color:var(--text-2);margin-bottom:3px;">
            Drop your PDF below
          </div>
          <div style="font-size:11px;color:var(--text-3);">
            Parsed — Chunked — Embedded — Indexed
          </div>
        </div>""")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")

        if uploaded:
            st.html(f"""
            <div style="background:var(--mint-bg);border:1px solid #A7F3D0;
              border-radius:var(--r-md);padding:10px 14px;margin-bottom:10px;">
              <div style="font-size:13px;font-weight:500;color:var(--text-1);">{uploaded.name}</div>
              <div style="font-size:11px;color:var(--mint-text);margin-top:2px;">{uploaded.size//1024} KB</div>
            </div>""")
            if st.button("Index Document", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing PDF..."):
                    try:
                        resp = requests.post(f"{API_BASE}/ingest",
                            files={"file":(uploaded.name, uploaded, "application/pdf")}, timeout=120)
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
            st.html("""<div style="font-size:10px;font-weight:600;color:var(--text-3);
              letter-spacing:1px;text-transform:uppercase;margin:14px 0 8px;">
              Indexed files</div>""")
            for f in files:
                fname = f.replace("\\", "/").split("/")[-1]
                st.html(f"""
                <div style="background:var(--surface);border:1px solid var(--border-soft);
                  border-radius:var(--r-md);padding:9px 13px;margin-bottom:5px;
                  display:flex;align-items:center;box-shadow:var(--sh-sm);">
                  <span style="font-size:13px;font-weight:500;color:var(--text-1);flex:1;">{fname}</span>
                  <span style="font-size:10px;font-weight:600;padding:2px 8px;
                    border-radius:var(--r-full);color:var(--mint-text);
                    background:var(--mint-bg);border:1px solid #A7F3D0;">indexed</span>
                </div>""")

        # Tips card
        st.html("""
        <div style="margin-top:18px;background:var(--surface);
          border:1px solid var(--border-soft);border-radius:var(--r-lg);
          padding:16px 18px;box-shadow:var(--sh-sm);">
          <div style="font-size:10px;font-weight:600;color:var(--text-3);
            letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">Tips</div>
          <div style="font-size:13px;color:var(--text-2);line-height:1.9;">
            Click <b style="color:var(--text-1);font-weight:600;">Clear</b> before switching documents.<br>
            Ask precise questions for best citation accuracy.<br>
            Every answer includes inline source references.<br>
            Unanswerable queries return a refusal, not a guess.
          </div>
        </div>""")

        st.html('</div>')

    # ── LEFT: Chat ────────────────────────────────────────────────────────────
    with col_chat:
        st.html('<div style="padding:0 0 0 24px;">')

        st.html(f"""
        <div style="display:flex;align-items:flex-end;
          justify-content:space-between;margin-bottom:18px;">
          <div>
            <div style="font-size:10px;font-weight:600;color:var(--violet-500);
              letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;">
              Document QA
            </div>
            <div style="font-family:'Instrument Serif',serif;font-size:24px;
              color:var(--text-1);line-height:1.1;">
              Ask your <em style="font-style:italic;color:var(--violet-500);">documents</em>
            </div>
          </div>
          <div style="display:flex;gap:7px;align-items:center;padding-bottom:3px;">
            <div style="font-size:11px;font-weight:500;color:var(--text-3);
              background:var(--surface2);padding:4px 10px;
              border-radius:var(--r-full);border:1px solid var(--border-soft);">
              {chunks} chunks
            </div>
            <div style="font-size:11px;font-weight:500;padding:4px 10px;
              border-radius:var(--r-full);border:1px solid;
              {'color:var(--mint-text);background:var(--mint-bg);border-color:#A7F3D0;' if ready else 'color:var(--rose-text);background:var(--rose-bg);border-color:#FECDD3;'}">
              {'Ready' if ready else 'Not ready'}
            </div>
          </div>
        </div>""")

        # Messages
        if st.session_state.messages:
            html = ""
            for m in st.session_state.messages:
                if m["role"] == "user":
                    html += f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
                      <div style="max-width:75%;padding:11px 15px;
                        background:var(--violet-500);color:white;
                        border-radius:14px 3px 14px 14px;
                        font-size:14px;line-height:1.65;
                        font-family:'Plus Jakarta Sans',sans-serif;
                        box-shadow:0 2px 8px rgba(139,92,246,0.18);">
                        {m['content']}
                      </div>
                    </div>"""
                else:
                    refs = ""
                    if m.get("references"):
                        refs = '<div style="margin-top:9px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs += f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:var(--r-full);color:var(--sky-text);background:var(--sky-bg);border:1px solid #BAE6FD;">{ref}</span>'
                        refs += "</div>"
                    rfsd = ""
                    if m.get("refused"):
                        rfsd = '<div style="margin-top:8px;font-size:12px;font-weight:500;color:var(--rose-text);background:var(--rose-bg);border:1px solid #FECDD3;padding:5px 12px;border-radius:var(--r-md);display:inline-block;">Insufficient evidence — refusal triggered</div>'
                    lat = ""
                    if m.get("latency_ms"):
                        lat = f'<div style="margin-top:5px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:var(--text-3);">{m["latency_ms"]} ms</div>'
                    html += f"""
                    <div style="display:flex;margin-bottom:14px;gap:9px;align-items:flex-start;">
                      <div style="width:26px;height:26px;border-radius:var(--r-sm);flex-shrink:0;
                        margin-top:2px;background:var(--violet-100);
                        display:flex;align-items:center;justify-content:center;
                        font-size:11px;font-weight:600;color:var(--violet-600);
                        border:1px solid var(--violet-200);">N</div>
                      <div style="max-width:86%;padding:11px 15px;
                        background:var(--surface);border:1px solid var(--border-soft);
                        border-radius:3px 14px 14px 14px;
                        font-size:14px;color:var(--text-1);line-height:1.75;
                        font-family:'Plus Jakarta Sans',sans-serif;
                        box-shadow:var(--sh-sm);">
                        {m['content']}{refs}{rfsd}{lat}
                      </div>
                    </div>"""
            st.html(f"""
            <div style="max-height:50vh;overflow-y:auto;padding:2px 2px 10px;
              scrollbar-width:thin;scrollbar-color:var(--violet-200) transparent;">
              {html}
            </div>""")
        else:
            st.html("""
            <div style="text-align:center;padding:52px 24px;
              background:var(--surface);border:1px solid var(--border-soft);
              border-radius:var(--r-xl);margin-bottom:14px;box-shadow:var(--sh-sm);">
              <div style="width:36px;height:36px;border-radius:var(--r-md);
                background:var(--violet-100);border:1px solid var(--violet-200);
                display:flex;align-items:center;justify-content:center;
                margin:0 auto 14px;font-size:15px;font-weight:700;color:var(--violet-600);">N</div>
              <div style="font-family:'Instrument Serif',serif;font-size:20px;
                color:var(--text-1);margin-bottom:7px;">Ask anything</div>
              <div style="font-size:13px;color:var(--text-3);max-width:280px;
                margin:0 auto;line-height:1.7;">
                Upload a PDF on the right, then ask questions here. Every answer is cited.
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:7px;
                justify-content:center;margin-top:18px;">
                <span style="font-size:12px;color:var(--violet-600);background:var(--violet-50);
                  border:1px solid var(--violet-200);padding:5px 12px;
                  border-radius:var(--r-full);">What is the main finding?</span>
                <span style="font-size:12px;color:var(--violet-600);background:var(--violet-50);
                  border:1px solid var(--violet-200);padding:5px 12px;
                  border-radius:var(--r-full);">Summarise section 3</span>
                <span style="font-size:12px;color:var(--violet-600);background:var(--violet-50);
                  border:1px solid var(--violet-200);padding:5px 12px;
                  border-radius:var(--r-full);">What are the key risks?</span>
              </div>
            </div>""")

        st.html('<div style="height:8px;"></div>')

        qc, bc = st.columns([6, 1])
        with qc:
            query = st.text_input(
                "Your question",
                placeholder="Ask anything about your documents...",
                label_visibility="hidden",
                key="q_in"
            )
        with bc:
            ask = st.button("Send", use_container_width=True)

        if ask and query:
            if not ready:
                st.warning("Upload and index a PDF first.")
            else:
                with st.spinner("Thinking..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/query", json={"query": query}, timeout=120)
                        if resp.status_code == 200:
                            d = resp.json()
                            st.session_state.messages.extend([
                                {"role": "user", "content": query},
                                {"role": "assistant", "content": d["answer"],
                                 "references": d["references"],
                                 "refused": d["refused"],
                                 "latency_ms": d["latency_ms"]}])
                            st.rerun()
                        else:
                            st.error(f"API error: {resp.json().get('detail', resp.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach API. Run: uv run uvicorn api:app --reload --port 8000")

        st.html('</div>')