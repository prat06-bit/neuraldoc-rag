"""RAG Chat page — NeuralDoc"""
import requests
import streamlit as st

st.set_page_config(
    page_title="NeuralDoc · Chat",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:8000"

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;}
[data-testid="stAppViewContainer"]{background:#020008;font-family:'Syne',sans-serif;}
[data-testid="stHeader"],[data-testid="stToolbar"]{display:none!important;}
.block-container{padding:2rem 2rem 4rem!important;max-width:1400px!important;}

/* Ambient background */
[data-testid="stAppViewContainer"]::before{
  content:'';position:fixed;inset:0;z-index:0;
  background:radial-gradient(ellipse 70% 50% at 10% 10%,rgba(123,0,255,.15),transparent 60%),
             radial-gradient(ellipse 50% 70% at 90% 90%,rgba(0,255,178,.1),transparent 60%);
  pointer-events:none;}

/* Sidebar */
[data-testid="stSidebar"]{
  background:rgba(10,0,25,.95)!important;
  border-right:1px solid rgba(123,0,255,.2)!important;}
[data-testid="stSidebar"] *{font-family:'Syne',sans-serif!important;}

/* ── Upload zone ── */
.upload-zone{
  background:rgba(123,0,255,.04);
  border:2px dashed rgba(123,0,255,.35);
  border-radius:24px;
  padding:56px 40px;
  text-align:center;
  position:relative;overflow:hidden;
  transition:all .4s ease;
  animation:zoneBreath 4s ease-in-out infinite;
  margin-bottom:32px;
}
@keyframes zoneBreath{
  0%,100%{border-color:rgba(123,0,255,.35);box-shadow:0 0 0 rgba(123,0,255,0);}
  50%{border-color:rgba(123,0,255,.7);box-shadow:0 0 40px rgba(123,0,255,.15);}
}
.upload-zone::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(123,0,255,.08),transparent 70%);
  animation:scanLine 3s ease-in-out infinite;
}
@keyframes scanLine{
  0%{background:radial-gradient(ellipse at 50% 0%,rgba(123,0,255,.08),transparent 70%);}
  50%{background:radial-gradient(ellipse at 50% 100%,rgba(0,255,178,.08),transparent 70%);}
  100%{background:radial-gradient(ellipse at 50% 0%,rgba(123,0,255,.08),transparent 70%);}
}
.upload-icon{
  font-size:52px;margin-bottom:16px;display:block;
  animation:iconBounce 3s ease-in-out infinite;
  filter:drop-shadow(0 0 20px rgba(123,0,255,.5));
}
@keyframes iconBounce{0%,100%{transform:translateY(0);}50%{transform:translateY(-8px);}}
.upload-title{
  font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:3px;
  background:linear-gradient(90deg,#7B00FF,#FF0080);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  margin-bottom:8px;
}
.upload-sub{color:rgba(255,255,255,.4);font-size:14px;letter-spacing:.5px;margin-bottom:28px;}
.upload-formats{
  display:inline-flex;gap:8px;flex-wrap:wrap;justify-content:center;
}
.fmt-badge{
  font-family:'JetBrains Mono',monospace;font-size:11px;
  padding:3px 10px;border-radius:20px;
  color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2);
}

