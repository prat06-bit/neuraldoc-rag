"""RAG Chat — NeuralDoc"""
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NeuralDoc · Chat",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stHeader"],[data-testid="stToolbar"],#MainMenu,footer{display:none!important;}
[data-testid="stAppViewContainer"]{background:#020008!important;}
[data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container{
    background:transparent!important;padding:1rem 1.5rem!important;max-width:100%!important;}
[data-testid="stSidebar"]{background:rgba(8,0,20,.97)!important;border-right:1px solid rgba(123,0,255,.2)!important;}
label,.stSelectbox label,.stSlider label{color:rgba(255,255,255,.6)!important;font-family:'Syne',sans-serif!important;}
.stTextInput input{
    background:rgba(123,0,255,.08)!important;border:1px solid rgba(123,0,255,.35)!important;
    color:#fff!important;border-radius:50px!important;padding:12px 20px!important;font-size:14px!important;}
.stTextInput input:focus{border-color:rgba(123,0,255,.7)!important;box-shadow:0 0 20px rgba(123,0,255,.2)!important;}
.stButton>button{
    background:linear-gradient(135deg,#7B00FF,#FF0080)!important;color:#fff!important;
    border:none!important;border-radius:50px!important;font-weight:700!important;
    transition:transform .3s,box-shadow .3s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(123,0,255,.4)!important;}
[data-testid="stFileUploaderDropzone"]{
    background:rgba(123,0,255,.05)!important;border:1px solid rgba(123,0,255,.3)!important;
    border-radius:16px!important;}
</style>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Syne:wght@400;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

API_BASE = "http://localhost:8000"

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Bebas Neue',sans-serif;font-size:26px;letter-spacing:3px;
         background:linear-gradient(135deg,#00FFB2,#7B00FF);-webkit-background-clip:text;
         -webkit-text-fill-color:transparent;margin-bottom:4px;">NeuralDoc</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,.3);
         letter-spacing:2px;margin-bottom:16px;">PRODUCTION RAG</div>
    """, unsafe_allow_html=True)

    try:
        h = requests.get(f"{API_BASE}/health", timeout=3).json()
        ready = h.get("pipeline_ready", False)
        chunks = h.get("total_chunks", 0)
        files = h.get("indexed_files", [])
        color = "#00FFB2" if ready else "#FF0080"
        label = f"READY &bull; {chunks} chunks" if ready else "NO DOCS INDEXED"
        st.markdown(f"""
        <div style="display:inline-flex;align-items:center;gap:6px;
             font-family:'JetBrains Mono',monospace;font-size:11px;color:{color};
             border:1px solid {color}44;background:{color}11;
             padding:5px 12px;border-radius:20px;letter-spacing:1px;margin-bottom:12px;">
          <span style="width:6px;height:6px;border-radius:50%;background:{color};display:inline-block;"></span>
          {label}
        </div>""", unsafe_allow_html=True)
        if files:
            st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,.3);letter-spacing:2px;margin:12px 0 6px;">INDEXED FILES</div>', unsafe_allow_html=True)
            for f in files:
                st.caption(f"📄 {f.split('/')[-1].split(chr(92))[-1]}")
    except Exception:
        st.error("API offline")

    st.divider()
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,.3);letter-spacing:2px;margin-bottom:8px;">MODEL SETTINGS</div>', unsafe_allow_html=True)

    try:
        cfg = requests.get(f"{API_BASE}/config", timeout=3).json()
        cur_p = cfg.get("provider","ollama"); cur_m = cfg.get("ollama_model","llama3.1:8b")
    except Exception:
        cur_p, cur_m = "ollama", "llama3.1:8b"

    provider = st.selectbox("Provider", ["ollama","openai"], index=0 if cur_p=="ollama" else 1)
    if provider == "ollama":
        model = st.selectbox("Model", ["llama3.1:8b","llama3.3:70b","mistral:7b","qwen2.5:7b","qwen2.5:72b"])
        upd: dict = {"provider":"ollama","ollama_model":model}
    else:
        model = st.selectbox("OpenAI Model", ["gpt-4o","gpt-4o-mini"])
        upd = {"provider":"openai","openai_model":model}

    thr = st.slider("Similarity Threshold", -10.0, 1.0, -10.0, 0.05)
    upd["similarity_threshold"] = thr

    if st.button("⚡ Apply", use_container_width=True):
        try:
            r = requests.post(f"{API_BASE}/config/update", json=upd, timeout=10)
            st.success(f"Switched to {r.json()['current']['model']}")
        except Exception:
            st.error("Update failed")

    st.divider()
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main layout ───────────────────────────────────────────────────────────────
col_chat, col_upload = st.columns([3, 2], gap="large")

# ── Left: Chat ────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown("""
    <div style="margin-bottom:20px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#7B00FF;letter-spacing:4px;margin-bottom:6px;">// ASK YOUR DOCUMENTS</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:52px;letter-spacing:2px;color:#fff;line-height:1;">
        NEURAL<span style="background:linear-gradient(90deg,#7B00FF,#FF0080);-webkit-background-clip:text;-webkit-text-fill-color:transparent;"> CHAT</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Status chips
    try:
        h2 = requests.get(f"{API_BASE}/health", timeout=2).json()
        r2 = h2.get("pipeline_ready", False)
        tc = h2.get("total_chunks", 0)
        st.markdown(f"""
        <div style="display:flex;gap:8px;flex-wrap:wrap;padding:14px 18px;background:rgba(255,255,255,.02);
             border:1px solid rgba(255,255,255,.06);border-radius:12px;margin-bottom:20px;">
          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;padding:3px 10px;border-radius:20px;
                color:{'#00FFB2' if r2 else '#FF0080'};background:{'rgba(0,255,178,.08)' if r2 else 'rgba(255,0,128,.08)'};
                border:1px solid {'rgba(0,255,178,.2)' if r2 else 'rgba(255,0,128,.2)'};letter-spacing:1px;">
            {'&#9679; READY' if r2 else '&#9675; OFFLINE'}</span>
          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;padding:3px 10px;border-radius:20px;
                color:#7B00FF;background:rgba(123,0,255,.08);border:1px solid rgba(123,0,255,.2);letter-spacing:1px;">
            {tc} CHUNKS</span>
          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;padding:3px 10px;border-radius:20px;
                color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2);letter-spacing:1px;">
            {model}</span>
        </div>""", unsafe_allow_html=True)
    except Exception:
        pass

    # Messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.session_state.messages:
        msgs = ""
        for m in st.session_state.messages:
            if m["role"] == "user":
                msgs += f"""
                <div style="display:flex;justify-content:flex-end;margin-bottom:14px;animation:mIn .4s ease both;">
                  <div style="max-width:75%;padding:14px 18px;background:linear-gradient(135deg,rgba(123,0,255,.25),rgba(255,0,128,.15));
                       border:1px solid rgba(123,0,255,.3);border-radius:20px 4px 20px 20px;
                       font-size:14px;color:rgba(255,255,255,.88);line-height:1.7;">{m['content']}</div>
                  <div style="width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.08);
                       border:1px solid rgba(255,255,255,.15);display:flex;align-items:center;
                       justify-content:center;font-size:14px;flex-shrink:0;margin-left:10px;">&#128100;</div>
                </div>"""
            else:
                refs = ""
                if m.get("references"):
                    refs = '<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:4px;">'
                    for ref in m["references"]:
                        refs += f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;padding:2px 8px;border-radius:20px;color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2);">&#128206; {ref}</span>'
                    refs += "</div>"
                refused = '<div style="margin-top:8px;font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#FF0080;background:rgba(255,0,128,.08);border:1px solid rgba(255,0,128,.2);padding:5px 10px;border-radius:8px;display:inline-block;">&#128683; REFUSAL TRIGGERED</div>' if m.get("refused") else ""
                lat = f'<div style="margin-top:8px;font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(255,255,255,.25);">&#9201; {m.get("latency_ms","")} ms</div>' if m.get("latency_ms") else ""
                msgs += f"""
                <div style="display:flex;margin-bottom:14px;animation:mIn .4s ease both;">
                  <div style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#7B00FF,#FF0080);
                       display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-right:10px;">&#9889;</div>
                  <div style="max-width:80%;padding:14px 18px;background:rgba(255,255,255,.04);
                       border:1px solid rgba(255,255,255,.08);border-radius:4px 20px 20px 20px;
                       font-size:14px;color:rgba(255,255,255,.85);line-height:1.7;">{m['content']}{refs}{refused}{lat}</div>
                </div>"""
        st.markdown(f"""
        <style>@keyframes mIn{{from{{opacity:0;transform:translateX(-10px);}}to{{opacity:1;transform:translateX(0);}}}}</style>
        <div style="max-height:52vh;overflow-y:auto;padding:4px 4px 16px;
             scrollbar-width:thin;scrollbar-color:rgba(123,0,255,.3) transparent;">{msgs}</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:52px 20px;color:rgba(255,255,255,.25);">
          <div style="font-size:52px;margin-bottom:14px;filter:drop-shadow(0 0 20px rgba(123,0,255,.4));">&#9889;</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:28px;letter-spacing:3px;margin-bottom:8px;">READY TO ANSWER</div>
          <div style="font-size:13px;">Upload a PDF on the right, then ask questions here</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    qc1, qc2 = st.columns([5, 1])
    with qc1:
        query = st.text_input("", placeholder="Ask anything about your documents...", label_visibility="collapsed", key="q")
    with qc2:
        ask = st.button("Ask ⚡", use_container_width=True)

    if ask and query:
        try:
            h3 = requests.get(f"{API_BASE}/health", timeout=2).json()
            if not h3.get("pipeline_ready"):
                st.warning("Upload and index a PDF first →")
            else:
                with st.spinner("Retrieving & generating..."):
                    resp = requests.post(f"{API_BASE}/query", json={"query": query}, timeout=120)
                if resp.status_code == 200:
                    d = resp.json()
                    st.session_state.messages.extend([
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": d["answer"],
                         "references": d["references"], "refused": d["refused"], "latency_ms": d["latency_ms"]}
                    ])
                    st.rerun()
                else:
                    st.error(resp.json().get("detail", "Error"))
        except requests.exceptions.ConnectionError:
            st.error("API not reachable — run `uvicorn api:app`")

# ── Right: Upload ─────────────────────────────────────────────────────────────
with col_upload:
    # Animated upload header using components.html
    components.html("""
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
    body{margin:0;background:transparent;font-family:'Bebas Neue',sans-serif;}
    .hdr{margin-bottom:4px;}
    .tag{font-family:'JetBrains Mono',monospace;font-size:11px;color:#FF0080;letter-spacing:4px;margin-bottom:8px;}
    .title{font-size:52px;letter-spacing:2px;color:#fff;line-height:1;}
    .title span{background:linear-gradient(90deg,#FF0080,#FFB800);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}

    .upload-box{
      background:rgba(123,0,255,.04);border:2px dashed rgba(123,0,255,.4);
      border-radius:22px;padding:48px 32px;text-align:center;
      position:relative;overflow:hidden;
      animation:zBreath 4s ease-in-out infinite;
      margin-bottom:8px;
    }
    @keyframes zBreath{
      0%,100%{border-color:rgba(123,0,255,.4);box-shadow:0 0 0 rgba(123,0,255,0);}
      50%{border-color:rgba(123,0,255,.75);box-shadow:0 0 40px rgba(123,0,255,.18);}
    }
    .upload-box::before{
      content:'';position:absolute;inset:0;
      background:radial-gradient(ellipse at 50% 0%,rgba(123,0,255,.1),transparent 70%);
      animation:scan 3.5s ease-in-out infinite;
    }
    @keyframes scan{
      0%{background:radial-gradient(ellipse at 50% 0%,rgba(123,0,255,.1),transparent 70%);}
      50%{background:radial-gradient(ellipse at 50% 100%,rgba(0,255,178,.1),transparent 70%);}
      100%{background:radial-gradient(ellipse at 50% 0%,rgba(123,0,255,.1),transparent 70%);}
    }
    .icon{font-size:48px;display:block;margin-bottom:14px;animation:bounce 3s ease-in-out infinite;filter:drop-shadow(0 0 20px rgba(123,0,255,.6));}
    @keyframes bounce{0%,100%{transform:translateY(0);}50%{transform:translateY(-10px);}}
    .ub-title{font-family:'Bebas Neue',sans-serif;font-size:28px;letter-spacing:3px;background:linear-gradient(90deg,#7B00FF,#FF0080);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:6px;}
    .ub-sub{font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,255,255,.38);margin-bottom:20px;}
    .fmts{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;}
    .fmt{font-family:'JetBrains Mono',monospace;font-size:10px;padding:3px 10px;border-radius:20px;color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2);}
    </style>
    <div class="hdr">
      <div class="tag">// INDEX DOCUMENTS</div>
      <div class="title">UPLOAD<span> PDF</span></div>
    </div>
    <div class="upload-box">
      <span class="icon">&#128196;</span>
      <div class="ub-title">DROP YOUR PDF</div>
      <div class="ub-sub">Parsed · Chunked · Indexed · Ready</div>
      <div class="fmts">
        <span class="fmt">PDF</span>
        <span class="fmt">Multi-column</span>
        <span class="fmt">Tables</span>
        <span class="fmt">Any domain</span>
      </div>
    </div>
    """, height=340)

    uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        st.markdown(f"""
        <div style="padding:12px 16px;background:rgba(0,255,178,.06);border:1px solid rgba(0,255,178,.2);
             border-radius:12px;margin-bottom:10px;">
          <span style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#00FFB2;letter-spacing:1px;">
            &#128196; {uploaded.name} &middot; {uploaded.size//1024} KB
          </span>
        </div>""", unsafe_allow_html=True)

        if st.button("⚡ Index This PDF", use_container_width=True):
            with st.spinner("Parsing, chunking, embedding..."):
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
                          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;padding:3px 10px;border-radius:20px;color:#00FFB2;background:rgba(0,255,178,.08);border:1px solid rgba(0,255,178,.2);">&#10003; {d['chunks_indexed']} NEW</span>
                          <span style="font-family:'JetBrains Mono',monospace;font-size:11px;padding:3px 10px;border-radius:20px;color:#7B00FF;background:rgba(123,0,255,.08);border:1px solid rgba(123,0,255,.2);">&#8721; {d['total_chunks']} TOTAL</span>
                        </div>""", unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error(resp.text)
                except Exception as e:
                    st.error(str(e))

    st.markdown("""
    <div style="margin-top:20px;padding:22px;background:rgba(255,255,255,.02);
         border:1px solid rgba(255,255,255,.06);border-radius:16px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,255,255,.28);letter-spacing:3px;margin-bottom:14px;">// TIPS</div>
      <div style="font-size:13px;color:rgba(255,255,255,.4);line-height:1.9;">
        &#9889; Ask specific questions for best results<br>
        &#128206; Every answer includes inline citations<br>
        &#128683; Unanswerable queries are refused, not guessed<br>
        &#128260; Upload multiple PDFs to expand knowledge
      </div>
    </div>""", unsafe_allow_html=True)