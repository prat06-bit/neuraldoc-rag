"""Landing page — NeuralDoc RAG"""
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NeuralDoc RAG",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
[data-testid="stHeader"],[data-testid="stToolbar"],
[data-testid="collapsedControl"],#MainMenu,footer,
section[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
[data-testid="stAppViewContainer"]{background:#030010!important;}
[data-testid="stMain"]{background:transparent!important;}
iframe{border:none!important;display:block!important;}
</style>
""", unsafe_allow_html=True)

page = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;}
html,body{
  min-height:100vh;
  background:#030010;
  font-family:'Syne',sans-serif;
  color:#fff;
  overflow-x:hidden;
}

/* Background */
.bg{
  position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 70% 55% at 12% 12%, rgba(110,0,240,0.32) 0%, transparent 55%),
    radial-gradient(ellipse 55% 65% at 88% 88%, rgba(0,220,160,0.22) 0%, transparent 55%),
    radial-gradient(ellipse 45% 45% at 55% 45%, rgba(220,0,100,0.12) 0%, transparent 60%);
  animation:bgShift 16s ease-in-out infinite alternate;
}
@keyframes bgShift{
  0%{filter:hue-rotate(0deg);}
  100%{filter:hue-rotate(22deg) brightness(1.08);}
}
.grid{
  position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(100,0,255,0.06) 1px,transparent 1px),
    linear-gradient(90deg,rgba(100,0,255,0.06) 1px,transparent 1px);
  background-size:56px 56px;
  animation:gridBreathe 6s ease-in-out infinite;
}
@keyframes gridBreathe{0%,100%{opacity:0.4;}50%{opacity:0.85;}}

.orb{position:fixed;border-radius:50%;filter:blur(100px);pointer-events:none;z-index:0;animation:orbDrift linear infinite;}
.orb1{width:480px;height:480px;background:rgba(110,0,240,0.28);top:-180px;left:-160px;animation-duration:24s;}
.orb2{width:400px;height:400px;background:rgba(0,210,150,0.2);bottom:-140px;right:-140px;animation-duration:30s;animation-delay:-12s;}
.orb3{width:300px;height:300px;background:rgba(220,0,90,0.16);top:42%;left:58%;animation-duration:21s;animation-delay:-7s;}
@keyframes orbDrift{
  0%{transform:translate(0,0) scale(1);}
  33%{transform:translate(44px,-60px) scale(1.08);}
  66%{transform:translate(-35px,44px) scale(0.93);}
  100%{transform:translate(0,0) scale(1);}
}

/* Layout */
.wrap{
  position:relative;z-index:1;
  max-width:1200px;margin:0 auto;
  padding:0 40px 120px;
}

/* Nav */
nav{
  display:flex;align-items:center;justify-content:space-between;
  padding:36px 0 0;
  animation:fadeDown 0.7s ease both;
}
@keyframes fadeDown{from{opacity:0;transform:translateY(-20px);}to{opacity:1;transform:translateY(0);}}
.logo{
  font-family:'Bebas Neue',sans-serif;font-size:28px;letter-spacing:5px;
  background:linear-gradient(135deg,#00DFA0,#6B00F0,#E0005A);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.nav-tag{
  font-family:'JetBrains Mono',monospace;font-size:11px;
  color:#00DFA0;letter-spacing:2px;
  border:1px solid rgba(0,223,160,0.3);
  padding:5px 14px;border-radius:20px;
  background:rgba(0,223,160,0.06);
}

/* Hero */
.hero{
  padding:80px 0 56px;
  text-align:center;
  animation:fadeUp 0.9s ease 0.2s both;
}
@keyframes fadeUp{from{opacity:0;transform:translateY(40px);}to{opacity:1;transform:translateY(0);}}

.hero-eyebrow{
  display:inline-flex;align-items:center;gap:8px;
  font-family:'JetBrains Mono',monospace;font-size:11px;
  color:#E0005A;letter-spacing:2.5px;
  border:1px solid rgba(224,0,90,0.3);background:rgba(224,0,90,0.07);
  padding:6px 18px;border-radius:30px;margin-bottom:32px;
  animation:eyebrowGlow 3.5s ease-in-out infinite;
}
@keyframes eyebrowGlow{
  0%,100%{box-shadow:0 0 0 transparent;}
  50%{box-shadow:0 0 20px rgba(224,0,90,0.3);}
}
.pulse-dot{
  width:6px;height:6px;border-radius:50%;background:#E0005A;
  animation:pulseDot 1.6s ease-in-out infinite;
}
@keyframes pulseDot{0%,100%{opacity:1;}50%{opacity:0.15;}}

.hero-title{
  font-family:'Bebas Neue',sans-serif;
  font-size:clamp(68px,10.5vw,124px);
  line-height:0.88;letter-spacing:3px;color:#fff;
  margin-bottom:0;
}
.t-purple{
  background:linear-gradient(90deg,#6B00F0,#E0005A);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  display:inline-block;
  animation:purpleShift 5s ease-in-out infinite alternate;
}
@keyframes purpleShift{from{filter:hue-rotate(0deg);}to{filter:hue-rotate(30deg);}}
.t-teal{
  background:linear-gradient(90deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  display:inline-block;
}

.hero-desc{
  font-size:17px;color:rgba(255,255,255,0.52);
  max-width:560px;margin:26px auto 0;line-height:1.8;
}
.hero-desc strong{color:#00DFA0;font-weight:700;}

/* CTA */
.cta{
  margin-top:48px;
  display:flex;gap:14px;justify-content:center;flex-wrap:wrap;
}
.btn{
  padding:14px 40px;font-family:'Syne',sans-serif;
  font-size:15px;font-weight:700;border-radius:50px;
  cursor:pointer;border:none;letter-spacing:0.5px;
  transition:transform 0.3s ease,box-shadow 0.3s ease;
  text-decoration:none;display:inline-block;
}
.btn-primary{
  background:linear-gradient(135deg,#6B00F0,#E0005A);
  color:#fff;
  box-shadow:0 0 36px rgba(107,0,240,0.45);
  animation:primaryGlow 3s ease-in-out infinite;
}
@keyframes primaryGlow{
  0%,100%{box-shadow:0 0 36px rgba(107,0,240,0.45);}
  50%{box-shadow:0 0 58px rgba(107,0,240,0.72);}
}
.btn-primary:hover{transform:translateY(-4px) scale(1.03);}
.btn-secondary{
  background:transparent;color:rgba(255,255,255,0.65);
  border:1px solid rgba(255,255,255,0.16)!important;
}
.btn-secondary:hover{
  border-color:rgba(0,223,160,0.5)!important;
  color:#00DFA0;transform:translateY(-4px);
}

/* Stats */
.stats{
  display:flex;
  max-width:860px;margin:70px auto 0;
  border:1px solid rgba(255,255,255,0.07);
  border-radius:18px;overflow:hidden;
  background:rgba(255,255,255,0.022);
  backdrop-filter:blur(20px);
  animation:fadeUp 0.9s ease 0.4s both;
}
.stat{
  flex:1;padding:28px 16px;text-align:center;
  border-right:1px solid rgba(255,255,255,0.06);
  transition:background 0.3s;
}
.stat:last-child{border-right:none;}
.stat:hover{background:rgba(107,0,240,0.1);}
.stat-val{
  font-family:'Bebas Neue',sans-serif;font-size:44px;letter-spacing:2px;
  background:linear-gradient(135deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.stat-lbl{
  font-family:'JetBrains Mono',monospace;font-size:10px;
  color:rgba(255,255,255,0.35);letter-spacing:2.5px;
  text-transform:uppercase;margin-top:4px;
}

/* Section */
.section{max-width:1200px;margin:96px auto 0;}
.sec-tag{
  font-family:'JetBrains Mono',monospace;font-size:11px;
  color:#6B00F0;letter-spacing:4px;text-transform:uppercase;margin-bottom:10px;
}
.sec-title{
  font-family:'Bebas Neue',sans-serif;font-size:50px;
  letter-spacing:2px;color:#fff;line-height:1;margin-bottom:48px;
}
.sec-title span{
  background:linear-gradient(90deg,#00DFA0,#6B00F0);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}

/* Cards */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;}
.card{
  padding:28px;
  background:rgba(255,255,255,0.025);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:18px;
  transition:transform 0.4s,border-color 0.4s,box-shadow 0.4s;
  animation:cardUp 0.7s ease both;
}
.card:nth-child(1){animation-delay:0.05s;}.card:nth-child(2){animation-delay:0.1s;}
.card:nth-child(3){animation-delay:0.15s;}.card:nth-child(4){animation-delay:0.2s;}
.card:nth-child(5){animation-delay:0.25s;}.card:nth-child(6){animation-delay:0.3s;}
@keyframes cardUp{from{opacity:0;transform:translateY(26px);}to{opacity:1;transform:translateY(0);}}
.card:hover{transform:translateY(-7px);border-color:rgba(107,0,240,0.35);box-shadow:0 14px 44px rgba(107,0,240,0.14);}
.card-num{
  font-family:'Bebas Neue',sans-serif;font-size:13px;letter-spacing:3px;
  color:rgba(255,255,255,0.2);margin-bottom:14px;
}
.card-title{
  font-family:'Syne',sans-serif;font-size:16px;font-weight:800;
  color:#fff;margin-bottom:10px;
}
.card-body{font-size:13px;color:rgba(255,255,255,0.42);line-height:1.75;}
.card-tech{
  display:inline-block;margin-top:14px;
  font-family:'JetBrains Mono',monospace;font-size:10px;
  padding:3px 10px;border-radius:20px;letter-spacing:1px;
}

/* Pipeline */
.pipeline{
  display:flex;align-items:center;justify-content:center;flex-wrap:wrap;
  padding:44px;
  background:rgba(255,255,255,0.018);
  border:1px solid rgba(255,255,255,0.06);
  border-radius:20px;gap:0;
}
.step{
  display:flex;flex-direction:column;align-items:center;gap:10px;
  padding:18px 22px;
  background:rgba(255,255,255,0.04);
  border:1px solid rgba(255,255,255,0.08);
  border-radius:14px;min-width:100px;
  transition:all 0.3s;cursor:default;
}
.step:hover{
  background:rgba(107,0,240,0.18);
  border-color:rgba(107,0,240,0.45);
  transform:translateY(-5px);
  box-shadow:0 12px 36px rgba(107,0,240,0.2);
}
.step-label{
  font-family:'JetBrains Mono',monospace;font-size:10px;
  color:rgba(255,255,255,0.45);text-align:center;letter-spacing:1px;
}
.step-icon{
  font-family:'Bebas Neue',sans-serif;font-size:11px;
  letter-spacing:1px;color:rgba(255,255,255,0.6);
}
.arrow{
  color:rgba(255,255,255,0.15);font-size:16px;
  padding:0 6px;flex-shrink:0;
  animation:arrowPulse 2.4s ease-in-out infinite;
}
.arrow:nth-child(even){animation-delay:0.6s;}
@keyframes arrowPulse{
  0%,100%{color:rgba(255,255,255,0.12);}
  50%{color:rgba(0,223,160,0.7);}
}

/* Tech tags */
.tags{display:flex;flex-wrap:wrap;gap:10px;}
.tag{
  padding:7px 16px;
  font-family:'JetBrains Mono',monospace;font-size:11px;
  border-radius:30px;border:1px solid;letter-spacing:1px;
  transition:transform 0.3s;cursor:default;
}
.tag:hover{transform:translateY(-2px);}
.tg{color:#00DFA0;border-color:rgba(0,223,160,0.3);background:rgba(0,223,160,0.06);}
.tp{color:#6B00F0;border-color:rgba(107,0,240,0.3);background:rgba(107,0,240,0.06);}
.tr{color:#E0005A;border-color:rgba(224,0,90,0.3);background:rgba(224,0,90,0.06);}
.ty{color:#F0A800;border-color:rgba(240,168,0,0.3);background:rgba(240,168,0,0.06);}

/* Footer */
footer{
  max-width:1200px;margin:96px auto 0;
  padding-top:28px;
  border-top:1px solid rgba(255,255,255,0.06);
  display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;
}
footer span{
  font-family:'JetBrains Mono',monospace;font-size:11px;
  color:rgba(255,255,255,0.22);
}
</style>
</head>
<body>

<div class="bg"></div>
<div class="grid"></div>
<div class="orb orb1"></div>
<div class="orb orb2"></div>
<div class="orb orb3"></div>

<div class="wrap">

  <!-- NAV -->
  <nav>
    <div class="logo">NeuralDoc</div>
    <div class="nav-tag">PRODUCTION RAG v1.0</div>
  </nav>

  <!-- HERO -->
  <div class="hero">
    <div class="hero-eyebrow">
      <span class="pulse-dot"></span>
      ZERO HALLUCINATION TOLERANCE
    </div>
    <h1 class="hero-title">
      <span class="t-purple">NEURAL</span><br>
      <span class="t-teal">DOC</span> RAG
    </h1>
    <p class="hero-desc">
      A <strong>production-grade</strong> RAG system that answers questions
      from your documents with <strong>inline citations</strong>,
      hybrid retrieval, and a hard refusal trigger &mdash; no guessing, ever.
    </p>
    <div class="cta">
      <a class="btn btn-primary" onclick="window.parent.location.href='/RAG_Chat'" href="#">
        Launch App &rarr;
      </a>
      <a class="btn btn-secondary" href="#features">
        How It Works &darr;
      </a>
    </div>
  </div>

  <!-- STATS -->
  <div class="stats">
    <div class="stat">
      <div class="stat-val">0%</div>
      <div class="stat-lbl">Hallucination Rate</div>
    </div>
    <div class="stat">
      <div class="stat-val">3x</div>
      <div class="stat-lbl">Retrieval Methods</div>
    </div>
    <div class="stat">
      <div class="stat-val">100%</div>
      <div class="stat-lbl">Local & Private</div>
    </div>
    <div class="stat">
      <div class="stat-val">inf</div>
      <div class="stat-lbl">Documents Supported</div>
    </div>
  </div>

  <!-- FEATURES -->
  <div class="section" id="features">
    <div class="sec-tag">// Capabilities</div>
    <div class="sec-title">SIX <span>PILLARS</span></div>
    <div class="cards">

      <div class="card">
        <div class="card-num">01 &mdash; INGESTION</div>
        <div class="card-title">Smart PDF Parsing</div>
        <div class="card-body">Handles multi-column layouts, embedded tables, and complex document structures. Headers and footers stripped automatically.</div>
        <span class="card-tech" style="color:#00DFA0;background:rgba(0,223,160,0.07);border:1px solid rgba(0,223,160,0.2)">pdfplumber</span>
      </div>

      <div class="card">
        <div class="card-num">02 &mdash; CHUNKING</div>
        <div class="card-title">Semantic Chunking</div>
        <div class="card-body">Header-aware chunks of 500&ndash;800 tokens. Every chunk carries source path, page number, and section breadcrumb as metadata.</div>
        <span class="card-tech" style="color:#6B00F0;background:rgba(107,0,240,0.07);border:1px solid rgba(107,0,240,0.2)">tiktoken</span>
      </div>

      <div class="card">
        <div class="card-num">03 &mdash; RETRIEVAL</div>
        <div class="card-title">Hybrid Search</div>
        <div class="card-body">BM25 keyword search fused with dense vector search via Reciprocal Rank Fusion. Catches what either method alone misses.</div>
        <span class="card-tech" style="color:#E0005A;background:rgba(224,0,90,0.07);border:1px solid rgba(224,0,90,0.2)">RRF Fusion</span>
      </div>

      <div class="card">
        <div class="card-num">04 &mdash; RERANKING</div>
        <div class="card-title">Cross-Encoder Precision</div>
        <div class="card-body">Top 20 candidates re-scored with a cross-encoder model. Only the highest-confidence 5 reach the generation layer.</div>
        <span class="card-tech" style="color:#F0A800;background:rgba(240,168,0,0.07);border:1px solid rgba(240,168,0,0.2)">ms-marco</span>
      </div>

      <div class="card">
        <div class="card-num">05 &mdash; GENERATION</div>
        <div class="card-title">Attributed Answers</div>
        <div class="card-body">Every factual claim carries an inline citation [Source, p.X]. A full References section is appended to every response, always.</div>
        <span class="card-tech" style="color:#00AAFF;background:rgba(0,170,255,0.07);border:1px solid rgba(0,170,255,0.2)">LangGraph</span>
      </div>

      <div class="card">
        <div class="card-num">06 &mdash; SAFETY</div>
        <div class="card-title">Hard Refusal Gate</div>
        <div class="card-body">When retrieved context falls below the confidence threshold, the model issues a fixed refusal string. No speculation, no hallucination.</div>
        <span class="card-tech" style="color:#FF6030;background:rgba(255,96,48,0.07);border:1px solid rgba(255,96,48,0.2)">Threshold Gate</span>
      </div>

    </div>
  </div>

  <!-- PIPELINE -->
  <div class="section">
    <div class="sec-tag">// Architecture</div>
    <div class="sec-title">THE <span>PIPELINE</span></div>
    <div class="pipeline">
      <div class="step"><div class="step-icon">PDF</div><div class="step-label">Parse</div></div>
      <div class="arrow">&rarr;</div>
      <div class="step"><div class="step-icon">SPLIT</div><div class="step-label">Chunk</div></div>
      <div class="arrow">&rarr;</div>
      <div class="step"><div class="step-icon">EMBED</div><div class="step-label">Vector</div></div>
      <div class="arrow">&rarr;</div>
      <div class="step"><div class="step-icon">BM25</div><div class="step-label">Keyword</div></div>
      <div class="arrow">&rarr;</div>
      <div class="step"><div class="step-icon">RRF</div><div class="step-label">Fuse</div></div>
      <div class="arrow">&rarr;</div>
      <div class="step"><div class="step-icon">RANK</div><div class="step-label">Rerank</div></div>
      <div class="arrow">&rarr;</div>
      <div class="step"><div class="step-icon">LLM</div><div class="step-label">Generate</div></div>
      <div class="arrow">&rarr;</div>
      <div class="step"><div class="step-icon">CITE</div><div class="step-label">Attribute</div></div>
    </div>
  </div>

  <!-- TECH STACK -->
  <div class="section">
    <div class="sec-tag">// Stack</div>
    <div class="sec-title">BUILT <span>WITH</span></div>
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
      <span class="tag tg">tiktoken</span>
    </div>
  </div>

  <!-- FOOTER -->
  <footer>
    <span>NeuralDoc &mdash; Production RAG System</span>
    <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
  </footer>

</div>
</body>
</html>"""

components.html(page, height=3800, scrolling=True)