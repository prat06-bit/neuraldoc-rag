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
/* Force ALL Streamlit containers to be transparent and non-clipping */
html, body { background: #020008 !important; }
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main, .block-container,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    overflow: visible !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
#MainMenu, footer { display: none !important; }

/* Animated background — sits behind everything */
body::before {
    content: '';
    position: fixed; inset: 0; z-index: -3;
    background: #020008;
}
body::after {
    content: '';
    position: fixed; inset: 0; z-index: -2;
    background:
        radial-gradient(ellipse 70% 60% at 15% 15%, rgba(120,0,255,0.25) 0%, transparent 55%),
        radial-gradient(ellipse 60% 70% at 85% 85%, rgba(0,255,178,0.18) 0%, transparent 55%),
        radial-gradient(ellipse 45% 45% at 50% 50%, rgba(255,0,120,0.1) 0%, transparent 65%);
    animation: meshAnim 14s ease-in-out infinite alternate;
}
@keyframes meshAnim {
    0%   { filter: hue-rotate(0deg); }
    50%  { filter: hue-rotate(25deg) brightness(1.1); }
    100% { filter: hue-rotate(-20deg); }
}

/* Grid overlay */
.nd-grid {
    position: fixed; inset: 0; z-index: -1;
    background-image:
        linear-gradient(rgba(123,0,255,0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(123,0,255,0.07) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridPulse 5s ease-in-out infinite;
    pointer-events: none;
}
@keyframes gridPulse { 0%,100%{opacity:0.4;} 50%{opacity:0.9;} }

/* Floating orbs */
.nd-orb {
    position: fixed; border-radius: 50%; filter: blur(90px);
    opacity: 0.3; pointer-events: none; z-index: -1;
    animation: orbFloat linear infinite;
}
.o1 { width:500px;height:500px;background:#7B00FF;top:-180px;left:-180px;animation-duration:22s; }
.o2 { width:420px;height:420px;background:#00FFB2;bottom:-150px;right:-150px;animation-duration:28s;animation-delay:-10s; }
.o3 { width:320px;height:320px;background:#FF0080;top:35%;left:55%;animation-duration:19s;animation-delay:-5s; }
@keyframes orbFloat {
    0%   { transform: translate(0,0) scale(1); }
    33%  { transform: translate(50px,-70px) scale(1.1); }
    66%  { transform: translate(-40px,50px) scale(0.92); }
    100% { transform: translate(0,0) scale(1); }
}

/* ── MAIN WRAPPER ── */
.nd-wrap {
    position: relative;
    width: 100%;
    padding: 0 32px 100px;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: 'Syne', sans-serif;
}

/* NAV */
.nd-nav {
    width: 100%; max-width: 1200px;
    display: flex; align-items: center; justify-content: space-between;
    padding: 32px 0 0;
    animation: slideDown 0.7s ease both;
}
@keyframes slideDown { from{opacity:0;transform:translateY(-24px);} to{opacity:1;transform:translateY(0);} }
.nd-logo {
    font-family: 'Bebas Neue', sans-serif; font-size: 30px; letter-spacing: 4px;
    background: linear-gradient(135deg, #00FFB2, #7B00FF, #FF0080);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.nd-badge {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00FFB2;
    border: 1px solid rgba(0,255,178,0.35); padding: 5px 14px; border-radius: 20px;
    background: rgba(0,255,178,0.06); letter-spacing: 2px;
}

/* HERO */
.nd-hero {
    width: 100%; max-width: 960px; text-align: center;
    padding: 72px 0 48px;
    animation: heroUp 0.9s ease 0.15s both;
}
@keyframes heroUp { from{opacity:0;transform:translateY(44px);} to{opacity:1;transform:translateY(0);} }

.nd-pill {
    display: inline-flex; align-items: center; gap: 8px;
    font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #FF0080;
    border: 1px solid rgba(255,0,128,0.35); background: rgba(255,0,128,0.07);
    padding: 6px 18px; border-radius: 30px; margin-bottom: 28px; letter-spacing: 2px;
    animation: pillGlow 3s ease-in-out infinite;
}
@keyframes pillGlow { 0%,100%{box-shadow:0 0 0 rgba(255,0,128,0);} 50%{box-shadow:0 0 22px rgba(255,0,128,0.35);} }
.nd-dot { width:6px;height:6px;border-radius:50%;background:#FF0080;display:inline-block;animation:dotBlink 1.6s ease-in-out infinite; }
@keyframes dotBlink { 0%,100%{opacity:1;} 50%{opacity:0.15;} }

.nd-h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(72px, 11vw, 130px);
    line-height: 0.88; letter-spacing: 3px; color: #fff;
}
.nd-h1 .g1 {
    background: linear-gradient(90deg, #7B00FF, #FF0080);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    display: inline-block; animation: g1shift 5s ease-in-out infinite alternate;
}
.nd-h1 .g2 {
    background: linear-gradient(90deg, #00FFB2, #7B00FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    display: inline-block;
}
@keyframes g1shift { from{filter:hue-rotate(0deg);} to{filter:hue-rotate(35deg);} }

.nd-sub {
    font-size: 17px; color: rgba(255,255,255,0.5);
    max-width: 580px; margin: 24px auto 0; line-height: 1.75;
}
.nd-sub b { color: #00FFB2; font-weight: 700; }

/* CTA */
.nd-cta { margin-top: 48px; display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
.nd-btn {
    display: inline-block; padding: 15px 42px;
    font-family: 'Syne', sans-serif; font-size: 15px; font-weight: 700;
    border-radius: 50px; text-decoration: none; letter-spacing: 0.5px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.nd-btn-p {
    background: linear-gradient(135deg, #7B00FF, #FF0080); color: #fff;
    box-shadow: 0 0 40px rgba(123,0,255,0.45);
    animation: btnPulse 3s ease-in-out infinite;
}
@keyframes btnPulse { 0%,100%{box-shadow:0 0 40px rgba(123,0,255,0.45);} 50%{box-shadow:0 0 65px rgba(123,0,255,0.75);} }
.nd-btn-p:hover { transform: translateY(-4px) scale(1.04); }
.nd-btn-s {
    background: transparent; color: rgba(255,255,255,0.65);
    border: 1px solid rgba(255,255,255,0.18);
}
.nd-btn-s:hover { border-color: rgba(0,255,178,0.55); color: #00FFB2; transform: translateY(-4px); }

/* STATS */
.nd-stats {
    display: flex; width: 100%; max-width: 880px; margin: 64px 0 0;
    border: 1px solid rgba(255,255,255,0.08); border-radius: 20px;
    overflow: hidden; background: rgba(255,255,255,0.025);
    backdrop-filter: blur(24px);
    animation: fadeUp 0.9s ease 0.35s both;
}
@keyframes fadeUp { from{opacity:0;transform:translateY(32px);} to{opacity:1;transform:translateY(0);} }
.nd-stat {
    flex: 1; padding: 28px 16px; text-align: center;
    border-right: 1px solid rgba(255,255,255,0.07);
    transition: background 0.35s;
}
.nd-stat:last-child { border-right: none; }
.nd-stat:hover { background: rgba(123,0,255,0.1); }
.nd-stat-n {
    font-family: 'Bebas Neue', sans-serif; font-size: 44px; letter-spacing: 2px;
    background: linear-gradient(135deg, #00FFB2, #7B00FF);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.nd-stat-l { font-size: 11px; color: rgba(255,255,255,0.38); letter-spacing: 2.5px; text-transform: uppercase; margin-top: 3px; font-family: 'JetBrains Mono', monospace; }

/* SECTION */
.nd-sec { width: 100%; max-width: 1200px; margin-top: 96px; }
.nd-sec-tag { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #7B00FF; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 12px; }
.nd-sec-h { font-family: 'Bebas Neue', sans-serif; font-size: 52px; letter-spacing: 2px; color: #fff; line-height: 1; margin-bottom: 48px; }
.nd-sec-h span { background: linear-gradient(90deg,#00FFB2,#7B00FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }

/* CARDS */
.nd-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px,1fr)); gap: 18px; }
.nd-card {
    padding: 30px; background: rgba(255,255,255,0.028);
    border: 1px solid rgba(255,255,255,0.07); border-radius: 20px;
    transition: transform 0.4s, border-color 0.4s, box-shadow 0.4s;
    animation: cardIn 0.7s ease both;
}
.nd-card:nth-child(1){animation-delay:0.05s;} .nd-card:nth-child(2){animation-delay:0.12s;}
.nd-card:nth-child(3){animation-delay:0.19s;} .nd-card:nth-child(4){animation-delay:0.26s;}
.nd-card:nth-child(5){animation-delay:0.33s;} .nd-card:nth-child(6){animation-delay:0.40s;}
@keyframes cardIn { from{opacity:0;transform:translateY(28px);} to{opacity:1;transform:translateY(0);} }
.nd-card:hover { transform: translateY(-8px); border-color: rgba(123,0,255,0.35); box-shadow: 0 16px 50px rgba(123,0,255,0.15); }
.nd-ci { font-size: 30px; margin-bottom: 14px; display: inline-block; width:52px;height:52px;line-height:52px;text-align:center;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:14px; }
.nd-ct { font-family: 'Syne',sans-serif; font-size: 17px; font-weight: 800; color: #fff; margin-bottom: 8px; }
.nd-cd { font-size: 13px; color: rgba(255,255,255,0.42); line-height: 1.7; }
.nd-cb { display:inline-block;margin-top:14px;font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:20px;letter-spacing:1px; }

/* PIPELINE */
.nd-pipe { display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:0;padding:44px;background:rgba(255,255,255,0.018);border:1px solid rgba(255,255,255,0.07);border-radius:22px; }
.nd-ps { display:flex;flex-direction:column;align-items:center;gap:8px;padding:18px 20px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:14px;min-width:100px;transition:all 0.3s;cursor:default; }
.nd-ps:hover { background:rgba(123,0,255,0.18);border-color:rgba(123,0,255,0.45);transform:translateY(-5px);box-shadow:0 14px 40px rgba(123,0,255,0.22); }
.nd-pi { font-size:26px; }
.nd-pl { font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,0.48);text-align:center;letter-spacing:1px; }
.nd-pa { color:rgba(255,255,255,0.18);font-size:18px;padding:0 6px;flex-shrink:0;animation:arrowPulse 2.2s ease-in-out infinite; }
.nd-pa:nth-child(even) { animation-delay:0.55s; }
@keyframes arrowPulse { 0%,100%{color:rgba(255,255,255,0.15);} 50%{color:rgba(0,255,178,0.65);} }

/* TECH */
.nd-tech { display:flex;flex-wrap:wrap;gap:10px; }
.nd-tt { padding:7px 16px;font-family:'JetBrains Mono',monospace;font-size:11px;border-radius:30px;border:1px solid;letter-spacing:1px;transition:transform 0.3s; }
.nd-tt:hover { transform:translateY(-2px); }
.t1{color:#00FFB2;border-color:rgba(0,255,178,.3);background:rgba(0,255,178,.06);}
.t2{color:#7B00FF;border-color:rgba(123,0,255,.3);background:rgba(123,0,255,.06);}
.t3{color:#FF0080;border-color:rgba(255,0,128,.3);background:rgba(255,0,128,.06);}
.t4{color:#FFB800;border-color:rgba(255,184,0,.3);background:rgba(255,184,0,.06);}

/* FOOTER */
.nd-foot { width:100%;max-width:1200px;margin-top:100px;padding-top:28px;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px; }
.nd-foot span { font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,255,255,0.22); }
</style>

<div class="nd-grid-bg"></div>
""", unsafe_allow_html=True)

# Inject fixed background elements separately so they don't get clipped
st.markdown("""
<div class="nd-grid"></div>
<div class="nd-orb o1"></div>
<div class="nd-orb o2"></div>
<div class="nd-orb o3"></div>

<div class="nd-wrap">

  <nav class="nd-nav">
    <div class="nd-logo">NeuralDoc</div>
    <div class="nd-badge">⚡ PRODUCTION RAG v1.0</div>
  </nav>

  <section class="nd-hero">
    <div class="nd-pill"><span class="nd-dot"></span>&nbsp;ZERO HALLUCINATION TOLERANCE</div>
    <h1 class="nd-h1">
      <span class="g1">NEURAL</span><br>
      <span class="g2">DOC</span> RAG
    </h1>
    <p class="nd-sub">
      A <b>production-grade</b> RAG system that answers questions from your documents
      with <b>inline citations</b>, hybrid retrieval, and a hard refusal trigger &mdash; no guessing, ever.
    </p>
    <div class="nd-cta">
      <a href="/RAG_Chat" class="nd-btn nd-btn-p">⚡ Launch App &rarr;</a>
      <a href="#features" class="nd-btn nd-btn-s">How It Works &darr;</a>
    </div>
  </section>

  <div class="nd-stats">
    <div class="nd-stat"><div class="nd-stat-n">0%</div><div class="nd-stat-l">Hallucination</div></div>
    <div class="nd-stat"><div class="nd-stat-n">3&times;</div><div class="nd-stat-l">Retrieval Methods</div></div>
    <div class="nd-stat"><div class="nd-stat-n">100%</div><div class="nd-stat-l">Local &amp; Private</div></div>
    <div class="nd-stat"><div class="nd-stat-n">&infin;</div><div class="nd-stat-l">Documents</div></div>
  </div>

  <section class="nd-sec" id="features">
    <div class="nd-sec-tag">// What It Does</div>
    <div class="nd-sec-h">SIX <span>PILLARS</span></div>
    <div class="nd-grid">
      <div class="nd-card"><div class="nd-ci">📄</div><div class="nd-ct">Smart PDF Ingestion</div><div class="nd-cd">Handles multi-column layouts, embedded tables, complex PDFs. Strips headers and footers automatically.</div><span class="nd-cb" style="color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2)">pdfplumber</span></div>
      <div class="nd-card"><div class="nd-ci">✂️</div><div class="nd-ct">Semantic Chunking</div><div class="nd-cd">Header-aware 500&ndash;800 token chunks. Every chunk carries source, page, and breadcrumb metadata.</div><span class="nd-cb" style="color:#7B00FF;background:rgba(123,0,255,.08);border:1px solid rgba(123,0,255,.2)">tiktoken</span></div>
      <div class="nd-card"><div class="nd-ci">🔍</div><div class="nd-ct">Hybrid Retrieval</div><div class="nd-cd">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion &mdash; catches what either misses.</div><span class="nd-cb" style="color:#FF0080;background:rgba(255,0,128,.08);border:1px solid rgba(255,0,128,.2)">RRF Fusion</span></div>
      <div class="nd-card"><div class="nd-ci">🏆</div><div class="nd-ct">Cross-Encoder Reranking</div><div class="nd-cd">Top-20 candidates re-scored with a cross-encoder. Only the best 5 reach the LLM &mdash; precision over recall.</div><span class="nd-cb" style="color:#FFB800;background:rgba(255,184,0,.08);border:1px solid rgba(255,184,0,.2)">ms-marco</span></div>
      <div class="nd-card"><div class="nd-ci">📎</div><div class="nd-ct">Attributed QA</div><div class="nd-cd">Every claim has an inline citation [Source, p.X]. A References section is auto-appended. Always grounded.</div><span class="nd-cb" style="color:#00C8FF;background:rgba(0,200,255,.08);border:1px solid rgba(0,200,255,.2)">LangGraph</span></div>
      <div class="nd-card"><div class="nd-ci">🚫</div><div class="nd-ct">Hard Refusal Trigger</div><div class="nd-cd">Insufficient context returns a fixed refusal &mdash; not a guess. Zero hallucination is a hard system constraint.</div><span class="nd-cb" style="color:#FF5000;background:rgba(255,80,0,.08);border:1px solid rgba(255,80,0,.2)">Threshold Gate</span></div>
    </div>
  </section>

  <section class="nd-sec">
    <div class="nd-sec-tag">// Architecture</div>
    <div class="nd-sec-h">THE <span>PIPELINE</span></div>
    <div class="nd-pipe">
      <div class="nd-ps"><div class="nd-pi">📄</div><div class="nd-pl">PDF Parse</div></div>
      <div class="nd-pa">&rarr;</div>
      <div class="nd-ps"><div class="nd-pi">✂️</div><div class="nd-pl">Chunk</div></div>
      <div class="nd-pa">&rarr;</div>
      <div class="nd-ps"><div class="nd-pi">🧠</div><div class="nd-pl">Embed</div></div>
      <div class="nd-pa">&rarr;</div>
      <div class="nd-ps"><div class="nd-pi">🔍</div><div class="nd-pl">Retrieve</div></div>
      <div class="nd-pa">&rarr;</div>
      <div class="nd-ps"><div class="nd-pi">🏆</div><div class="nd-pl">Rerank</div></div>
      <div class="nd-pa">&rarr;</div>
      <div class="nd-ps"><div class="nd-pi">⚡</div><div class="nd-pl">Generate</div></div>
      <div class="nd-pa">&rarr;</div>
      <div class="nd-ps"><div class="nd-pi">📎</div><div class="nd-pl">Cite</div></div>
    </div>
  </section>

  <section class="nd-sec">
    <div class="nd-sec-tag">// Tech Stack</div>
    <div class="nd-sec-h">BUILT <span>WITH</span></div>
    <div class="nd-tech">
      <span class="nd-tt t1">pdfplumber</span><span class="nd-tt t1">ChromaDB</span><span class="nd-tt t1">sentence-transformers</span>
      <span class="nd-tt t2">LangGraph</span><span class="nd-tt t2">langchain-ollama</span><span class="nd-tt t2">llama3.1:8b</span>
      <span class="nd-tt t3">BM25 + RRF</span><span class="nd-tt t3">cross-encoder</span>
      <span class="nd-tt t4">FastAPI</span><span class="nd-tt t4">Streamlit</span><span class="nd-tt t4">Python 3.14</span>
    </div>
  </section>

  <footer class="nd-foot">
    <span>NeuralDoc RAG &mdash; Production Grade</span>
    <span>Built with Ollama &middot; ChromaDB &middot; LangGraph</span>
  </footer>

</div>
""", unsafe_allow_html=True)