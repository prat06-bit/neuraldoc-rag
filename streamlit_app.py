import requests
import streamlit as st
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from chat_history import (save_conversation, load_all_conversations,
                               load_conversation, export_as_markdown)
    from analytics import record_query, get_stats
except ImportError:
    def save_conversation(m, t=None): return ""
    def load_all_conversations(): return []
    def load_conversation(cid): return []
    def export_as_markdown(m, title=""): return "\n".join(f"{x['role']}: {x['content']}" for x in m)
    def record_query(q, lat, ref, model=""): pass
    def get_stats(): return {"total_queries":0,"answered":0,"refused":0,"refusal_rate":0,"avg_latency_ms":0,"recent":[]}

st.set_page_config(page_title="NeuralDoc", page_icon="N", layout="wide",
                   initial_sidebar_state="collapsed")

for k,v in [("page","landing"),("messages",[]),("active_conv_id",None),
            ("show_analytics",False),("tab","chat")]:
    if k not in st.session_state:
        st.session_state[k] = v

API_BASE = "http://localhost:8000"

if st.query_params.get("launch") == "1":
    st.query_params.clear()
    st.session_state.page = "chat"
    st.rerun()

st.html("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital,wght@0,400;1,400&family=JetBrains+Mono:wght@400;500&display=swap');
:root{
  --bg:#F6F5FF; --s:#FFFFFF; --s2:#F0EEFF; --s3:#EAE7FF;
  --v:#7C3AED; --v2:#6D28D9; --v3:#8B5CF6;
  --v-10:rgba(124,58,237,0.10); --v-15:rgba(124,58,237,0.15);
  --v-20:rgba(124,58,237,0.20); --v-pill:#EDE9FE; --v-pill-b:#DDD6FE;
  --cyan:#06B6D4; --pink:#EC4899; --green:#10B981;
  --t1:#1E1B4B; --t2:#4C4888; --t3:#9CA3AF;
  --bd:rgba(124,58,237,0.12); --bd2:rgba(0,0,0,0.06);
  --sh:0 1px 3px rgba(124,58,237,0.08),0 4px 16px rgba(124,58,237,0.06);
  --sh2:0 8px 32px rgba(124,58,237,0.14),0 2px 8px rgba(0,0,0,0.04);
  --r:10px; --r2:16px; --r3:24px; --rf:9999px;
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{font-family:'Plus Jakarta Sans',sans-serif!important;background:var(--bg)!important;color:var(--t1)!important;}
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
    
#LANDING PAGE

if st.session_state.page == "landing":
    st.html("""
<style>
[data-testid="stAppViewContainer"]{background:var(--bg)!important;}

.land{
  min-height:100vh;
  background:var(--bg);
  position:relative;overflow:hidden;
}
.land::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 55% 50% at 15% 10%,rgba(167,139,250,0.18),transparent 60%),
    radial-gradient(ellipse 45% 45% at 85% 85%,rgba(6,182,212,0.10),transparent 55%),
    radial-gradient(ellipse 35% 35% at 50% 50%,rgba(236,72,153,0.06),transparent 55%);
}

.nav{
  position:relative;z-index:10;
  display:flex;align-items:center;justify-content:space-between;
  max-width:1200px;margin:0 auto;padding:28px 56px 0;
  animation:fD .5s ease both;
}
@keyframes fD{from{opacity:0;transform:translateY(-12px);}to{opacity:1;transform:translateY(0);}}
.logo{
  font-family:'Instrument Serif',serif;font-size:22px;color:var(--t1);
  display:flex;align-items:center;gap:8px;
}
.logo-dot{width:9px;height:9px;border-radius:50%;background:var(--v);}
.nav-pill{
  font-family:'Plus Jakarta Sans',sans-serif;font-size:12px;font-weight:600;
  color:var(--v);text-transform:uppercase;letter-spacing:0.08em;
  border:1px solid var(--v-pill-b);background:var(--v-pill);
  padding:6px 16px;border-radius:var(--rf);
}

/* HERO */
.hero{
  position:relative;z-index:10;
  max-width:820px;margin:0 auto;
  padding:80px 56px 0;text-align:center;
  animation:fU .7s ease .15s both;
}
@keyframes fU{from{opacity:0;transform:translateY(22px);}to{opacity:1;transform:translateY(0);}}
.h-eyebrow{
  display:inline-flex;align-items:center;gap:6px;
  font-size:12px;font-weight:600;color:var(--v);
  border:1px solid var(--v-pill-b);background:var(--v-pill);
  padding:5px 16px;border-radius:var(--rf);margin-bottom:28px;
  letter-spacing:0.04em;
}
.h-dot{width:5px;height:5px;border-radius:50%;background:var(--v);animation:dp 1.8s ease-in-out infinite;}
@keyframes dp{0%,100%{opacity:1;}50%{opacity:0.2;}}
.h1{
  font-family:'Instrument Serif',serif;
  font-size:clamp(44px,6vw,68px);font-weight:400;
  color:var(--t1);line-height:1.06;letter-spacing:-1px;margin-bottom:8px;
}
.h1 em{font-style:italic;color:var(--v);}
.h-sub{
  font-size:17px;color:var(--t2);line-height:1.8;
  max-width:560px;margin:0 auto 44px;font-weight:400;
}
.h-sub b{color:var(--t1);font-weight:600;}

/* CTA — form submit for reliable navigation */
.cta-form{display:flex;justify-content:center;margin-bottom:0;}
.btn-primary{
  display:inline-flex;align-items:center;justify-content:center;gap:8px;
  height:52px;padding:0 40px;
  background:var(--v);color:#fff;border:none;border-radius:var(--rf);
  font-family:'Plus Jakarta Sans',sans-serif;font-size:16px;font-weight:600;
  cursor:pointer;letter-spacing:0.01em;
  box-shadow:0 4px 20px rgba(124,58,237,0.32);
  transition:background 0.18s,transform 0.15s,box-shadow 0.18s;
}
.btn-primary:hover{background:var(--v2);transform:translateY(-2px);box-shadow:0 8px 28px rgba(124,58,237,0.42);}
.btn-primary:active{transform:scale(0.97);}

/* STATS */
.stats{
  position:relative;z-index:10;
  display:flex;max-width:780px;margin:52px auto 0;
  background:var(--s);border:1px solid var(--bd2);border-radius:var(--r3);
  overflow:hidden;box-shadow:var(--sh);
  animation:fU .7s ease .3s both;
}
.stat{
  flex:1;padding:26px 12px;text-align:center;
  border-right:1px solid var(--bd2);transition:background 0.18s;
}
.stat:last-child{border-right:none;}
.stat:hover{background:var(--v-pill);}
.sv{
  font-family:'Instrument Serif',serif;font-size:32px;
  color:var(--v);line-height:1;margin-bottom:5px;
}
.sl{font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.1em;text-transform:uppercase;}

/* SECTION */
.sec{position:relative;z-index:10;max-width:1200px;margin:88px auto 0;padding:0 56px;}
.sec-label{font-size:11px;font-weight:700;color:var(--v);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;}
.sec-title{font-family:'Instrument Serif',serif;font-size:38px;color:var(--t1);margin-bottom:36px;font-weight:400;}
.sec-title em{font-style:italic;color:var(--v);}

/* FEATURE CARDS */
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
.card{
  background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
  padding:26px;box-shadow:var(--sh);
  transition:transform 0.22s,box-shadow 0.22s,border-color 0.22s;
}
.card:hover{transform:translateY(-5px);box-shadow:var(--sh2);border-color:var(--v-pill-b);}
.card-num{font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;}
.card-title{font-size:15px;font-weight:700;color:var(--t1);margin-bottom:7px;}
.card-body{font-size:13px;color:var(--t2);line-height:1.75;}
.card-tag{display:inline-block;margin-top:13px;font-size:10px;font-weight:700;
  padding:3px 10px;border-radius:var(--rf);border:1px solid;}
.tg{color:var(--green);border-color:rgba(16,185,129,0.3);background:rgba(16,185,129,0.08);}
.tv{color:var(--v);border-color:var(--v-pill-b);background:var(--v-pill);}
.tc{color:var(--cyan);border-color:rgba(6,182,212,0.3);background:rgba(6,182,212,0.08);}
.tp{color:var(--pink);border-color:rgba(236,72,153,0.3);background:rgba(236,72,153,0.08);}
.tam{color:#F59E0B;border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.08);}

/* NEW FEATURES HIGHLIGHT */
.feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
.feat{
  background:linear-gradient(135deg,var(--v-pill),var(--s2));
  border:1px solid var(--v-pill-b);border-radius:var(--r2);
  padding:24px;transition:transform 0.2s,box-shadow 0.2s;
}
.feat:hover{transform:translateY(-3px);box-shadow:var(--sh2);}
.feat-icon{font-size:22px;margin-bottom:12px;}
.feat-title{font-size:14px;font-weight:700;color:var(--t1);margin-bottom:6px;}
.feat-body{font-size:12px;color:var(--t2);line-height:1.7;}
.feat-badge{display:inline-block;margin-top:10px;font-size:10px;font-weight:700;
  color:var(--v);background:var(--s);border:1px solid var(--v-pill-b);
  padding:3px 10px;border-radius:var(--rf);}

/* PIPELINE */
.pipe-row{
  display:flex;align-items:center;justify-content:space-between;
  background:var(--s);border:1px solid var(--bd2);
  border-radius:var(--r2);padding:28px 36px;
  box-shadow:var(--sh);
}
.p-step{
  display:flex;flex-direction:column;align-items:center;gap:5px;
  flex:1;padding:8px 4px;border-radius:var(--r);transition:all 0.18s;cursor:default;
}
.p-step:hover{background:var(--v-pill);transform:translateY(-2px);}
.p-lbl{font-size:11px;font-weight:700;color:var(--t1);letter-spacing:0.04em;}
.p-sub{font-size:10px;color:var(--t3);}
.p-arr{color:var(--v-pill-b);font-size:14px;flex-shrink:0;
  animation:aP 2.5s ease-in-out infinite;}
@keyframes aP{0%,100%{color:var(--v-pill-b);}50%{color:var(--v);}}

/* STACK TAGS */
.tags{display:flex;flex-wrap:wrap;gap:9px;}
.tag{
  padding:6px 14px;font-size:11px;font-weight:600;
  border-radius:var(--rf);border:1px solid;
  transition:transform 0.15s;cursor:default;
}
.tag:hover{transform:translateY(-2px);}

/* FOOTER */
.foot{
  position:relative;z-index:10;max-width:1200px;
  margin:72px auto 0;padding:22px 56px 64px;
  border-top:1px solid var(--bd2);
  display:flex;justify-content:space-between;
  align-items:center;flex-wrap:wrap;gap:10px;
}
.foot span{font-size:12px;color:var(--t3);}
</style>

<div class="land">
<div class="wrap" style="position:relative;z-index:1;">

  <!-- NAV -->
  <nav class="nav">
    <div class="logo">
      <div class="logo-dot"></div>NeuralDoc
    </div>
    <div class="nav-pill">Production RAG v1.0</div>
  </nav>

  <!-- HERO -->
  <section class="hero">
    <div class="h-eyebrow">
      <span class="h-dot"></span>Zero hallucination tolerance
    </div>
    <h1 class="h1">Ask anything.<br><em>Know everything.</em></h1>
    <p class="h-sub">
      A <b>production-grade</b> RAG system with <b>inline citations</b>,
      hybrid retrieval, persistent chat history, live analytics,
      and a hard refusal trigger — no guessing, ever.
    </p>
    <form class="cta-form" method="get" action="">
      <input type="hidden" name="launch" value="1">
      <button type="submit" class="btn-primary">Open App &nbsp;&#8594;</button>
    </form>
  </section>

  <!-- STATS -->
  <div class="stats">
    <div class="stat"><div class="sv">0%</div><div class="sl">Hallucination Rate</div></div>
    <div class="stat"><div class="sv">3&times;</div><div class="sl">Retrieval Methods</div></div>
    <div class="stat"><div class="sv">100%</div><div class="sl">Local &amp; Private</div></div>
    <div class="stat"><div class="sv">&infin;</div><div class="sl">Documents</div></div>
  </div>

  <!-- NEW FEATURES -->
  <div class="sec">
    <div class="sec-label">New in v1.0</div>
    <div class="sec-title">Three <em>new</em> features</div>
    <div class="feat-grid">

      <div class="feat">
        <div class="feat-icon" style="color:var(--v);font-size:20px;font-weight:700;font-family:'Instrument Serif',serif;font-style:italic;">&#x1F4AC;</div>
        <div class="feat-title">Persistent Chat History</div>
        <div class="feat-body">Every conversation is auto-saved to disk. Load any past chat in one click. Never lose a research session again.</div>
        <span class="feat-badge">chat_history.py</span>
      </div>

      <div class="feat">
        <div class="feat-icon" style="color:var(--cyan);font-size:20px;font-weight:700;font-family:'Instrument Serif',serif;font-style:italic;">&#x2B07;</div>
        <div class="feat-title">Export as Markdown</div>
        <div class="feat-body">Download any conversation as a clean Markdown file — with all source citations, refusal flags, and latency metadata included.</div>
        <span class="feat-badge" style="color:var(--cyan);border-color:rgba(6,182,212,0.3);background:rgba(6,182,212,0.08);">Export MD</span>
      </div>

      <div class="feat">
        <div class="feat-icon" style="color:var(--pink);font-size:20px;font-weight:700;font-family:'Instrument Serif',serif;font-style:italic;">&#x1F4CA;</div>
        <div class="feat-title">Live Query Analytics</div>
        <div class="feat-body">Real-time dashboard tracking total queries, refusal rate, and avg latency. Built-in MLOps observability for your RAG pipeline.</div>
        <span class="feat-badge" style="color:var(--pink);border-color:rgba(236,72,153,0.3);background:rgba(236,72,153,0.08);">analytics.py</span>
      </div>

    </div>
  </div>

  <!-- 6 PILLARS -->
  <div class="sec">
    <div class="sec-label">Capabilities</div>
    <div class="sec-title">Six <em>pillars</em> of precision</div>
    <div class="cards">
      <div class="card"><div class="card-num">01 &mdash; Ingestion</div><div class="card-title">Smart PDF Parsing</div><div class="card-body">Multi-column layouts, embedded tables, complex structures. Headers and footers stripped automatically.</div><span class="card-tag tg">pdfplumber</span></div>
      <div class="card"><div class="card-num">02 &mdash; Chunking</div><div class="card-title">Semantic Chunking</div><div class="card-body">Header-aware 500–800 token chunks. Source, page, and section breadcrumb on every chunk.</div><span class="card-tag tv">tiktoken</span></div>
      <div class="card"><div class="card-num">03 &mdash; Retrieval</div><div class="card-title">Hybrid Search</div><div class="card-body">BM25 keyword fused with dense vector search via Reciprocal Rank Fusion. Catches what either alone misses.</div><span class="card-tag tc">RRF Fusion</span></div>
      <div class="card"><div class="card-num">04 &mdash; Reranking</div><div class="card-title">Cross-Encoder Precision</div><div class="card-body">Top 20 candidates re-scored. Only the highest-confidence 5 reach the generation layer.</div><span class="card-tag tam">ms-marco</span></div>
      <div class="card"><div class="card-num">05 &mdash; Generation</div><div class="card-title">Attributed Answers</div><div class="card-body">Every claim carries an inline citation [Source, p.X]. Full References section appended to every response.</div><span class="card-tag tv">LangGraph</span></div>
      <div class="card"><div class="card-num">06 &mdash; Safety</div><div class="card-title">Hard Refusal Gate</div><div class="card-body">Context below confidence threshold triggers a fixed refusal. No speculation, no hallucination, by design.</div><span class="card-tag tp">Threshold Gate</span></div>
    </div>
  </div>

  <!-- PIPELINE -->
  <div class="sec">
    <div class="sec-label">Architecture</div>
    <div class="sec-title">The <em>pipeline</em></div>
    <div class="pipe-row">
      <div class="p-step"><div class="p-lbl">Parse</div><div class="p-sub">pdfplumber</div></div>
      <div class="p-arr">&#8594;</div>
      <div class="p-step"><div class="p-lbl">Chunk</div><div class="p-sub">tiktoken</div></div>
      <div class="p-arr">&#8594;</div>
      <div class="p-step"><div class="p-lbl">Embed</div><div class="p-sub">miniLM</div></div>
      <div class="p-arr">&#8594;</div>
      <div class="p-step"><div class="p-lbl">BM25</div><div class="p-sub">keyword</div></div>
      <div class="p-arr">&#8594;</div>
      <div class="p-step"><div class="p-lbl">Fuse</div><div class="p-sub">RRF</div></div>
      <div class="p-arr">&#8594;</div>
      <div class="p-step"><div class="p-lbl">Rerank</div><div class="p-sub">cross-enc</div></div>
      <div class="p-arr">&#8594;</div>
      <div class="p-step"><div class="p-lbl">Generate</div><div class="p-sub">llama3.1</div></div>
      <div class="p-arr">&#8594;</div>
      <div class="p-step"><div class="p-lbl">Cite</div><div class="p-sub">attributed</div></div>
    </div>
  </div>

  <!-- STACK -->
  <div class="sec">
    <div class="sec-label">Stack</div>
    <div class="sec-title">Built <em>with</em></div>
    <div class="tags">
      <span class="tag tg">pdfplumber</span><span class="tag tg">ChromaDB</span>
      <span class="tag tg">sentence-transformers</span>
      <span class="tag tv">LangGraph</span><span class="tag tv">langchain-ollama</span>
      <span class="tag tv">llama3.1:8b</span>
      <span class="tag tc">BM25 + RRF</span><span class="tag tc">cross-encoder</span>
      <span class="tag tp">FastAPI</span><span class="tag tp">Streamlit</span>
      <span class="tag tam">Python 3.14</span>
    </div>
  </div>

  <!-- FOOTER -->
  <div class="foot">
    <span>NeuralDoc &mdash; Production RAG System</span>
    <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
  </div>

</div>
</div>""")


# ═══════════════════════════════════════════════════════════════════════════
# CHAT / APP PAGE
# ═══════════════════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    [data-testid="stAppViewContainer"]{background:var(--bg)!important;}
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container{
      padding:0!important;background:transparent!important;max-width:100%!important;}

    /* Inputs */
    .stTextInput input{
      background:var(--s)!important;border:1.5px solid var(--bd)!important;
      border-radius:var(--r)!important;color:var(--t1)!important;
      font-family:'Plus Jakarta Sans',sans-serif!important;font-size:14px!important;
      padding:12px 16px!important;transition:all 0.15s!important;
    }
    .stTextInput input:focus{
      border-color:var(--v)!important;
      box-shadow:0 0 0 3px rgba(124,58,237,0.12)!important;outline:none!important;
    }
    .stTextInput input::placeholder{color:var(--t3)!important;}
    .stTextInput label,.stFileUploader label{display:none!important;}

    /* Buttons */
    .stButton>button{
      background:var(--v)!important;color:#fff!important;
      border:none!important;border-radius:var(--r)!important;
      font-family:'Plus Jakarta Sans',sans-serif!important;
      font-weight:600!important;font-size:13px!important;
      padding:11px 0!important;
      box-shadow:0 2px 8px rgba(124,58,237,0.2)!important;
      transition:all 0.15s!important;
    }
    .stButton>button:hover{
      background:var(--v2)!important;transform:translateY(-1px)!important;
      box-shadow:0 4px 16px rgba(124,58,237,0.3)!important;
    }
    .stButton>button:active{transform:scale(0.97)!important;}

    /* File uploader */
    [data-testid="stFileUploaderDropzone"]{
      background:var(--s)!important;border:1.5px dashed var(--v-pill-b)!important;
      border-radius:var(--r2)!important;transition:all 0.18s!important;
    }
    [data-testid="stFileUploaderDropzone"]:hover{
      border-color:var(--v)!important;background:var(--v-pill)!important;
    }
    [data-testid="stFileUploaderDropzone"] *{color:var(--t2)!important;}

    /* Download button */
    [data-testid="stDownloadButton"]>button{
      background:var(--s)!important;color:var(--v)!important;
      border:1.5px solid var(--v-pill-b)!important;border-radius:var(--r)!important;
      font-weight:600!important;font-size:13px!important;
      box-shadow:none!important;
    }
    [data-testid="stDownloadButton"]>button:hover{
      background:var(--v-pill)!important;transform:translateY(-1px)!important;
    }
    hr{border-color:var(--bd2)!important;}
    </style>""")

    def get_health():
        try:
            r=requests.get(f"{API_BASE}/health",timeout=3).json()
            r["_reachable"]=True; return r
        except:
            return {"pipeline_ready":False,"total_chunks":0,"indexed_files":[],"_reachable":False}

    h=get_health()
    api_ok=h.get("_reachable",False); ready=h.get("pipeline_ready",False)
    chunks=h.get("total_chunks",0);   files=h.get("indexed_files",[])

    if ready:   bs="color:#059669;background:#ECFDF5;border-color:#A7F3D0;"; bd="#059669"; bt=f"Ready &middot; {chunks} chunks"
    elif api_ok:bs="color:#D97706;background:#FEF3C7;border-color:#FDE68A;"; bd="#D97706"; bt="API online &mdash; No docs"
    else:       bs="color:#DC2626;background:#FEE2E2;border-color:#FECACA;"; bd="#DC2626"; bt="API offline"

    # ── TOPBAR ────────────────────────────────────────────────────────────────
    st.html(f"""
    <div style="
      display:flex;align-items:center;justify-content:space-between;
      height:60px;padding:0 48px;
      background:rgba(255,255,255,0.92);backdrop-filter:blur(12px);
      border-bottom:1px solid var(--bd2);
      position:sticky;top:0;z-index:200;
    ">
      <div style="display:flex;align-items:center;gap:8px;">
        <div style="width:8px;height:8px;border-radius:50%;background:var(--v);"></div>
        <span style="font-family:'Instrument Serif',serif;font-size:18px;color:var(--t1);">NeuralDoc</span>
      </div>
      <div style="display:inline-flex;align-items:center;gap:6px;
        font-size:12px;font-weight:600;padding:5px 14px;border-radius:var(--rf);
        border:1.5px solid;{bs}">
        <div style="width:5px;height:5px;border-radius:50%;background:{bd};flex-shrink:0;"></div>
        {bt}
      </div>
    </div>""")

    # ── INNER TABS (Chat / Analytics) ─────────────────────────────────────────
    st.html('<div style="max-width:1400px;margin:0 auto;padding:28px 48px 48px;">')

    tc1, tc2, tc3, tc4, tc5 = st.columns([1, 1, 1, 1, 5])
    with tc1:
        if st.button("← Home", key="home_btn", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.page = "landing"
            st.rerun()
    with tc2:
        if st.button("Clear Chat", key="clr_btn", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.messages = []
            st.rerun()
    with tc3:
        if st.session_state.messages:
            md = export_as_markdown(st.session_state.messages, "NeuralDoc Chat")
            st.download_button(
                "Export .md", data=md,
                file_name=f"neuraldoc_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown", use_container_width=True, key="exp_md"
            )
        else:
            st.html('<div style="height:44px;"></div>')
    with tc4:
        label = "Hide Stats" if st.session_state.show_analytics else "Analytics"
        if st.button(label, key="analytics_btn", use_container_width=True):
            st.session_state.show_analytics = not st.session_state.show_analytics
            st.rerun()

    st.html('<div style="height:20px;"></div>')

    if st.session_state.show_analytics:
        stats = get_stats()

        recent_html = ""
        if stats["recent"]:
            rows = ""
            for q in stats["recent"]:
                icon = "✕" if q["refused"] else "✓"
                query_text = q["query"][:72]
                lat = q["latency_ms"]
                rows += (
                    f'<div style="display:flex;align-items:center;justify-content:space-between;'
                    f'padding:7px 10px;border-radius:var(--r);margin-bottom:4px;background:var(--bg);">'
                    f'<span style="font-size:12px;color:var(--t2);">{icon}&nbsp;{query_text}</span>'
                    f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;'
                    f'color:var(--t3);">{lat}ms</span></div>'
                )
            recent_html = (
                '<div style="border-top:1px solid var(--bd2);padding-top:16px;">'
                '<div style="font-size:10px;font-weight:700;color:var(--t3);'
                'letter-spacing:0.08em;text-transform:uppercase;margin-bottom:10px;">'
                'Recent queries</div>'
                + rows +
                '</div>'
            )

        st.html(f"""
        <div style="
          background:var(--s);border:1.5px solid var(--v-pill-b);
          border-radius:var(--r2);padding:28px 32px;
          margin-bottom:24px;box-shadow:var(--sh);
        ">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
            <div style="font-size:11px;font-weight:700;color:var(--v);
              letter-spacing:0.1em;text-transform:uppercase;">Query Analytics</div>
            <div style="font-size:11px;color:var(--t3);">Live &mdash; updated per query</div>
          </div>
          <div style="display:flex;gap:0;background:var(--bg);border:1px solid var(--bd2);
            border-radius:var(--r2);overflow:hidden;margin-bottom:20px;">
            <div style="flex:1;padding:20px 16px;text-align:center;border-right:1px solid var(--bd2);">
              <div style="font-family:'Instrument Serif',serif;font-size:32px;color:var(--v);line-height:1;margin-bottom:4px;">{stats['total_queries']}</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.08em;text-transform:uppercase;">Total Queries</div>
            </div>
            <div style="flex:1;padding:20px 16px;text-align:center;border-right:1px solid var(--bd2);">
              <div style="font-family:'Instrument Serif',serif;font-size:32px;color:#059669;line-height:1;margin-bottom:4px;">{stats['answered']}</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.08em;text-transform:uppercase;">Answered</div>
            </div>
            <div style="flex:1;padding:20px 16px;text-align:center;border-right:1px solid var(--bd2);">
              <div style="font-family:'Instrument Serif',serif;font-size:32px;color:#DC2626;line-height:1;margin-bottom:4px;">{stats['refused']}</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.08em;text-transform:uppercase;">Refused</div>
            </div>
            <div style="flex:1;padding:20px 16px;text-align:center;border-right:1px solid var(--bd2);">
              <div style="font-family:'Instrument Serif',serif;font-size:32px;color:#D97706;line-height:1;margin-bottom:4px;">{stats['refusal_rate']}%</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.08em;text-transform:uppercase;">Refusal Rate</div>
            </div>
            <div style="flex:1;padding:20px 16px;text-align:center;">
              <div style="font-family:'Instrument Serif',serif;font-size:32px;color:var(--cyan);line-height:1;margin-bottom:4px;">{int(stats['avg_latency_ms'])}ms</div>
              <div style="font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.08em;text-transform:uppercase;">Avg Latency</div>
            </div>
          </div>
          {recent_html}
        </div>""")

    # ── MAIN COLUMNS ──────────────────────────────────────────────────────────
    col_chat, col_right = st.columns([3, 2], gap="large")

    # ── RIGHT: Upload + History ───────────────────────────────────────────────
    with col_right:
        # Upload card
        st.html("""<div style="
          background:var(--s);border:1px solid var(--bd2);
          border-radius:var(--r2);padding:28px;
          box-shadow:var(--sh);margin-bottom:16px;
        ">""")
        uh1, uh2 = st.columns([3, 1])
        with uh1:
            st.html("""<div style="margin-bottom:16px;">
              <div style="font-size:10px;font-weight:700;color:var(--v);
                letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">Knowledge Base</div>
              <div style="font-family:'Instrument Serif',serif;font-size:22px;color:var(--t1);">
                Upload <em style="font-style:italic;color:var(--v);">documents</em>
              </div>
            </div>""")
        with uh2:
            st.html('<div style="height:26px;"></div>')
            if st.button("Clear", key="clear_idx", use_container_width=True):
                try:
                    r=requests.delete(f"{API_BASE}/index",timeout=15)
                    if r.status_code==200: st.success("Index cleared."); st.rerun()
                    else: st.error(f"Error: {r.text}")
                except: st.error("API offline.")

        st.html("""<div style="
          background:var(--v-pill);border:1.5px dashed var(--v-pill-b);
          border-radius:var(--r2);padding:18px 16px;
          margin-bottom:12px;text-align:center;
          transition:border-color 0.18s,background 0.18s;"
          onmouseover="this.style.borderColor='var(--v)';this.style.background='var(--s3)'"
          onmouseout="this.style.borderColor='var(--v-pill-b)';this.style.background='var(--v-pill)'">
          <div style="font-size:13px;font-weight:500;color:var(--t1);margin-bottom:4px;">
            Drop your PDF below</div>
          <div style="font-size:11px;color:var(--t3);">
            Parsed &#8594; Chunked &#8594; Embedded &#8594; Indexed</div>
        </div>""")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")
        if uploaded:
            st.html(f"""<div style="
              background:var(--s);border:1px solid #A7F3D0;
              border-radius:var(--r);padding:10px 14px;margin-bottom:10px;
            ">
              <div style="font-size:13px;font-weight:600;color:var(--t1);">{uploaded.name}</div>
              <div style="font-size:11px;color:#059669;margin-top:2px;">{uploaded.size//1024} KB</div>
            </div>""")
            if st.button("Index Document", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing PDF..."):
                    try:
                        resp=requests.post(f"{API_BASE}/ingest",
                          files={"file":(uploaded.name,uploaded,"application/pdf")},timeout=120)
                        if resp.status_code==200:
                            d=resp.json()
                            st.success(f"Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                            st.rerun()
                        else: st.error(f"Error: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("API offline. Run: uv run uvicorn api:app --reload --port 8000")
                    except Exception as e: st.error(str(e))

        if files:
            st.html("""<div style="font-size:10px;font-weight:700;color:var(--t3);
              letter-spacing:0.08em;text-transform:uppercase;margin:12px 0 7px;">Indexed files</div>""")
            for f in files:
                fname=f.replace("\\","/").split("/")[-1]
                st.html(f"""<div style="
                  background:var(--bg);border:1px solid var(--bd2);
                  border-radius:var(--r);padding:8px 13px;margin-bottom:5px;
                  display:flex;align-items:center;">
                  <span style="font-size:12px;font-weight:500;color:var(--t1);flex:1;">{fname}</span>
                  <span style="font-size:10px;font-weight:700;padding:2px 8px;
                    border-radius:var(--rf);color:#059669;background:#ECFDF5;
                    border:1px solid #A7F3D0;">indexed</span>
                </div>""")

        st.html("""<div style="
          margin-top:14px;background:var(--bg);
          border:1px solid var(--bd2);border-radius:var(--r);padding:14px 16px;
        ">
          <div style="font-size:10px;font-weight:700;color:var(--t3);
            letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;">Tips</div>
          <div style="font-size:12px;color:var(--t2);line-height:1.9;">
            Click <b style="color:var(--v);">Clear</b> before switching documents.<br>
            Ask precise questions for best citation accuracy.<br>
            Every answer includes inline source references.<br>
            Unanswerable queries return a refusal, not a guess.
          </div>
        </div>""")
        st.html('</div>')

        # Chat History card
        convs = load_all_conversations()
        if convs:
            st.html("""<div style="
              background:var(--s);border:1px solid var(--bd2);
              border-radius:var(--r2);padding:24px 24px 16px;
              box-shadow:var(--sh);
            ">
              <div style="font-size:10px;font-weight:700;color:var(--v);
                letter-spacing:0.1em;text-transform:uppercase;margin-bottom:14px;">
                Chat History</div>""")
            for i, conv in enumerate(convs[:5]):
                ts = conv["timestamp"][:10]
                title = conv["title"][:34] + ("…" if len(conv["title"]) > 34 else "")
                n = len([m for m in conv["messages"] if m["role"]=="user"])
                hc1, hc2 = st.columns([4, 1])
                with hc1:
                    st.html(f"""<div style="
                      padding:8px 10px;border-radius:var(--r);cursor:pointer;
                      border:1px solid var(--bd2);margin-bottom:5px;
                      transition:border-color 0.15s,background 0.15s;"
                      onmouseover="this.style.borderColor='var(--v-pill-b)';this.style.background='var(--v-pill)'"
                      onmouseout="this.style.borderColor='var(--bd2)';this.style.background=''">
                      <div style="font-size:12px;font-weight:500;color:var(--t1);">{title}</div>
                      <div style="font-size:10px;color:var(--t3);margin-top:2px;">
                        {ts} &middot; {n} {'query' if n==1 else 'queries'}</div>
                    </div>""")
                with hc2:
                    if st.button("Load", key=f"ld_{conv['id']}_{i}", use_container_width=True):
                        st.session_state.messages = load_conversation(conv["id"])
                        st.rerun()
            st.html('</div>')

    # ── LEFT: Chat ────────────────────────────────────────────────────────────
    with col_chat:
        st.html("""<div style="
          background:var(--s);border:1px solid var(--bd2);
          border-radius:var(--r2);padding:28px 28px 22px;
          box-shadow:var(--sh);
        ">""")

        st.html(f"""
        <div style="display:flex;align-items:flex-start;
          justify-content:space-between;margin-bottom:22px;">
          <div>
            <div style="font-size:10px;font-weight:700;color:var(--v);
              letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">Document QA</div>
            <div style="font-family:'Instrument Serif',serif;font-size:28px;
              color:var(--t1);line-height:1.1;">
              Ask your <em style="font-style:italic;color:var(--v);">documents</em>
            </div>
          </div>
          <div style="display:flex;gap:7px;align-items:center;padding-top:16px;flex-shrink:0;">
            <span style="font-size:12px;font-weight:600;color:var(--v);
              background:var(--v-pill);border:1px solid var(--v-pill-b);
              padding:4px 12px;border-radius:var(--rf);">{chunks} chunks</span>
            <span style="font-size:12px;font-weight:700;padding:4px 12px;
              border-radius:var(--rf);border:1.5px solid;
              {'color:#059669;background:#ECFDF5;border-color:#A7F3D0;' if ready else 'color:#DC2626;background:#FEE2E2;border-color:#FECACA;'}">
              {'Ready' if ready else 'Not ready'}</span>
          </div>
        </div>""")

        # Messages
        if st.session_state.messages:
            html=""
            for m in st.session_state.messages:
                if m["role"]=="user":
                    html+=f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
                      <div style="max-width:74%;padding:12px 16px;
                        background:var(--v);color:#fff;
                        border-radius:16px 3px 16px 16px;
                        font-size:14px;line-height:1.65;
                        font-family:'Plus Jakarta Sans',sans-serif;
                        box-shadow:0 2px 10px rgba(124,58,237,0.2);">
                        {m['content']}</div></div>"""
                else:
                    refs=""
                    if m.get("references"):
                        refs='<div style="margin-top:9px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs+=f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:var(--rf);color:var(--cyan);background:rgba(6,182,212,0.08);border:1px solid rgba(6,182,212,0.25);">{ref}</span>'
                        refs+="</div>"
                    rfsd=""
                    if m.get("refused"):
                        rfsd='<div style="margin-top:7px;font-size:12px;font-weight:600;color:#DC2626;background:#FEE2E2;border:1px solid #FECACA;padding:5px 11px;border-radius:var(--r);display:inline-block;">Insufficient evidence — refusal triggered</div>'
                    lat=""
                    if m.get("latency_ms"):
                        lat=f'<div style="margin-top:4px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:var(--t3);">{m["latency_ms"]} ms</div>'
                    html+=f"""
                    <div style="display:flex;margin-bottom:14px;gap:9px;align-items:flex-start;">
                      <div style="width:26px;height:26px;border-radius:7px;flex-shrink:0;
                        margin-top:2px;background:var(--v-pill);
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Instrument Serif',serif;font-size:13px;
                        color:var(--v);border:1px solid var(--v-pill-b);">N</div>
                      <div style="max-width:86%;padding:13px 16px;
                        background:var(--bg);border:1px solid var(--bd2);
                        border-radius:3px 16px 16px 16px;
                        font-size:14px;color:var(--t1);line-height:1.75;
                        font-family:'Plus Jakarta Sans',sans-serif;
                        box-shadow:var(--sh);">
                        {m['content']}{refs}{rfsd}{lat}</div></div>"""
            st.html(f"""<div style="max-height:48vh;overflow-y:auto;margin-bottom:16px;
              padding:2px;scrollbar-width:thin;scrollbar-color:var(--v-pill-b) transparent;">
              {html}</div>""")
        else:
            st.html("""
            <div style="text-align:center;padding:52px 24px 40px;
              background:var(--bg);border:1px solid var(--bd2);
              border-radius:var(--r2);margin-bottom:16px;">
              <div style="font-family:'Instrument Serif',serif;font-size:22px;
                color:var(--t1);margin-bottom:8px;">Ask anything</div>
              <div style="font-size:13px;color:var(--t3);max-width:300px;
                margin:0 auto 20px;line-height:1.7;">
                Upload a PDF on the right, then ask questions here.
                Every answer is cited.</div>
              <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
                <span style="font-size:12px;font-weight:500;color:var(--v);
                  background:var(--v-pill);border:1px solid var(--v-pill-b);
                  padding:6px 14px;border-radius:var(--rf);cursor:default;
                  transition:background 0.15s;"
                  onmouseover="this.style.background='var(--s3)'"
                  onmouseout="this.style.background='var(--v-pill)'">
                  What is the main finding?</span>
                <span style="font-size:12px;font-weight:500;color:var(--v);
                  background:var(--v-pill);border:1px solid var(--v-pill-b);
                  padding:6px 14px;border-radius:var(--rf);cursor:default;"
                  onmouseover="this.style.background='var(--s3)'"
                  onmouseout="this.style.background='var(--v-pill)'">
                  Summarise section 3</span>
                <span style="font-size:12px;font-weight:500;color:var(--v);
                  background:var(--v-pill);border:1px solid var(--v-pill-b);
                  padding:6px 14px;border-radius:var(--rf);cursor:default;"
                  onmouseover="this.style.background='var(--s3)'"
                  onmouseout="this.style.background='var(--v-pill)'">
                  What are the key risks?</span>
              </div>
            </div>""")

        # Input
        qc, bc = st.columns([6, 1])
        with qc:
            query = st.text_input("Question",
                                  placeholder="Ask anything about your documents...",
                                  label_visibility="hidden", key="q_in")
        with bc:
            ask = st.button("Send →", use_container_width=True)

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
                            record_query(query=query,latency_ms=d["latency_ms"],refused=d["refused"])
                            st.rerun()
                        else:
                            st.error(f"API error: {resp.json().get('detail',resp.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach API. Run: uv run uvicorn api:app --reload --port 8000")

        st.html('</div>')
    st.html('</div>')  
