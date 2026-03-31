import streamlit as st

st.set_page_config(
    page_title="NeuralDoc RAG",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.html("""
<style>
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"],
[data-testid="collapsedControl"],
#MainMenu, footer,
section[data-testid="stSidebar"] {
  display: none !important;
  height: 0 !important;
  overflow: hidden !important;
}
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.block-container {
  background: #030010 !important;
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
}
/* Remove gaps between Streamlit elements */
[data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stVerticalBlock"] > div { margin: 0 !important; padding: 0 !important; }
</style>
""")

# Background layers
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

.nd-bg {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(ellipse 70% 55% at 12% 12%, rgba(110,0,240,.32) 0%, transparent 55%),
    radial-gradient(ellipse 55% 65% at 88% 88%, rgba(0,210,150,.2) 0%, transparent 55%),
    radial-gradient(ellipse 40% 40% at 50% 40%, rgba(210,0,90,.1) 0%, transparent 60%),
    #030010;
  animation: ndBgS 16s ease-in-out infinite alternate;
}
@keyframes ndBgS { 0%{filter:hue-rotate(0deg);} 100%{filter:hue-rotate(20deg) brightness(1.06);} }

.nd-grid {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(100,0,255,.065) 1px, transparent 1px),
    linear-gradient(90deg, rgba(100,0,255,.065) 1px, transparent 1px);
  background-size: 58px 58px;
  animation: ndGP 6s ease-in-out infinite;
}
@keyframes ndGP { 0%,100%{opacity:.35;} 50%{opacity:.8;} }

