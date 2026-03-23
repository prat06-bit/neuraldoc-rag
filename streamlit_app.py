"""NeuralDoc RAG — Pixel-perfect pastel redesign."""
import requests
import streamlit as st

st.set_page_config(
    page_title="NeuralDoc",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "page" not in st.session_state:
    st.session_state.page = "landing"
if "messages" not in st.session_state:
    st.session_state.messages = []

API_BASE = "http://localhost:8000"

# ── Global reset ──────────────────────────────────────────────────────────────
st.html("""<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:          #F8F7FF;
  --surface:     #FFFFFF;
  --surface2:    #F4F0FF;
  --border:      #F1F1F9;
  --border2:     #E9DFFF;

  --purple:      #8B5CF6;
  --purple-dark: #7C3AED;
  --purple-pale: #A084F6;
  --purple-bg:   #F3EDFF;

  --text-1:  #18181B;
  --text-2:  #71717A;
  --text-3:  #A1A1AA;
  --text-4:  #B0A7C3;

  --mint-bg:   #ECFDF5; --mint-text:  #059669;
  --rose-bg:   #FCA5A5; --rose-text:  #B91C1C;
  --amber-bg:  #FDE68A; --amber-text: #B45309;

  --r-sm:   8px;  --r-md:  12px; --r-lg: 16px;
  --r-xl:   18px; --r-2xl: 24px; --r-full: 9999px;

  --sh: 0 4px 24px rgba(139,92,246,0.08);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  background: var(--bg)!important;
  font-family: 'Inter', sans-serif!important;
  color: var(--text-1)!important;
}

[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],#MainMenu,footer {
  display:none!important; height:0!important; }

[data-testid="stAppViewContainer"],[data-testid="stMain"],
[data-testid="stMainBlockContainer"],.block-container {
  background:transparent!important; padding:0!important;
  margin:0!important; max-width:100%!important; border:none!important; }

[data-testid="stVerticalBlock"] { gap:0!important; }
[data-testid="stVerticalBlock"]>div { margin:0!important; padding:0!important; }
</style>""")


# ═════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":

    st.html("""<style>
    [data-testid="stAppViewContainer"] { background: var(--bg)!important; }

    /* Button override for landing */
    [data-testid="stButton"]>button {
      background: var(--purple)!important;
      color: white!important;
      border: none!important;
      border-radius: var(--r-full)!important;
      font-family: 'Inter', sans-serif!important;
      font-size: 17px!important;
      font-weight: 500!important;
      padding: 16px 0!important;
      letter-spacing: 0!important;
      box-shadow: none!important;
      transition: background 0.18s, transform 0.15s!important;
      width: 100%!important;
    }
    [data-testid="stButton"]>button:hover {
      background: var(--purple-dark)!important;
      transform: translateY(-1px)!important;
    }
    [data-testid="stButton"]>button:active {
      transform: scale(0.98)!important;
    }
    </style>""")

    # Full background wrapper
    st.html("""<div style="
      min-height:100vh;
      background: radial-gradient(ellipse 80% 60% at 50% 0%, #EDE9FE 0%, #F8F7FF 55%, #F8F7FF 100%);
      position:relative;
    ">

    <!-- NAVBAR -->
    <nav style="
      display:flex; align-items:center; justify-content:space-between;
      max-width:1200px; margin:0 auto;
      padding:28px 48px 0;
    ">
      <div style="display:flex;align-items:center;gap:9px;">
        <div style="width:10px;height:10px;border-radius:50%;background:var(--purple-pale);flex-shrink:0;"></div>
        <span style="font-family:'Inter',sans-serif;font-size:19px;font-weight:500;color:var(--text-1);letter-spacing:-0.3px;">NeuralDoc</span>
      </div>
      <div style="
        font-family:'Inter',sans-serif; font-size:13px; font-weight:500;
        color:var(--purple-pale); text-transform:uppercase; letter-spacing:0.5px;
        border:1px solid var(--border2); background:var(--purple-bg);
        padding:7px 18px; border-radius:var(--r-full);
      ">Production RAG v1.0</div>
    </nav>

    <!-- HERO -->
    <section style="
      max-width:780px; margin:0 auto;
      padding:72px 48px 0; text-align:center;
    ">
      <!-- Badge -->
      <div style="
        display:inline-flex; align-items:center; gap:7px;
        font-family:'Inter',sans-serif; font-size:14px; font-weight:400;
        color:var(--text-1);
        border:1px solid var(--border2); background:var(--surface);
        padding:7px 18px; border-radius:var(--r-full);
        margin-bottom:36px;
      ">
        <div style="width:6px;height:6px;border-radius:50%;background:var(--purple-pale);flex-shrink:0;"></div>
        Zero hallucination tolerance
      </div>

      <!-- Headline -->
      <h1 style="
        font-family:'Playfair Display',serif;
        font-size:clamp(48px,6.5vw,72px);
        font-weight:700; color:var(--text-1);
        line-height:1.05; letter-spacing:-1.5px;
        margin-bottom:6px;
      ">Ask anything.</h1>
      <h1 style="
        font-family:'Playfair Display',serif;
        font-size:clamp(48px,6.5vw,72px);
        font-weight:400; font-style:italic;
        color:var(--purple-pale);
        line-height:1.05; letter-spacing:-1.5px;
        margin-bottom:28px;
      ">Know everything.</h1>

      <!-- Description -->
      <p style="
        font-family:'Inter',sans-serif; font-size:18px;
        color:var(--text-1); line-height:1.75;
        max-width:560px; margin:0 auto 44px;
      ">
        A <strong>production-grade</strong> RAG system that answers questions from
        your documents with <strong>inline citations</strong>, hybrid retrieval,
        and a hard refusal trigger — no guessing, ever.
      </p>
    </section>
    </div>""")

    # Open App button — rendered by Streamlit in correct position
    _l, _m, _r = st.columns([2, 2, 2])
    with _m:
        if st.button("Open App", key="go_chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

    # Stats + rest of page
    st.html("""<div style="
      background: radial-gradient(ellipse 80% 60% at 50% 0%, #EDE9FE 0%, #F8F7FF 55%, #F8F7FF 100%);
      padding-bottom: 80px;
    ">

    <!-- STATS CARD -->
    <div style="
      display:flex; max-width:820px; margin:48px auto 0;
      background:var(--surface); border-radius:var(--r-2xl);
      border:1px solid var(--border); box-shadow:var(--sh);
      overflow:hidden;
    ">
      <div style="flex:1;padding:28px 16px;text-align:center;border-right:1px solid var(--border2);">
        <div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:var(--purple-pale);line-height:1;margin-bottom:8px;">0%</div>
        <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:600;color:var(--text-3);letter-spacing:0.08em;text-transform:uppercase;">Hallucination Rate</div>
      </div>
      <div style="flex:1;padding:28px 16px;text-align:center;border-right:1px solid var(--border2);">
        <div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:var(--purple-pale);line-height:1;margin-bottom:8px;">3x</div>
        <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:600;color:var(--text-3);letter-spacing:0.08em;text-transform:uppercase;">Retrieval Methods</div>
      </div>
      <div style="flex:1;padding:28px 16px;text-align:center;border-right:1px solid var(--border2);">
        <div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:var(--purple-pale);line-height:1;margin-bottom:8px;">100%</div>
        <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:600;color:var(--text-3);letter-spacing:0.08em;text-transform:uppercase;">Local &amp; Private</div>
      </div>
      <div style="flex:1;padding:28px 16px;text-align:center;">
        <div style="font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:var(--purple-pale);line-height:1;margin-bottom:8px;">inf</div>
        <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:600;color:var(--text-3);letter-spacing:0.08em;text-transform:uppercase;">Documents</div>
      </div>
    </div>

    <!-- CAPABILITIES -->
    <div style="max-width:1200px;margin:80px auto 0;padding:0 48px;">
      <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
        color:var(--purple);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">
        Capabilities
      </div>
      <div style="font-family:'Playfair Display',serif;font-size:38px;font-weight:700;
        color:var(--text-1);margin-bottom:40px;letter-spacing:-0.5px;">
        Six pillars of <em style="font-style:italic;color:var(--purple-pale);">precision</em>
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;">

        <div style="background:var(--surface);border:1px solid var(--border);
          border-radius:var(--r-xl);padding:24px;box-shadow:var(--sh);
          transition:transform 0.2s,box-shadow 0.2s;"
          onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 32px rgba(139,92,246,0.14)'"
          onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)'">
          <div style="font-size:10px;font-weight:700;color:var(--text-3);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">01 — Ingestion</div>
          <div style="font-size:15px;font-weight:600;color:var(--text-1);margin-bottom:7px;">Smart PDF Parsing</div>
          <div style="font-size:13px;color:var(--text-2);line-height:1.7;">Multi-column layouts, embedded tables, complex structures. Headers and footers stripped automatically.</div>
          <span style="display:inline-block;margin-top:12px;font-size:10px;font-weight:600;padding:3px 10px;border-radius:var(--r-full);color:var(--mint-text);background:var(--mint-bg);border:1px solid #A7F3D0;">pdfplumber</span>
        </div>

        <div style="background:var(--surface);border:1px solid var(--border);
          border-radius:var(--r-xl);padding:24px;box-shadow:var(--sh);"
          onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 32px rgba(139,92,246,0.14)'"
          onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)'">
          <div style="font-size:10px;font-weight:700;color:var(--text-3);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">02 — Chunking</div>
          <div style="font-size:15px;font-weight:600;color:var(--text-1);margin-bottom:7px;">Semantic Chunking</div>
          <div style="font-size:13px;color:var(--text-2);line-height:1.7;">Header-aware chunks of 500–800 tokens. Every chunk carries source, page, and section breadcrumb.</div>
          <span style="display:inline-block;margin-top:12px;font-size:10px;font-weight:600;padding:3px 10px;border-radius:var(--r-full);color:var(--purple);background:var(--purple-bg);border:1px solid var(--border2);">tiktoken</span>
        </div>

        <div style="background:var(--surface);border:1px solid var(--border);
          border-radius:var(--r-xl);padding:24px;box-shadow:var(--sh);"
          onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 32px rgba(139,92,246,0.14)'"
          onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)'">
          <div style="font-size:10px;font-weight:700;color:var(--text-3);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">03 — Retrieval</div>
          <div style="font-size:15px;font-weight:600;color:var(--text-1);margin-bottom:7px;">Hybrid Search</div>
          <div style="font-size:13px;color:var(--text-2);line-height:1.7;">BM25 keyword fused with dense vector search via Reciprocal Rank Fusion. Catches what either alone misses.</div>
          <span style="display:inline-block;margin-top:12px;font-size:10px;font-weight:600;padding:3px 10px;border-radius:var(--r-full);color:#0284C7;background:#F0F9FF;border:1px solid #BAE6FD;">RRF Fusion</span>
        </div>

        <div style="background:var(--surface);border:1px solid var(--border);
          border-radius:var(--r-xl);padding:24px;box-shadow:var(--sh);"
          onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 32px rgba(139,92,246,0.14)'"
          onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)'">
          <div style="font-size:10px;font-weight:700;color:var(--text-3);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">04 — Reranking</div>
          <div style="font-size:15px;font-weight:600;color:var(--text-1);margin-bottom:7px;">Cross-Encoder Precision</div>
          <div style="font-size:13px;color:var(--text-2);line-height:1.7;">Top 20 candidates re-scored. Only the highest-confidence 5 reach the generation layer.</div>
          <span style="display:inline-block;margin-top:12px;font-size:10px;font-weight:600;padding:3px 10px;border-radius:var(--r-full);color:#D97706;background:#FFFBEB;border:1px solid #FDE68A;">ms-marco</span>
        </div>

        <div style="background:var(--surface);border:1px solid var(--border);
          border-radius:var(--r-xl);padding:24px;box-shadow:var(--sh);"
          onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 32px rgba(139,92,246,0.14)'"
          onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)'">
          <div style="font-size:10px;font-weight:700;color:var(--text-3);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">05 — Generation</div>
          <div style="font-size:15px;font-weight:600;color:var(--text-1);margin-bottom:7px;">Attributed Answers</div>
          <div style="font-size:13px;color:var(--text-2);line-height:1.7;">Every claim carries an inline citation [Source, p.X]. Full References section on every response.</div>
          <span style="display:inline-block;margin-top:12px;font-size:10px;font-weight:600;padding:3px 10px;border-radius:var(--r-full);color:#9333EA;background:#FAF5FF;border:1px solid #E9D5FF;">LangGraph</span>
        </div>

        <div style="background:var(--surface);border:1px solid var(--border);
          border-radius:var(--r-xl);padding:24px;box-shadow:var(--sh);"
          onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 32px rgba(139,92,246,0.14)'"
          onmouseout="this.style.transform='';this.style.boxShadow='var(--sh)'">
          <div style="font-size:10px;font-weight:700;color:var(--text-3);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;">06 — Safety</div>
          <div style="font-size:15px;font-weight:600;color:var(--text-1);margin-bottom:7px;">Hard Refusal Gate</div>
          <div style="font-size:13px;color:var(--text-2);line-height:1.7;">Context below confidence threshold triggers a fixed refusal. No speculation, no hallucination.</div>
          <span style="display:inline-block;margin-top:12px;font-size:10px;font-weight:600;padding:3px 10px;border-radius:var(--r-full);color:#E11D48;background:#FFF1F2;border:1px solid #FECDD3;">Threshold Gate</span>
        </div>

      </div>
    </div>

    <!-- PIPELINE -->
    <div style="max-width:1200px;margin:80px auto 0;padding:0 48px;">
      <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
        color:var(--purple);letter-spacing:0.12em;text-transform:uppercase;margin-bottom:16px;">
        Architecture
      </div>
      <div style="font-family:'Playfair Display',serif;font-size:38px;font-weight:700;
        color:var(--text-1);margin-bottom:32px;letter-spacing:-0.5px;">
        The <em style="font-style:italic;color:var(--purple-pale);">pipeline</em>
      </div>
      <div style="background:var(--surface);border:1px solid var(--border);
        border-radius:var(--r-2xl);padding:32px 40px;box-shadow:var(--sh);
        display:flex;align-items:center;flex-wrap:wrap;gap:4px;">
        <div style="display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 14px;border-radius:12px;min-width:72px;transition:background 0.2s;"
          onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background=''">
          <div style="font-size:12px;font-weight:600;color:var(--text-2);">Parse</div>
          <div style="font-size:10px;color:var(--text-3);">pdfplumber</div>
        </div>
        <div style="color:var(--border2);font-size:14px;padding:0 2px;">&#8594;</div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 14px;border-radius:12px;min-width:72px;transition:background 0.2s;"
          onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background=''">
          <div style="font-size:12px;font-weight:600;color:var(--text-2);">Chunk</div>
          <div style="font-size:10px;color:var(--text-3);">tiktoken</div>
        </div>
        <div style="color:var(--border2);font-size:14px;padding:0 2px;">&#8594;</div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 14px;border-radius:12px;min-width:72px;transition:background 0.2s;"
          onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background=''">
          <div style="font-size:12px;font-weight:600;color:var(--text-2);">Embed</div>
          <div style="font-size:10px;color:var(--text-3);">miniLM</div>
        </div>
        <div style="color:var(--border2);font-size:14px;padding:0 2px;">&#8594;</div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 14px;border-radius:12px;min-width:72px;transition:background 0.2s;"
          onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background=''">
          <div style="font-size:12px;font-weight:600;color:var(--text-2);">BM25</div>
          <div style="font-size:10px;color:var(--text-3);">keyword</div>
        </div>
        <div style="color:var(--border2);font-size:14px;padding:0 2px;">&#8594;</div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 14px;border-radius:12px;min-width:72px;transition:background 0.2s;"
          onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background=''">
          <div style="font-size:12px;font-weight:600;color:var(--text-2);">Fuse</div>
          <div style="font-size:10px;color:var(--text-3);">RRF</div>
        </div>
        <div style="color:var(--border2);font-size:14px;padding:0 2px;">&#8594;</div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 14px;border-radius:12px;min-width:72px;transition:background 0.2s;"
          onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background=''">
          <div style="font-size:12px;font-weight:600;color:var(--text-2);">Rerank</div>
          <div style="font-size:10px;color:var(--text-3);">cross-enc</div>
        </div>
        <div style="color:var(--border2);font-size:14px;padding:0 2px;">&#8594;</div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 14px;border-radius:12px;min-width:72px;transition:background 0.2s;"
          onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background=''">
          <div style="font-size:12px;font-weight:600;color:var(--text-2);">Generate</div>
          <div style="font-size:10px;color:var(--text-3);">llama3.1</div>
        </div>
        <div style="color:var(--border2);font-size:14px;padding:0 2px;">&#8594;</div>
        <div style="display:flex;flex-direction:column;align-items:center;gap:5px;padding:10px 14px;border-radius:12px;min-width:72px;transition:background 0.2s;"
          onmouseover="this.style.background='var(--surface2)'" onmouseout="this.style.background=''">
          <div style="font-size:12px;font-weight:600;color:var(--text-2);">Cite</div>
          <div style="font-size:10px;color:var(--text-3);">attributed</div>
        </div>
      </div>
    </div>

    <!-- FOOTER -->
    <div style="max-width:1200px;margin:72px auto 0;padding:22px 48px 56px;
      border-top:1px solid var(--border);
      display:flex;justify-content:space-between;align-items:center;">
      <span style="font-size:12px;color:var(--text-3);">NeuralDoc — Production RAG System</span>
      <span style="font-size:12px;color:var(--text-3);">Ollama · ChromaDB · LangGraph · FastAPI</span>
    </div>

    </div>""")


# ═════════════════════════════════════════════════════════════════════════════
# CHAT PAGE — Dashboard matching specs
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.html("""<style>
    [data-testid="stAppViewContainer"] { background: var(--bg)!important; }
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container {
      padding: 0!important; background: transparent!important; max-width:100%!important; }

    /* Inputs */
    .stTextInput input {
      background: var(--surface)!important;
      border: 1px solid #E5E7EB!important;
      border-radius: var(--r-md)!important;
      color: var(--text-1)!important;
      font-family: 'Inter', sans-serif!important;
      font-size: 15px!important;
      padding: 14px 18px!important;
      transition: border-color 0.18s, box-shadow 0.18s!important;
    }
    .stTextInput input:focus {
      border-color: var(--purple)!important;
      box-shadow: 0 0 0 2px var(--border2)!important;
      outline: none!important;
    }
    .stTextInput input::placeholder { color: var(--text-3)!important; }
    .stTextInput label, .stFileUploader label { display:none!important; }

    /* Buttons */
    .stButton>button {
      background: var(--purple)!important;
      color: white!important;
      border: none!important;
      border-radius: var(--r-md)!important;
      font-family: 'Inter', sans-serif!important;
      font-weight: 600!important;
      font-size: 14px!important;
      padding: 12px 0!important;
      box-shadow: none!important;
      transition: background 0.15s, transform 0.12s, box-shadow 0.15s!important;
    }
    .stButton>button:hover {
      background: var(--purple-dark)!important;
      transform: translateY(-1px)!important;
      box-shadow: 0 4px 16px rgba(139,92,246,0.18)!important;
    }
    .stButton>button:active { transform: scale(0.97)!important; }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
      background: var(--surface)!important;
      border: 2px dashed var(--border2)!important;
      border-radius: var(--r-lg)!important;
      transition: all 0.18s!important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
      border-color: var(--purple)!important;
      background: var(--purple-bg)!important;
    }
    [data-testid="stFileUploaderDropzone"] * { color: var(--text-2)!important; }

    .stSelectbox [data-baseweb="select"]>div {
      background: var(--surface)!important;
      border: 1px solid #E5E7EB!important;
      border-radius: var(--r-md)!important;
      color: var(--text-1)!important;
    }
    hr { border-color: #E5E7EB!important; }
    </style>""")

    def get_health():
        try:
            r = requests.get(f"{API_BASE}/health", timeout=3).json()
            r["_reachable"] = True
            return r
        except Exception:
            return {"pipeline_ready":False,"total_chunks":0,"indexed_files":[],"_reachable":False}

    h = get_health()
    api_ok  = h.get("_reachable", False)
    ready   = h.get("pipeline_ready", False)
    chunks  = h.get("total_chunks", 0)
    files   = h.get("indexed_files", [])

    if ready:
        s_cls  = "s-ready"; s_dot = "#059669"
        s_text = f"Ready &middot; {chunks} chunks"
    elif api_ok:
        s_cls  = "s-warn"; s_dot = "#B45309"
        s_text = "API online &middot; No documents indexed"
    else:
        s_cls  = "s-off"; s_dot = "#B91C1C"
        s_text = "API offline"

    # Topbar
    st.html(f"""<style>
    .topbar {{ display:flex; align-items:center; justify-content:space-between;
      padding:0 40px; height:64px;
      background:var(--surface); border-bottom:1px solid var(--border);
      position:sticky; top:0; z-index:100; }}
    .tb-logo {{ display:flex; align-items:center; gap:9px;
      font-family:'Inter',sans-serif; font-size:17px; font-weight:500;
      color:var(--text-1); }}
    .tb-dot {{ width:10px; height:10px; border-radius:50%; background:var(--purple-pale); flex-shrink:0; }}
    .s-pill {{ display:inline-flex; align-items:center; gap:6px;
      font-family:'Inter',sans-serif; font-size:13px; font-weight:500;
      padding:5px 14px; border-radius:var(--r-full); border:1px solid; }}
    .s-ready {{ color:#059669; background:#ECFDF5; border-color:#A7F3D0; }}
    .s-warn  {{ color:#B45309; background:#FDE68A; border-color:#FCD34D; }}
    .s-off   {{ color:#B91C1C; background:#FCA5A5; border-color:#F87171; }}
    .s-dot-el{{ width:5px; height:5px; border-radius:50%; flex-shrink:0; }}
    </style>
    <div class="topbar">
      <div class="tb-logo"><div class="tb-dot"></div>NeuralDoc</div>
      <div class="s-pill {s_cls}">
        <div class="s-dot-el" style="background:{s_dot};"></div>
        {s_text}
      </div>
    </div>""")

    # Nav buttons
    st.html('<div style="padding:20px 40px 0;">')
    nb1, nb2, _ = st.columns([1, 1, 9])
    with nb1:
        if st.button("Home", key="back_home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
    with nb2:
        if st.button("Clear Chat", key="clr_chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    st.html('</div><div style="height:16px;"></div>')

    # Two-panel layout
    col_chat, col_upload = st.columns([3, 2], gap="large")

    # ── RIGHT: Knowledge Base panel ───────────────────────────────────────────
    with col_upload:
        st.html('<div style="padding:0 32px 0 0;">')

        # Header + Clear button
        uh1, uh2 = st.columns([3, 1])
        with uh1:
            st.html("""
            <div style="margin-bottom:16px;">
              <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
                color:var(--text-4);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">
                Knowledge Base
              </div>
              <div style="font-family:'Playfair Display',serif;font-size:26px;
                font-weight:400;color:var(--purple);line-height:1.15;">
                Upload <em>documents</em>
              </div>
            </div>""")
        with uh2:
            st.html('<div style="height:32px;"></div>')
            if st.button("Clear", key="clear_idx", use_container_width=True,
                         help="Wipe all indexed documents"):
                try:
                    resp = requests.delete(f"{API_BASE}/index", timeout=15)
                    if resp.status_code == 200:
                        st.success("Index cleared.")
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("API offline.")

        # Drop hint
        st.html("""
        <div style="background:var(--surface);border:2px dashed var(--border2);
          border-radius:var(--r-lg);padding:20px;margin-bottom:12px;text-align:center;">
          <div style="font-size:13px;font-weight:500;color:var(--text-1);margin-bottom:4px;">
            Drop your PDF below
          </div>
          <div style="font-size:12px;color:var(--text-3);">
            Parsed &#8594; Chunked &#8594; Embedded &#8594; Indexed
          </div>
        </div>""")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")

        if uploaded:
            st.html(f"""
            <div style="background:var(--surface);border:1px solid #A7F3D0;
              border-radius:var(--r-md);padding:10px 14px;margin-bottom:10px;">
              <div style="font-size:13px;font-weight:600;color:var(--text-1);">{uploaded.name}</div>
              <div style="font-size:11px;color:#059669;margin-top:2px;">{uploaded.size//1024} KB</div>
            </div>""")
            if st.button("Index Document", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing PDF..."):
                    try:
                        resp = requests.post(f"{API_BASE}/ingest",
                            files={"file":(uploaded.name, uploaded, "application/pdf")},
                            timeout=120)
                        if resp.status_code == 200:
                            d = resp.json()
                            st.success(f"Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                            st.rerun()
                        else:
                            st.error(f"Error: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("API offline. Run: uv run uvicorn api:app --reload --port 8000")
                    except Exception as e:
                        st.error(str(e))

        if files:
            st.html("""<div style="font-size:10px;font-weight:700;color:var(--text-4);
              letter-spacing:0.1em;text-transform:uppercase;margin:14px 0 8px;">
              Indexed files</div>""")
            for f in files:
                fname = f.replace("\\", "/").split("/")[-1]
                st.html(f"""
                <div style="background:var(--surface);border:1px solid var(--border);
                  border-radius:var(--r-md);padding:9px 13px;margin-bottom:5px;
                  display:flex;align-items:center;box-shadow:var(--sh);">
                  <span style="font-size:13px;font-weight:500;color:var(--text-1);flex:1;">{fname}</span>
                  <span style="font-size:10px;font-weight:600;padding:2px 9px;
                    border-radius:var(--r-full);color:#059669;background:#ECFDF5;border:1px solid #A7F3D0;">indexed</span>
                </div>""")

        # Tips
        st.html("""
        <div style="margin-top:16px;background:var(--surface);border:1px solid var(--border);
          border-radius:var(--r-lg);padding:16px 18px;box-shadow:var(--sh);">
          <div style="font-family:'Inter',sans-serif;font-size:10px;font-weight:700;
            color:var(--text-4);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px;">
            Tips
          </div>
          <div style="font-family:'Inter',sans-serif;font-size:13px;
            color:var(--text-2);line-height:1.9;">
            Click <b style="color:var(--text-1);font-weight:600;">Clear</b> before switching documents.<br>
            Ask precise questions for best citation accuracy.<br>
            Every answer includes inline source references.<br>
            Unanswerable queries return a refusal, not a guess.
          </div>
        </div>""")

        st.html('</div>')

    # ── LEFT: Document QA panel ───────────────────────────────────────────────
    with col_chat:
        st.html('<div style="padding:0 0 0 32px;">')

        # Header
        st.html(f"""
        <div style="display:flex;align-items:flex-start;
          justify-content:space-between;margin-bottom:18px;">
          <div>
            <div style="font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
              color:var(--text-4);letter-spacing:0.1em;text-transform:uppercase;margin-bottom:8px;">
              Document QA
            </div>
            <div style="font-family:'Playfair Display',serif;font-size:28px;
              font-weight:400;color:var(--purple);line-height:1.15;">
              Ask your <em>documents</em>
            </div>
          </div>
          <div style="display:flex;gap:8px;align-items:center;padding-top:20px;">
            <span style="font-family:'Inter',sans-serif;font-size:12px;font-weight:500;
              color:var(--purple);background:var(--purple-bg);
              border:1px solid var(--border2);padding:4px 11px;border-radius:var(--r-full);">
              {chunks} chunks
            </span>
            <span style="font-family:'Inter',sans-serif;font-size:12px;font-weight:600;
              padding:4px 11px;border-radius:var(--r-full);border:1px solid;
              {'color:#059669;background:#ECFDF5;border-color:#A7F3D0;' if ready else 'color:#B91C1C;background:#FCA5A5;border-color:#F87171;'}">
              {'Ready' if ready else 'Not ready'}
            </span>
          </div>
        </div>""")

        # Messages
        if st.session_state.messages:
            html = ""
            for m in st.session_state.messages:
                if m["role"] == "user":
                    html += f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:14px;">
                      <div style="max-width:75%;padding:12px 16px;
                        background:var(--purple);color:white;
                        border-radius:16px 4px 16px 16px;
                        font-family:'Inter',sans-serif;font-size:14px;line-height:1.65;
                        box-shadow:0 2px 8px rgba(139,92,246,0.18);">
                        {m['content']}
                      </div>
                    </div>"""
                else:
                    refs = ""
                    if m.get("references"):
                        refs = '<div style="margin-top:9px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs += f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:var(--r-full);color:#0284C7;background:#F0F9FF;border:1px solid #BAE6FD;">{ref}</span>'
                        refs += "</div>"
                    rfsd = ""
                    if m.get("refused"):
                        rfsd = '<div style="margin-top:8px;font-family:\'Inter\',sans-serif;font-size:12px;font-weight:500;color:#B91C1C;background:#FCA5A5;border:1px solid #F87171;padding:5px 12px;border-radius:var(--r-md);display:inline-block;">Insufficient evidence — refusal triggered</div>'
                    lat = ""
                    if m.get("latency_ms"):
                        lat = f'<div style="margin-top:5px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:var(--text-3);">{m["latency_ms"]} ms</div>'
                    html += f"""
                    <div style="display:flex;margin-bottom:14px;gap:9px;align-items:flex-start;">
                      <div style="width:26px;height:26px;border-radius:var(--r-sm);flex-shrink:0;
                        margin-top:2px;background:var(--purple-bg);
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Inter',sans-serif;font-size:11px;font-weight:700;
                        color:var(--purple);border:1px solid var(--border2);">N</div>
                      <div style="max-width:86%;padding:12px 15px;
                        background:var(--surface);border:1px solid var(--border);
                        border-radius:4px 14px 14px 14px;
                        font-family:'Inter',sans-serif;font-size:14px;
                        color:var(--text-1);line-height:1.75;
                        box-shadow:var(--sh);">
                        {m['content']}{refs}{rfsd}{lat}
                      </div>
                    </div>"""
            st.html(f"""
            <div style="max-height:50vh;overflow-y:auto;padding:2px 2px 8px;
              scrollbar-width:thin;scrollbar-color:var(--border2) transparent;">
              {html}
            </div>""")
        else:
            st.html("""
            <div style="text-align:center;padding:52px 24px;
              background:var(--surface);border:1px solid var(--border);
              border-radius:var(--r-xl);margin-bottom:14px;box-shadow:var(--sh);">
              <div style="font-family:'Playfair Display',serif;font-size:22px;
                color:var(--text-1);margin-bottom:8px;">Ask anything</div>
              <div style="font-family:'Inter',sans-serif;font-size:13px;
                color:var(--text-3);max-width:300px;margin:0 auto 20px;line-height:1.7;">
                Upload a PDF on the right, then ask questions here. Every answer is cited.
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
                <span style="font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
                  color:var(--purple);background:var(--purple-bg);
                  border:1px solid var(--border2);padding:7px 14px;border-radius:var(--r-full);cursor:default;">
                  What is the main finding?</span>
                <span style="font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
                  color:var(--purple);background:var(--purple-bg);
                  border:1px solid var(--border2);padding:7px 14px;border-radius:var(--r-full);cursor:default;">
                  Summarise section 3</span>
                <span style="font-family:'Inter',sans-serif;font-size:13px;font-weight:500;
                  color:var(--purple);background:var(--purple-bg);
                  border:1px solid var(--border2);padding:7px 14px;border-radius:var(--r-full);cursor:default;">
                  What are the key risks?</span>
              </div>
            </div>""")

        st.html('<div style="height:6px;"></div>')

        # Input
        qc, bc = st.columns([6, 1])
        with qc:
            query = st.text_input(
                "Your question",
                placeholder="Ask anything about your documents...",
                label_visibility="hidden",
                key="q_in"
            )
        with bc:
            ask = st.button("Send", use_container_width=True)

        if ask and query:
            if not ready:
                st.warning("Upload and index a PDF first.")
            else:
                with st.spinner("Thinking..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/query", json={"query": query}, timeout=120)
                        if resp.status_code == 200:
                            d = resp.json()
                            st.session_state.messages.extend([
                                {"role": "user", "content": query},
                                {"role": "assistant", "content": d["answer"],
                                 "references": d["references"],
                                 "refused": d["refused"],
                                 "latency_ms": d["latency_ms"]}])
                            st.rerun()
                        else:
                            st.error(f"API error: {resp.json().get('detail', resp.text)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot reach API. Run: uv run uvicorn api:app --reload --port 8000")

        st.html('</div>')