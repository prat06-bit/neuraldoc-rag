"""Landing page — NeuralDoc RAG"""
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NeuralDoc RAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit chrome
st.markdown("""
<style>
[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="collapsedControl"],#MainMenu,footer,
section[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
[data-testid="stAppViewContainer"]{background:#020008!important;}
iframe{border:none!important;}
</style>
""", unsafe_allow_html=True)

components.html("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{min-height:100%;background:#020008;font-family:'Syne',sans-serif;color:#fff;overflow-x:hidden;}

body::after{
  content:'';position:fixed;inset:0;z-index:0;
  background:
    radial-gradient(ellipse 75% 60% at 15% 15%,rgba(120,0,255,.28) 0%,transparent 55%),
    radial-gradient(ellipse 60% 75% at 85% 85%,rgba(0,255,178,.2) 0%,transparent 55%),
    radial-gradient(ellipse 50% 50% at 50% 50%,rgba(255,0,120,.1) 0%,transparent 65%);
  animation:meshAnim 14s ease-in-out infinite alternate;
  pointer-events:none;
}
@keyframes meshAnim{0%{filter:hue-rotate(0deg);}50%{filter:hue-rotate(25deg) brightness(1.1);}100%{filter:hue-rotate(-20deg);}}

.grid{position:fixed;inset:0;z-index:0;
  background-image:linear-gradient(rgba(123,0,255,.08) 1px,transparent 1px),linear-gradient(90deg,rgba(123,0,255,.08) 1px,transparent 1px);
  background-size:60px 60px;animation:gridP 5s ease-in-out infinite;pointer-events:none;}
@keyframes gridP{0%,100%{opacity:.4;}50%{opacity:.9;}}

.orb{position:fixed;border-radius:50%;filter:blur(90px);opacity:.32;pointer-events:none;z-index:0;animation:orbF linear infinite;}
.o1{width:520px;height:520px;background:#7B00FF;top:-200px;left:-200px;animation-duration:22s;}
.o2{width:440px;height:440px;background:#00FFB2;bottom:-160px;right:-160px;animation-duration:28s;animation-delay:-10s;}
.o3{width:340px;height:340px;background:#FF0080;top:38%;left:57%;animation-duration:20s;animation-delay:-5s;}
@keyframes orbF{0%{transform:translate(0,0) scale(1);}33%{transform:translate(50px,-70px) scale(1.1);}66%{transform:translate(-40px,50px) scale(.92);}100%{transform:translate(0,0) scale(1);}}

.wrap{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;padding:0 32px 100px;}

/* NAV */
nav{width:100%;max-width:1200px;display:flex;align-items:center;justify-content:space-between;padding:32px 0 0;animation:slideD .7s ease both;}
@keyframes slideD{from{opacity:0;transform:translateY(-24px);}to{opacity:1;transform:translateY(0);}}
.logo{font-family:'Bebas Neue',sans-serif;font-size:30px;letter-spacing:4px;background:linear-gradient(135deg,#00FFB2,#7B00FF,#FF0080);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.badge{font-family:'JetBrains Mono',monospace;font-size:11px;color:#00FFB2;border:1px solid rgba(0,255,178,.35);padding:5px 14px;border-radius:20px;background:rgba(0,255,178,.06);letter-spacing:2px;}

/* HERO */
.hero{width:100%;max-width:960px;text-align:center;padding:72px 0 48px;animation:heroU .9s ease .15s both;}
@keyframes heroU{from{opacity:0;transform:translateY(44px);}to{opacity:1;transform:translateY(0);}}
.pill{display:inline-flex;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#FF0080;border:1px solid rgba(255,0,128,.35);background:rgba(255,0,128,.07);padding:6px 18px;border-radius:30px;margin-bottom:28px;letter-spacing:2px;animation:pillG 3s ease-in-out infinite;}
@keyframes pillG{0%,100%{box-shadow:0 0 0 rgba(255,0,128,0);}50%{box-shadow:0 0 22px rgba(255,0,128,.35);}}
.dot{width:6px;height:6px;border-radius:50%;background:#FF0080;display:inline-block;animation:dotB 1.6s ease-in-out infinite;}
@keyframes dotB{0%,100%{opacity:1;}50%{opacity:.15;}}
h1{font-family:'Bebas Neue',sans-serif;font-size:clamp(72px,11vw,130px);line-height:.88;letter-spacing:3px;color:#fff;}
.g1{background:linear-gradient(90deg,#7B00FF,#FF0080);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;animation:g1s 5s ease-in-out infinite alternate;}
.g2{background:linear-gradient(90deg,#00FFB2,#7B00FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;}
@keyframes g1s{from{filter:hue-rotate(0deg);}to{filter:hue-rotate(35deg);}}
.sub{font-size:17px;color:rgba(255,255,255,.5);max-width:580px;margin:24px auto 0;line-height:1.75;}
.sub b{color:#00FFB2;font-weight:700;}

/* CTA */
.cta{margin-top:48px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap;}
.btn{display:inline-block;padding:15px 42px;font-family:'Syne',sans-serif;font-size:15px;font-weight:700;border-radius:50px;text-decoration:none;letter-spacing:.5px;transition:transform .3s,box-shadow .3s;cursor:pointer;}
.btn-p{background:linear-gradient(135deg,#7B00FF,#FF0080);color:#fff;box-shadow:0 0 40px rgba(123,0,255,.45);animation:bP 3s ease-in-out infinite;}
@keyframes bP{0%,100%{box-shadow:0 0 40px rgba(123,0,255,.45);}50%{box-shadow:0 0 65px rgba(123,0,255,.75);}}
.btn-p:hover{transform:translateY(-4px) scale(1.04);}
.btn-s{background:transparent;color:rgba(255,255,255,.65);border:1px solid rgba(255,255,255,.18);}
.btn-s:hover{border-color:rgba(0,255,178,.55);color:#00FFB2;transform:translateY(-4px);}

/* STATS */
.stats{display:flex;width:100%;max-width:880px;margin:64px 0 0;border:1px solid rgba(255,255,255,.08);border-radius:20px;overflow:hidden;background:rgba(255,255,255,.025);backdrop-filter:blur(24px);animation:fU .9s ease .35s both;}
@keyframes fU{from{opacity:0;transform:translateY(32px);}to{opacity:1;transform:translateY(0);}}
.stat{flex:1;padding:28px 16px;text-align:center;border-right:1px solid rgba(255,255,255,.07);transition:background .35s;}
.stat:last-child{border-right:none;}
.stat:hover{background:rgba(123,0,255,.1);}
.stat-n{font-family:'Bebas Neue',sans-serif;font-size:44px;letter-spacing:2px;background:linear-gradient(135deg,#00FFB2,#7B00FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stat-l{font-size:11px;color:rgba(255,255,255,.38);letter-spacing:2.5px;text-transform:uppercase;margin-top:3px;font-family:'JetBrains Mono',monospace;}

/* SECTION */
.sec{width:100%;max-width:1200px;margin-top:96px;}
.sec-tag{font-family:'JetBrains Mono',monospace;font-size:11px;color:#7B00FF;letter-spacing:4px;text-transform:uppercase;margin-bottom:12px;}
.sec-h{font-family:'Bebas Neue',sans-serif;font-size:52px;letter-spacing:2px;color:#fff;line-height:1;margin-bottom:48px;}
.sec-h span{background:linear-gradient(90deg,#00FFB2,#7B00FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}

/* CARDS */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px;}
.card{padding:30px;background:rgba(255,255,255,.028);border:1px solid rgba(255,255,255,.07);border-radius:20px;transition:transform .4s,border-color .4s,box-shadow .4s;animation:cIn .7s ease both;}
.card:nth-child(1){animation-delay:.05s;}.card:nth-child(2){animation-delay:.12s;}.card:nth-child(3){animation-delay:.19s;}
.card:nth-child(4){animation-delay:.26s;}.card:nth-child(5){animation-delay:.33s;}.card:nth-child(6){animation-delay:.40s;}
@keyframes cIn{from{opacity:0;transform:translateY(28px);}to{opacity:1;transform:translateY(0);}}
.card:hover{transform:translateY(-8px);border-color:rgba(123,0,255,.35);box-shadow:0 16px 50px rgba(123,0,255,.15);}
.ci{font-size:30px;margin-bottom:14px;display:inline-block;width:52px;height:52px;line-height:52px;text-align:center;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);border-radius:14px;}
.ct{font-family:'Syne',sans-serif;font-size:17px;font-weight:800;color:#fff;margin-bottom:8px;}
.cd{font-size:13px;color:rgba(255,255,255,.42);line-height:1.7;}
.cb{display:inline-block;margin-top:14px;font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:20px;letter-spacing:1px;}

/* PIPELINE */
.pipe{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:0;padding:44px;background:rgba(255,255,255,.018);border:1px solid rgba(255,255,255,.07);border-radius:22px;}
.ps{display:flex;flex-direction:column;align-items:center;gap:8px;padding:18px 20px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:14px;min-width:100px;transition:all .3s;}
.ps:hover{background:rgba(123,0,255,.18);border-color:rgba(123,0,255,.45);transform:translateY(-5px);box-shadow:0 14px 40px rgba(123,0,255,.22);}
.pi{font-size:26px;}.pl{font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,.48);text-align:center;letter-spacing:1px;}
.pa{color:rgba(255,255,255,.18);font-size:18px;padding:0 6px;flex-shrink:0;animation:aP 2.2s ease-in-out infinite;}
.pa:nth-child(even){animation-delay:.55s;}
@keyframes aP{0%,100%{color:rgba(255,255,255,.15);}50%{color:rgba(0,255,178,.65);}}

/* TECH */
.tech{display:flex;flex-wrap:wrap;gap:10px;}
.tt{padding:7px 16px;font-family:'JetBrains Mono',monospace;font-size:11px;border-radius:30px;border:1px solid;letter-spacing:1px;transition:transform .3s;}
.tt:hover{transform:translateY(-2px);}
.t1{color:#00FFB2;border-color:rgba(0,255,178,.3);background:rgba(0,255,178,.06);}
.t2{color:#7B00FF;border-color:rgba(123,0,255,.3);background:rgba(123,0,255,.06);}
.t3{color:#FF0080;border-color:rgba(255,0,128,.3);background:rgba(255,0,128,.06);}
.t4{color:#FFB800;border-color:rgba(255,184,0,.3);background:rgba(255,184,0,.06);}

/* FOOTER */
.foot{width:100%;max-width:1200px;margin-top:100px;padding-top:28px;border-top:1px solid rgba(255,255,255,.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;}
.foot span{font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,.22);}
</style>
</head>
<body>

<div class="grid"></div>
<div class="orb o1"></div>
<div class="orb o2"></div>
<div class="orb o3"></div>

<div class="wrap">
  <nav>
    <div class="logo">NeuralDoc</div>
    <div class="badge">&#9889; PRODUCTION RAG v1.0</div>
  </nav>

  <section class="hero">
    <div class="pill"><span class="dot"></span>&nbsp;ZERO HALLUCINATION TOLERANCE</div>
    <h1><span class="g1">NEURAL</span><br><span class="g2">DOC</span> RAG</h1>
    <p class="sub">A <b>production-grade</b> RAG system that answers questions from your documents with <b>inline citations</b>, hybrid retrieval, and a hard refusal trigger &mdash; no guessing, ever.</p>
    <div class="cta">
      <a href="http://localhost:8501/RAG_Chat" class="btn btn-p">&#9889; Launch App &rarr;</a>
      <a href="#features" class="btn btn-s">How It Works &darr;</a>
    </div>
  </section>

  <div class="stats">
    <div class="stat"><div class="stat-n">0%</div><div class="stat-l">Hallucination</div></div>
    <div class="stat"><div class="stat-n">3&times;</div><div class="stat-l">Retrieval Methods</div></div>
    <div class="stat"><div class="stat-n">100%</div><div class="stat-l">Local &amp; Private</div></div>
    <div class="stat"><div class="stat-n">&infin;</div><div class="stat-l">Documents</div></div>
  </div>

  <section class="sec" id="features">
    <div class="sec-tag">// What It Does</div>
    <div class="sec-h">SIX <span>PILLARS</span></div>
    <div class="cards">
      <div class="card"><div class="ci">&#128196;</div><div class="ct">Smart PDF Ingestion</div><div class="cd">Handles multi-column layouts, embedded tables, complex PDFs. Strips headers and footers automatically.</div><span class="cb" style="color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2)">pdfplumber</span></div>
      <div class="card"><div class="ci">&#9986;&#65039;</div><div class="ct">Semantic Chunking</div><div class="cd">Header-aware 500&ndash;800 token chunks. Every chunk carries source, page, and breadcrumb metadata.</div><span class="cb" style="color:#7B00FF;background:rgba(123,0,255,.08);border:1px solid rgba(123,0,255,.2)">tiktoken</span></div>
      <div class="card"><div class="ci">&#128269;</div><div class="ct">Hybrid Retrieval</div><div class="cd">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion &mdash; catches what either misses.</div><span class="cb" style="color:#FF0080;background:rgba(255,0,128,.08);border:1px solid rgba(255,0,128,.2)">RRF Fusion</span></div>
      <div class="card"><div class="ci">&#127942;</div><div class="ct">Cross-Encoder Reranking</div><div class="cd">Top-20 candidates re-scored with a cross-encoder. Only the best 5 reach the LLM &mdash; precision over recall.</div><span class="cb" style="color:#FFB800;background:rgba(255,184,0,.08);border:1px solid rgba(255,184,0,.2)">ms-marco</span></div>
      <div class="card"><div class="ci">&#128206;</div><div class="ct">Attributed QA</div><div class="cd">Every claim has an inline citation [Source, p.X]. A References section is auto-appended. Always grounded.</div><span class="cb" style="color:#00C8FF;background:rgba(0,200,255,.08);border:1px solid rgba(0,200,255,.2)">LangGraph</span></div>
      <div class="card"><div class="ci">&#128683;</div><div class="ct">Hard Refusal Trigger</div><div class="cd">Insufficient context returns a fixed refusal &mdash; not a guess. Zero hallucination is a hard system constraint.</div><span class="cb" style="color:#FF5000;background:rgba(255,80,0,.08);border:1px solid rgba(255,80,0,.2)">Threshold Gate</span></div>
    </div>
  </section>

  <section class="sec">
    <div class="sec-tag">// Architecture</div>
    <div class="sec-h">THE <span>PIPELINE</span></div>
    <div class="pipe">
      <div class="ps"><div class="pi">&#128196;</div><div class="pl">PDF Parse</div></div><div class="pa">&rarr;</div>
      <div class="ps"><div class="pi">&#9986;&#65039;</div><div class="pl">Chunk</div></div><div class="pa">&rarr;</div>
      <div class="ps"><div class="pi">&#129504;</div><div class="pl">Embed</div></div><div class="pa">&rarr;</div>
      <div class="ps"><div class="pi">&#128269;</div><div class="pl">Retrieve</div></div><div class="pa">&rarr;</div>
      <div class="ps"><div class="pi">&#127942;</div><div class="pl">Rerank</div></div><div class="pa">&rarr;</div>
      <div class="ps"><div class="pi">&#9889;</div><div class="pl">Generate</div></div><div class="pa">&rarr;</div>
      <div class="ps"><div class="pi">&#128206;</div><div class="pl">Cite</div></div>
    </div>
  </section>

  <section class="sec">
    <div class="sec-tag">// Tech Stack</div>
    <div class="sec-h">BUILT <span>WITH</span></div>
    <div class="tech">
      <span class="tt t1">pdfplumber</span><span class="tt t1">ChromaDB</span><span class="tt t1">sentence-transformers</span>
      <span class="tt t2">LangGraph</span><span class="tt t2">langchain-ollama</span><span class="tt t2">llama3.1:8b</span>
      <span class="tt t3">BM25 + RRF</span><span class="tt t3">cross-encoder</span>
      <span class="tt t4">FastAPI</span><span class="tt t4">Streamlit</span><span class="tt t4">Python 3.14</span>
    </div>
  </section>

  <footer class="foot">
    <span>NeuralDoc RAG &mdash; Production Grade</span>
    <span>Built with Ollama &middot; ChromaDB &middot; LangGraph</span>
  </footer>
</div>

</body>
</html>
""", height=4200, scrolling=True)