"""Landing page — hero, features, pipeline, tech stack."""

from __future__ import annotations

import streamlit as st


def render_landing() -> None:
    """Render the full landing page."""
    st.html("""
    <style>
    .land{min-height:calc(100vh - 56px);background:var(--bg);position:relative;overflow:hidden;}
    .land::before{content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
      background:
        radial-gradient(ellipse 55% 50% at 15% 10%,rgba(167,139,250,0.18),transparent 60%),
        radial-gradient(ellipse 45% 45% at 85% 85%,rgba(6,182,212,0.10),transparent 55%),
        radial-gradient(ellipse 35% 35% at 50% 50%,rgba(236,72,153,0.06),transparent 55%);}
    .hero{position:relative;z-index:10;max-width:820px;margin:0 auto;
      padding:48px 56px 0;text-align:center;animation:fU .8s cubic-bezier(0.16,1,0.3,1) .15s both;}
    .h-eyebrow{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;
      color:var(--v);border:1px solid var(--vpb);background:var(--vp);
      padding:5px 16px;border-radius:var(--rf);margin-bottom:28px;letter-spacing:0.04em;
      animation:fU .6s cubic-bezier(0.16,1,0.3,1) .25s both;}
    .h-dot{width:5px;height:5px;border-radius:50%;background:var(--v);
      animation:dp 1.8s ease-in-out infinite;}
    .h1{font-family:'Instrument Serif',serif;font-size:clamp(44px,6vw,68px);font-weight:400;
      color:var(--t1);line-height:1.06;letter-spacing:-1px;margin-bottom:8px;
      animation:fU .8s cubic-bezier(0.16,1,0.3,1) .4s both;}
    .h1 em{font-style:italic;color:var(--v);}
    .h-sub{font-size:17px;color:var(--t2);line-height:1.8;max-width:560px;
      margin:0 auto 44px;font-weight:400;
      animation:fU .7s cubic-bezier(0.16,1,0.3,1) .55s both;}
    .h-sub b{color:var(--t1);font-weight:600;}
    .cta-wrap{display:flex;justify-content:center;margin-bottom:0;
      animation:fU .6s cubic-bezier(0.16,1,0.3,1) .7s both;}
    .btn-lnd{display:inline-flex;align-items:center;justify-content:center;gap:8px;
      height:52px;padding:0 48px;background:var(--v);color:#fff;border:none;
      border-radius:var(--rf);font-family:'Plus Jakarta Sans',sans-serif;
      font-size:16px;font-weight:600;cursor:pointer;
      box-shadow:0 4px 20px rgba(124,58,237,0.32);
      transition:background 0.18s,transform 0.15s,box-shadow 0.18s;}
    .btn-lnd:hover{background:var(--v2);transform:translateY(-2px);
      box-shadow:0 8px 28px rgba(124,58,237,0.42);}
    .btn-lnd:active{transform:scale(0.97);}
    .stats{position:relative;z-index:10;display:flex;max-width:780px;
      margin:52px auto 0;background:var(--s);border:1px solid var(--bd2);
      border-radius:var(--r3);overflow:hidden;box-shadow:var(--sh);
      animation:fU .7s ease .85s both;}
    .stat{flex:1;padding:26px 12px;text-align:center;border-right:1px solid var(--bd2);
      transition:background 0.18s;}
    .stat:last-child{border-right:none;}.stat:hover{background:var(--vp);}
    .sv{font-family:'Instrument Serif',serif;font-size:32px;color:var(--v);
      line-height:1;margin-bottom:5px;}
    .sl{font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.1em;text-transform:uppercase;}
    .sec{position:relative;z-index:10;max-width:1200px;margin:88px auto 0;padding:0 56px;}
    .sec-lbl{font-size:11px;font-weight:700;color:var(--v);letter-spacing:0.12em;
      text-transform:uppercase;margin-bottom:10px;}
    .sec-ttl{font-family:'Instrument Serif',serif;font-size:38px;color:var(--t1);
      margin-bottom:36px;font-weight:400;}
    .sec-ttl em{font-style:italic;color:var(--v);}
    .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
    .card{background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
      padding:26px;box-shadow:var(--sh);
      transition:transform 0.22s,box-shadow 0.22s,border-color 0.22s;}
    .card:hover{transform:translateY(-5px);box-shadow:var(--sh2);border-color:var(--vpb);}
    .c-num{font-size:10px;font-weight:700;color:var(--t3);letter-spacing:0.12em;
      text-transform:uppercase;margin-bottom:10px;}
    .c-ttl{font-size:15px;font-weight:700;color:var(--t1);margin-bottom:7px;}
    .c-bdy{font-size:13px;color:var(--t2);line-height:1.75;}
    .c-tag{display:inline-block;margin-top:13px;font-size:10px;font-weight:700;
      padding:3px 10px;border-radius:var(--rf);border:1px solid;}
    .tg{color:#059669;border-color:rgba(5,150,105,0.3);background:rgba(5,150,105,0.08);}
    .tv{color:var(--v);border-color:var(--vpb);background:var(--vp);}
    .tc{color:var(--cyan);border-color:rgba(6,182,212,0.3);background:rgba(6,182,212,0.08);}
    .tp{color:var(--pink);border-color:rgba(236,72,153,0.3);background:rgba(236,72,153,0.08);}
    .tam{color:var(--amber);border-color:rgba(245,158,11,0.3);background:rgba(245,158,11,0.08);}
    .feat-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
    .feat{background:linear-gradient(135deg,var(--vp),var(--s2));
      border:1px solid var(--vpb);border-radius:var(--r2);padding:24px;
      transition:transform 0.2s,box-shadow 0.2s;}
    .feat:hover{transform:translateY(-3px);box-shadow:var(--sh2);}
    .feat-ttl{font-size:14px;font-weight:700;color:var(--t1);margin-bottom:6px;}
    .feat-bdy{font-size:12px;color:var(--t2);line-height:1.7;}
    .feat-badge{display:inline-block;margin-top:10px;font-size:10px;font-weight:700;
      color:var(--v);background:var(--s);border:1px solid var(--vpb);
      padding:3px 10px;border-radius:var(--rf);}
    .pipe-row{display:flex;align-items:center;justify-content:space-between;
      background:var(--s);border:1px solid var(--bd2);border-radius:var(--r2);
      padding:28px 36px;box-shadow:var(--sh);}
    .p-step{display:flex;flex-direction:column;align-items:center;gap:5px;
      flex:1;padding:8px 4px;border-radius:var(--r);transition:all 0.18s;cursor:default;}
    .p-step:hover{background:var(--vp);transform:translateY(-2px);}
    .p-lbl{font-size:11px;font-weight:700;color:var(--t1);letter-spacing:0.04em;}
    .p-sub{font-size:10px;color:var(--t3);}
    .p-arr{color:var(--vpb);font-size:14px;flex-shrink:0;
      animation:aP 2.5s ease-in-out infinite;}
    .tags{display:flex;flex-wrap:wrap;gap:9px;}
    .tag{padding:6px 14px;font-size:11px;font-weight:600;border-radius:var(--rf);
      border:1px solid;transition:transform 0.15s;cursor:default;}
    .tag:hover{transform:translateY(-2px);}
    .foot{position:relative;z-index:10;max-width:1200px;margin:72px auto 0;
      padding:22px 56px 64px;border-top:1px solid var(--bd2);
      display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;}
    .foot span{font-size:12px;color:var(--t3);}
    </style>

    <div class="land">
    <div style="position:relative;z-index:1;">

      <section class="hero">
        <div class="h-eyebrow"><span class="h-dot"></span>Zero hallucination tolerance</div>
        <h1 class="h1">Ask anything.<br><em>Know everything.</em></h1>
        <p class="h-sub">
          A <b>production-grade</b> RAG system with <b>inline citations</b>,
          persistent chat history, live analytics, and a hard refusal trigger — no guessing, ever.
        </p>
        <div class="cta-wrap">
          <form method="get" action="" style="margin:0;">
            <input type="hidden" name="launch" value="1">
            <button type="submit" class="btn-lnd">Open App &nbsp;&#8594;</button>
          </form>
        </div>
      </section>

      <div class="stats">
        <div class="stat"><div class="sv">0%</div><div class="sl">Hallucination Rate</div></div>
        <div class="stat"><div class="sv">3&times;</div><div class="sl">Retrieval Methods</div></div>
        <div class="stat"><div class="sv">100%</div><div class="sl">Local &amp; Private</div></div>
        <div class="stat"><div class="sv">&infin;</div><div class="sl">Documents</div></div>
      </div>

      <div class="sec">
        <div class="sec-lbl">New in v1.0</div>
        <div class="sec-ttl">Three <em>new</em> features</div>
        <div class="feat-grid">
          <div class="feat">
            <div class="feat-ttl">Persistent Chat History</div>
            <div class="feat-bdy">Every conversation auto-saved to disk. Load any past chat in one click.</div>
            <span class="feat-badge">chat_history.py</span>
          </div>
          <div class="feat">
            <div class="feat-ttl">Export as Markdown</div>
            <div class="feat-bdy">Download any conversation as a clean .md file with all citations included.</div>
            <span class="feat-badge" style="color:var(--cyan);border-color:rgba(6,182,212,0.3);background:rgba(6,182,212,0.08);">Export MD</span>
          </div>
          <div class="feat">
            <div class="feat-ttl">Live Query Analytics</div>
            <div class="feat-bdy">Real-time dashboard: total queries, refusal rate, avg latency. MLOps observability.</div>
            <span class="feat-badge" style="color:var(--pink);border-color:rgba(236,72,153,0.3);background:rgba(236,72,153,0.08);">analytics.py</span>
          </div>
        </div>
      </div>

      <div class="sec">
        <div class="sec-lbl">Capabilities</div>
        <div class="sec-ttl">Six <em>pillars</em> of precision</div>
        <div class="cards">
          <div class="card"><div class="c-num">01 &mdash; Ingestion</div><div class="c-ttl">Smart PDF Parsing</div><div class="c-bdy">Multi-column layouts, embedded tables, complex structures. Headers and footers stripped automatically.</div><span class="c-tag tg">pdfplumber</span></div>
          <div class="card"><div class="c-num">02 &mdash; Chunking</div><div class="c-ttl">Semantic Chunking</div><div class="c-bdy">Header-aware 500–800 token chunks. Source, page, and section breadcrumb on every chunk.</div><span class="c-tag tv">tiktoken</span></div>
          <div class="card"><div class="c-num">03 &mdash; Retrieval</div><div class="c-ttl">Hybrid Search</div><div class="c-bdy">BM25 fused with dense vector search via Reciprocal Rank Fusion. Catches what either alone misses.</div><span class="c-tag tc">RRF Fusion</span></div>
          <div class="card"><div class="c-num">04 &mdash; Reranking</div><div class="c-ttl">Cross-Encoder Precision</div><div class="c-bdy">Top 20 re-scored. Only the highest-confidence 5 reach the generation layer.</div><span class="c-tag tam">ms-marco</span></div>
          <div class="card"><div class="c-num">05 &mdash; Generation</div><div class="c-ttl">Attributed Answers</div><div class="c-bdy">Every claim carries an inline citation [Source, p.X]. Full References section appended.</div><span class="c-tag tv">LangGraph</span></div>
          <div class="card"><div class="c-num">06 &mdash; Safety</div><div class="c-ttl">Hard Refusal Gate</div><div class="c-bdy">Context below confidence threshold triggers a fixed refusal. No speculation, no hallucination.</div><span class="c-tag tp">Threshold Gate</span></div>
        </div>
      </div>

      <div class="sec">
        <div class="sec-lbl">Architecture</div>
        <div class="sec-ttl">The <em>pipeline</em></div>
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

      <div class="sec">
        <div class="sec-lbl">Stack</div>
        <div class="sec-ttl">Built <em>with</em></div>
        <div class="tags">
          <span class="tag tg">pdfplumber</span><span class="tag tg">ChromaDB</span>
          <span class="tag tg">sentence-transformers</span><span class="tag tv">LangGraph</span>
          <span class="tag tv">langchain-ollama</span><span class="tag tv">llama3.1:8b</span>
          <span class="tag tc">BM25 + RRF</span><span class="tag tc">cross-encoder</span>
          <span class="tag tp">FastAPI</span><span class="tag tp">Streamlit</span>
          <span class="tag tam">Python 3.14</span>
        </div>
      </div>

      <div class="foot">
        <span>NeuralDoc &mdash; Production RAG System</span>
        <span>Ollama &middot; ChromaDB &middot; LangGraph &middot; FastAPI</span>
      </div>
    </div>
    </div>""")
