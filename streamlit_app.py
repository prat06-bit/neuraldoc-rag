"""NeuralDoc RAG — Fixed button, no blank space, 3 resume features."""
import json
import requests
import streamlit as st
from datetime import datetime
from pathlib import Path

# ── Copy chat_history.py and analytics.py to project root if not present ─────
# (inline fallback so the app works standalone)
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from chat_history import save_conversation, load_all_conversations, \
                             load_conversation, delete_conversation, export_as_markdown
    from analytics import record_query, get_stats, reset_analytics
except ImportError:
    # Minimal inline fallbacks
    def save_conversation(msgs, title=None): return ""
    def load_all_conversations(): return []
    def load_conversation(cid): return []
    def delete_conversation(cid): pass
    def export_as_markdown(msgs, title="Chat"): return "\n".join(f"{m['role']}: {m['content']}" for m in msgs)
    def record_query(q, lat, ref, model=""): pass
    def get_stats(): return {"total_queries":0,"answered":0,"refused":0,"refusal_rate":0,"avg_latency_ms":0,"recent":[]}
    def reset_analytics(): pass

st.set_page_config(
    page_title="NeuralDoc",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("page","landing"),("messages",[]),("active_conv_id",None),("show_analytics",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

API_BASE = "http://localhost:8000"

# ── BUTTON FIX: detect ?launch=1 query param ─────────────────────────────────
# The landing page HTML form submits to ?launch=1 which triggers a Streamlit rerun
if st.query_params.get("launch") == "1":
    st.query_params.clear()
    st.session_state.page = "chat"
    st.rerun()

# ── Global chrome kill ────────────────────────────────────────────────────────
st.html("""<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root{
  --black:#0A0A1A;--cyan:#00FFD0;--magenta:#FF006B;
  --green:#00FFB0;--purple:#6B1AFF;--body:#E0E0E0;--r-full:9999px;
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{font-family:'Inter',sans-serif!important;}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],#MainMenu,footer{display:none!important;height:0!important;}
[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],.block-container{
  background:transparent!important;padding:0!important;
  margin:0!important;max-width:100%!important;border:none!important;}
[data-testid="stVerticalBlock"]{gap:0!important;}
[data-testid="stVerticalBlock"]>div{margin:0!important;padding:0!important;}
</style>""")


# ═════════════════════════════════════════════════════════════════════════════
# LANDING — everything in st.html(), button via form submit to ?launch=1
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.html("""
<style>
[data-testid="stAppViewContainer"]{background:#0A0A1A!important;}
</style>

<style>
/* Full page */
.land{
  background:
    radial-gradient(ellipse 70% 60% at 0% 0%,   rgba(107,26,255,0.38),transparent 60%),
    radial-gradient(ellipse 55% 55% at 100% 100%,rgba(0,255,208,0.22),transparent 55%),
    radial-gradient(ellipse 45% 45% at 55% 45%,  rgba(255,0,107,0.18),transparent 50%),
    #0A0A1A;
  min-height:100vh;position:relative;overflow-x:hidden;
}
/* Grid */
.land::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(255,255,255,0.04) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,0.04) 1px,transparent 1px);
  background-size:80px 80px;}
/* Orbs */
.orb{position:fixed;border-radius:50%;filter:blur(80px);pointer-events:none;z-index:0;animation:oD linear infinite;}
.o1{width:520px;height:520px;background:rgba(107,26,255,.22);top:-180px;left:-180px;animation-duration:22s;}
.o2{width:420px;height:420px;background:rgba(0,255,208,.14);bottom:-140px;right:-140px;animation-duration:28s;animation-delay:-10s;}
.o3{width:320px;height:320px;background:rgba(255,0,107,.12);top:40%;left:52%;animation-duration:18s;animation-delay:-5s;}
@keyframes oD{0%,100%{transform:translate(0,0) scale(1);}33%{transform:translate(30px,-40px) scale(1.08);}66%{transform:translate(-20px,30px) scale(0.94);}}
.wrap{position:relative;z-index:1;}
/* Nav */
nav{display:flex;align-items:center;justify-content:space-between;
  max-width:1200px;margin:0 auto;padding:36px 48px 0;}
.logo{font-family:'Montserrat',sans-serif;font-size:24px;font-weight:800;
  letter-spacing:0.1em;text-transform:uppercase;}
.logo-n{color:#00FFD0;}.logo-d{color:#FF006B;}
.nav-badge{font-size:12px;font-weight:500;color:#00FFD0;text-transform:uppercase;
  letter-spacing:0.15em;border:1.5px solid #00FFD0;border-radius:24px;
  padding:7px 20px;background:transparent;}
/* Hero */
.hero{max-width:860px;margin:0 auto;padding:72px 48px 64px;text-align:center;}
.h-badge{display:inline-block;font-size:13px;font-weight:500;color:#FF006B;
  text-transform:uppercase;letter-spacing:0.15em;border:1.5px solid #FF006B;
  border-radius:24px;padding:6px 20px;margin-bottom:40px;
  box-shadow:0 0 18px rgba(255,0,107,0.28);animation:bIn 0.7s ease 0.1s both;}
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
.h-body{font-size:18px;color:#E0E0E0;line-height:1.75;max-width:600px;
  margin:0 auto 48px;animation:bdy 0.7s ease 0.5s both;}
@keyframes bdy{from{opacity:0;}to{opacity:1;}}
.hl1{color:#00FFD0;font-weight:700;}.hl2{color:#00FFB0;font-weight:700;}
/* CTA button — form submit to ?launch=1 */
.cta-form{display:flex;justify-content:center;animation:bdy 0.6s ease 0.7s both;}
.btn-launch{
  width:100%;max-width:520px;height:60px;cursor:pointer;
  background:linear-gradient(90deg,#6B1AFF 0%,#FF006B 50%,#00FFD0 100%);
  background-size:200% 100%;
  color:#fff;border:none;border-radius:32px;
  font-family:'Inter',sans-serif;font-size:18px;font-weight:500;
  letter-spacing:0.02em;
  box-shadow:0 4px 32px rgba(0,255,208,0.22);
  transition:background-position 0.4s,box-shadow 0.3s,transform 0.15s;
}
.btn-launch:hover{
  background-position:100% 0;
  box-shadow:0 6px 40px rgba(0,255,208,0.42),0 2px 16px rgba(255,0,107,0.28);
  transform:translateY(-2px);
}
.btn-launch:active{transform:scale(0.97);}
/* Stats */
.stats{display:flex;max-width:900px;margin:0 auto 0;
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
  border-radius:20px;overflow:hidden;position:relative;z-index:1;}
.stat{flex:1;padding:28px 12px;text-align:center;
  border-right:1px solid rgba(255,255,255,0.07);transition:background 0.2s;}
.stat:last-child{border-right:none;}
.stat:hover{background:rgba(107,26,255,0.12);}
.sv{font-family:'Montserrat',sans-serif;font-size:34px;font-weight:800;
  background:linear-gradient(90deg,#00FFD0,#6B1AFF);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  line-height:1;margin-bottom:7px;}
.sl{font-size:10px;font-weight:700;color:rgba(255,255,255,0.35);
  letter-spacing:0.12em;text-transform:uppercase;}
/* Sections */
.sec{max-width:1200px;margin:88px auto 0;padding:0 48px;}
.s-tag{font-size:11px;font-weight:700;color:#00FFD0;letter-spacing:0.15em;
  text-transform:uppercase;margin-bottom:10px;}
.s-title{font-family:'Montserrat',sans-serif;font-size:36px;font-weight:800;
  color:#fff;text-transform:uppercase;letter-spacing:-0.02em;margin-bottom:32px;}
.s-title em{font-style:italic;background:linear-gradient(90deg,#00FFD0,#FF006B);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
/* Cards */
.cgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}
.ccard{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
  border-radius:14px;padding:22px;
  transition:transform 0.2s,border-color 0.2s,box-shadow 0.2s;}
.ccard:hover{transform:translateY(-4px);border-color:rgba(0,255,208,0.28);
  box-shadow:0 8px 28px rgba(0,255,208,0.07);}
.c-num{font-size:10px;font-weight:700;color:rgba(255,255,255,0.22);
  letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;}
.c-ttl{font-size:14px;font-weight:600;color:#fff;margin-bottom:6px;}
.c-bdy{font-size:12px;color:rgba(255,255,255,0.45);line-height:1.7;}
.c-tag{display:inline-block;margin-top:10px;font-size:10px;font-weight:600;
  padding:3px 10px;border-radius:9999px;border:1px solid;}
.tc{color:#00FFD0;border-color:rgba(0,255,208,0.32);background:rgba(0,255,208,0.07);}
.tv{color:#A78BFA;border-color:rgba(167,139,250,0.32);background:rgba(167,139,250,0.07);}
.tm{color:#FF006B;border-color:rgba(255,0,107,0.32);background:rgba(255,0,107,0.07);}
.ta{color:#FFD600;border-color:rgba(255,214,0,0.32);background:rgba(255,214,0,0.07);}
/* Pipeline */
.pipe-row{display:flex;align-items:center;justify-content:space-between;
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);
  border-radius:18px;padding:32px 40px;width:100%;}
.p-step{display:flex;flex-direction:column;align-items:center;gap:5px;
  flex:1;padding:8px 4px;border-radius:10px;transition:all 0.2s;cursor:default;}
.p-step:hover{background:rgba(107,26,255,0.2);transform:translateY(-3px);}
.p-lbl{font-family:'Montserrat',sans-serif;font-size:12px;font-weight:800;
  color:rgba(255,255,255,0.72);letter-spacing:0.05em;text-transform:uppercase;}
.p-sub{font-size:10px;color:rgba(255,255,255,0.3);}
.p-arr{color:rgba(255,255,255,0.15);font-size:16px;flex-shrink:0;
  animation:aP 2.5s ease-in-out infinite;}
@keyframes aP{0%,100%{color:rgba(255,255,255,0.12);}50%{color:#00FFD0;}}
/* Stack */
.tags{display:flex;flex-wrap:wrap;gap:10px;}
.tag{padding:7px 16px;font-size:11px;font-weight:600;
  border-radius:9999px;border:1px solid;letter-spacing:0.04em;transition:transform 0.2s;}
.tag:hover{transform:translateY(-2px);}
/* Footer */
.foot{max-width:1200px;margin:72px auto 0;padding:22px 48px 64px;
  border-top:1px solid rgba(255,255,255,0.07);
  display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
.foot span{font-size:12px;color:rgba(255,255,255,0.25);}
</style>

<div class="land">
<div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
<div class="wrap">

<nav>
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
  <!-- FORM SUBMIT = most reliable navigation method in Streamlit -->
  <form class="cta-form" method="get" action="">
    <input type="hidden" name="launch" value="1">
    <button type="submit" class="btn-launch">Launch App &rarr;</button>
  </form>
</section>

<div class="stats">
  <div class="stat"><div class="sv">0%</div><div class="sl">Hallucination Rate</div></div>
  <div class="stat"><div class="sv">3x</div><div class="sl">Retrieval Methods</div></div>
  <div class="stat"><div class="sv">100%</div><div class="sl">Local &amp; Private</div></div>
  <div class="stat"><div class="sv">inf</div><div class="sl">Documents</div></div>
</div>

<div class="sec">
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

<div class="sec">
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

<div class="sec">
  <div class="s-tag">// Stack</div>
  <div class="s-title">BUILT <em>WITH</em></div>
  <div class="tags">
    <span class="tag tc">pdfplumber</span><span class="tag tc">ChromaDB</span>
    <span class="tag tc">sentence-transformers</span><span class="tag tv">LangGraph</span>
    <span class="tag tv">langchain-ollama</span><span class="tag tv">llama3.1:8b</span>
    <span class="tag tm">BM25 + RRF</span><span class="tag tm">cross-encoder reranker</span>
    <span class="tag ta">FastAPI</span><span class="tag ta">Streamlit</span>
    <span class="tag ta">Python 3.14</span>
  </div>
</div>

<div class="foot">
  <span>NeuralDoc &mdash; Production RAG System</span>
  <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
</div>

</div>
</div>""")


# ═════════════════════════════════════════════════════════════════════════════
# CHAT PAGE
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    [data-testid="stAppViewContainer"]{
      background:
        radial-gradient(ellipse 65% 50% at 0% 0%,   rgba(107,26,255,0.28),transparent 60%),
        radial-gradient(ellipse 50% 60% at 100% 100%,rgba(0,255,208,0.14),transparent 55%),
        radial-gradient(ellipse 40% 40% at 60% 40%, rgba(255,0,107,0.10),transparent 50%),
        #0A0A1A !important;
    }
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container{
      padding:0!important;background:transparent!important;max-width:100%!important;}
    [data-testid="stAppViewContainer"]::before{
      content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
      background-image:linear-gradient(rgba(255,255,255,0.035) 1px,transparent 1px),
        linear-gradient(90deg,rgba(255,255,255,0.035) 1px,transparent 1px);
      background-size:80px 80px;}
    .stTextInput input{
      background:rgba(255,255,255,0.06)!important;
      border:1px solid rgba(255,255,255,0.12)!important;
      border-radius:12px!important;color:#E0E0E0!important;
      font-family:'Inter',sans-serif!important;font-size:15px!important;
      padding:14px 18px!important;
      transition:border-color 0.18s,box-shadow 0.18s!important;}
    .stTextInput input:focus{
      border-color:#00FFD0!important;
      box-shadow:0 0 0 2px rgba(0,255,208,0.15)!important;outline:none!important;}
    .stTextInput input::placeholder{color:rgba(255,255,255,0.3)!important;}
    .stTextInput label,.stFileUploader label{display:none!important;}
    .stButton>button{
      background:linear-gradient(90deg,#6B1AFF,#FF006B)!important;
      color:#fff!important;border:none!important;border-radius:12px!important;
      font-family:'Inter',sans-serif!important;font-weight:600!important;
      font-size:14px!important;padding:12px 0!important;
      box-shadow:0 2px 12px rgba(107,26,255,0.3)!important;transition:all 0.15s!important;}
    .stButton>button:hover{
      box-shadow:0 4px 20px rgba(255,0,107,0.4)!important;transform:translateY(-1px)!important;}
    .stButton>button:active{transform:scale(0.97)!important;}
    [data-testid="stFileUploaderDropzone"]{
      background:rgba(255,255,255,0.04)!important;
      border:1.5px dashed rgba(0,255,208,0.3)!important;
      border-radius:14px!important;transition:all 0.2s!important;}
    [data-testid="stFileUploaderDropzone"]:hover{
      border-color:#00FFD0!important;background:rgba(0,255,208,0.04)!important;}
    [data-testid="stFileUploaderDropzone"] *{color:rgba(255,255,255,0.6)!important;}
    hr{border-color:rgba(255,255,255,0.08)!important;}
    /* Download button */
    [data-testid="stDownloadButton"]>button{
      background:rgba(0,255,208,0.1)!important;color:#00FFD0!important;
      border:1px solid rgba(0,255,208,0.3)!important;border-radius:12px!important;
      font-size:13px!important;font-weight:600!important;padding:10px 0!important;
      box-shadow:none!important;}
    [data-testid="stDownloadButton"]>button:hover{
      background:rgba(0,255,208,0.18)!important;transform:translateY(-1px)!important;}
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
        bd="#FFD600"; bt="API online &mdash; No docs indexed"
    else:
        bs="color:#FF006B;background:rgba(255,0,107,0.1);border:1px solid rgba(255,0,107,0.3);"
        bd="#FF006B"; bt="API offline"

    # ── Topbar ────────────────────────────────────────────────────────────────
    st.html(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
      height:60px;padding:0 40px;
      background:rgba(10,10,26,0.88);backdrop-filter:blur(12px);
      border-bottom:1px solid rgba(255,255,255,0.08);
      position:sticky;top:0;z-index:100;">
      <div style="display:flex;align-items:center;gap:9px;">
        <div style="width:10px;height:10px;border-radius:50%;
          background:linear-gradient(135deg,#00FFD0,#6B1AFF);"></div>
        <span style="font-family:'Montserrat',sans-serif;font-size:18px;font-weight:800;
          letter-spacing:0.08em;text-transform:uppercase;">
          <span style="color:#00FFD0;">NEURAL</span><span style="color:#FF006B;">DOC</span>
        </span>
      </div>
      <div style="display:inline-flex;align-items:center;gap:6px;
        font-family:'Inter',sans-serif;font-size:12px;font-weight:500;
        padding:5px 14px;border-radius:9999px;{bs}">
        <div style="width:5px;height:5px;border-radius:50%;background:{bd};flex-shrink:0;"></div>
        {bt}
      </div>
    </div>""")

    # ── Action buttons row ────────────────────────────────────────────────────
    st.html('<div style="padding:16px 40px 0;position:relative;z-index:10;">')
    ab = st.columns([1, 1, 1, 1, 4])
    with ab[0]:
        if st.button("← Home", key="back_home", use_container_width=True):
            # Auto-save conversation on exit
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.page = "landing"
            st.rerun()
    with ab[1]:
        if st.button("Clear Chat", key="clr_chat", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.messages = []
            st.session_state.active_conv_id = None
            st.rerun()
    with ab[2]:
        # FEATURE 2: Export as Markdown
        if st.session_state.messages:
            md = export_as_markdown(st.session_state.messages, "NeuralDoc Chat Export")
            st.download_button(
                "Export MD",
                data=md,
                file_name=f"neuraldoc_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
                key="export_md"
            )
        else:
            st.html('<div style="height:44px;"></div>')
    with ab[3]:
        # FEATURE 3: Analytics toggle
        toggle_label = "Hide Stats" if st.session_state.show_analytics else "Analytics"
        if st.button(toggle_label, key="toggle_analytics", use_container_width=True):
            st.session_state.show_analytics = not st.session_state.show_analytics
            st.rerun()
    st.html('</div>')

    # ── FEATURE 3: Analytics panel ────────────────────────────────────────────
    if st.session_state.show_analytics:
        stats = get_stats()
        st.html(f"""
        <div style="margin:12px 40px 0;padding:20px 24px;
          background:rgba(255,255,255,0.04);border:1px solid rgba(0,255,208,0.2);
          border-radius:14px;position:relative;z-index:10;">
          <div style="font-family:'Inter',sans-serif;font-size:10px;font-weight:700;
            color:#00FFD0;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:14px;">
            // Query Analytics</div>
          <div style="display:flex;gap:24px;flex-wrap:wrap;">
            <div style="text-align:center;">
              <div style="font-family:'Montserrat',sans-serif;font-size:28px;font-weight:800;
                background:linear-gradient(90deg,#00FFD0,#6B1AFF);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                {stats['total_queries']}</div>
              <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,0.3);
                letter-spacing:0.1em;text-transform:uppercase;">Total Queries</div>
            </div>
            <div style="text-align:center;">
              <div style="font-family:'Montserrat',sans-serif;font-size:28px;font-weight:800;
                background:linear-gradient(90deg,#00FFD0,#6B1AFF);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                {stats['answered']}</div>
              <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,0.3);
                letter-spacing:0.1em;text-transform:uppercase;">Answered</div>
            </div>
            <div style="text-align:center;">
              <div style="font-family:'Montserrat',sans-serif;font-size:28px;font-weight:800;
                color:#FF006B;">{stats['refused']}</div>
              <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,0.3);
                letter-spacing:0.1em;text-transform:uppercase;">Refused</div>
            </div>
            <div style="text-align:center;">
              <div style="font-family:'Montserrat',sans-serif;font-size:28px;font-weight:800;
                color:#FFD600;">{stats['refusal_rate']}%</div>
              <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,0.3);
                letter-spacing:0.1em;text-transform:uppercase;">Refusal Rate</div>
            </div>
            <div style="text-align:center;">
              <div style="font-family:'Montserrat',sans-serif;font-size:28px;font-weight:800;
                color:#A78BFA;">{int(stats['avg_latency_ms'])}ms</div>
              <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,0.3);
                letter-spacing:0.1em;text-transform:uppercase;">Avg Latency</div>
            </div>
          </div>
          {f'''<div style="margin-top:14px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.06);">
            <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,0.25);
              letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">Recent queries</div>
            {''.join(f'<div style="font-size:12px;color:rgba(255,255,255,0.45);padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.04);">{"⚠" if q["refused"] else "✓"} {q["query"][:80]} <span style="color:rgba(255,255,255,0.25);font-family:\'JetBrains Mono\',monospace;font-size:10px;">{q["latency_ms"]}ms</span></div>' for q in stats["recent"])}
          </div>''' if stats["recent"] else ''}
        </div>""")

    st.html('<div style="height:20px;"></div>')

    # ── Main layout ───────────────────────────────────────────────────────────
    st.html('<div style="padding:0 40px 40px;position:relative;z-index:10;">')
    col_chat, col_right = st.columns([2, 1], gap="large")

    # ── RIGHT: Upload + FEATURE 1 Chat History ────────────────────────────────
    with col_right:
        # Upload panel
        st.html("""<div style="background:rgba(255,255,255,0.04);
          border:1px solid rgba(255,255,255,0.09);border-radius:18px;
          padding:28px 28px 22px;box-shadow:0 4px 24px rgba(0,255,208,0.05);
          margin-bottom:16px;">""")
        uh1, uh2 = st.columns([3, 1])
        with uh1:
            st.html("""<div>
              <div style="font-size:11px;font-weight:700;color:rgba(255,255,255,0.3);
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">Knowledge Base</div>
              <div style="font-family:'Montserrat',sans-serif;font-size:20px;font-weight:800;
                text-transform:uppercase;letter-spacing:0.02em;margin-bottom:16px;">
                <span style="color:#fff;">UPLOAD </span>
                <em style="font-style:italic;background:linear-gradient(90deg,#00FFD0,#00FFB0);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;">DOCS</em>
              </div></div>""")
        with uh2:
            st.html('<div style="height:24px;"></div>')
            if st.button("Clear", key="clear_idx", use_container_width=True):
                try:
                    resp=requests.delete(f"{API_BASE}/index",timeout=15)
                    if resp.status_code==200: st.success("Index cleared."); st.rerun()
                    else: st.error(f"Error: {resp.text}")
                except: st.error("API offline.")

        st.html("""<div style="background:rgba(0,255,208,0.04);
          border:1.5px dashed rgba(0,255,208,0.25);border-radius:12px;
          padding:16px;margin-bottom:12px;text-align:center;
          transition:border-color 0.2s,background 0.2s;"
          onmouseover="this.style.borderColor='#00FFD0';this.style.background='rgba(0,255,208,0.07)'"
          onmouseout="this.style.borderColor='rgba(0,255,208,0.25)';this.style.background='rgba(0,255,208,0.04)'">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none"
            stroke="#00FFD0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
            style="margin:0 auto 7px;display:block;opacity:0.8;">
            <polyline points="16 16 12 12 8 16"></polyline>
            <line x1="12" y1="12" x2="12" y2="21"></line>
            <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"></path>
          </svg>
          <div style="font-size:13px;font-weight:500;color:#E0E0E0;margin-bottom:3px;">Drop PDF below</div>
          <div style="font-size:11px;color:rgba(255,255,255,0.3);">
            Parsed &#8594; Chunked &#8594; Embedded &#8594; Indexed</div>
        </div>""")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")
        if uploaded:
            st.html(f"""<div style="background:rgba(0,255,208,0.07);
              border:1px solid rgba(0,255,208,0.25);border-radius:10px;
              padding:9px 13px;margin-bottom:10px;">
              <div style="font-size:13px;font-weight:600;color:#E0E0E0;">{uploaded.name}</div>
              <div style="font-size:11px;color:#00FFD0;margin-top:2px;">{uploaded.size//1024} KB</div>
            </div>""")
            if st.button("Index Document", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing..."):
                    try:
                        resp=requests.post(f"{API_BASE}/ingest",
                          files={"file":(uploaded.name,uploaded,"application/pdf")},timeout=120)
                        if resp.status_code==200:
                            d=resp.json()
                            st.success(f"Indexed {d['chunks_indexed']} chunks")
                            st.rerun()
                        else: st.error(f"Error: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("API offline.")
                    except Exception as e: st.error(str(e))

        if files:
            for f in files:
                fname=f.replace("\\","/").split("/")[-1]
                st.html(f"""<div style="background:rgba(255,255,255,0.04);
                  border:1px solid rgba(255,255,255,0.08);border-radius:10px;
                  padding:7px 12px;margin-bottom:5px;display:flex;align-items:center;">
                  <span style="font-size:12px;font-weight:500;color:#E0E0E0;flex:1;">{fname}</span>
                  <span style="font-size:10px;font-weight:700;padding:2px 8px;border-radius:9999px;
                    color:#00FFD0;background:rgba(0,255,208,0.1);border:1px solid rgba(0,255,208,0.3);">
                    indexed</span>
                </div>""")

        st.html("""<div style="margin-top:14px;background:rgba(255,255,255,0.03);
          border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:13px 15px;">
          <div style="font-size:10px;font-weight:700;color:rgba(255,255,255,0.28);
            letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">Tips</div>
          <div style="font-size:12px;color:rgba(255,255,255,0.42);line-height:1.9;">
            Click <b style="color:#00FFD0;">Clear</b> before switching documents.<br>
            Ask precise questions for best citation accuracy.<br>
            Every answer includes inline source references.<br>
            Unanswerable queries return a refusal, not a guess.
          </div></div>""")
        st.html('</div>')

        # ── FEATURE 1: Chat History Panel ─────────────────────────────────────
        convs = load_all_conversations()
        if convs:
            st.html("""<div style="background:rgba(255,255,255,0.04);
              border:1px solid rgba(255,255,255,0.09);border-radius:18px;
              padding:20px 22px;">
              <div style="font-size:10px;font-weight:700;color:#00FFD0;
                letter-spacing:0.15em;text-transform:uppercase;margin-bottom:14px;">
                // Chat History</div>""")

            for i, conv in enumerate(convs[:5]):
                ts = conv["timestamp"][:10]
                title = conv["title"][:36] + ("…" if len(conv["title"]) > 36 else "")
                n_msgs = len([m for m in conv["messages"] if m["role"]=="user"])
                hc1, hc2 = st.columns([4, 1])
                with hc1:
                    st.html(f"""<div style="padding:8px 10px;border-radius:8px;cursor:pointer;
                      border:1px solid rgba(255,255,255,0.07);margin-bottom:5px;
                      transition:border-color 0.2s,background 0.2s;"
                      onmouseover="this.style.borderColor='rgba(107,26,255,0.4)';this.style.background='rgba(107,26,255,0.08)'"
                      onmouseout="this.style.borderColor='rgba(255,255,255,0.07)';this.style.background=''">
                      <div style="font-size:12px;font-weight:500;color:#E0E0E0;">{title}</div>
                      <div style="font-size:10px;color:rgba(255,255,255,0.3);margin-top:2px;">
                        {ts} &middot; {n_msgs} queries</div>
                    </div>""")
                with hc2:
                    if st.button("Load", key=f"load_{conv['id']}_{i}", use_container_width=True):
                        st.session_state.messages = load_conversation(conv["id"])
                        st.session_state.active_conv_id = conv["id"]
                        st.rerun()

            st.html('</div>')

    # ── LEFT: Chat ────────────────────────────────────────────────────────────
    with col_chat:
        st.html("""<div style="background:rgba(255,255,255,0.04);
          border:1px solid rgba(255,255,255,0.09);border-radius:18px;
          padding:28px 28px 22px;box-shadow:0 4px 24px rgba(107,26,255,0.08);">""")

        st.html(f"""<div style="display:flex;align-items:flex-start;
          justify-content:space-between;margin-bottom:20px;">
          <div>
            <div style="font-size:11px;font-weight:700;color:rgba(255,255,255,0.3);
              letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">Document QA</div>
            <div style="font-family:'Montserrat',sans-serif;font-size:24px;font-weight:800;
              text-transform:uppercase;letter-spacing:0.01em;line-height:1.1;">
              <span style="color:#fff;">ASK YOUR </span>
              <em style="font-style:italic;background:linear-gradient(90deg,#6B1AFF,#FF006B);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">DOCS</em>
            </div>
          </div>
          <div style="display:flex;gap:7px;align-items:center;padding-top:18px;flex-shrink:0;">
            <span style="font-size:12px;font-weight:600;color:#A78BFA;
              background:rgba(167,139,250,0.12);border:1px solid rgba(167,139,250,0.3);
              padding:4px 12px;border-radius:9999px;">{chunks} chunks</span>
            <span style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:9999px;border:1px solid;
              {'color:#00FFD0;background:rgba(0,255,208,0.1);border-color:rgba(0,255,208,0.3);' if ready else 'color:#FF006B;background:rgba(255,0,107,0.1);border-color:rgba(255,0,107,0.3);'}">
              {'Ready' if ready else 'Not ready'}</span>
          </div>
        </div>""")

        if st.session_state.messages:
            html=""
            for m in st.session_state.messages:
                if m["role"]=="user":
                    html+=f"""<div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
                      <div style="max-width:72%;padding:12px 16px;
                        background:linear-gradient(135deg,rgba(107,26,255,0.5),rgba(255,0,107,0.4));
                        color:#fff;border-radius:14px 3px 14px 14px;
                        font-size:14px;line-height:1.65;border:1px solid rgba(255,255,255,0.12);">
                        {m['content']}</div></div>"""
                else:
                    refs=""
                    if m.get("references"):
                        refs='<div style="margin-top:9px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs+=f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:9999px;color:#00FFD0;background:rgba(0,255,208,0.08);border:1px solid rgba(0,255,208,0.25);">{ref}</span>'
                        refs+="</div>"
                    rfsd=""
                    if m.get("refused"):
                        rfsd='<div style="margin-top:7px;font-size:12px;font-weight:600;color:#FF006B;background:rgba(255,0,107,0.1);border:1px solid rgba(255,0,107,0.3);padding:5px 11px;border-radius:10px;display:inline-block;">Insufficient evidence — refusal triggered</div>'
                    lat=""
                    if m.get("latency_ms"):
                        lat=f'<div style="margin-top:4px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,0.25);">{m["latency_ms"]} ms</div>'
                    html+=f"""<div style="display:flex;margin-bottom:14px;gap:9px;align-items:flex-start;">
                      <div style="width:26px;height:26px;border-radius:7px;flex-shrink:0;margin-top:2px;
                        background:linear-gradient(135deg,rgba(107,26,255,0.4),rgba(0,255,208,0.2));
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Montserrat',sans-serif;font-size:11px;font-weight:800;
                        color:#00FFD0;border:1px solid rgba(0,255,208,0.2);">N</div>
                      <div style="max-width:86%;padding:13px 16px;background:rgba(255,255,255,0.05);
                        border:1px solid rgba(255,255,255,0.09);border-radius:3px 14px 14px 14px;
                        font-size:14px;color:#E0E0E0;line-height:1.75;">
                        {m['content']}{refs}{rfsd}{lat}</div></div>"""
            st.html(f"""<div style="max-height:46vh;overflow-y:auto;margin-bottom:14px;
              padding:2px;scrollbar-width:thin;scrollbar-color:rgba(107,26,255,0.4) transparent;">
              {html}</div>""")
        else:
            st.html("""<div style="text-align:center;padding:48px 20px 36px;
              background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
              border-radius:14px;margin-bottom:14px;">
              <div style="font-family:'Montserrat',sans-serif;font-size:18px;font-weight:800;
                text-transform:uppercase;letter-spacing:0.02em;margin-bottom:10px;
                background:linear-gradient(90deg,#6B1AFF,#FF006B,#00FFD0);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Ask Anything</div>
              <div style="font-size:13px;color:rgba(255,255,255,0.35);
                max-width:300px;margin:0 auto 20px;line-height:1.7;">
                Upload a PDF on the right, then ask questions here. Every answer is cited.</div>
              <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
                <span style="font-size:12px;font-weight:500;color:#A78BFA;
                  background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.25);
                  padding:6px 14px;border-radius:9999px;cursor:default;">What is the main finding?</span>
                <span style="font-size:12px;font-weight:500;color:#A78BFA;
                  background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.25);
                  padding:6px 14px;border-radius:9999px;cursor:default;">Summarise section 3</span>
                <span style="font-size:12px;font-weight:500;color:#A78BFA;
                  background:rgba(167,139,250,0.1);border:1px solid rgba(167,139,250,0.25);
                  padding:6px 14px;border-radius:9999px;cursor:default;">What are the key risks?</span>
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
                            # Record to analytics
                            record_query(
                                query=query,
                                latency_ms=d["latency_ms"],
                                refused=d["refused"],
                            )
                            st.rerun()
                        else:
                            st.error(f"API error: {resp.json().get('detail',resp.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach API. Run: uv run uvicorn api:app --reload --port 8000")
        st.html('</div>')
    st.html('</div>')