/* Progress bar */
.prog-wrap{
  background:rgba(255,255,255,.05);border-radius:30px;
  height:6px;overflow:hidden;margin-top:16px;
}
.prog-bar{
  height:100%;border-radius:30px;
  background:linear-gradient(90deg,#7B00FF,#FF0080,#00FFB2);
  animation:progFlow 2s ease-in-out infinite;
}
@keyframes progFlow{
  0%{background-size:200% 100%;background-position:200% 0;}
  100%{background-size:200% 100%;background-position:-200% 0;}
}

/* ── Status chips ── */
.status-bar{
  display:flex;gap:12px;flex-wrap:wrap;
  padding:16px 20px;
  background:rgba(255,255,255,.02);
  border:1px solid rgba(255,255,255,.06);
  border-radius:14px;margin-bottom:24px;
  animation:fadeIn .6s ease both;
}
@keyframes fadeIn{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}
.chip{
  display:inline-flex;align-items:center;gap:6px;
  font-family:'JetBrains Mono',monospace;font-size:11px;
  padding:4px 12px;border-radius:20px;letter-spacing:1px;
}
.chip-green{color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2);}
.chip-purple{color:#7B00FF;background:rgba(123,0,255,.08);border:1px solid rgba(123,0,255,.2);}
.chip-pink{color:#FF0080;background:rgba(255,0,128,.08);border:1px solid rgba(255,0,128,.2);}
.chip-dot{width:5px;height:5px;border-radius:50%;background:currentColor;animation:blink 1.5s ease-in-out infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.2;}}

/* ── Chat messages ── */
.msg-wrap{
  display:flex;flex-direction:column;gap:16px;
  max-height:55vh;overflow-y:auto;
  padding:4px 4px 20px;
  scrollbar-width:thin;scrollbar-color:rgba(123,0,255,.3) transparent;
}
.msg{
  display:flex;gap:12px;align-items:flex-start;
  animation:msgSlide .4s ease both;
}
@keyframes msgSlide{from{opacity:0;transform:translateX(-10px);}to{opacity:1;transform:translateX(0);}}
.msg-user{flex-direction:row-reverse;}
.msg-user .msg-bubble{
  background:linear-gradient(135deg,rgba(123,0,255,.25),rgba(255,0,128,.15));
  border:1px solid rgba(123,0,255,.3);
  border-radius:20px 4px 20px 20px;
  margin-left:40px;
}
.msg-ai .msg-bubble{
  background:rgba(255,255,255,.04);
  border:1px solid rgba(255,255,255,.08);
  border-radius:4px 20px 20px 20px;
  margin-right:40px;
}
.msg-bubble{padding:16px 20px;font-size:14px;color:rgba(255,255,255,.85);line-height:1.7;}
.msg-avatar{
  width:36px;height:36px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  font-size:16px;
}
.avatar-ai{background:linear-gradient(135deg,#7B00FF,#FF0080);}
.avatar-user{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);}

.ref-pill{
  display:inline-flex;align-items:center;gap:4px;
  font-family:'JetBrains Mono',monospace;font-size:10px;
  padding:2px 8px;border-radius:20px;margin:2px;
  color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2);
}
.refused-badge{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 14px;border-radius:8px;font-size:12px;
  color:#FF0080;background:rgba(255,0,128,.08);border:1px solid rgba(255,0,128,.2);
  margin-top:8px;font-family:'JetBrains Mono',monospace;
}
.latency{
  font-family:'JetBrains Mono',monospace;font-size:10px;
  color:rgba(255,255,255,.25);margin-top:8px;
}

/* ── Query input ── */
.stTextInput input{
  background:rgba(255,255,255,.04)!important;
  border:1px solid rgba(123,0,255,.3)!important;
  color:#fff!important;font-family:'Syne',sans-serif!important;
  border-radius:50px!important;padding:14px 20px!important;
  font-size:15px!important;
  transition:all .3s!important;
}
.stTextInput input:focus{
  border-color:rgba(123,0,255,.7)!important;
  box-shadow:0 0 20px rgba(123,0,255,.2)!important;
}
.stButton button{
  background:linear-gradient(135deg,#7B00FF,#FF0080)!important;
  color:#fff!important;border:none!important;
  border-radius:50px!important;font-family:'Syne',sans-serif!important;
  font-weight:700!important;letter-spacing:.5px!important;
  transition:all .3s!important;
}
.stButton button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(123,0,255,.4)!important;}

/* ── File uploader ── */
[data-testid="stFileUploader"]{
  background:transparent!important;border:none!important;
}
[data-testid="stFileUploaderDropzone"]{
  background:rgba(123,0,255,.05)!important;
  border:1px solid rgba(123,0,255,.3)!important;
  border-radius:16px!important;
}

/* Sidebar styling */
.sidebar-logo{
  font-family:'Bebas Neue',sans-serif;font-size:24px;letter-spacing:3px;
  background:linear-gradient(135deg,#00FFB2,#7B00FF);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  margin-bottom:4px;
}
.sidebar-section{
  font-family:'JetBrains Mono',monospace;font-size:10px;
  color:rgba(255,255,255,.3);letter-spacing:3px;
  text-transform:uppercase;margin:20px 0 8px;
}
.stSelectbox select,.stSlider{filter:none!important;}
label,.stSelectbox label,.stSlider label{color:rgba(255,255,255,.6)!important;font-size:13px!important;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">NeuralDoc</div>', unsafe_allow_html=True)
    st.caption("Production RAG System")
    st.divider()

    # Health
    try:
        h = requests.get(f"{API_BASE}/health", timeout=3).json()
        ready = h.get("pipeline_ready", False)
        chunks = h.get("total_chunks", 0)
        files = h.get("indexed_files", [])
        if ready:
            st.markdown(f'<span class="chip chip-green"><span class="chip-dot"></span>PIPELINE READY · {chunks} chunks</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="chip chip-pink">NO DOCUMENTS YET</span>', unsafe_allow_html=True)
        if files:
            st.markdown('<div class="sidebar-section">Indexed Files</div>', unsafe_allow_html=True)
            for f in files:
                st.caption(f"📄 {f.split('/')[-1].split('\\')[-1]}")
    except Exception:
        st.error("API offline — run `uvicorn api:app`")

    st.divider()
    st.markdown('<div class="sidebar-section">Model Settings</div>', unsafe_allow_html=True)

    try:
        cfg = requests.get(f"{API_BASE}/config", timeout=3).json()
        cur_provider = cfg.get("provider", "ollama")
        cur_model = cfg.get("ollama_model", "llama3.1:8b")
    except Exception:
        cur_provider, cur_model = "ollama", "llama3.1:8b"

    provider = st.selectbox("Provider", ["ollama", "openai"],
                            index=0 if cur_provider == "ollama" else 1)
    if provider == "ollama":
        model = st.selectbox("Model",
            ["llama3.1:8b", "llama3.3:70b", "mistral:7b", "qwen2.5:7b", "qwen2.5:72b"])
        payload: dict = {"provider": "ollama", "ollama_model": model}
    else:
        model = st.selectbox("OpenAI Model", ["gpt-4o", "gpt-4o-mini"])
        payload = {"provider": "openai", "openai_model": model}

    threshold = st.slider("Similarity Threshold", -10.0, 1.0, -10.0, 0.05)
    payload["similarity_threshold"] = threshold

    if st.button("⚡ Apply Settings"):
        try:
            r = requests.post(f"{API_BASE}/config/update", json=payload, timeout=10)
            if r.status_code == 200:
                st.success(f"Switched to {r.json()['current']['model']}")
        except Exception:
            st.error("Config update failed")

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Main ─────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    # Page header
    st.markdown("""
    <div style="margin-bottom:28px;animation:fadeIn .6s ease both;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#7B00FF;letter-spacing:4px;margin-bottom:8px;">// ASK YOUR DOCUMENTS</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:48px;letter-spacing:2px;color:#fff;line-height:1;">
        NEURAL<span style="background:linear-gradient(90deg,#7B00FF,#FF0080);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"> CHAT</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Status bar
    try:
        h2 = requests.get(f"{API_BASE}/health", timeout=2).json()
        ready2 = h2.get("pipeline_ready", False)
        tc = h2.get("total_chunks", 0)
        status_html = f"""
        <div class="status-bar">
          <span class="chip {'chip-green' if ready2 else 'chip-pink'}">
            <span class="chip-dot"></span>{'READY' if ready2 else 'NOT READY'}
          </span>
          <span class="chip chip-purple"><span class="chip-dot"></span>{tc} CHUNKS</span>
          <span class="chip chip-green"><span class="chip-dot"></span>{model}</span>
        </div>"""
        st.markdown(status_html, unsafe_allow_html=True)
    except Exception:
        st.markdown('<div class="status-bar"><span class="chip chip-pink">API OFFLINE</span></div>', unsafe_allow_html=True)

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.session_state.messages:
        msgs_html = '<div class="msg-wrap">'
        for m in st.session_state.messages:
            role = m["role"]
            content = m["content"]
            if role == "user":
                msgs_html += f'<div class="msg msg-user"><div class="msg-avatar avatar-user">👤</div><div class="msg-bubble">{content}</div></div>'
            else:
                refs_html = ""
                if m.get("references"):
                    refs_html = '<div style="margin-top:10px;">'
                    for ref in m["references"]:
                        refs_html += f'<span class="ref-pill">📎 {ref}</span>'
                    refs_html += "</div>"
                refused_html = '<div class="refused-badge">🚫 REFUSAL TRIGGERED</div>' if m.get("refused") else ""
                lat_html = f'<div class="latency">⏱ {m.get("latency_ms", "")} ms</div>' if m.get("latency_ms") else ""
                msgs_html += f'<div class="msg msg-ai"><div class="msg-avatar avatar-ai">⚡</div><div class="msg-bubble">{content}{refs_html}{refused_html}{lat_html}</div></div>'
        msgs_html += "</div>"
        st.markdown(msgs_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px;color:rgba(255,255,255,.25);animation:fadeIn 1s ease both;">
          <div style="font-size:48px;margin-bottom:12px;filter:drop-shadow(0 0 20px rgba(123,0,255,.3));">⚡</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:24px;letter-spacing:2px;margin-bottom:8px;">READY TO ANSWER</div>
          <div style="font-size:13px;">Upload a PDF and start asking questions</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Query input
    qcol1, qcol2 = st.columns([5, 1])
    with qcol1:
        query = st.text_input("", placeholder="Ask anything about your documents...", label_visibility="collapsed", key="query_input")
    with qcol2:
        ask = st.button("Ask ⚡", use_container_width=True)

    if (ask or query) and query:
        try:
            h_check = requests.get(f"{API_BASE}/health", timeout=2).json()
            if not h_check.get("pipeline_ready"):
                st.warning("Upload and index a PDF first →")
            else:
                with st.spinner("Retrieving & generating..."):
                    resp = requests.post(f"{API_BASE}/query", json={"query": query}, timeout=120)
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.messages.append({"role": "user", "content": query})
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"],
                        "references": data["references"],
                        "refused": data["refused"],
                        "latency_ms": data["latency_ms"],
                    })
                    st.rerun()
                else:
                    st.error(f"Error: {resp.json().get('detail', resp.text)}")
        except requests.exceptions.ConnectionError:
            st.error("API not reachable. Start: `uv run uvicorn api:app --reload`")

# Right column — Upload
with col_right:
    st.markdown("""
    <div style="margin-bottom:20px;animation:fadeIn .6s ease .2s both;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#FF0080;letter-spacing:4px;margin-bottom:8px;">// INDEX DOCUMENTS</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:48px;letter-spacing:2px;color:#fff;line-height:1;">
        UPLOAD<span style="background:linear-gradient(90deg,#FF0080,#FFB800);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"> PDF</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Animated upload zone header
    st.markdown("""
    <div class="upload-zone">
      <span class="upload-icon">📄</span>
      <div class="upload-title">DROP YOUR PDF</div>
      <div class="upload-sub">Parsed · Chunked · Indexed · Ready for Questions</div>
      <div class="upload-formats">
        <span class="fmt-badge">PDF</span>
        <span class="fmt-badge">Multi-column</span>
        <span class="fmt-badge">Tables</span>
        <span class="fmt-badge">Any domain</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        st.markdown(f"""
        <div style="padding:12px 16px;background:rgba(0,255,178,.06);border:1px solid rgba(0,255,178,.2);
                    border-radius:12px;margin-bottom:12px;animation:fadeIn .4s ease both;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#00FFB2;letter-spacing:1px;">
            📄 {uploaded.name} · {uploaded.size // 1024} KB
          </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Index This PDF", use_container_width=True):
            with st.spinner("Parsing, chunking, embedding..."):
                st.markdown('<div class="prog-wrap"><div class="prog-bar"></div></div>', unsafe_allow_html=True)
                try:
                    resp = requests.post(
                        f"{API_BASE}/ingest",
                        files={"file": (uploaded.name, uploaded, "application/pdf")},
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        d = resp.json()
                        st.success(f"✓ Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                        st.markdown(f"""
                        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;">
                          <span class="chip chip-green">✓ {d['chunks_indexed']} NEW CHUNKS</span>
                          <span class="chip chip-purple">∑ {d['total_chunks']} TOTAL</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Failed: {e}")

    # Tips card
    st.markdown("""
    <div style="margin-top:24px;padding:24px;background:rgba(255,255,255,.02);
                border:1px solid rgba(255,255,255,.07);border-radius:16px;
                animation:fadeIn .6s ease .4s both;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                  color:rgba(255,255,255,.3);letter-spacing:3px;margin-bottom:16px;">// TIPS</div>
      <div style="font-size:13px;color:rgba(255,255,255,.4);line-height:1.8;">
        ⚡ Ask specific questions for best results<br>
        📎 Every answer includes inline citations<br>
        🚫 Unanswerable queries are refused — not guessed<br>
        🔄 Upload multiple PDFs to expand knowledge
      </div>
    </div>
    """, unsafe_allow_html=True)