    h_col, btn_col = st.columns([4, 1])
    with h_col:
        st.html("""<div style="margin-bottom:8px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#E0005A;
               letter-spacing:4px;margin-bottom:6px;">// STEP 1</div>
          <div style="font-family:'Bebas Neue',sans-serif;font-size:44px;letter-spacing:2px;
               color:#fff;line-height:1;">UPLOAD
            <span style="background:linear-gradient(90deg,#E0005A,#F0A800);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;"> YOUR PDF</span>
          </div>
        </div>""")
    with btn_col:
        st.html('<div style="height:36px"></div>')
        if st.button("Clear Index", key="clear_idx", use_container_width=True,
                     help="Wipe all indexed documents and start fresh"):
            try:
                resp = requests.delete(f"{API_BASE}/index", timeout=15)
                if resp.status_code == 200:
                    st.success("Index cleared. Upload a new PDF to start fresh.")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error("API offline.")

    st.html("""<style>@keyframes dP{0%,100%{border-color:rgba(107,0,240,.35);box-shadow:none;}
      50%{border-color:rgba(107,0,240,.7);box-shadow:0 0 28px rgba(107,0,240,.12);}}</style>
    <div style="padding:20px 24px;background:rgba(107,0,240,.04);border:1px dashed rgba(107,0,240,.38);
      border-radius:14px;margin-bottom:12px;animation:dP 4s ease-in-out infinite;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:18px;letter-spacing:3px;
           color:rgba(255,255,255,.45);margin-bottom:4px;">SELECT A PDF TO INDEX</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
           color:rgba(255,255,255,.28);letter-spacing:1px;">
        Parsed &rarr; Chunked &rarr; Embedded &rarr; Indexed into ChromaDB</div>
    </div>""")

    uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="hidden")

    if uploaded:
        col_f1, col_f2 = st.columns([3,1])
        with col_f1:
            st.html(f"""<div style="padding:11px 16px;background:rgba(0,223,160,.06);
              border:1px solid rgba(0,223,160,.22);border-radius:8px;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:#00DFA0;">
                {uploaded.name} &mdash; {uploaded.size//1024} KB</div></div>""")
        with col_f2:
            if st.button("Index Now", use_container_width=True, key="idx_btn"):
                with st.spinner("Processing PDF..."):
                    try:
                        resp = requests.post(f"{API_BASE}/ingest",
                            files={"file":(uploaded.name, uploaded, "application/pdf")}, timeout=120)
                        if resp.status_code==200:
                            d = resp.json()
                            st.success(f"Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                            st.rerun()
                        else:
                            st.error(f"Error: {resp.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("API offline. Start: uv run uvicorn api:app --reload --port 8000")
                    except Exception as e:
                        st.error(str(e))

    # Indexed files display
    if h_check.get("indexed_files"):
        cols_files = st.columns(min(len(h_check["indexed_files"]), 4))
        for i, f in enumerate(h_check["indexed_files"]):
            fname = f.replace("\\","/").split("/")[-1]
            with cols_files[i % 4]:
                st.html(f"""<div style="padding:8px 12px;background:rgba(0,223,160,.07);
                  border:1px solid rgba(0,223,160,.2);border-radius:8px;
                  font-family:'JetBrains Mono',monospace;font-size:11px;color:#00DFA0;">
                  {fname}</div>""")
