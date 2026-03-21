"""RAG Chat — NeuralDoc"""
import requests
import streamlit as st

st.set_page_config(
    page_title="NeuralDoc · Chat",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
/* Base */
html,body,[data-testid="stAppViewContainer"]{background:#030010!important;}
[data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container{
  background:transparent!important;padding:1.5rem 2rem 3rem!important;max-width:100%!important;}
[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer{display:none!important;}

/* Ambient background */
[data-testid="stAppViewContainer"]::before{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 65% 50% at 10% 10%,rgba(110,0,240,0.2),transparent 60%),
    radial-gradient(ellipse 50% 65% at 90% 90%,rgba(0,210,150,0.14),transparent 60%);
}

/* Sidebar */
[data-testid="stSidebar"]{
  background:rgba(5,0,18,0.97)!important;
  border-right:1px solid rgba(107,0,240,0.2)!important;
}
[data-testid="stSidebar"] *{font-family:'Syne',sans-serif!important;}
[data-testid="stSidebar"] label{color:rgba(255,255,255,0.55)!important;font-size:12px!important;}

/* Inputs */
.stTextInput input{
  background:rgba(107,0,240,0.07)!important;
  border:1px solid rgba(107,0,240,0.3)!important;
  color:#fff!important;border-radius:8px!important;
  padding:11px 16px!important;font-size:14px!important;
  font-family:'Syne',sans-serif!important;
  transition:border-color 0.3s,box-shadow 0.3s!important;
}
.stTextInput input:focus{
  border-color:rgba(107,0,240,0.65)!important;
  box-shadow:0 0 18px rgba(107,0,240,0.18)!important;
}
.stTextInput input::placeholder{color:rgba(255,255,255,0.3)!important;}

/* Buttons */
.stButton>button{
  background:linear-gradient(135deg,#6B00F0,#E0005A)!important;
  color:#fff!important;border:none!important;
  border-radius:8px!important;
  font-family:'Syne',sans-serif!important;
  font-weight:700!important;font-size:13px!important;
  letter-spacing:0.5px!important;
  transition:transform 0.2s,box-shadow 0.2s!important;
}
.stButton>button:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 8px 28px rgba(107,0,240,0.4)!important;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"]{
  background:rgba(107,0,240,0.04)!important;
  border:1px dashed rgba(107,0,240,0.35)!important;
  border-radius:12px!important;
  animation:dropzonePulse 4s ease-in-out infinite!important;
}
@keyframes dropzonePulse{
  0%,100%{border-color:rgba(107,0,240,0.35);}
  50%{border-color:rgba(107,0,240,0.7);box-shadow:0 0 30px rgba(107,0,240,0.12);}
}
[data-testid="stFileUploaderDropzone"] *{color:rgba(255,255,255,0.5)!important;}

/* Select, Slider */
.stSelectbox [data-baseweb="select"]>div{
  background:rgba(255,255,255,0.04)!important;
  border-color:rgba(255,255,255,0.12)!important;
  color:#fff!important;border-radius:8px!important;
}
.stSlider [data-baseweb="slider"]>div{background:rgba(107,0,240,0.3)!important;}

/* Divider */
hr{border-color:rgba(255,255,255,0.07)!important;}

/* General text */
p,span,div{font-family:'Syne',sans-serif;}

/* Custom scrollbar for chat */
.chat-scroll::-webkit-scrollbar{width:4px;}
.chat-scroll::-webkit-scrollbar-thumb{background:rgba(107,0,240,0.4);border-radius:4px;}
.chat-scroll::-webkit-scrollbar-track{background:transparent;}
</style>
""", unsafe_allow_html=True)

API_BASE = "http://localhost:8000"

# ── Health check helper ───────────────────────────────────────────────────────
def get_health() -> dict:
    try:
        return requests.get(f"{API_BASE}/health", timeout=3).json()
    except Exception:
        return {"pipeline_ready": False, "total_chunks": 0, "indexed_files": []}

def get_config() -> dict:
    try:
        return requests.get(f"{API_BASE}/config", timeout=3).json()
    except Exception:
        return {"provider": "ollama", "ollama_model": "llama3.1:8b"}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif;font-size:24px;letter-spacing:4px;
         background:linear-gradient(135deg,#00DFA0,#6B00F0);-webkit-background-clip:text;
         -webkit-text-fill-color:transparent;">NeuralDoc</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
         color:rgba(255,255,255,0.3);letter-spacing:2px;margin-bottom:16px;">RAG SYSTEM</div>
    """, unsafe_allow_html=True)

    h = get_health()
    ready = h.get("pipeline_ready", False)
    chunks = h.get("total_chunks", 0)
    files = h.get("indexed_files", [])

    status_color = "#00DFA0" if ready else "#E0005A"
    status_text = f"READY &bull; {chunks} chunks" if ready else "NO DOCUMENTS INDEXED"
    st.markdown(f"""
    <div style="display:inline-flex;align-items:center;gap:7px;margin-bottom:12px;
         font-family:'JetBrains Mono',monospace;font-size:11px;color:{status_color};
         border:1px solid {status_color}33;background:{status_color}0E;
         padding:5px 12px;border-radius:6px;letter-spacing:1px;">
      <span style="width:6px;height:6px;border-radius:50%;background:{status_color};
            display:inline-block;animation:dot 1.5s ease-in-out infinite;"></span>
      {status_text}
    </div>
    <style>@keyframes dot{{0%,100%{{opacity:1;}}50%{{opacity:0.2;}}}}</style>
    """, unsafe_allow_html=True)

    if files:
        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,0.28);letter-spacing:2px;margin:10px 0 6px;">INDEXED</div>', unsafe_allow_html=True)
        for f in files:
            name = f.replace("\\", "/").split("/")[-1]
            st.caption(f"— {name}")

    st.divider()

    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,0.28);letter-spacing:2px;margin-bottom:10px;">MODEL</div>', unsafe_allow_html=True)

    cfg = get_config()
    cur_provider = cfg.get("provider", "ollama")

    provider = st.selectbox("Provider", ["ollama", "openai"],
                            index=0 if cur_provider == "ollama" else 1)
    if provider == "ollama":
        model = st.selectbox("Model",
            ["llama3.1:8b", "llama3.3:70b", "mistral:7b", "qwen2.5:7b", "qwen2.5:72b"])
        upd: dict = {"provider": "ollama", "ollama_model": model}
    else:
        model = st.selectbox("OpenAI Model", ["gpt-4o", "gpt-4o-mini"])
        upd = {"provider": "openai", "openai_model": model}

    thr = st.slider("Evidence Threshold", -10.0, 1.0, -10.0, 0.05,
                    help="Cross-encoder score cutoff. -10 = accept all.")
    upd["similarity_threshold"] = thr

    if st.button("Apply Settings", use_container_width=True):
        try:
            r = requests.post(f"{API_BASE}/config/update", json=upd, timeout=10)
            if r.status_code == 200:
                st.success(f"Active: {r.json()['current']['model']}")
        except Exception:
            st.error("Could not reach API")

    st.divider()
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main ──────────────────────────────────────────────────────────────────────
col_chat, col_upload = st.columns([3, 2], gap="large")

