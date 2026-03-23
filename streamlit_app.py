"""NeuralDoc RAG — Single file app."""
import requests
import streamlit as st

st.set_page_config(
    page_title="NeuralDoc RAG",
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
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="collapsedControl"],#MainMenu,footer {
  display:none!important; height:0!important; }
html,body { margin:0!important; padding:0!important; background:#030010!important; }
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

    st.html("<style>section[data-testid='stSidebar']{display:none!important;} [data-testid='stAppViewContainer']{background:#030010!important;}</style>")

    st.html("""<style>
    .bg{position:fixed;inset:0;z-index:0;pointer-events:none;
      background:radial-gradient(ellipse 70% 55% at 12% 12%,rgba(110,0,240,.35),transparent 55%),
                radial-gradient(ellipse 55% 65% at 88% 88%,rgba(0,210,150,.22),transparent 55%),
                radial-gradient(ellipse 40% 40% at 50% 40%,rgba(210,0,90,.12),transparent 60%),#030010;
      animation:bgS 16s ease-in-out infinite alternate;}
    @keyframes bgS{0%{filter:hue-rotate(0deg);}100%{filter:hue-rotate(20deg) brightness(1.06);}}
    .gl{position:fixed;inset:0;z-index:0;pointer-events:none;
      background-image:linear-gradient(rgba(100,0,255,.07) 1px,transparent 1px),
                       linear-gradient(90deg,rgba(100,0,255,.07) 1px,transparent 1px);
      background-size:58px 58px;animation:gP 6s ease-in-out infinite;}
    @keyframes gP{0%,100%{opacity:.35;}50%{opacity:.8;}}
    .orb{position:fixed;border-radius:50%;filter:blur(100px);pointer-events:none;z-index:0;animation:oD linear infinite;}
    .o1{width:500px;height:500px;background:rgba(110,0,240,.28);top:-200px;left:-180px;animation-duration:23s;}
    .o2{width:420px;height:420px;background:rgba(0,200,140,.2);bottom:-150px;right:-150px;animation-duration:29s;animation-delay:-11s;}
    .o3{width:320px;height:320px;background:rgba(210,0,80,.16);top:38%;left:54%;animation-duration:20s;animation-delay:-6s;}
    @keyframes oD{0%{transform:translate(0,0) scale(1);}33%{transform:translate(42px,-56px) scale(1.08);}
      66%{transform:translate(-32px,42px) scale(.93);}100%{transform:translate(0,0) scale(1);}}
    </style>
    <div class="bg"></div><div class="gl"></div>
    <div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>""")

    st.html("""<style>
    .nav{position:relative;z-index:10;display:flex;align-items:center;justify-content:space-between;
      max-width:1200px;margin:0 auto;padding:36px 48px 0;animation:fD .7s ease both;}
    @keyframes fD{from{opacity:0;transform:translateY(-18px);}to{opacity:1;transform:translateY(0);}}
    .logo{font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:6px;
      background:linear-gradient(135deg,#00DFA0,#6B00F0,#E0005A);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .npill{font-family:'JetBrains Mono',monospace;font-size:12px;color:#00DFA0;letter-spacing:2px;
      border:1px solid rgba(0,223,160,.35);padding:6px 16px;border-radius:20px;background:rgba(0,223,160,.06);}
    </style>
    <nav class="nav"><div class="logo">NeuralDoc</div><div class="npill">PRODUCTION RAG v1.0</div></nav>""")

    st.html("""<style>
    .hero{position:relative;z-index:10;max-width:1000px;margin:0 auto;padding:68px 48px 0;
      text-align:center;animation:fU .9s ease .2s both;}
    @keyframes fU{from{opacity:0;transform:translateY(36px);}to{opacity:1;transform:translateY(0);}}
    .eyebrow{display:inline-flex;align-items:center;gap:10px;font-family:'JetBrains Mono',monospace;
      font-size:12px;color:#E0005A;letter-spacing:3px;border:1px solid rgba(224,0,90,.3);
      background:rgba(224,0,90,.07);padding:8px 20px;border-radius:30px;margin-bottom:32px;
      animation:eG 3.5s ease-in-out infinite;}
    @keyframes eG{0%,100%{box-shadow:none;}50%{box-shadow:0 0 22px rgba(224,0,90,.35);}}
    .edot{width:7px;height:7px;border-radius:50%;background:#E0005A;animation:dB 1.6s ease-in-out infinite;flex-shrink:0;}
    @keyframes dB{0%,100%{opacity:1;}50%{opacity:.1;}}
    .htitle{font-family:'Bebas Neue',sans-serif;font-size:clamp(80px,11vw,132px);
      line-height:.88;letter-spacing:4px;color:#fff;margin:0;}
    .t1{background:linear-gradient(90deg,#6B00F0,#E0005A);-webkit-background-clip:text;-webkit-text-fill-color:transparent;
      display:inline-block;animation:t1S 5s ease-in-out infinite alternate;}
    @keyframes t1S{from{filter:hue-rotate(0deg);}to{filter:hue-rotate(28deg);}}
    .t2{background:linear-gradient(90deg,#00DFA0,#6B00F0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;}
    .hdesc{font-family:'Syne',sans-serif;font-size:19px;color:rgba(255,255,255,.55);max-width:600px;margin:28px auto 0;line-height:1.85;}
    .hdesc strong{color:#00DFA0;font-weight:700;}
    </style>
    <div class="hero">
      <div class="eyebrow"><span class="edot"></span>ZERO HALLUCINATION TOLERANCE</div>
      <h1 class="htitle"><span class="t1">NEURAL</span><br><span class="t2">DOC</span> RAG</h1>
      <p class="hdesc">A <strong>production-grade</strong> RAG system that answers questions from
        your documents with <strong>inline citations</strong>, hybrid retrieval,
        and a hard refusal trigger &mdash; no guessing, ever.</p>
    </div>""")

    st.html("""<style>
    [data-testid="stButton"]>button{display:block!important;width:100%!important;padding:18px 0!important;
      font-family:'Syne',sans-serif!important;font-size:18px!important;font-weight:700!important;
      border-radius:50px!important;letter-spacing:.5px!important;
      background:linear-gradient(135deg,#6B00F0,#E0005A)!important;
      color:#fff!important;border:none!important;box-shadow:0 0 44px rgba(107,0,240,.55)!important;
      animation:bGL 3s ease-in-out infinite!important;transition:transform .3s!important;}
    @keyframes bGL{0%,100%{box-shadow:0 0 44px rgba(107,0,240,.55);}50%{box-shadow:0 0 70px rgba(107,0,240,.82);}}
    [data-testid="stButton"]>button:hover{transform:translateY(-4px) scale(1.03)!important;}
    </style>""")
    st.html('<div style="height:44px;position:relative;z-index:10;"></div>')
    _l, _mid, _r = st.columns([3, 2, 3])
    with _mid:
        if st.button("Launch App →", key="go_chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()
    st.html('<div style="height:20px;"></div>')

    st.html("""<style>
    .stats{position:relative;z-index:10;display:flex;max-width:900px;margin:52px auto 0;
      border:1px solid rgba(255,255,255,.08);border-radius:20px;overflow:hidden;background:rgba(255,255,255,.025);}
    .stat{flex:1;padding:30px 16px;text-align:center;border-right:1px solid rgba(255,255,255,.07);transition:background .3s;}
    .stat:last-child{border-right:none;}.stat:hover{background:rgba(107,0,240,.1);}
    .sv{font-family:'Bebas Neue',sans-serif;font-size:48px;letter-spacing:3px;
      background:linear-gradient(135deg,#00DFA0,#6B00F0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .sl{font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,.38);letter-spacing:3px;text-transform:uppercase;margin-top:5px;}
    </style>
    <div class="stats">
      <div class="stat"><div class="sv">0%</div><div class="sl">Hallucination Rate</div></div>
      <div class="stat"><div class="sv">3x</div><div class="sl">Retrieval Methods</div></div>
      <div class="stat"><div class="sv">100%</div><div class="sl">Local &amp; Private</div></div>
      <div class="stat"><div class="sv">inf</div><div class="sl">Documents Supported</div></div>
    </div>""")

    st.html("""<style>
    .section{position:relative;z-index:10;max-width:1200px;margin:88px auto 0;padding:0 48px;}
    .stag{font-family:'JetBrains Mono',monospace;font-size:12px;color:#6B00F0;letter-spacing:4px;text-transform:uppercase;margin-bottom:12px;}
    .sh{font-family:'Bebas Neue',sans-serif;font-size:56px;letter-spacing:2px;color:#fff;line-height:1;margin-bottom:44px;}
    .sh span{background:linear-gradient(90deg,#00DFA0,#6B00F0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px;}
    .card{padding:28px;background:rgba(255,255,255,.025);border:1px solid rgba(255,255,255,.08);border-radius:18px;transition:transform .4s,border-color .4s,box-shadow .4s;}
    .card:hover{transform:translateY(-8px);border-color:rgba(107,0,240,.4);box-shadow:0 16px 50px rgba(107,0,240,.16);}
    .cn{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2px;color:rgba(255,255,255,.25);margin-bottom:14px;}
    .ct{font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#fff;margin-bottom:10px;}
    .cb{font-family:'Syne',sans-serif;font-size:14px;color:rgba(255,255,255,.45);line-height:1.8;}
    .ctch{display:inline-block;margin-top:14px;font-family:'JetBrains Mono',monospace;font-size:11px;padding:4px 12px;border-radius:20px;letter-spacing:1px;}
    </style>
    <div class="section">
      <div class="stag">// Capabilities</div>
      <div class="sh">SIX <span>PILLARS</span></div>
      <div class="cards">
        <div class="card"><div class="cn">01 &mdash; INGESTION</div><div class="ct">Smart PDF Parsing</div><div class="cb">Handles multi-column layouts, embedded tables, and complex structures. Headers and footers stripped automatically.</div><span class="ctch" style="color:#00DFA0;background:rgba(0,223,160,.07);border:1px solid rgba(0,223,160,.2)">pdfplumber</span></div>
        <div class="card"><div class="cn">02 &mdash; CHUNKING</div><div class="ct">Semantic Chunking</div><div class="cb">Header-aware chunks of 500&ndash;800 tokens. Every chunk carries source, page, and section breadcrumb as metadata.</div><span class="ctch" style="color:#6B00F0;background:rgba(107,0,240,.07);border:1px solid rgba(107,0,240,.2)">tiktoken</span></div>
        <div class="card"><div class="cn">03 &mdash; RETRIEVAL</div><div class="ct">Hybrid Search</div><div class="cb">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion. Catches what either method alone misses.</div><span class="ctch" style="color:#E0005A;background:rgba(224,0,90,.07);border:1px solid rgba(224,0,90,.2)">RRF Fusion</span></div>
        <div class="card"><div class="cn">04 &mdash; RERANKING</div><div class="ct">Cross-Encoder Precision</div><div class="cb">Top 20 candidates re-scored by a cross-encoder. Only the highest-confidence 5 reach the generation layer.</div><span class="ctch" style="color:#F0A800;background:rgba(240,168,0,.07);border:1px solid rgba(240,168,0,.2)">ms-marco</span></div>
        <div class="card"><div class="cn">05 &mdash; GENERATION</div><div class="ct">Attributed Answers</div><div class="cb">Every claim carries an inline citation [Source, p.X]. A full References section is appended to every response.</div><span class="ctch" style="color:#00AAFF;background:rgba(0,170,255,.07);border:1px solid rgba(0,170,255,.2)">LangGraph</span></div>
        <div class="card"><div class="cn">06 &mdash; SAFETY</div><div class="ct">Hard Refusal Gate</div><div class="cb">Context below the confidence threshold triggers a fixed refusal string. No speculation, no hallucination, by design.</div><span class="ctch" style="color:#FF6030;background:rgba(255,96,48,.07);border:1px solid rgba(255,96,48,.2)">Threshold Gate</span></div>
      </div>
    </div>""")

    st.html("""<style>
    .pipe-wrap{position:relative;z-index:10;max-width:1200px;margin:88px auto 0;padding:0 48px;}
    .pipe{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;padding:44px;
      background:rgba(255,255,255,.018);border:1px solid rgba(255,255,255,.07);border-radius:20px;}
    .step{display:flex;flex-direction:column;align-items:center;gap:10px;padding:18px 22px;
      background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.09);border-radius:14px;
      min-width:92px;transition:all .3s;}
    .step:hover{background:rgba(107,0,240,.2);border-color:rgba(107,0,240,.5);transform:translateY(-6px);}
    .si{font-family:'Bebas Neue',sans-serif;font-size:14px;letter-spacing:2px;color:rgba(255,255,255,.7);}
    .slb{font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,.4);letter-spacing:1px;}
    .arr{color:rgba(255,255,255,.18);font-size:18px;padding:0 5px;flex-shrink:0;animation:aP 2.4s ease-in-out infinite;}
    .arr:nth-child(even){animation-delay:.6s;}
    @keyframes aP{0%,100%{color:rgba(255,255,255,.14);}50%{color:rgba(0,223,160,.72);}}
    </style>
    <div class="pipe-wrap">
      <div class="stag">// Architecture</div>
      <div class="sh">THE <span>PIPELINE</span></div>
      <div class="pipe">
        <div class="step"><div class="si">PDF</div><div class="slb">Parse</div></div><div class="arr">&rarr;</div>
        <div class="step"><div class="si">SPLIT</div><div class="slb">Chunk</div></div><div class="arr">&rarr;</div>
        <div class="step"><div class="si">EMBED</div><div class="slb">Vector</div></div><div class="arr">&rarr;</div>
        <div class="step"><div class="si">BM25</div><div class="slb">Keyword</div></div><div class="arr">&rarr;</div>
        <div class="step"><div class="si">RRF</div><div class="slb">Fuse</div></div><div class="arr">&rarr;</div>
        <div class="step"><div class="si">RANK</div><div class="slb">Rerank</div></div><div class="arr">&rarr;</div>
        <div class="step"><div class="si">LLM</div><div class="slb">Generate</div></div><div class="arr">&rarr;</div>
        <div class="step"><div class="si">CITE</div><div class="slb">Attribute</div></div>
      </div>
    </div>""")

    st.html("""<style>
    .stack{position:relative;z-index:10;max-width:1200px;margin:88px auto 0;padding:0 48px;}
    .tags{display:flex;flex-wrap:wrap;gap:12px;}
    .tag{padding:9px 18px;font-family:'JetBrains Mono',monospace;font-size:12px;border-radius:30px;border:1px solid;letter-spacing:1px;transition:transform .3s;cursor:default;}
    .tag:hover{transform:translateY(-3px);}
    .tg{color:#00DFA0;border-color:rgba(0,223,160,.3);background:rgba(0,223,160,.06);}
    .tp{color:#6B00F0;border-color:rgba(107,0,240,.3);background:rgba(107,0,240,.06);}
    .tr{color:#E0005A;border-color:rgba(224,0,90,.3);background:rgba(224,0,90,.06);}
    .ty{color:#F0A800;border-color:rgba(240,168,0,.3);background:rgba(240,168,0,.06);}
    </style>
    <div class="stack">
      <div class="stag">// Stack</div>
      <div class="sh">BUILT <span>WITH</span></div>
      <div class="tags">
        <span class="tag tg">pdfplumber</span><span class="tag tg">ChromaDB</span><span class="tag tg">sentence-transformers</span>
        <span class="tag tp">LangGraph</span><span class="tag tp">langchain-ollama</span><span class="tag tp">llama3.1:8b</span>
        <span class="tag tr">BM25 + RRF</span><span class="tag tr">cross-encoder reranker</span>
        <span class="tag ty">FastAPI</span><span class="tag ty">Streamlit</span><span class="tag ty">Python 3.14</span>
      </div>
    </div>""")

    st.html("""<style>
    .foot{position:relative;z-index:10;max-width:1200px;margin:80px auto 0;padding:24px 48px 72px;
      border-top:1px solid rgba(255,255,255,.07);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;}
    .foot span{font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,255,255,.25);}
    </style>
    <div class="foot">
      <span>NeuralDoc &mdash; Production RAG System</span>
      <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
    </div>""")


# ═════════════════════════════════════════════════════════════════════════════
# CHAT PAGE — Horizontal: Chat left, Upload right
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    [data-testid="stAppViewContainer"]{background:#030010!important;}
    [data-testid="stAppViewContainer"]::before{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
      background:radial-gradient(ellipse 65% 50% at 10% 10%,rgba(110,0,240,.18),transparent 60%),
                radial-gradient(ellipse 50% 65% at 90% 90%,rgba(0,200,140,.12),transparent 60%);}
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container {
      padding:2rem 2.5rem 3rem!important; max-width:1400px!important; background:transparent!important;}
    section[data-testid="stSidebar"]{display:flex!important;}
    [data-testid="collapsedControl"]{display:flex!important;}
    [data-testid="stSidebar"]{background:rgba(5,0,18,.97)!important;border-right:1px solid rgba(107,0,240,.2)!important;}
    [data-testid="stSidebar"] *{font-family:'Syne',sans-serif!important;}
    [data-testid="stSidebar"] label{color:rgba(255,255,255,.6)!important;font-size:12px!important;}
    .stTextInput input{background:rgba(107,0,240,.07)!important;border:1px solid rgba(107,0,240,.3)!important;
      color:#fff!important;border-radius:8px!important;padding:12px 16px!important;
      font-size:14px!important;font-family:'Syne',sans-serif!important;}
    .stTextInput input:focus{border-color:rgba(107,0,240,.65)!important;box-shadow:0 0 18px rgba(107,0,240,.18)!important;}
    .stTextInput input::placeholder{color:rgba(255,255,255,.3)!important;}
    .stTextInput label,.stFileUploader label{display:none!important;}
    .stButton>button{background:linear-gradient(135deg,#6B00F0,#E0005A)!important;color:#fff!important;
      border:none!important;border-radius:8px!important;font-family:'Syne',sans-serif!important;
      font-weight:700!important;font-size:13px!important;letter-spacing:.5px!important;
      padding:12px 0!important;transition:transform .2s,box-shadow .2s!important;}
    .stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 28px rgba(107,0,240,.4)!important;}
    [data-testid="stFileUploaderDropzone"]{background:rgba(107,0,240,.04)!important;
      border:1px dashed rgba(107,0,240,.35)!important;border-radius:12px!important;}
    [data-testid="stFileUploaderDropzone"] *{color:rgba(255,255,255,.6)!important;}
    .stSelectbox [data-baseweb="select"]>div{background:rgba(255,255,255,.05)!important;
      border-color:rgba(255,255,255,.15)!important;color:#fff!important;border-radius:8px!important;}
    .stSlider label{color:rgba(255,255,255,.6)!important;font-size:12px!important;}
    hr{border-color:rgba(255,255,255,.07)!important;}
    </style>""")

    def get_health():
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3).json()
            r["_reachable"] = True
            return r
        except Exception:
            return {"pipeline_ready": False, "total_chunks": 0,
                    "indexed_files": [], "_reachable": False}

    def get_cfg():
        try: return requests.get(f"{API_BASE}/config", timeout=3).json()
        except: return {"provider":"ollama","ollama_model":"llama3.1:8b"}

    h_check = get_health()
    api_reachable = h_check.get("_reachable", False)

    # Show API offline banner ONLY when genuinely unreachable
    if not api_reachable:
        st.html("""<div style="background:rgba(224,0,90,.1);border:1px solid rgba(224,0,90,.3);
          border-radius:10px;padding:12px 18px;margin-bottom:16px;
          font-family:'JetBrains Mono',monospace;font-size:12px;color:#E0005A;letter-spacing:1px;">
          API OFFLINE &mdash; Run in a separate terminal:
          <span style="color:#fff;background:rgba(255,255,255,.08);padding:2px 8px;border-radius:4px;margin-left:8px;">
          uv run uvicorn api:app --reload --port 8000</span></div>""")

    # ── HORIZONTAL LAYOUT: Chat left, Upload right ────────────────────────────
    col_chat, col_upload = st.columns([3, 2], gap="large")

    # ── RIGHT: Upload ─────────────────────────────────────────────────────────
    with col_upload:
        # Header + Clear Index button
        uh1, uh2 = st.columns([3, 1])
        with uh1:
            st.html("""<div style="margin-bottom:12px;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#E0005A;
                   letter-spacing:4px;margin-bottom:6px;">// INDEX DOCUMENTS</div>
              <div style="font-family:'Bebas Neue',sans-serif;font-size:40px;letter-spacing:2px;
                   color:#fff;line-height:1;">UPLOAD
                <span style="background:linear-gradient(90deg,#E0005A,#F0A800);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;"> PDF</span>
              </div>
            </div>""")
        with uh2:
            st.html('<div style="height:40px"></div>')
            if st.button("Clear Index", key="clear_idx", use_container_width=True,
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

        st.html("""<style>@keyframes dP{0%,100%{border-color:rgba(107,0,240,.35);}
          50%{border-color:rgba(107,0,240,.7);box-shadow:0 0 24px rgba(107,0,240,.12);}}</style>
        <div style="padding:18px 20px;background:rgba(107,0,240,.04);border:1px dashed rgba(107,0,240,.38);
          border-radius:12px;margin-bottom:12px;text-align:center;animation:dP 4s ease-in-out infinite;">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:16px;letter-spacing:2px;
               color:rgba(255,255,255,.4);margin-bottom:4px;">DROP PDF BELOW</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,.25);">
            Parsed &rarr; Chunked &rarr; Embedded &rarr; Indexed</div>
        </div>""")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")

        if uploaded:
            st.html(f"""<div style="padding:10px 14px;background:rgba(0,223,160,.06);
              border:1px solid rgba(0,223,160,.22);border-radius:8px;margin-bottom:10px;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#00DFA0;">
                {uploaded.name} &mdash; {uploaded.size//1024} KB</div></div>""")
            if st.button("Index Now", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing PDF..."):
                    try:
                        resp = requests.post(f"{API_BASE}/ingest",
                            files={"file":(uploaded.name, uploaded, "application/pdf")}, timeout=120)
                        if resp.status_code==200:
                            d = resp.json()
                            st.success(f"Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                            st.rerun()
                        else:
                            st.error(f"Error: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("API offline. Start: uv run uvicorn api:app --reload --port 8000")
                    except Exception as e:
                        st.error(str(e))

        if h_check.get("indexed_files"):
            for f in h_check["indexed_files"]:
                fname = f.replace("\\","/").split("/")[-1]
                st.html(f"""<div style="padding:7px 12px;background:rgba(0,223,160,.07);
                  border:1px solid rgba(0,223,160,.2);border-radius:8px;margin-top:6px;
                  font-family:'JetBrains Mono',monospace;font-size:11px;color:#00DFA0;">
                  {fname}</div>""")

        st.html("""<div style="margin-top:20px;padding:18px 20px;background:rgba(255,255,255,.018);
          border:1px solid rgba(255,255,255,.06);border-radius:12px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
               color:rgba(255,255,255,.25);letter-spacing:3px;margin-bottom:12px;">NOTES</div>
          <div style="font-size:13px;color:rgba(255,255,255,.38);line-height:1.9;font-family:'Syne',sans-serif;">
            Click <b style="color:rgba(255,255,255,.6)">Clear Index</b> before uploading a new document.<br>
            Ask precise questions for best results.<br>
            Every answer includes inline source citations.<br>
            Unanswerable queries return a refusal, not a guess.
          </div></div>""")

    # ── LEFT: Chat ────────────────────────────────────────────────────────────
    with col_chat:
        st.html("""<div style="margin-bottom:20px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#6B00F0;
               letter-spacing:4px;margin-bottom:6px;">// DOCUMENT QA</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:48px;letter-spacing:2px;
               color:#fff;line-height:1;">ASK YOUR
            <span style="background:linear-gradient(90deg,#6B00F0,#E0005A);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;"> DOCS</span>
          </div>
        </div>""")

        tc = h_check.get("total_chunks", 0)
        r2 = h_check.get("pipeline_ready", False)
        c1, c2, c3 = st.columns(3)
        def chip(col, text, color, bg, border):
            col.html(f"""<div style="padding:10px 14px;background:{bg};border:1px solid {border};
              border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:11px;
              color:{color};letter-spacing:1px;text-align:center;">{text}</div>""")
        chip(c1, "READY" if r2 else "OFFLINE",
             "#00DFA0" if r2 else "#E0005A",
             "rgba(0,223,160,.06)" if r2 else "rgba(224,0,90,.06)",
             "rgba(0,223,160,.2)" if r2 else "rgba(224,0,90,.2)")
        chip(c2, f"{tc} CHUNKS", "#6B00F0", "rgba(107,0,240,.06)", "rgba(107,0,240,.2)")
        chip(c3, model[:16], "#00DFA0", "rgba(0,223,160,.06)", "rgba(0,223,160,.2)")

        st.html("<div style='height:16px'></div>")

        if st.session_state.messages:
            html = ""
            for m in st.session_state.messages:
                if m["role"] == "user":
                    html += f"""<div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
                      <div style="max-width:78%;padding:14px 18px;background:rgba(107,0,240,.2);
                        border:1px solid rgba(107,0,240,.35);border-radius:18px 4px 18px 18px;
                        font-size:15px;color:rgba(255,255,255,.9);line-height:1.7;font-family:'Syne',sans-serif;">
                        {m['content']}</div></div>"""
                else:
                    refs = ""
                    if m.get("references"):
                        refs = '<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs += f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:4px;color:#00DFA0;background:rgba(0,223,160,.08);border:1px solid rgba(0,223,160,.2);">ref: {ref}</span>'
                        refs += "</div>"
                    rfsd = '<div style="margin-top:8px;font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#E0005A;background:rgba(224,0,90,.08);border:1px solid rgba(224,0,90,.2);padding:5px 10px;border-radius:6px;display:inline-block;">REFUSAL — Insufficient evidence</div>' if m.get("refused") else ""
                    lat = f'<div style="margin-top:6px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,.2);">{m.get("latency_ms","")} ms</div>' if m.get("latency_ms") else ""
                    html += f"""<div style="display:flex;margin-bottom:14px;gap:12px;align-items:flex-start;">
                      <div style="width:32px;height:32px;border-radius:8px;flex-shrink:0;margin-top:2px;
                        background:linear-gradient(135deg,#6B00F0,#E0005A);display:flex;align-items:center;
                        justify-content:center;font-family:'Bebas Neue',sans-serif;font-size:11px;color:#fff;letter-spacing:1px;">AI</div>
                      <div style="max-width:85%;padding:14px 18px;background:rgba(255,255,255,.04);
                        border:1px solid rgba(255,255,255,.09);border-radius:4px 18px 18px 18px;
                        font-size:15px;color:rgba(255,255,255,.88);line-height:1.75;font-family:'Syne',sans-serif;">
                        {m['content']}{refs}{rfsd}{lat}</div></div>"""
            st.html(f"""<div style="max-height:52vh;overflow-y:auto;padding:4px 2px 12px;
              scrollbar-width:thin;scrollbar-color:rgba(107,0,240,.4) transparent;">{html}</div>""")
        else:
            st.html("""<div style="text-align:center;padding:60px 20px;color:rgba(255,255,255,.22);">
              <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:3px;
                margin-bottom:10px;background:linear-gradient(90deg,rgba(107,0,240,.5),rgba(0,223,160,.5));
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">AWAITING INPUT</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:1px;">
                Upload a PDF on the right, then ask questions here</div></div>""")

        st.html("<div style='height:12px'></div>")
        qc, bc = st.columns([5, 1])
        with qc:
            query = st.text_input(
                "Your question",
                placeholder="Type your question here...",
                label_visibility="hidden",
                key="q_in"
            )
        with bc:
            ask = st.button("Send", use_container_width=True)

        if ask and query:
            if not r2:
                st.warning("Upload and index a PDF first.")
            else:
                with st.spinner("Retrieving and generating answer..."):
                    try:
                        resp = requests.post(f"{API_BASE}/query", json={"query": query}, timeout=120)
                        if resp.status_code == 200:
                            d = resp.json()
                            st.session_state.messages.extend([
                                {"role": "user", "content": query},
                                {"role": "assistant", "content": d["answer"],
                                 "references": d["references"], "refused": d["refused"],
                                 "latency_ms": d["latency_ms"]}])
                            st.rerun()
                        else:
                            st.error(f"API error: {resp.json().get('detail', resp.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach API. Run: uv run uvicorn api:app --reload --port 8000")