.nd-orb { position:fixed; border-radius:50%; filter:blur(100px); pointer-events:none; z-index:0; animation:ndOD linear infinite; }
.nd-o1 { width:460px;height:460px;background:rgba(110,0,240,.26);top:-170px;left:-150px;animation-duration:23s; }
.nd-o2 { width:380px;height:380px;background:rgba(0,200,140,.18);bottom:-130px;right:-130px;animation-duration:29s;animation-delay:-11s; }
.nd-o3 { width:280px;height:280px;background:rgba(210,0,80,.14);top:40%;left:55%;animation-duration:20s;animation-delay:-6s; }
@keyframes ndOD {
  0%{transform:translate(0,0) scale(1);}
  33%{transform:translate(42px,-56px) scale(1.08);}
  66%{transform:translate(-32px,42px) scale(.93);}
  100%{transform:translate(0,0) scale(1);}
}
</style>
<div class="nd-bg"></div>
<div class="nd-grid"></div>
<div class="nd-orb nd-o1"></div>
<div class="nd-orb nd-o2"></div>
<div class="nd-orb nd-o3"></div>
""")

# Nav
st.html("""
<style>
.nd-nav {
  position: relative; z-index: 10;
  display: flex; align-items: center; justify-content: space-between;
  max-width: 1200px; margin: 0 auto;
  padding: 32px 40px 0;
  animation: ndFD .7s ease both;
}
@keyframes ndFD { from{opacity:0;transform:translateY(-18px);} to{opacity:1;transform:translateY(0);} }
.nd-logo {
  font-family:'Bebas Neue',sans-serif; font-size:28px; letter-spacing:5px;
  background:linear-gradient(135deg,#00DFA0,#6B00F0,#E0005A);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.nd-pill {
  font-family:'JetBrains Mono',monospace; font-size:11px; color:#00DFA0;
  letter-spacing:2px; border:1px solid rgba(0,223,160,.3);
  padding:5px 14px; border-radius:20px; background:rgba(0,223,160,.06);
}
</style>
<nav class="nd-nav">
  <div class="nd-logo">NeuralDoc</div>
  <div class="nd-pill">PRODUCTION RAG v1.0</div>
</nav>
""")

# Hero
st.html("""
<style>
.nd-hero {
  position: relative; z-index: 10;
  max-width: 960px; margin: 0 auto;
  padding: 64px 40px 0;
  text-align: center;
  animation: ndFU .9s ease .2s both;
}
@keyframes ndFU { from{opacity:0;transform:translateY(36px);} to{opacity:1;transform:translateY(0);} }
.nd-eyebrow {
  display: inline-flex; align-items:center; gap:8px;
  font-family:'JetBrains Mono',monospace; font-size:11px;
  color:#E0005A; letter-spacing:2.5px;
  border:1px solid rgba(224,0,90,.3); background:rgba(224,0,90,.07);
  padding:6px 18px; border-radius:30px; margin-bottom:28px;
  animation:ndEG 3.5s ease-in-out infinite;
}
@keyframes ndEG { 0%,100%{box-shadow:none;} 50%{box-shadow:0 0 18px rgba(224,0,90,.3);} }
.nd-dot {
  width:6px; height:6px; border-radius:50%; background:#E0005A;
  animation:ndDB 1.6s ease-in-out infinite;
}
@keyframes ndDB { 0%,100%{opacity:1;} 50%{opacity:.15;} }
.nd-h1 {
  font-family:'Bebas Neue',sans-serif;
  font-size: clamp(68px, 10.5vw, 118px);
  line-height:.9; letter-spacing:3px; color:#fff; margin:0;
}
.nd-t1 {
  background:linear-gradient(90deg,#6B00F0,#E0005A);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  display:inline-block;
  animation:ndT1S 5s ease-in-out infinite alternate;
}
@keyframes ndT1S { from{filter:hue-rotate(0deg);} to{filter:hue-rotate(28deg);} }
.nd-t2 {
  background:linear-gradient(90deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  display:inline-block;
}
.nd-desc {
  font-family:'Syne',sans-serif;
  font-size:17px; color:rgba(255,255,255,.5);
  max-width:560px; margin:22px auto 0; line-height:1.8;
}
.nd-desc strong { color:#00DFA0; font-weight:700; }
</style>
<div class="nd-hero">
  <div class="nd-eyebrow"><span class="nd-dot"></span>&nbsp;ZERO HALLUCINATION TOLERANCE</div>
  <h1 class="nd-h1">
    <span class="nd-t1">NEURAL</span><br>
    <span class="nd-t2">DOC</span> RAG
  </h1>
  <p class="nd-desc">
    A <strong>production-grade</strong> RAG system that answers questions
    from your documents with <strong>inline citations</strong>, hybrid
    retrieval, and a hard refusal trigger &mdash; no guessing, ever.
  </p>
</div>
""")

# CTA Buttons
st.html("""
<style>
.nd-cta-wrap {
  position: relative; z-index: 10;
  display: flex; justify-content: center; align-items: center;
  gap: 14px; flex-wrap: wrap;
  padding: 40px 40px 0;
}
/* Override Streamlit button style */
.nd-cta-wrap [data-testid="stButton"] > button {
  padding: 15px 44px !important;
  font-family: 'Syne', sans-serif !important;
  font-size: 16px !important; font-weight: 700 !important;
  border-radius: 50px !important; letter-spacing: .5px !important;
  background: linear-gradient(135deg,#6B00F0,#E0005A) !important;
  color: #fff !important; border: none !important;
  box-shadow: 0 0 40px rgba(107,0,240,.52) !important;
  animation: ndBG 3s ease-in-out infinite !important;
  transition: transform .3s !important;
  min-width: 180px !important;
}
@keyframes ndBG {
  0%,100%{box-shadow:0 0 40px rgba(107,0,240,.52);}
  50%{box-shadow:0 0 65px rgba(107,0,240,.78);}
}
.nd-cta-wrap [data-testid="stButton"] > button:hover {
  transform: translateY(-4px) scale(1.03) !important;
}
</style>
<div class="nd-cta-wrap" id="nd-cta"></div>
""")

cta1, cta2, cta3 = st.columns([2, 1, 2])
with cta2:
    if st.button("Launch App →", key="launch", use_container_width=True):
        st.switch_page("pages/RAG_Chat.py")

# Stats bar
st.html("""
<style>
.nd-stats {
  position: relative; z-index: 10;
  display: flex; max-width: 860px; margin: 52px auto 0;
  border: 1px solid rgba(255,255,255,.07); border-radius: 18px;
  overflow: hidden; background: rgba(255,255,255,.022);
  animation: ndFU .9s ease .4s both;
}
.nd-stat {
  flex:1; padding:26px 16px; text-align:center;
  border-right:1px solid rgba(255,255,255,.06);
  transition:background .3s;
}
.nd-stat:last-child { border-right:none; }
.nd-stat:hover { background:rgba(107,0,240,.1); }
.nd-sv {
  font-family:'Bebas Neue',sans-serif; font-size:44px; letter-spacing:2px;
  background:linear-gradient(135deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.nd-sl {
  font-family:'JetBrains Mono',monospace; font-size:10px;
  color:rgba(255,255,255,.35); letter-spacing:2.5px;
  text-transform:uppercase; margin-top:4px;
}
</style>
<div class="nd-stats">
  <div class="nd-stat"><div class="nd-sv">0%</div><div class="nd-sl">Hallucination Rate</div></div>
  <div class="nd-stat"><div class="nd-sv">3x</div><div class="nd-sl">Retrieval Methods</div></div>
  <div class="nd-stat"><div class="nd-sv">100%</div><div class="nd-sl">Local &amp; Private</div></div>
  <div class="nd-stat"><div class="nd-sv">inf</div><div class="nd-sl">Documents Supported</div></div>
</div>
""")

# Feature Cards
st.html("""
<style>
.nd-section {
  position:relative; z-index:10;
  max-width:1200px; margin:80px auto 0; padding:0 40px;
}
.nd-stag {
  font-family:'JetBrains Mono',monospace; font-size:11px;
  color:#6B00F0; letter-spacing:4px; text-transform:uppercase; margin-bottom:10px;
}
.nd-sh {
  font-family:'Bebas Neue',sans-serif; font-size:50px;
  letter-spacing:2px; color:#fff; line-height:1; margin-bottom:40px;
}
.nd-sh span {
  background:linear-gradient(90deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.nd-cards {
  display:grid; grid-template-columns:repeat(auto-fit,minmax(258px,1fr)); gap:16px;
}
.nd-card {
  padding:26px; background:rgba(255,255,255,.025);
  border:1px solid rgba(255,255,255,.07); border-radius:16px;
  transition:transform .4s,border-color .4s,box-shadow .4s;
}
.nd-card:hover {
  transform:translateY(-7px);
  border-color:rgba(107,0,240,.35);
  box-shadow:0 14px 44px rgba(107,0,240,.14);
}
.nd-cn {
  font-family:'JetBrains Mono',monospace; font-size:11px;
  letter-spacing:2px; color:rgba(255,255,255,.22); margin-bottom:12px;
}
.nd-ct { font-family:'Syne',sans-serif; font-size:16px; font-weight:800; color:#fff; margin-bottom:8px; }
.nd-cb { font-family:'Syne',sans-serif; font-size:13px; color:rgba(255,255,255,.42); line-height:1.75; }
.nd-ctch {
  display:inline-block; margin-top:12px;
  font-family:'JetBrains Mono',monospace; font-size:10px;
  padding:3px 10px; border-radius:20px; letter-spacing:1px;
}
</style>
<div class="nd-section" id="features">
  <div class="nd-stag">// Capabilities</div>
  <div class="nd-sh">SIX <span>PILLARS</span></div>
  <div class="nd-cards">
    <div class="nd-card">
      <div class="nd-cn">01 &mdash; INGESTION</div>
      <div class="nd-ct">Smart PDF Parsing</div>
      <div class="nd-cb">Handles multi-column layouts, embedded tables, and complex structures. Headers and footers stripped automatically.</div>
      <span class="nd-ctch" style="color:#00DFA0;background:rgba(0,223,160,.07);border:1px solid rgba(0,223,160,.2)">pdfplumber</span>
    </div>
    <div class="nd-card">
      <div class="nd-cn">02 &mdash; CHUNKING</div>
      <div class="nd-ct">Semantic Chunking</div>
      <div class="nd-cb">Header-aware chunks of 500&ndash;800 tokens. Every chunk carries source, page, and section breadcrumb as metadata.</div>
      <span class="nd-ctch" style="color:#6B00F0;background:rgba(107,0,240,.07);border:1px solid rgba(107,0,240,.2)">tiktoken</span>
    </div>
    <div class="nd-card">
      <div class="nd-cn">03 &mdash; RETRIEVAL</div>
      <div class="nd-ct">Hybrid Search</div>
      <div class="nd-cb">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion. Catches what either method alone misses.</div>
      <span class="nd-ctch" style="color:#E0005A;background:rgba(224,0,90,.07);border:1px solid rgba(224,0,90,.2)">RRF Fusion</span>
    </div>
    <div class="nd-card">
      <div class="nd-cn">04 &mdash; RERANKING</div>
      <div class="nd-ct">Cross-Encoder Precision</div>
      <div class="nd-cb">Top 20 candidates re-scored by a cross-encoder. Only the highest-confidence 5 reach the generation layer.</div>
      <span class="nd-ctch" style="color:#F0A800;background:rgba(240,168,0,.07);border:1px solid rgba(240,168,0,.2)">ms-marco</span>
    </div>
    <div class="nd-card">
      <div class="nd-cn">05 &mdash; GENERATION</div>
      <div class="nd-ct">Attributed Answers</div>
      <div class="nd-cb">Every claim carries an inline citation [Source, p.X]. A full References section is appended to every response.</div>
      <span class="nd-ctch" style="color:#00AAFF;background:rgba(0,170,255,.07);border:1px solid rgba(0,170,255,.2)">LangGraph</span>
    </div>
    <div class="nd-card">
      <div class="nd-cn">06 &mdash; SAFETY</div>
      <div class="nd-ct">Hard Refusal Gate</div>
      <div class="nd-cb">Context below the confidence threshold triggers a fixed refusal string. No speculation, no hallucination, by design.</div>
      <span class="nd-ctch" style="color:#FF6030;background:rgba(255,96,48,.07);border:1px solid rgba(255,96,48,.2)">Threshold Gate</span>
    </div>
  </div>
</div>
""")

# Pipeline
st.html("""
<style>
.nd-pipe-wrap { position:relative; z-index:10; max-width:1200px; margin:80px auto 0; padding:0 40px; }
.nd-pipe {
  display:flex; align-items:center; justify-content:center;
  flex-wrap:wrap; padding:40px;
  background:rgba(255,255,255,.018);
  border:1px solid rgba(255,255,255,.06); border-radius:18px;
}
.nd-step {
  display:flex; flex-direction:column; align-items:center; gap:8px;
  padding:16px 18px;
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.08); border-radius:12px;
  min-width:86px; transition:all .3s;
}
.nd-step:hover {
  background:rgba(107,0,240,.18); border-color:rgba(107,0,240,.45);
  transform:translateY(-5px); box-shadow:0 12px 36px rgba(107,0,240,.2);
}
.nd-si { font-family:'Bebas Neue',sans-serif; font-size:12px; letter-spacing:1px; color:rgba(255,255,255,.65); }
.nd-slb { font-family:'JetBrains Mono',monospace; font-size:10px; color:rgba(255,255,255,.38); letter-spacing:1px; }
.nd-arr {
  color:rgba(255,255,255,.15); font-size:16px; padding:0 4px; flex-shrink:0;
  animation:ndAP 2.4s ease-in-out infinite;
}
.nd-arr:nth-child(even) { animation-delay:.6s; }
@keyframes ndAP { 0%,100%{color:rgba(255,255,255,.12);} 50%{color:rgba(0,223,160,.7);} }
</style>
<div class="nd-pipe-wrap">
  <div class="nd-stag">// Architecture</div>
  <div class="nd-sh">THE <span>PIPELINE</span></div>
  <div class="nd-pipe">
    <div class="nd-step"><div class="nd-si">PDF</div><div class="nd-slb">Parse</div></div>
    <div class="nd-arr">&rarr;</div>
    <div class="nd-step"><div class="nd-si">SPLIT</div><div class="nd-slb">Chunk</div></div>
    <div class="nd-arr">&rarr;</div>
    <div class="nd-step"><div class="nd-si">EMBED</div><div class="nd-slb">Vector</div></div>
    <div class="nd-arr">&rarr;</div>
    <div class="nd-step"><div class="nd-si">BM25</div><div class="nd-slb">Keyword</div></div>
    <div class="nd-arr">&rarr;</div>
    <div class="nd-step"><div class="nd-si">RRF</div><div class="nd-slb">Fuse</div></div>
    <div class="nd-arr">&rarr;</div>
    <div class="nd-step"><div class="nd-si">RANK</div><div class="nd-slb">Rerank</div></div>
    <div class="nd-arr">&rarr;</div>
    <div class="nd-step"><div class="nd-si">LLM</div><div class="nd-slb">Generate</div></div>
    <div class="nd-arr">&rarr;</div>
    <div class="nd-step"><div class="nd-si">CITE</div><div class="nd-slb">Attribute</div></div>
  </div>
</div>
""")

# Tech Stack 
st.html("""
<style>
.nd-stack-wrap { position:relative; z-index:10; max-width:1200px; margin:80px auto 0; padding:0 40px; }
.nd-tags { display:flex; flex-wrap:wrap; gap:10px; }
.nd-tag {
  padding:7px 15px;
  font-family:'JetBrains Mono',monospace; font-size:11px;
  border-radius:30px; border:1px solid; letter-spacing:1px;
  transition:transform .3s; cursor:default;
}
.nd-tag:hover { transform:translateY(-2px); }
.nd-tg { color:#00DFA0; border-color:rgba(0,223,160,.3); background:rgba(0,223,160,.06); }
.nd-tp { color:#6B00F0; border-color:rgba(107,0,240,.3); background:rgba(107,0,240,.06); }
.nd-tr { color:#E0005A; border-color:rgba(224,0,90,.3); background:rgba(224,0,90,.06); }
.nd-ty { color:#F0A800; border-color:rgba(240,168,0,.3); background:rgba(240,168,0,.06); }
</style>
<div class="nd-stack-wrap">
  <div class="nd-stag">// Stack</div>
  <div class="nd-sh">BUILT <span>WITH</span></div>
  <div class="nd-tags">
    <span class="nd-tag nd-tg">pdfplumber</span>
    <span class="nd-tag nd-tg">ChromaDB</span>
    <span class="nd-tag nd-tg">sentence-transformers</span>
    <span class="nd-tag nd-tp">LangGraph</span>
    <span class="nd-tag nd-tp">langchain-ollama</span>
    <span class="nd-tag nd-tp">llama3.1:8b</span>
    <span class="nd-tag nd-tr">BM25 + RRF</span>
    <span class="nd-tag nd-tr">cross-encoder reranker</span>
    <span class="nd-tag nd-ty">FastAPI</span>
    <span class="nd-tag nd-ty">Streamlit</span>
    <span class="nd-tag nd-ty">Python 3.14</span>
  </div>
</div>
""")

# Footer 
st.html("""
<style>
.nd-foot {
  position:relative; z-index:10;
  max-width:1200px; margin:72px auto 0; padding:24px 40px 60px;
  border-top:1px solid rgba(255,255,255,.06);
  display:flex; justify-content:space-between;
  align-items:center; flex-wrap:wrap; gap:12px;
}
.nd-foot span {
  font-family:'JetBrains Mono',monospace; font-size:11px;
  color:rgba(255,255,255,.22);
}
</style>
<div class="nd-foot">
  <span>NeuralDoc &mdash; Production RAG System</span>
  <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
</div>
""")
