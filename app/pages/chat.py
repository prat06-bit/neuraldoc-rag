from __future__ import annotations

import shutil
import tempfile
import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from app.analytics import record_query
from app.chat_history import (
    delete_all_conversations,
    delete_conversation,
    export_as_markdown,
    load_all_conversations,
    load_conversation,
    save_conversation,
)
from rag.pipeline import Pipeline

import os as _os
import tempfile as _tempfile

def _upload_dir() -> Path:
    if _os.environ.get("STREAMLIT_SERVER_HEADLESS") or _os.path.exists("/mount"):
        return Path(_tempfile.gettempdir()) / "neuraldoc_uploads"
    return Path("uploaded_pdfs")

UPLOAD_DIR = _upload_dir()


def render_chat(
    pipe: Pipeline,
    ready: bool,
    chunks: int,
    files: list[str],
) -> None:

    st.html("""<style>
    [data-testid="stAppViewContainer"]{background:var(--bg)!important;}
    [data-testid="stAppViewContainer"]::before{
      content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
      background:
        radial-gradient(ellipse 55% 45% at 10% 5%,  rgba(167,139,250,0.14),transparent 55%),
        radial-gradient(ellipse 40% 40% at 90% 90%,  rgba(6,182,212,0.08),transparent 50%),
        radial-gradient(ellipse 30% 30% at 50% 50%,  rgba(236,72,153,0.05),transparent 50%);
      animation:meshMove 20s ease-in-out infinite alternate;
    }
    [data-testid="stMain"],[data-testid="stMainBlockContainer"],.block-container{
      padding:0!important;background:transparent!important;max-width:100%!important;}
    </style>""")

    st.html("""<style>
    /* Page padding via CSS — not a wrapper div */
    [data-testid="stMainBlockContainer"] .block-container {
      padding-left: 0 !important; padding-right: 0 !important;
    }
    /* Suppress default Streamlit column/block white backgrounds and borders */
    [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
      background: transparent !important;
    }
    /* RIGHT column  */
    .upload-card {
      background: var(--s);
      border: 1px solid var(--bd2);
      border-radius: var(--r2);
      padding: 20px 20px 18px;
      box-shadow: var(--sh);
      margin-bottom: 14px;
      animation: slideUp 0.5s ease .1s both;
      transition: box-shadow 0.2s, border-color 0.2s;
    }
    .upload-card:hover { box-shadow: var(--sh2); border-color: var(--vpb); }
    /*  LEFT column */
    .chat-card {
      background: var(--s);
      border: 1px solid var(--bd2);
      border-radius: var(--r2);
      padding: 20px 22px 18px;
      box-shadow: var(--sh);
      animation: slideUp 0.5s ease both;
    }
    /*  History card  */
    .history-card {
      background: var(--s);
      border: 1px solid var(--bd2);
      border-radius: var(--r2);
      padding: 18px 20px 12px;
      box-shadow: var(--sh);
      animation: slideUp 0.5s ease .2s both;
    }
    /* Suppress Streamlit's own column gap rendering artifact */
    [data-testid="stHorizontalBlock"] { gap: 0 !important; }
    </style>""")

    # --- Action row ---
    st.html('<div style="padding:10px 52px 0;display:flex;gap:12px;align-items:center;'
            'animation:slideUp 0.5s ease .1s both;position:relative;z-index:10;"></div>')
    a1, a2, _ = st.columns([1, 1, 8])
    with a1:
        if st.button("Clear Chat", key="clr_btn", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.messages = []
            st.rerun()
    with a2:
        if st.session_state.messages:
            md = export_as_markdown(st.session_state.messages, "NeuralDoc Chat")
            st.download_button("Export .md", data=md,
                file_name=f"neuraldoc_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown", use_container_width=True, key="exp_md")
        else:
            st.html('<div style="height:44px;"></div>')

    st.html('<div style="height:6px;"></div>')

    col_chat, col_right = st.columns([3, 2], gap="large")

    with col_right:
        st.html("""<div class="upload-card">
          <div style="display:flex;align-items:center;justify-content:space-between;
            margin-bottom:14px;">
            <div>
              <div style="font-size:10px;font-weight:700;color:var(--v);
                letter-spacing:0.1em;text-transform:uppercase;margin-bottom:5px;">
                Knowledge Base</div>
              <div style="font-family:'Instrument Serif',serif;font-size:20px;color:var(--t1);">
                Upload <em style="font-style:italic;color:var(--v);">documents</em></div>
            </div>
          </div>
          <div style="background:var(--vp);border:2px dashed var(--vpb);
            border-radius:var(--r2);padding:14px;margin-bottom:10px;text-align:center;
            transition:all 0.2s ease;"
            onmouseover="this.style.borderColor='var(--v)';this.style.background='var(--s3)';this.style.transform='scale(1.01)'"
            onmouseout="this.style.borderColor='var(--vpb)';this.style.background='var(--vp)';this.style.transform=''">
            <div style="font-size:13px;font-weight:500;color:var(--t1);margin-bottom:4px;">
              Drop your PDF below</div>
            <div style="font-size:11px;color:var(--t3);">
              Parsed &#8594; Chunked &#8594; Embedded &#8594; Indexed</div>
          </div>
        </div>""")

        if st.button("Clear Index", key="clear_idx", use_container_width=False):
            try:
                pipe.clear()
                # Also delete uploaded PDFs
                if UPLOAD_DIR.exists():
                    shutil.rmtree(UPLOAD_DIR)
                    UPLOAD_DIR.mkdir(exist_ok=True)
                st.success("Index cleared.")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing index: {e}")

        uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")
        if uploaded:
            st.html(f"""<div style="background:rgba(5,150,105,0.07);
              border:1px solid rgba(5,150,105,0.25);border-radius:var(--r);
              padding:10px 14px;margin-bottom:10px;animation:slideUp 0.3s ease both;">
              <div style="font-size:13px;font-weight:600;color:var(--t1);">{uploaded.name}</div>
              <div style="font-size:11px;color:#059669;margin-top:2px;">{uploaded.size//1024} KB ready</div>
            </div>""")
            if st.button("Index Document", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing PDF..."):
                    try:
                        # Save uploaded file to disk
                        UPLOAD_DIR.mkdir(exist_ok=True)
                        save_path = UPLOAD_DIR / (uploaded.name or "upload.pdf")
                        with open(save_path, "wb") as f:
                            f.write(uploaded.getbuffer())

                        # Ingest via Pipeline directly
                        new_chunks = pipe.ingest(str(save_path))
                        st.success(f"Indexed {len(new_chunks)} chunks from {uploaded.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Indexing failed: {e}")

        if files:
            st.html("""<div style="font-size:10px;font-weight:700;color:var(--t3);
              letter-spacing:0.08em;text-transform:uppercase;margin:10px 0 6px;">
              Indexed files</div>""")
            for f in files:
                fname = f.replace("\\","/").split("/")[-1]
                st.html(f"""<div style="background:var(--bg);border:1px solid var(--bd2);
                  border-radius:var(--r);padding:8px 13px;margin-bottom:5px;
                  display:flex;align-items:center;transition:border-color 0.15s,transform 0.15s;"
                  onmouseover="this.style.borderColor='var(--vpb)';this.style.transform='translateX(2px)'"
                  onmouseout="this.style.borderColor='var(--bd2)';this.style.transform=''">
                  <span style="font-size:12px;font-weight:500;color:var(--t1);flex:1;">{fname}</span>
                  <span style="font-size:10px;font-weight:700;padding:2px 8px;
                    border-radius:var(--rf);color:#059669;background:rgba(5,150,105,0.08);
                    border:1px solid rgba(5,150,105,0.3);">indexed</span>
                </div>""")

        st.html("""<div style="margin-top:10px;background:var(--bg);border:1px solid var(--bd2);
          border-radius:var(--r);padding:12px 14px;">
          <div style="font-size:10px;font-weight:700;color:var(--t3);
            letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px;">Tips</div>
          <div style="font-size:12px;color:var(--t2);line-height:1.8;">
            Click <b style="color:var(--v);">Clear Index</b> before switching documents.<br>
            Ask precise questions for best citation accuracy.<br>
            Every answer includes inline source references.<br>
            Unanswerable queries return a refusal, not a guess.
          </div></div>""")

        # Chat History
    convs = load_all_conversations()
    if convs:
            show = convs[:5]
 
            # Header + Clear All on same row
            h1, h2 = st.columns([3, 1])
            with h1:
                st.html("""<div style="font-size:10px;font-weight:700;color:var(--v);
                  letter-spacing:0.1em;text-transform:uppercase;margin:14px 0 6px;">
                  Chat History</div>""")
            with h2:
                if st.button("Clear All", key="clear_all_hist", use_container_width=True):
                    delete_all_conversations()
                    st.rerun()
 
            # One tab per conversation — Streamlit renders these as a horizontal tab bar
            tab_labels = [
                conv["title"][:18] + ("…" if len(conv["title"]) > 18 else "")
                for conv in show
            ]
            tabs = st.tabs(tab_labels)
 
            for tab, conv in zip(tabs, show):
                with tab:
                    ts = conv["timestamp"][:10]
                    n = len([m for m in conv["messages"] if m["role"] == "user"])
                    st.caption(f"{ts} · {n} {'query' if n == 1 else 'queries'}")
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Load", key=f"ld_{conv['id']}",
                                     use_container_width=True):
                            st.session_state.messages = load_conversation(conv["id"])
                            st.rerun()
                    with b2:
                        if st.button("🗑 Delete", key=f"del_{conv['id']}",
                                     use_container_width=True):
                            delete_conversation(conv["id"])
                            st.rerun()
            st.html('</div>')

    #   LEFT COLUMN chat  
    with col_chat:
        st.html(f"""<div class="chat-card">
          <div style="display:flex;align-items:flex-start;
            justify-content:space-between;margin-bottom:18px;">
            <div>
              <div style="font-size:10px;font-weight:700;color:var(--v);
                letter-spacing:0.1em;text-transform:uppercase;margin-bottom:5px;">Document QA</div>
              <div style="font-family:'Instrument Serif',serif;font-size:26px;
                color:var(--t1);line-height:1.1;">
                Ask your <em style="font-style:italic;color:var(--v);">documents</em></div>
            </div>
            <div style="display:flex;gap:7px;align-items:center;padding-top:12px;flex-shrink:0;">
              <span style="font-size:12px;font-weight:600;color:var(--v);
                background:var(--vp);border:1px solid var(--vpb);
                padding:4px 12px;border-radius:var(--rf);">{chunks} chunks</span>
              <span style="font-size:12px;font-weight:700;padding:4px 12px;
                border-radius:var(--rf);border:1.5px solid;
                {'color:#059669;background:rgba(5,150,105,0.08);border-color:rgba(5,150,105,0.3);' if ready else 'color:#DC2626;background:rgba(220,38,38,0.08);border-color:rgba(220,38,38,0.3);'} ">
                {'Ready' if ready else 'Not ready'}</span>
            </div>
          </div>
        </div>""")

        if st.session_state.messages:
            html = ""
            for idx, m in enumerate(st.session_state.messages):
                delay = f"{idx * 0.05:.2f}s"
                if m["role"] == "user":
                    html += f"""
                    <div style="display:flex;justify-content:flex-end;margin-bottom:14px;
                      animation:slideUp 0.3s ease {delay} both;">
                      <div style="max-width:74%;padding:13px 17px;
                        background:linear-gradient(135deg,var(--v),var(--v3));
                        color:#fff;border-radius:16px 3px 16px 16px;
                        font-size:14px;line-height:1.65;
                        font-family:'Plus Jakarta Sans',sans-serif;
                        box-shadow:0 3px 12px rgba(124,58,237,0.25);">
                        {m['content']}</div></div>"""
                else:
                    refs = ""
                    if m.get("references"):
                        refs = '<div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:5px;">'
                        for ref in m["references"]:
                            refs += (
                                f'<span style="font-family:\'JetBrains Mono\',monospace;'
                                f'font-size:10px;padding:2px 9px;border-radius:var(--rf);'
                                f'color:var(--cyan);background:rgba(6,182,212,0.08);'
                                f'border:1px solid rgba(6,182,212,0.25);">{ref}</span>'
                            )
                        refs += "</div>"
                    rfsd = ""
                    if m.get("refused"):
                        rfsd = (
                            '<div style="margin-top:8px;font-size:12px;font-weight:600;'
                            'color:#DC2626;background:rgba(220,38,38,0.08);border:1px solid rgba(220,38,38,0.3);'
                            'padding:5px 12px;border-radius:var(--r);display:inline-block;">'
                            'Insufficient evidence — refusal triggered</div>'
                        )
                    lat = ""
                    if m.get("latency_ms"):
                        lat = (
                            f'<div style="margin-top:5px;font-family:\'JetBrains Mono\','
                            f'monospace;font-size:10px;color:var(--t3);">'
                            f'{m["latency_ms"]} ms</div>'
                        )
                    html += f"""
                    <div style="display:flex;margin-bottom:14px;gap:10px;align-items:flex-start;
                      animation:slideUp 0.3s ease {delay} both;">
                      <div style="width:28px;height:28px;border-radius:8px;flex-shrink:0;
                        margin-top:2px;background:linear-gradient(135deg,var(--vp),var(--s2));
                        display:flex;align-items:center;justify-content:center;
                        font-family:'Instrument Serif',serif;font-size:13px;
                        color:var(--v);border:1px solid var(--vpb);">N</div>
                      <div style="max-width:86%;padding:13px 17px;
                        background:var(--bg);border:1px solid var(--bd2);
                        border-radius:3px 16px 16px 16px;
                        font-size:14px;color:var(--t1);line-height:1.75;
                        font-family:'Plus Jakarta Sans',sans-serif;
                        box-shadow:var(--sh);transition:border-color 0.15s;"
                        onmouseover="this.style.borderColor='var(--vpb)'"
                        onmouseout="this.style.borderColor='var(--bd2)'">
                        {m['content']}{refs}{rfsd}{lat}</div></div>"""
            st.html(f"""<div style="max-height:50vh;overflow-y:auto;margin-bottom:14px;
              padding:2px;scrollbar-width:thin;
              scrollbar-color:var(--vpb) transparent;">{html}</div>""")
        else:
            st.html("""
            <div style="text-align:center;padding:44px 24px 36px;
              background:var(--bg);border:1px solid var(--bd2);
              border-radius:var(--r2);margin-bottom:14px;animation:fadeIn 0.5s ease both;">
              <div style="width:44px;height:44px;border-radius:12px;
                background:linear-gradient(135deg,var(--vp),var(--s2));
                border:1px solid var(--vpb);display:flex;align-items:center;
                justify-content:center;margin:0 auto 12px;
                font-family:'Instrument Serif',serif;font-size:18px;color:var(--v);
                box-shadow:var(--sh);">N</div>
              <div style="font-family:'Instrument Serif',serif;font-size:22px;
                color:var(--t1);margin-bottom:8px;">Ask anything</div>
              <div style="font-size:13px;color:var(--t3);
                max-width:280px;margin:0 auto 20px;line-height:1.7;">
                Upload a PDF on the right, then ask questions here.
                Every answer is cited.</div>
              <div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">
                <span style="font-size:12px;font-weight:500;color:var(--v);
                  background:var(--vp);border:1px solid var(--vpb);
                  padding:6px 14px;border-radius:var(--rf);cursor:default;transition:all 0.15s;"
                  onmouseover="this.style.background='var(--s3)';this.style.transform='translateY(-1px)'"
                  onmouseout="this.style.background='var(--vp)';this.style.transform=''">
                  What is the main finding?</span>
                <span style="font-size:12px;font-weight:500;color:var(--v);
                  background:var(--vp);border:1px solid var(--vpb);
                  padding:6px 14px;border-radius:var(--rf);cursor:default;transition:all 0.15s;"
                  onmouseover="this.style.background='var(--s3)';this.style.transform='translateY(-1px)'"
                  onmouseout="this.style.background='var(--vp)';this.style.transform=''">
                  Summarise section 3</span>
                <span style="font-size:12px;font-weight:500;color:var(--v);
                  background:var(--vp);border:1px solid var(--vpb);
                  padding:6px 14px;border-radius:var(--rf);cursor:default;transition:all 0.15s;"
                  onmouseover="this.style.background='var(--s3)';this.style.transform='translateY(-1px)'"
                  onmouseout="this.style.background='var(--vp)';this.style.transform=''">
                  What are the key risks?</span>
              </div>
            </div>""")

        # Input bar 
        qc, bc = st.columns([4, 2])
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
                        start = time.perf_counter()
                        result = pipe.query(query)
                        latency_ms = round((time.perf_counter() - start) * 1000, 1)

                        st.session_state.messages.extend([
                            {"role": "user", "content": query},
                            {"role": "assistant", "content": result["response"],
                             "references": result["references"],
                             "refused": result["refused"],
                             "latency_ms": latency_ms}
                        ])
                        record_query(query=query, latency_ms=latency_ms,
                                     refused=result["refused"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"Query failed: {e}")