# ── LEFT: Chat ────────────────────────────────────────────────────────────────
with col_chat:
    # Header
    st.markdown("""
    <div style="margin-bottom:20px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#6B00F0;
           letter-spacing:4px;margin-bottom:6px;">// DOCUMENT QA</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:48px;letter-spacing:2px;
           color:#fff;line-height:1;">
        ASK YOUR<span style="background:linear-gradient(90deg,#6B00F0,#E0005A);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;"> DOCS</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Status row
    h2 = get_health()
    r2 = h2.get("pipeline_ready", False)
    tc = h2.get("total_chunks", 0)
    active_model = cfg.get("ollama_model", model) if provider == "ollama" else cfg.get("openai_model", model)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div style="padding:10px 14px;background:rgba(255,255,255,0.025);
            border:1px solid {'rgba(0,223,160,0.2)' if r2 else 'rgba(224,0,90,0.2)'};
            border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:11px;
            color:{'#00DFA0' if r2 else '#E0005A'};letter-spacing:1px;">
            {'PIPELINE READY' if r2 else 'OFFLINE'}</div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style="padding:10px 14px;background:rgba(255,255,255,0.025);
            border:1px solid rgba(107,0,240,0.2);border-radius:8px;
            font-family:'JetBrains Mono',monospace;font-size:11px;color:#6B00F0;letter-spacing:1px;">
            {tc} CHUNKS</div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div style="padding:10px 14px;background:rgba(255,255,255,0.025);
            border:1px solid rgba(0,223,160,0.2);border-radius:8px;
            font-family:'JetBrains Mono',monospace;font-size:11px;color:#00DFA0;letter-spacing:1px;
            overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
            title="{active_model}">{active_model[:14]}</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.session_state.messages:
        msgs_html = ""
        for m in st.session_state.messages:
            if m["role"] == "user":
                msgs_html += f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:12px;">
                  <div style="max-width:78%;padding:13px 17px;
                       background:rgba(107,0,240,0.18);
                       border:1px solid rgba(107,0,240,0.3);
                       border-radius:16px 4px 16px 16px;
                       font-size:14px;color:rgba(255,255,255,0.88);line-height:1.7;
                       font-family:'Syne',sans-serif;">
                    {m['content']}
                  </div>
                </div>"""
            else:
                refs_html = ""
                if m.get("references"):
                    refs_html = '<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:5px;">'
                    for ref in m["references"]:
                        refs_html += f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 9px;border-radius:4px;color:#00DFA0;background:rgba(0,223,160,0.08);border:1px solid rgba(0,223,160,0.2);">ref: {ref}</span>'
                    refs_html += "</div>"
                refused_html = ""
                if m.get("refused"):
                    refused_html = '<div style="margin-top:8px;font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#E0005A;background:rgba(224,0,90,0.08);border:1px solid rgba(224,0,90,0.2);padding:5px 10px;border-radius:6px;display:inline-block;">REFUSAL &mdash; Insufficient evidence</div>'
                lat_html = ""
                if m.get("latency_ms"):
                    lat_html = f'<div style="margin-top:8px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,0.22);">{m["latency_ms"]} ms</div>'

                msgs_html += f"""
                <div style="display:flex;margin-bottom:12px;gap:10px;align-items:flex-start;">
                  <div style="width:30px;height:30px;border-radius:6px;flex-shrink:0;margin-top:2px;
                       background:linear-gradient(135deg,#6B00F0,#E0005A);
                       display:flex;align-items:center;justify-content:center;">
                    <span style="font-family:'Bebas Neue',sans-serif;font-size:12px;color:#fff;letter-spacing:1px;">AI</span>
                  </div>
                  <div style="max-width:85%;padding:13px 17px;
                       background:rgba(255,255,255,0.035);
                       border:1px solid rgba(255,255,255,0.08);
                       border-radius:4px 16px 16px 16px;
                       font-size:14px;color:rgba(255,255,255,0.85);line-height:1.75;
                       font-family:'Syne',sans-serif;">
                    {m['content']}{refs_html}{refused_html}{lat_html}
                  </div>
                </div>"""

        st.markdown(f"""
        <div style="max-height:50vh;overflow-y:auto;padding:4px 2px 12px;
             scrollbar-width:thin;scrollbar-color:rgba(107,0,240,0.4) transparent;">
          {msgs_html}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:56px 20px;color:rgba(255,255,255,0.22);">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:36px;
               letter-spacing:3px;margin-bottom:10px;
               background:linear-gradient(90deg,rgba(107,0,240,0.5),rgba(0,223,160,0.5));
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            AWAITING INPUT
          </div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:1px;">
            Upload a document, then ask any question
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    qcol, bcol = st.columns([5, 1])
    with qcol:
        query = st.text_input("", placeholder="Type your question here...",
                              label_visibility="collapsed", key="q_input")
    with bcol:
        ask = st.button("Send", use_container_width=True)

    if ask and query:
        h3 = get_health()
        if not h3.get("pipeline_ready"):
            st.warning("No documents indexed. Upload a PDF on the right first.")
        else:
            with st.spinner("Retrieving and generating answer..."):
                try:
                    resp = requests.post(f"{API_BASE}/query",
                                         json={"query": query}, timeout=120)
                    if resp.status_code == 200:
                        d = resp.json()
                        st.session_state.messages.extend([
                            {"role": "user", "content": query},
                            {"role": "assistant", "content": d["answer"],
                             "references": d["references"],
                             "refused": d["refused"],
                             "latency_ms": d["latency_ms"]}
                        ])
                        st.rerun()
                    else:
                        st.error(f"API error: {resp.json().get('detail', resp.text)}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach API. Run: uv run uvicorn api:app --reload")

# ── RIGHT: Upload ─────────────────────────────────────────────────────────────
with col_upload:
    st.markdown("""
    <div style="margin-bottom:20px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#E0005A;
           letter-spacing:4px;margin-bottom:6px;">// INDEX DOCUMENTS</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:48px;letter-spacing:2px;
           color:#fff;line-height:1;">
        UPLOAD<span style="background:linear-gradient(90deg,#E0005A,#F0A800);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;"> PDF</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload zone description
    st.markdown("""
    <div style="padding:24px 22px;
         background:rgba(107,0,240,0.04);
         border:1px dashed rgba(107,0,240,0.38);
         border-radius:14px;margin-bottom:16px;
         animation:zonePulse 4s ease-in-out infinite;text-align:center;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:3px;
           color:rgba(255,255,255,0.5);margin-bottom:6px;">DROP PDF BELOW</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
           color:rgba(255,255,255,0.28);letter-spacing:1px;">
        Parsed &rarr; Chunked &rarr; Embedded &rarr; Indexed
      </div>
    </div>
    <style>
    @keyframes zonePulse{
      0%,100%{border-color:rgba(107,0,240,0.38);box-shadow:0 0 0 transparent;}
      50%{border-color:rgba(107,0,240,0.72);box-shadow:0 0 32px rgba(107,0,240,0.12);}
    }
    </style>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        kb = uploaded.size // 1024
        st.markdown(f"""
        <div style="padding:11px 15px;background:rgba(0,223,160,0.06);
             border:1px solid rgba(0,223,160,0.2);border-radius:8px;margin-bottom:12px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
               color:#00DFA0;letter-spacing:0.5px;">
            {uploaded.name} &mdash; {kb} KB
          </div>
        </div>""", unsafe_allow_html=True)

        if st.button("Index Document", use_container_width=True):
            with st.spinner("Processing PDF..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/ingest",
                        files={"file": (uploaded.name, uploaded, "application/pdf")},
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        d = resp.json()
                        st.success(f"Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                        c1i, c2i = st.columns(2)
                        with c1i:
                            st.markdown(f"""<div style="padding:10px;background:rgba(0,223,160,0.07);
                                border:1px solid rgba(0,223,160,0.2);border-radius:8px;
                                font-family:'JetBrains Mono',monospace;font-size:11px;
                                color:#00DFA0;text-align:center;">
                                +{d['chunks_indexed']} new</div>""", unsafe_allow_html=True)
                        with c2i:
                            st.markdown(f"""<div style="padding:10px;background:rgba(107,0,240,0.07);
                                border:1px solid rgba(107,0,240,0.2);border-radius:8px;
                                font-family:'JetBrains Mono',monospace;font-size:11px;
                                color:#6B00F0;text-align:center;">
                                {d['total_chunks']} total</div>""", unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error(resp.text)
                except Exception as e:
                    st.error(str(e))

    # Info panel
    st.markdown("""
    <div style="margin-top:20px;padding:20px 22px;background:rgba(255,255,255,0.018);
         border:1px solid rgba(255,255,255,0.06);border-radius:12px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
           color:rgba(255,255,255,0.25);letter-spacing:3px;margin-bottom:14px;">NOTES</div>
      <div style="font-size:13px;color:rgba(255,255,255,0.38);line-height:1.9;
           font-family:'Syne',sans-serif;">
        Ask precise questions for best results.<br>
        Every answer includes source citations.<br>
        Unanswerable queries return a refusal &mdash; not a guess.<br>
        Multiple PDFs can be uploaded and searched together.
      </div>
    </div>
    """, unsafe_allow_html=True)