"""Landing page — NeuralDoc RAG"""
import streamlit as st

st.set_page_config(
    page_title="NeuralDoc RAG",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Kill EVERY Streamlit chrome element ───────────────────────────────────────
st.html("""<style>
/* Nuclear option — hide/collapse everything Streamlit adds */
#root > div:first-child { padding-top: 0 !important; }
[data-testid="stHeader"]          { display:none!important; height:0!important; }
[data-testid="stToolbar"]         { display:none!important; height:0!important; }
[data-testid="stDecoration"]      { display:none!important; height:0!important; }
[data-testid="stStatusWidget"]    { display:none!important; }
[data-testid="collapsedControl"]  { display:none!important; }
[data-testid="stSidebarNav"]      { display:none!important; }
section[data-testid="stSidebar"]  { display:none!important; }
#MainMenu                         { display:none!important; }
footer                            { display:none!important; }
/* Remove all wrapper padding/margin */
html, body { margin:0!important; padding:0!important; background:#030010!important; }
[data-testid="stAppViewContainer"]        { background:#030010!important; padding:0!important; margin:0!important; border:none!important; }
[data-testid="stMain"]                    { background:transparent!important; padding:0!important; }
[data-testid="stMainBlockContainer"]      { background:transparent!important; padding:0!important; }
[data-testid="stAppViewBlockContainer"]   { padding:0!important; max-width:100%!important; }
.block-container                          { padding:0!important; max-width:100%!important; border:none!important; }
/* Remove gaps between st.html blocks */
[data-testid="stVerticalBlock"]          { gap:0!important; }
[data-testid="stVerticalBlock"] > div    { margin:0!important; padding:0!important; }
/* Remove white/gray top line from stMainBlockContainer */
[data-testid="stMainBlockContainer"]::before { display:none!important; }
</style>""")

# ── Fonts + background ────────────────────────────────────────────────────────
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
.bg {
  position:fixed; inset:0; z-index:0; pointer-events:none;
  background:
    radial-gradient(ellipse 70% 55% at 12% 12%, rgba(110,0,240,.35) 0%, transparent 55%),
    radial-gradient(ellipse 55% 65% at 88% 88%, rgba(0,210,150,.22) 0%, transparent 55%),
    radial-gradient(ellipse 40% 40% at 50% 40%, rgba(210,0,90,.12) 0%, transparent 60%),
    #030010;
  animation: bgS 16s ease-in-out infinite alternate;
}
@keyframes bgS { 0%{filter:hue-rotate(0deg);} 100%{filter:hue-rotate(20deg) brightness(1.06);} }
.gridlines {
  position:fixed; inset:0; z-index:0; pointer-events:none;
  background-image:
    linear-gradient(rgba(100,0,255,.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(100,0,255,.07) 1px, transparent 1px);
  background-size:58px 58px;
  animation:gP 6s ease-in-out infinite;
}
@keyframes gP { 0%,100%{opacity:.35;} 50%{opacity:.8;} }
.orb { position:fixed; border-radius:50%; filter:blur(100px); pointer-events:none; z-index:0; animation:oD linear infinite; }
.o1 { width:500px;height:500px;background:rgba(110,0,240,.28);top:-200px;left:-180px;animation-duration:23s; }
.o2 { width:420px;height:420px;background:rgba(0,200,140,.2);bottom:-150px;right:-150px;animation-duration:29s;animation-delay:-11s; }
.o3 { width:320px;height:320px;background:rgba(210,0,80,.16);top:38%;left:54%;animation-duration:20s;animation-delay:-6s; }
@keyframes oD {
  0%{transform:translate(0,0) scale(1);}
  33%{transform:translate(42px,-56px) scale(1.08);}
  66%{transform:translate(-32px,42px) scale(.93);}
  100%{transform:translate(0,0) scale(1);}
}
</style>
<div class="bg"></div>
<div class="gridlines"></div>
<div class="orb o1"></div>
<div class="orb o2"></div>
<div class="orb o3"></div>
""")

# ── Nav ───────────────────────────────────────────────────────────────────────
st.html("""<style>
.nav {
  position:relative; z-index:10;
  display:flex; align-items:center; justify-content:space-between;
  max-width:1200px; margin:0 auto;
  padding:36px 48px 0;
  animation:fD .7s ease both;
}
@keyframes fD { from{opacity:0;transform:translateY(-18px);} to{opacity:1;transform:translateY(0);} }
.logo {
  font-family:'Bebas Neue',sans-serif; font-size:32px; letter-spacing:6px;
  background:linear-gradient(135deg,#00DFA0,#6B00F0,#E0005A);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.nav-pill {
  font-family:'JetBrains Mono',monospace; font-size:12px; color:#00DFA0;
  letter-spacing:2px; border:1px solid rgba(0,223,160,.35);
  padding:6px 16px; border-radius:20px; background:rgba(0,223,160,.06);
}
</style>
<nav class="nav">
  <div class="logo">NeuralDoc</div>
  <div class="nav-pill">PRODUCTION RAG v1.0</div>
</nav>""")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.html("""<style>
.hero {
  position:relative; z-index:10;
  max-width:1000px; margin:0 auto;
  padding:68px 48px 0;
  text-align:center;
  animation:fU .9s ease .2s both;
}
@keyframes fU { from{opacity:0;transform:translateY(36px);} to{opacity:1;transform:translateY(0);} }
.eyebrow {
  display:inline-flex; align-items:center; gap:10px;
  font-family:'JetBrains Mono',monospace; font-size:12px;
  color:#E0005A; letter-spacing:3px;
  border:1px solid rgba(224,0,90,.3); background:rgba(224,0,90,.07);
  padding:8px 20px; border-radius:30px; margin-bottom:32px;
  animation:eG 3.5s ease-in-out infinite;
}
@keyframes eG { 0%,100%{box-shadow:none;} 50%{box-shadow:0 0 22px rgba(224,0,90,.35);} }
.edot {
  width:7px; height:7px; border-radius:50%; background:#E0005A;
  animation:dB 1.6s ease-in-out infinite; flex-shrink:0;
}
@keyframes dB { 0%,100%{opacity:1;} 50%{opacity:.1;} }
.hero-title {
  font-family:'Bebas Neue',sans-serif;
  font-size:clamp(80px,11vw,132px);
  line-height:.88; letter-spacing:4px; color:#fff; margin:0;
}
.t1 {
  background:linear-gradient(90deg,#6B00F0,#E0005A);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  display:inline-block; animation:t1S 5s ease-in-out infinite alternate;
}
@keyframes t1S { from{filter:hue-rotate(0deg);} to{filter:hue-rotate(28deg);} }
.t2 {
  background:linear-gradient(90deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  display:inline-block;
}
.hero-desc {
  font-family:'Syne',sans-serif;
  font-size:19px; color:rgba(255,255,255,.55);
  max-width:600px; margin:28px auto 0; line-height:1.85;
}
.hero-desc strong { color:#00DFA0; font-weight:700; }
</style>
<div class="hero">
  <div class="eyebrow"><span class="edot"></span>ZERO HALLUCINATION TOLERANCE</div>
  <h1 class="hero-title">
    <span class="t1">NEURAL</span><br>
    <span class="t2">DOC</span> RAG
  </h1>
  <p class="hero-desc">
    A <strong>production-grade</strong> RAG system that answers questions from
    your documents with <strong>inline citations</strong>, hybrid retrieval,
    and a hard refusal trigger &mdash; no guessing, ever.
  </p>
</div>""")

# ── Launch button (native Streamlit — only reliable navigation method) ─────────
st.html("""<style>
/* Target the column that holds the button */
.launch-col { position:relative; z-index:10; }
[data-testid="stButton"] > button {
  display:block!important;
  width:100%!important;
  padding:17px 0!important;
  font-family:'Syne',sans-serif!important;
  font-size:18px!important; font-weight:700!important;
  border-radius:50px!important; letter-spacing:.5px!important;
  background:linear-gradient(135deg,#6B00F0,#E0005A)!important;
  color:#fff!important; border:none!important;
  box-shadow:0 0 44px rgba(107,0,240,.55)!important;
  animation:bG 3s ease-in-out infinite!important;
  transition:transform .3s!important;
}
@keyframes bG {
  0%,100%{box-shadow:0 0 44px rgba(107,0,240,.55);}
  50%{box-shadow:0 0 70px rgba(107,0,240,.82);}
}
[data-testid="stButton"] > button:hover {
  transform:translateY(-4px) scale(1.03)!important;
}
</style>""")

# Center the button using columns
_l, _mid, _r = st.columns([3, 2, 3])
with _mid:
    st.html('<div style="height:44px"></div>')
    if st.button("Launch App →", key="launch_btn", use_container_width=True):
        st.switch_page("pages/RAG_Chat.py")
    st.html('<div style="height:16px"></div>')

# ── Stats bar ─────────────────────────────────────────────────────────────────
st.html("""<style>
.stats {
  position:relative; z-index:10;
  display:flex; max-width:900px; margin:52px auto 0;
  border:1px solid rgba(255,255,255,.08); border-radius:20px;
  overflow:hidden; background:rgba(255,255,255,.025);
  animation:fU .9s ease .4s both;
}
.stat {
  flex:1; padding:30px 16px; text-align:center;
  border-right:1px solid rgba(255,255,255,.07);
  transition:background .3s;
}
.stat:last-child { border-right:none; }
.stat:hover { background:rgba(107,0,240,.1); }
.sv {
  font-family:'Bebas Neue',sans-serif; font-size:48px; letter-spacing:3px;
  background:linear-gradient(135deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.sl {
  font-family:'JetBrains Mono',monospace; font-size:11px;
  color:rgba(255,255,255,.38); letter-spacing:3px;
  text-transform:uppercase; margin-top:5px;
}
</style>
<div class="stats">
  <div class="stat"><div class="sv">0%</div><div class="sl">Hallucination Rate</div></div>
  <div class="stat"><div class="sv">3x</div><div class="sl">Retrieval Methods</div></div>
  <div class="stat"><div class="sv">100%</div><div class="sl">Local &amp; Private</div></div>
  <div class="stat"><div class="sv">inf</div><div class="sl">Documents Supported</div></div>
</div>""")

# ── Features ──────────────────────────────────────────────────────────────────
st.html("""<style>
.section {
  position:relative; z-index:10;
  max-width:1200px; margin:88px auto 0; padding:0 48px;
}
.stag {
  font-family:'JetBrains Mono',monospace; font-size:12px;
  color:#6B00F0; letter-spacing:4px; text-transform:uppercase; margin-bottom:12px;
}
.sh {
  font-family:'Bebas Neue',sans-serif; font-size:56px;
  letter-spacing:2px; color:#fff; line-height:1; margin-bottom:44px;
}
.sh span {
  background:linear-gradient(90deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.cards {
  display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); gap:18px;
}
.card {
  padding:28px; background:rgba(255,255,255,.025);
  border:1px solid rgba(255,255,255,.08); border-radius:18px;
  transition:transform .4s,border-color .4s,box-shadow .4s;
}
.card:hover {
  transform:translateY(-8px);
  border-color:rgba(107,0,240,.4);
  box-shadow:0 16px 50px rgba(107,0,240,.16);
}
.cn {
  font-family:'JetBrains Mono',monospace; font-size:11px;
  letter-spacing:2px; color:rgba(255,255,255,.25); margin-bottom:14px;
}
.ct { font-family:'Syne',sans-serif; font-size:18px; font-weight:800; color:#fff; margin-bottom:10px; }
.cb { font-family:'Syne',sans-serif; font-size:14px; color:rgba(255,255,255,.45); line-height:1.8; }
.ctch {
  display:inline-block; margin-top:14px;
  font-family:'JetBrains Mono',monospace; font-size:11px;
  padding:4px 12px; border-radius:20px; letter-spacing:1px;
}
</style>
<div class="section" id="features">
  <div class="stag">// Capabilities</div>
  <div class="sh">SIX <span>PILLARS</span></div>
  <div class="cards">
    <div class="card">
      <div class="cn">01 &mdash; INGESTION</div>
      <div class="ct">Smart PDF Parsing</div>
      <div class="cb">Handles multi-column layouts, embedded tables, and complex structures. Headers and footers stripped automatically.</div>
      <span class="ctch" style="color:#00DFA0;background:rgba(0,223,160,.07);border:1px solid rgba(0,223,160,.2)">pdfplumber</span>
    </div>
    <div class="card">
      <div class="cn">02 &mdash; CHUNKING</div>
      <div class="ct">Semantic Chunking</div>
      <div class="cb">Header-aware chunks of 500&ndash;800 tokens. Every chunk carries source, page, and section breadcrumb as metadata.</div>
      <span class="ctch" style="color:#6B00F0;background:rgba(107,0,240,.07);border:1px solid rgba(107,0,240,.2)">tiktoken</span>
    </div>
    <div class="card">
      <div class="cn">03 &mdash; RETRIEVAL</div>
      <div class="ct">Hybrid Search</div>
      <div class="cb">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion. Catches what either method alone misses.</div>
      <span class="ctch" style="color:#E0005A;background:rgba(224,0,90,.07);border:1px solid rgba(224,0,90,.2)">RRF Fusion</span>
    </div>
    <div class="card">
      <div class="cn">04 &mdash; RERANKING</div>
      <div class="ct">Cross-Encoder Precision</div>
      <div class="cb">Top 20 candidates re-scored by a cross-encoder. Only the highest-confidence 5 reach the generation layer.</div>
      <span class="ctch" style="color:#F0A800;background:rgba(240,168,0,.07);border:1px solid rgba(240,168,0,.2)">ms-marco</span>
    </div>
    <div class="card">
      <div class="cn">05 &mdash; GENERATION</div>
      <div class="ct">Attributed Answers</div>
      <div class="cb">Every claim carries an inline citation [Source, p.X]. A full References section is appended to every response.</div>
      <span class="ctch" style="color:#00AAFF;background:rgba(0,170,255,.07);border:1px solid rgba(0,170,255,.2)">LangGraph</span>
    </div>
    <div class="card">
      <div class="cn">06 &mdash; SAFETY</div>
      <div class="ct">Hard Refusal Gate</div>
      <div class="cb">Context below the confidence threshold triggers a fixed refusal string. No speculation, no hallucination, by design.</div>
      <span class="ctch" style="color:#FF6030;background:rgba(255,96,48,.07);border:1px solid rgba(255,96,48,.2)">Threshold Gate</span>
    </div>
  </div>
</div>""")

# ── Pipeline ──────────────────────────────────────────────────────────────────
st.html("""<style>
.pipe-wrap { position:relative; z-index:10; max-width:1200px; margin:88px auto 0; padding:0 48px; }
.pipe {
  display:flex; align-items:center; justify-content:center;
  flex-wrap:wrap; padding:44px;
  background:rgba(255,255,255,.018);
  border:1px solid rgba(255,255,255,.07); border-radius:20px;
}
.step {
  display:flex; flex-direction:column; align-items:center; gap:10px;
  padding:18px 22px;
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.09); border-radius:14px;
  min-width:92px; transition:all .3s;
}
.step:hover {
  background:rgba(107,0,240,.2); border-color:rgba(107,0,240,.5);
  transform:translateY(-6px); box-shadow:0 14px 40px rgba(107,0,240,.22);
}
.si {
  font-family:'Bebas Neue',sans-serif; font-size:14px;
  letter-spacing:2px; color:rgba(255,255,255,.7);
}
.slb {
  font-family:'JetBrains Mono',monospace; font-size:11px;
  color:rgba(255,255,255,.4); letter-spacing:1px;
}
.arr {
  color:rgba(255,255,255,.18); font-size:18px; padding:0 5px; flex-shrink:0;
  animation:aP 2.4s ease-in-out infinite;
}
.arr:nth-child(even) { animation-delay:.6s; }
@keyframes aP { 0%,100%{color:rgba(255,255,255,.14);} 50%{color:rgba(0,223,160,.72);} }
</style>
<div class="pipe-wrap">
  <div class="stag">// Architecture</div>
  <div class="sh">THE <span>PIPELINE</span></div>
  <div class="pipe">
    <div class="step"><div class="si">PDF</div><div class="slb">Parse</div></div>
    <div class="arr">&rarr;</div>
    <div class="step"><div class="si">SPLIT</div><div class="slb">Chunk</div></div>
    <div class="arr">&rarr;</div>
    <div class="step"><div class="si">EMBED</div><div class="slb">Vector</div></div>
    <div class="arr">&rarr;</div>
    <div class="step"><div class="si">BM25</div><div class="slb">Keyword</div></div>
    <div class="arr">&rarr;</div>
    <div class="step"><div class="si">RRF</div><div class="slb">Fuse</div></div>
    <div class="arr">&rarr;</div>
    <div class="step"><div class="si">RANK</div><div class="slb">Rerank</div></div>
    <div class="arr">&rarr;</div>
    <div class="step"><div class="si">LLM</div><div class="slb">Generate</div></div>
    <div class="arr">&rarr;</div>
    <div class="step"><div class="si">CITE</div><div class="slb">Attribute</div></div>
  </div>
</div>""")

# ── Tech Stack ────────────────────────────────────────────────────────────────
st.html("""<style>
.stack { position:relative; z-index:10; max-width:1200px; margin:88px auto 0; padding:0 48px; }
.tags { display:flex; flex-wrap:wrap; gap:12px; }
.tag {
  padding:9px 18px;
  font-family:'JetBrains Mono',monospace; font-size:12px;
  border-radius:30px; border:1px solid; letter-spacing:1px;
  transition:transform .3s; cursor:default;
}
.tag:hover { transform:translateY(-3px); }
.tg { color:#00DFA0; border-color:rgba(0,223,160,.3); background:rgba(0,223,160,.06); }
.tp { color:#6B00F0; border-color:rgba(107,0,240,.3); background:rgba(107,0,240,.06); }
.tr { color:#E0005A; border-color:rgba(224,0,90,.3); background:rgba(224,0,90,.06); }
.ty { color:#F0A800; border-color:rgba(240,168,0,.3); background:rgba(240,168,0,.06); }
</style>
<div class="stack">
  <div class="stag">// Stack</div>
  <div class="sh">BUILT <span>WITH</span></div>
  <div class="tags">
    <span class="tag tg">pdfplumber</span>
    <span class="tag tg">ChromaDB</span>
    <span class="tag tg">sentence-transformers</span>
    <span class="tag tp">LangGraph</span>
    <span class="tag tp">langchain-ollama</span>
    <span class="tag tp">llama3.1:8b</span>
    <span class="tag tr">BM25 + RRF</span>
    <span class="tag tr">cross-encoder reranker</span>
    <span class="tag ty">FastAPI</span>
    <span class="tag ty">Streamlit</span>
    <span class="tag ty">Python 3.14</span>
  </div>
</div>""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.html("""<style>
.foot {
  position:relative; z-index:10;
  max-width:1200px; margin:80px auto 0; padding:24px 48px 72px;
  border-top:1px solid rgba(255,255,255,.07);
  display:flex; justify-content:space-between;
  align-items:center; flex-wrap:wrap; gap:12px;
}
.foot span {
  font-family:'JetBrains Mono',monospace; font-size:12px;
  color:rgba(255,255,255,.25);
}
</style>
<div class="foot">
  <span>NeuralDoc &mdash; Production RAG System</span>
  <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
</div>""")