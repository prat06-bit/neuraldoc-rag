"""Landing page — NeuralDoc RAG"""
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NeuralDoc RAG",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide all Streamlit chrome
st.markdown("""
<style>
[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="collapsedControl"],#MainMenu,footer,
section[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{
  background:#030010!important;}
/* Style the page_link button to look like our CTA */
[data-testid="stPageLink"] a {
  display:inline-block!important;
  padding:14px 40px!important;
  background:linear-gradient(135deg,#6B00F0,#E0005A)!important;
  color:#fff!important;
  font-family:'Syne',sans-serif!important;
  font-size:16px!important;font-weight:700!important;
  border-radius:50px!important;
  text-decoration:none!important;
  letter-spacing:0.5px!important;
  box-shadow:0 0 40px rgba(107,0,240,0.5)!important;
  transition:transform 0.3s,box-shadow 0.3s!important;
  animation:btnGlow 3s ease-in-out infinite!important;
}
[data-testid="stPageLink"] a:hover{
  transform:translateY(-4px) scale(1.03)!important;
  box-shadow:0 0 60px rgba(107,0,240,0.75)!important;
}
@keyframes btnGlow{
  0%,100%{box-shadow:0 0 40px rgba(107,0,240,0.5);}
  50%{box-shadow:0 0 65px rgba(107,0,240,0.78);}
}
/* Center the launch button */
.launch-btn{
  display:flex;justify-content:center;align-items:center;
  gap:16px;
  position:relative;z-index:10;
  margin:-40px 0 0;
  padding-bottom:60px;
  background:#030010;
}
/* Remove iframe border and margin */
iframe{border:none!important;display:block!important;margin:0!important;}
/* Remove Streamlit's default element spacing */
[data-testid="stVerticalBlock"]>div{gap:0!important;}
</style>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ── Hero section via iframe (visual only, no nav button) ──────────────────────
hero_html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
html,body{background:#030010;font-family:'Syne',sans-serif;color:#fff;overflow:hidden;}

.bg{position:fixed;inset:0;pointer-events:none;
  background:
    radial-gradient(ellipse 70% 55% at 12% 12%,rgba(110,0,240,0.32) 0%,transparent 55%),
    radial-gradient(ellipse 55% 65% at 88% 88%,rgba(0,220,160,0.22) 0%,transparent 55%),
    radial-gradient(ellipse 45% 45% at 55% 45%,rgba(220,0,100,0.12) 0%,transparent 60%);
  animation:bgShift 16s ease-in-out infinite alternate;}
@keyframes bgShift{0%{filter:hue-rotate(0deg);}100%{filter:hue-rotate(22deg) brightness(1.08);}}

.grid{position:fixed;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(100,0,255,0.07) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(100,0,255,0.07) 1px,transparent 1px);
  background-size:56px 56px;animation:gridB 6s ease-in-out infinite;}
@keyframes gridB{0%,100%{opacity:0.4;}50%{opacity:0.85;}}

.orb{position:fixed;border-radius:50%;filter:blur(100px);pointer-events:none;animation:orbD linear infinite;}
.o1{width:480px;height:480px;background:rgba(110,0,240,0.28);top:-180px;left:-160px;animation-duration:24s;}
.o2{width:400px;height:400px;background:rgba(0,210,150,0.2);bottom:-140px;right:-140px;animation-duration:30s;animation-delay:-12s;}
.o3{width:300px;height:300px;background:rgba(220,0,90,0.16);top:42%;left:58%;animation-duration:21s;animation-delay:-7s;}
@keyframes orbD{0%{transform:translate(0,0) scale(1);}33%{transform:translate(44px,-60px) scale(1.08);}66%{transform:translate(-35px,44px) scale(0.93);}100%{transform:translate(0,0) scale(1);}}

.wrap{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:0 40px 72px;}

nav{display:flex;align-items:center;justify-content:space-between;padding:36px 0 0;animation:fadeD 0.7s ease both;}
@keyframes fadeD{from{opacity:0;transform:translateY(-20px);}to{opacity:1;transform:translateY(0);}}
.logo{font-family:'Bebas Neue',sans-serif;font-size:28px;letter-spacing:5px;
  background:linear-gradient(135deg,#00DFA0,#6B00F0,#E0005A);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.nav-tag{font-family:'JetBrains Mono',monospace;font-size:11px;color:#00DFA0;letter-spacing:2px;
  border:1px solid rgba(0,223,160,0.3);padding:5px 14px;border-radius:20px;background:rgba(0,223,160,0.06);}

.hero{padding:72px 0 20px;text-align:center;animation:fadeU 0.9s ease 0.2s both;}
@keyframes fadeU{from{opacity:0;transform:translateY(40px);}to{opacity:1;transform:translateY(0);}}
.eyebrow{display:inline-flex;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;
  font-size:11px;color:#E0005A;letter-spacing:2.5px;border:1px solid rgba(224,0,90,0.3);
  background:rgba(224,0,90,0.07);padding:6px 18px;border-radius:30px;margin-bottom:30px;
  animation:eyeG 3.5s ease-in-out infinite;}
@keyframes eyeG{0%,100%{box-shadow:none;}50%{box-shadow:0 0 20px rgba(224,0,90,0.3);}}
.dot{width:6px;height:6px;border-radius:50%;background:#E0005A;animation:dotB 1.6s ease-in-out infinite;}
@keyframes dotB{0%,100%{opacity:1;}50%{opacity:0.15;}}
h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(68px,10.5vw,124px);line-height:0.88;letter-spacing:3px;color:#fff;}
.tp{background:linear-gradient(90deg,#6B00F0,#E0005A);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;animation:tpS 5s ease-in-out infinite alternate;}
@keyframes tpS{from{filter:hue-rotate(0deg);}to{filter:hue-rotate(30deg);}}
.tt{background:linear-gradient(90deg,#00DFA0,#6B00F0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;}
.desc{font-size:17px;color:rgba(255,255,255,0.52);max-width:560px;margin:24px auto 0;line-height:1.8;}
.desc strong{color:#00DFA0;font-weight:700;}

/* Spacer for the Streamlit button below */
.cta-space{height:80px;}

.stats{display:flex;max-width:860px;margin:56px auto 0;border:1px solid rgba(255,255,255,0.07);border-radius:18px;overflow:hidden;background:rgba(255,255,255,0.022);backdrop-filter:blur(20px);animation:fadeU 0.9s ease 0.4s both;}
.stat{flex:1;padding:26px 16px;text-align:center;border-right:1px solid rgba(255,255,255,0.06);transition:background 0.3s;}
.stat:last-child{border-right:none;}.stat:hover{background:rgba(107,0,240,0.1);}
.stat-v{font-family:'Bebas Neue',sans-serif;font-size:44px;letter-spacing:2px;background:linear-gradient(135deg,#00DFA0,#6B00F0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stat-l{font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,0.35);letter-spacing:2.5px;text-transform:uppercase;margin-top:4px;}

.sec{margin-top:90px;}
.sec-tag{font-family:'JetBrains Mono',monospace;font-size:11px;color:#6B00F0;letter-spacing:4px;text-transform:uppercase;margin-bottom:10px;}
.sec-h{font-family:'Bebas Neue',sans-serif;font-size:50px;letter-spacing:2px;color:#fff;line-height:1;margin-bottom:44px;}
.sec-h span{background:linear-gradient(90deg,#00DFA0,#6B00F0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}

.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;}
.card{padding:26px;background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:16px;transition:transform 0.4s,border-color 0.4s,box-shadow 0.4s;}
.card:hover{transform:translateY(-7px);border-color:rgba(107,0,240,0.35);box-shadow:0 14px 44px rgba(107,0,240,0.14);}
.card-num{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:2px;color:rgba(255,255,255,0.22);margin-bottom:12px;}
.card-title{font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:#fff;margin-bottom:8px;}
.card-body{font-size:13px;color:rgba(255,255,255,0.42);line-height:1.75;}
.card-tech{display:inline-block;margin-top:12px;font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:20px;letter-spacing:1px;}

.pipeline{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;padding:40px;background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.06);border-radius:18px;gap:0;}
.step{display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 20px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;min-width:90px;transition:all 0.3s;}
.step:hover{background:rgba(107,0,240,0.18);border-color:rgba(107,0,240,0.45);transform:translateY(-5px);box-shadow:0 12px 36px rgba(107,0,240,0.2);}
.step-icon{font-family:'Bebas Neue',sans-serif;font-size:12px;letter-spacing:1px;color:rgba(255,255,255,0.65);}
.step-lbl{font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,0.4);letter-spacing:1px;}
.arr{color:rgba(255,255,255,0.15);font-size:16px;padding:0 5px;flex-shrink:0;animation:arrP 2.4s ease-in-out infinite;}
.arr:nth-child(even){animation-delay:0.6s;}
@keyframes arrP{0%,100%{color:rgba(255,255,255,0.12);}50%{color:rgba(0,223,160,0.7);}}

.tags{display:flex;flex-wrap:wrap;gap:10px;}
.tag{padding:7px 15px;font-family:'JetBrains Mono',monospace;font-size:11px;border-radius:30px;border:1px solid;letter-spacing:1px;transition:transform 0.3s;}
.tag:hover{transform:translateY(-2px);}
.tg{color:#00DFA0;border-color:rgba(0,223,160,0.3);background:rgba(0,223,160,0.06);}
.tp2{color:#6B00F0;border-color:rgba(107,0,240,0.3);background:rgba(107,0,240,0.06);}
.tr{color:#E0005A;border-color:rgba(224,0,90,0.3);background:rgba(224,0,90,0.06);}
.ty{color:#F0A800;border-color:rgba(240,168,0,0.3);background:rgba(240,168,0,0.06);}

.foot{margin-top:80px;padding-top:24px;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;}
.foot span{font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.22);}
</style>
</head>
<body>
<div class="bg"></div><div class="grid"></div>
<div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
<div class="wrap">
  <nav>
    <div class="logo">NeuralDoc</div>
    <div class="nav-tag">PRODUCTION RAG v1.0</div>
  </nav>
  <div class="hero">
    <div class="eyebrow"><span class="dot"></span>&nbsp;ZERO HALLUCINATION TOLERANCE</div>
    <h1><span class="tp">NEURAL</span><br><span class="tt">DOC</span> RAG</h1>
    <p class="desc">A <strong>production-grade</strong> RAG system that answers questions from your documents with <strong>inline citations</strong>, hybrid retrieval, and a hard refusal trigger &mdash; no guessing, ever.</p>
    <div class="cta-space"></div>
  </div>

  <div class="stats">
    <div class="stat"><div class="stat-v">0%</div><div class="stat-l">Hallucination Rate</div></div>
    <div class="stat"><div class="stat-v">3x</div><div class="stat-l">Retrieval Methods</div></div>
    <div class="stat"><div class="stat-v">100%</div><div class="stat-l">Local & Private</div></div>
    <div class="stat"><div class="stat-v">inf</div><div class="stat-l">Documents Supported</div></div>
  </div>

  <div class="sec">
    <div class="sec-tag">// Capabilities</div>
    <div class="sec-h">SIX <span>PILLARS</span></div>
    <div class="cards">
      <div class="card"><div class="card-num">01 &mdash; INGESTION</div><div class="card-title">Smart PDF Parsing</div><div class="card-body">Handles multi-column layouts, embedded tables, and complex document structures. Headers and footers stripped automatically.</div><span class="card-tech" style="color:#00DFA0;background:rgba(0,223,160,0.07);border:1px solid rgba(0,223,160,0.2)">pdfplumber</span></div>
      <div class="card"><div class="card-num">02 &mdash; CHUNKING</div><div class="card-title">Semantic Chunking</div><div class="card-body">Header-aware chunks of 500&ndash;800 tokens. Every chunk carries source path, page number, and section breadcrumb as metadata.</div><span class="card-tech" style="color:#6B00F0;background:rgba(107,0,240,0.07);border:1px solid rgba(107,0,240,0.2)">tiktoken</span></div>
      <div class="card"><div class="card-num">03 &mdash; RETRIEVAL</div><div class="card-title">Hybrid Search</div><div class="card-body">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion. Catches what either method alone misses.</div><span class="card-tech" style="color:#E0005A;background:rgba(224,0,90,0.07);border:1px solid rgba(224,0,90,0.2)">RRF Fusion</span></div>
      <div class="card"><div class="card-num">04 &mdash; RERANKING</div><div class="card-title">Cross-Encoder Precision</div><div class="card-body">Top 20 candidates re-scored with a cross-encoder model. Only the highest-confidence 5 reach the generation layer.</div><span class="card-tech" style="color:#F0A800;background:rgba(240,168,0,0.07);border:1px solid rgba(240,168,0,0.2)">ms-marco</span></div>
      <div class="card"><div class="card-num">05 &mdash; GENERATION</div><div class="card-title">Attributed Answers</div><div class="card-body">Every factual claim carries an inline citation [Source, p.X]. A full References section is appended to every response, always.</div><span class="card-tech" style="color:#00AAFF;background:rgba(0,170,255,0.07);border:1px solid rgba(0,170,255,0.2)">LangGraph</span></div>
      <div class="card"><div class="card-num">06 &mdash; SAFETY</div><div class="card-title">Hard Refusal Gate</div><div class="card-body">When retrieved context falls below the confidence threshold, the model issues a fixed refusal. No speculation, no hallucination.</div><span class="card-tech" style="color:#FF6030;background:rgba(255,96,48,0.07);border:1px solid rgba(255,96,48,0.2)">Threshold Gate</span></div>
    </div>
  </div>

  <div class="sec">
    <div class="sec-tag">// Architecture</div>
    <div class="sec-h">THE <span>PIPELINE</span></div>
    <div class="pipeline">
      <div class="step"><div class="step-icon">PDF</div><div class="step-lbl">Parse</div></div><div class="arr">&rarr;</div>
      <div class="step"><div class="step-icon">SPLIT</div><div class="step-lbl">Chunk</div></div><div class="arr">&rarr;</div>
      <div class="step"><div class="step-icon">EMBED</div><div class="step-lbl">Vector</div></div><div class="arr">&rarr;</div>
      <div class="step"><div class="step-icon">BM25</div><div class="step-lbl">Keyword</div></div><div class="arr">&rarr;</div>
      <div class="step"><div class="step-icon">RRF</div><div class="step-lbl">Fuse</div></div><div class="arr">&rarr;</div>
      <div class="step"><div class="step-icon">RANK</div><div class="step-lbl">Rerank</div></div><div class="arr">&rarr;</div>
      <div class="step"><div class="step-icon">LLM</div><div class="step-lbl">Generate</div></div><div class="arr">&rarr;</div>
      <div class="step"><div class="step-icon">CITE</div><div class="step-lbl">Attribute</div></div>
    </div>
  </div>

  <div class="sec">
    <div class="sec-tag">// Stack</div>
    <div class="sec-h">BUILT <span>WITH</span></div>
    <div class="tags">
      <span class="tag tg">pdfplumber</span><span class="tag tg">ChromaDB</span><span class="tag tg">sentence-transformers</span>
      <span class="tag tp2">LangGraph</span><span class="tag tp2">langchain-ollama</span><span class="tag tp2">llama3.1:8b</span>
      <span class="tag tr">BM25 + RRF</span><span class="tag tr">cross-encoder reranker</span>
      <span class="tag ty">FastAPI</span><span class="tag ty">Streamlit</span><span class="tag ty">Python 3.14</span>
    </div>
  </div>

  <div class="foot">
    <span>NeuralDoc &mdash; Production RAG System</span>
    <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
  </div>
</div>

<script>
// Auto-report actual content height to Streamlit so iframe fits perfectly
function sendHeight() {
  const h = document.body.scrollHeight;
  window.parent.postMessage({isStreamlitMessage: true, type: 'streamlit:setFrameHeight', height: h}, '*');
}
window.addEventListener('load', sendHeight);
window.addEventListener('resize', sendHeight);
setTimeout(sendHeight, 500);
setTimeout(sendHeight, 1500);
</script>
</body>
</html>"""

components.html(hero_html, height=2800, scrolling=False)

# ── Launch button — native Streamlit, works correctly ─────────────────────────
st.markdown("""
<style>
/* Pull the button up into the hero's CTA space */
.launch-wrap{
  display:flex;justify-content:center;align-items:center;gap:14px;
  background:#030010;
  padding:0 0 0px;
  margin-top:-200px;
  position:relative;z-index:20;
}
[data-testid="stPageLink"]{margin:0!important;}
[data-testid="stPageLink"] a{
  display:inline-block!important;
  padding:15px 44px!important;
  background:linear-gradient(135deg,#6B00F0,#E0005A)!important;
  color:#fff!important;font-family:'Syne',sans-serif!important;
  font-size:16px!important;font-weight:700!important;
  border-radius:50px!important;text-decoration:none!important;
  letter-spacing:0.5px!important;
  box-shadow:0 0 42px rgba(107,0,240,0.52)!important;
  animation:glowBtn 3s ease-in-out infinite!important;
  transition:transform 0.3s!important;
}
[data-testid="stPageLink"] a:hover{transform:translateY(-4px) scale(1.03)!important;}
@keyframes glowBtn{
  0%,100%{box-shadow:0 0 42px rgba(107,0,240,0.52);}
  50%{box-shadow:0 0 66px rgba(107,0,240,0.8);}
}
</style>
<div class="launch-wrap">
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.page_link("pages/1_RAG_Chat.py", label="Launch App →")

st.markdown("</div>", unsafe_allow_html=True)