"""Landing page — NeuralDoc RAG System"""
import streamlit as st

st.set_page_config(
    page_title="NeuralDoc RAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
[data-testid="stAppViewContainer"]{background:#020008;font-family:'Syne',sans-serif;overflow-x:hidden;}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="collapsedControl"],section[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}

.bg-mesh{position:fixed;inset:0;z-index:0;
  background:radial-gradient(ellipse 80% 60% at 20% 20%,rgba(120,0,255,.18) 0%,transparent 60%),
             radial-gradient(ellipse 60% 80% at 80% 80%,rgba(0,255,180,.12) 0%,transparent 60%),
             radial-gradient(ellipse 50% 50% at 50% 50%,rgba(255,0,120,.08) 0%,transparent 70%),#020008;
  animation:meshShift 12s ease-in-out infinite alternate;}
@keyframes meshShift{0%{filter:hue-rotate(0deg) brightness(1);}50%{filter:hue-rotate(20deg) brightness(1.05);}100%{filter:hue-rotate(-15deg) brightness(.95);}}

.orb{position:fixed;border-radius:50%;filter:blur(80px);opacity:.35;z-index:0;animation:floatOrb linear infinite;}
.orb-1{width:500px;height:500px;background:#7B00FF;top:-100px;left:-150px;animation-duration:20s;}
.orb-2{width:400px;height:400px;background:#00FFB2;bottom:-100px;right:-100px;animation-duration:25s;animation-delay:-8s;}
.orb-3{width:300px;height:300px;background:#FF0080;top:40%;left:60%;animation-duration:18s;animation-delay:-4s;}
@keyframes floatOrb{0%{transform:translate(0,0) scale(1);}33%{transform:translate(40px,-60px) scale(1.1);}66%{transform:translate(-30px,40px) scale(.95);}100%{transform:translate(0,0) scale(1);}}

.grid-lines{position:fixed;inset:0;z-index:0;
  background-image:linear-gradient(rgba(123,0,255,.06) 1px,transparent 1px),linear-gradient(90deg,rgba(123,0,255,.06) 1px,transparent 1px);
  background-size:60px 60px;animation:gridPulse 6s ease-in-out infinite;}
@keyframes gridPulse{0%,100%{opacity:.5;}50%{opacity:1;}}

.page-wrap{position:relative;z-index:2;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:0 24px 80px;}

.nav{width:100%;max-width:1200px;display:flex;align-items:center;justify-content:space-between;padding:28px 0 0;animation:fadeDown .8s ease both;}
.nav-logo{font-family:'Bebas Neue',sans-serif;font-size:28px;letter-spacing:3px;background:linear-gradient(135deg,#00FFB2,#7B00FF,#FF0080);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.nav-badge{font-family:'JetBrains Mono',monospace;font-size:11px;color:#00FFB2;border:1px solid rgba(0,255,178,.3);padding:4px 12px;border-radius:20px;background:rgba(0,255,178,.05);letter-spacing:2px;}
@keyframes fadeDown{from{opacity:0;transform:translateY(-20px);}to{opacity:1;transform:translateY(0);}}

.hero{width:100%;max-width:1000px;text-align:center;padding:80px 0 60px;animation:heroReveal 1s ease .2s both;}
@keyframes heroReveal{from{opacity:0;transform:translateY(40px);}to{opacity:1;transform:translateY(0);}}
.hero-tag{display:inline-flex;align-items:center;gap:8px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#FF0080;border:1px solid rgba(255,0,128,.3);background:rgba(255,0,128,.07);padding:6px 18px;border-radius:30px;margin-bottom:32px;letter-spacing:2px;animation:tagPulse 3s ease-in-out infinite;}
@keyframes tagPulse{0%,100%{box-shadow:0 0 0 rgba(255,0,128,0);}50%{box-shadow:0 0 20px rgba(255,0,128,.3);}}
.tag-dot{width:6px;height:6px;border-radius:50%;background:#FF0080;display:inline-block;animation:blink 1.5s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.2;}}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(64px,10vw,120px);line-height:.9;letter-spacing:2px;color:#fff;margin-bottom:8px;}
.hero-title .a1{background:linear-gradient(90deg,#7B00FF,#FF0080);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;animation:gradShift 4s ease-in-out infinite alternate;}
.hero-title .a2{background:linear-gradient(90deg,#00FFB2,#7B00FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;display:inline-block;}
@keyframes gradShift{from{filter:hue-rotate(0deg);}to{filter:hue-rotate(30deg);}}
.hero-sub{font-size:18px;color:rgba(255,255,255,.55);max-width:600px;margin:28px auto 0;line-height:1.7;}
.hero-sub strong{color:#00FFB2;font-weight:700;}

.cta-wrap{margin-top:52px;display:flex;gap:16px;justify-content:center;flex-wrap:wrap;}
.btn-primary{display:inline-flex;align-items:center;gap:10px;padding:16px 40px;background:linear-gradient(135deg,#7B00FF,#FF0080);color:#fff;font-family:'Syne',sans-serif;font-size:16px;font-weight:700;border-radius:50px;text-decoration:none;box-shadow:0 0 40px rgba(123,0,255,.4);animation:btnGlow 3s ease-in-out infinite;letter-spacing:.5px;transition:transform .3s;}
@keyframes btnGlow{0%,100%{box-shadow:0 0 40px rgba(123,0,255,.4);}50%{box-shadow:0 0 70px rgba(123,0,255,.7);}}
.btn-primary:hover{transform:translateY(-3px) scale(1.03);}
.btn-secondary{display:inline-flex;align-items:center;gap:10px;padding:16px 40px;background:transparent;color:rgba(255,255,255,.7);font-family:'Syne',sans-serif;font-size:16px;font-weight:600;border-radius:50px;text-decoration:none;border:1px solid rgba(255,255,255,.15);transition:all .3s;}
.btn-secondary:hover{border-color:rgba(0,255,178,.5);color:#00FFB2;transform:translateY(-3px);}

.stats-bar{display:flex;gap:0;justify-content:center;margin:72px 0 0;width:100%;max-width:900px;border:1px solid rgba(255,255,255,.08);border-radius:20px;overflow:hidden;background:rgba(255,255,255,.02);backdrop-filter:blur(20px);animation:fadeUp 1s ease .5s both;}
@keyframes fadeUp{from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
.stat-item{flex:1;padding:28px 20px;text-align:center;border-right:1px solid rgba(255,255,255,.06);transition:background .3s;}
.stat-item:last-child{border-right:none;}
.stat-item:hover{background:rgba(123,0,255,.08);}
.stat-num{font-family:'Bebas Neue',sans-serif;font-size:42px;letter-spacing:2px;background:linear-gradient(135deg,#00FFB2,#7B00FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stat-label{font-size:12px;color:rgba(255,255,255,.4);letter-spacing:2px;text-transform:uppercase;margin-top:4px;font-family:'JetBrains Mono',monospace;}

.section{width:100%;max-width:1200px;margin-top:100px;}
.section-label{font-family:'JetBrains Mono',monospace;font-size:11px;color:#7B00FF;letter-spacing:4px;text-transform:uppercase;margin-bottom:16px;}
.section-title{font-family:'Bebas Neue',sans-serif;font-size:56px;letter-spacing:2px;color:#fff;margin-bottom:60px;line-height:1;}
.section-title span{background:linear-gradient(90deg,#00FFB2,#7B00FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}

.cards-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;}
.card{padding:32px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:20px;transition:all .4s ease;position:relative;overflow:hidden;animation:cardReveal .8s ease both;}
.card:nth-child(1){animation-delay:.1s;}.card:nth-child(2){animation-delay:.2s;}.card:nth-child(3){animation-delay:.3s;}.card:nth-child(4){animation-delay:.4s;}.card:nth-child(5){animation-delay:.5s;}.card:nth-child(6){animation-delay:.6s;}
@keyframes cardReveal{from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
.card::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at top left,var(--g,rgba(123,0,255,.1)),transparent 70%);opacity:0;transition:opacity .4s;}
.card:hover{transform:translateY(-8px);border-color:rgba(255,255,255,.15);}.card:hover::before{opacity:1;}
.card-icon{font-size:32px;margin-bottom:16px;display:inline-flex;align-items:center;justify-content:center;width:56px;height:56px;border-radius:14px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);}
.card-title{font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:#fff;margin-bottom:10px;}
.card-desc{font-size:14px;color:rgba(255,255,255,.45);line-height:1.7;}
.card-badge{display:inline-block;margin-top:16px;font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:20px;letter-spacing:1px;}

.pipeline{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:0;padding:48px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.07);border-radius:24px;position:relative;overflow:hidden;}
.pipeline::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(123,0,255,.05),rgba(0,255,178,.03));}
.pipe-step{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;gap:10px;padding:20px 24px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:16px;min-width:110px;transition:all .3s;}
.pipe-step:hover{background:rgba(123,0,255,.15);border-color:rgba(123,0,255,.4);transform:translateY(-4px);box-shadow:0 12px 40px rgba(123,0,255,.2);}
.pipe-icon{font-size:28px;}.pipe-label{font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,.5);text-align:center;letter-spacing:1px;}
.pipe-arrow{color:rgba(255,255,255,.2);font-size:20px;padding:0 8px;flex-shrink:0;animation:arrowFlow 2s ease-in-out infinite;}
.pipe-arrow:nth-child(even){animation-delay:.5s;}
@keyframes arrowFlow{0%,100%{color:rgba(255,255,255,.15);}50%{color:rgba(0,255,178,.6);}}

.tech-grid{display:flex;flex-wrap:wrap;gap:12px;}
.tech-tag{padding:8px 18px;font-family:'JetBrains Mono',monospace;font-size:12px;border-radius:30px;border:1px solid;letter-spacing:1px;transition:all .3s;}
.tech-tag:hover{transform:translateY(-2px);}
.t1{color:#00FFB2;border-color:rgba(0,255,178,.3);background:rgba(0,255,178,.06);}
.t2{color:#7B00FF;border-color:rgba(123,0,255,.3);background:rgba(123,0,255,.06);}
.t3{color:#FF0080;border-color:rgba(255,0,128,.3);background:rgba(255,0,128,.06);}
.t4{color:#FFB800;border-color:rgba(255,184,0,.3);background:rgba(255,184,0,.06);}

.footer{width:100%;max-width:1200px;margin-top:120px;padding-top:32px;border-top:1px solid rgba(255,255,255,.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;}
.footer-left,.footer-right{font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,255,255,.25);}
</style>

<div class="bg-mesh"></div><div class="grid-lines"></div>
<div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div>

<div class="page-wrap">
  <nav class="nav">
    <div class="nav-logo">NeuralDoc</div>
    <div class="nav-badge">⚡ PRODUCTION RAG v1.0</div>
  </nav>

  <section class="hero">
    <div class="hero-tag"><span class="tag-dot"></span>&nbsp;ZERO HALLUCINATION TOLERANCE</div>
    <h1 class="hero-title"><span class="a1">NEURAL</span><br><span class="a2">DOC</span> RAG</h1>
    <p class="hero-sub">A <strong>production-grade</strong> RAG system that answers questions from your documents with <strong>inline citations</strong>, hybrid retrieval, and a hard refusal trigger — no guessing, ever.</p>
    <div class="cta-wrap">
      <a href="/RAG_Chat" class="btn-primary">⚡ Launch App →</a>
      <a href="#features" class="btn-secondary">How It Works ↓</a>
    </div>
  </section>

  <div class="stats-bar">
    <div class="stat-item"><div class="stat-num">0%</div><div class="stat-label">Hallucination</div></div>
    <div class="stat-item"><div class="stat-num">3×</div><div class="stat-label">Retrieval Methods</div></div>
    <div class="stat-item"><div class="stat-num">100%</div><div class="stat-label">Local & Private</div></div>
    <div class="stat-item"><div class="stat-num">∞</div><div class="stat-label">Documents</div></div>
  </div>

  <section class="section" id="features">
    <div class="section-label">// What It Does</div>
    <div class="section-title">SIX <span>PILLARS</span></div>
    <div class="cards-grid">
      <div class="card" style="--g:rgba(0,255,178,.12)"><div class="card-icon">📄</div><div class="card-title">Smart PDF Ingestion</div><div class="card-desc">Handles multi-column layouts, embedded tables, and complex PDFs. Strips headers/footers. Extracts structure-aware text.</div><span class="card-badge" style="color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2)">pdfplumber</span></div>
      <div class="card" style="--g:rgba(123,0,255,.12)"><div class="card-icon">✂️</div><div class="card-title">Semantic Chunking</div><div class="card-desc">Header-aware chunks of 500–800 tokens. Every chunk carries source, page, and breadcrumb path as metadata.</div><span class="card-badge" style="color:#7B00FF;background:rgba(123,0,255,.08);border:1px solid rgba(123,0,255,.2)">tiktoken</span></div>
      <div class="card" style="--g:rgba(255,0,128,.12)"><div class="card-icon">🔍</div><div class="card-title">Hybrid Retrieval</div><div class="card-desc">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion — catches what either method alone misses.</div><span class="card-badge" style="color:#FF0080;background:rgba(255,0,128,.08);border:1px solid rgba(255,0,128,.2)">RRF Fusion</span></div>
      <div class="card" style="--g:rgba(255,184,0,.12)"><div class="card-icon">🏆</div><div class="card-title">Cross-Encoder Reranking</div><div class="card-desc">Top-20 candidates re-scored with a cross-encoder model. Only the best 5 reach the LLM — precision over recall.</div><span class="card-badge" style="color:#FFB800;background:rgba(255,184,0,.08);border:1px solid rgba(255,184,0,.2)">ms-marco</span></div>
      <div class="card" style="--g:rgba(0,200,255,.12)"><div class="card-icon">📎</div><div class="card-title">Attributed QA</div><div class="card-desc">Every claim has an inline citation [Source, p.X]. A References section is automatically appended. Always grounded.</div><span class="card-badge" style="color:#00C8FF;background:rgba(0,200,255,.08);border:1px solid rgba(0,200,255,.2)">LangGraph</span></div>
      <div class="card" style="--g:rgba(255,80,0,.12)"><div class="card-icon">🚫</div><div class="card-title">Hard Refusal Trigger</div><div class="card-desc">If retrieved context is insufficient, the model returns a fixed refusal — not a guess. Zero hallucination by design.</div><span class="card-badge" style="color:#FF5000;background:rgba(255,80,0,.08);border:1px solid rgba(255,80,0,.2)">Threshold Gate</span></div>
    </div>
  </section>

  <section class="section">
    <div class="section-label">// Architecture</div>
    <div class="section-title">THE <span>PIPELINE</span></div>
    <div class="pipeline">
      <div class="pipe-step"><div class="pipe-icon">📄</div><div class="pipe-label">PDF Parse</div></div>
      <div class="pipe-arrow">→</div>
      <div class="pipe-step"><div class="pipe-icon">✂️</div><div class="pipe-label">Chunk</div></div>
      <div class="pipe-arrow">→</div>
      <div class="pipe-step"><div class="pipe-icon">🧠</div><div class="pipe-label">Embed</div></div>
      <div class="pipe-arrow">→</div>
      <div class="pipe-step"><div class="pipe-icon">🔍</div><div class="pipe-label">Retrieve</div></div>
      <div class="pipe-arrow">→</div>
      <div class="pipe-step"><div class="pipe-icon">🏆</div><div class="pipe-label">Rerank</div></div>
      <div class="pipe-arrow">→</div>
      <div class="pipe-step"><div class="pipe-icon">⚡</div><div class="pipe-label">Generate</div></div>
      <div class="pipe-arrow">→</div>
      <div class="pipe-step"><div class="pipe-icon">📎</div><div class="pipe-label">Cite</div></div>
    </div>
  </section>

  <section class="section">
    <div class="section-label">// Tech Stack</div>
    <div class="section-title">BUILT <span>WITH</span></div>
    <div class="tech-grid">
      <span class="tech-tag t1">pdfplumber</span><span class="tech-tag t1">ChromaDB</span><span class="tech-tag t1">sentence-transformers</span>
      <span class="tech-tag t2">LangGraph</span><span class="tech-tag t2">langchain-ollama</span><span class="tech-tag t2">llama3.1:8b</span>
      <span class="tech-tag t3">BM25 + RRF</span><span class="tech-tag t3">cross-encoder</span>
      <span class="tech-tag t4">FastAPI</span><span class="tech-tag t4">Streamlit</span><span class="tech-tag t4">Python 3.14</span>
    </div>
  </section>

  <footer class="footer">
    <div class="footer-left">NeuralDoc RAG System — Production Grade</div>
    <div class="footer-right">Built with Ollama · ChromaDB · LangGraph</div>
  </footer>
</div>
""", unsafe_allow_html=True)