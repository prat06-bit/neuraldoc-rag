import os
import sys
import requests
import streamlit as st
from datetime import datetime

# Insert path to allow imports
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

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

st.set_page_config(page_title="NeuralDoc SaaS", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

API_BASE = "http://localhost:8000"

# --- 1. SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_view" not in st.session_state:
    st.session_state.active_view = "Chat"

# --- 2. CUSTOM CSS MINIMALIST SAAS ---
st.markdown("""
<style>
    /* Global fixes to match SaaS aesthetics */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Soften container boxes */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
        background-color: var(--secondary-background-color);
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    /* Minimal inputs */
    .stTextInput input {
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: none;
        transition: all 0.2s ease;
    }
    .stTextInput input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .stButton > button:hover {
        border-color: #6366f1;
        color: #6366f1;
    }
    
    /* Primary Action Buttons */
    [data-testid="stButton"] button[kind="primary"] {
        background-color: #6366f1;
        color: white;
        border: none;
    }
    [data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #4f46e5;
        color: white;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #6366f1;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""
    # Read password from env, fallback to "neuraldoc123" for demo
    expected_password = os.getenv("APP_PASSWORD", "neuraldoc123")

    def password_entered():
        if st.session_state["password"] == expected_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password in session
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Login UI
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h2 style='text-align: center;'>🔐 Sign In to NeuralDoc</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Enter the access token to continue.</p>", unsafe_allow_html=True)
        st.text_input("Access Password", type="password", key="password", on_change=password_entered)
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("Incorrect password.")
        st.markdown("<br><p style='text-align: center; font-size: 12px; color: gray;'>Default demo password is <b>neuraldoc123</b></p>", unsafe_allow_html=True)
    return False

if not check_password():
    st.stop()  # Do not continue running the script if not authenticated

# --- 4. BACKEND HEALTH & HELPERS ---
@st.cache_data(ttl=5)
def get_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3).json()
        r["_reachable"] = True
        return r
    except Exception:
        return {"pipeline_ready": False, "total_chunks": 0, "indexed_files": [], "_reachable": False}

health = get_health()
api_ok = health.get("_reachable", False)
ready = health.get("pipeline_ready", False)
chunks = health.get("total_chunks", 0)
files = health.get("indexed_files", [])

# --- 5. SIDEBAR NAVIGATION & KNOWLEDGE BASE ---
with st.sidebar:
    st.title("⚡ NeuralDoc")
    st.markdown("---")
    
    # Navigation
    st.session_state.active_view = st.radio("Navigation", ["💬 Chat", "📊 Analytics"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # Knowledge Base
    st.subheader("Knowledge Base")
    
    if api_ok:
        if ready:
            st.success(f"Pipeline Ready • {chunks} chunks")
        else:
            st.warning("No documents indexed.")
            
        uploaded = st.file_uploader("Upload PDF", type=["pdf"])
        if uploaded:
            if st.button("Index Document", type="primary", use_container_width=True):
                with st.spinner("Processing PDF..."):
                    try:
                        resp = requests.post(f"{API_BASE}/ingest",
                                             files={"file": (uploaded.name, uploaded, "application/pdf")},
                                             timeout=120)
                        if resp.status_code == 200:
                            d = resp.json()
                            st.success(f"Indexed {d['chunks_indexed']} chunks from {d['filename']}")
                        else:
                            st.error(f"Error: {resp.text}")
                    except Exception as e:
                        st.error(f"Error connecting: {str(e)}")
                        
        if files:
            with st.expander("Indexed Files", expanded=False):
                for f in files:
                    st.caption(f.split("/")[-1])
                if st.button("Clear Index", use_container_width=True):
                    requests.delete(f"{API_BASE}/index", timeout=15)
                    st.success("Cleared. Refreshing...")
                    st.rerun()
    else:
        st.error("API Offline. Run backend.")
        
    st.markdown("---")
    
    # Chat History
    st.subheader("Chat History")
    convs = load_all_conversations()
    if convs:
        for i, conv in enumerate(convs[:5]):
            title = conv["title"][:25] + ("..." if len(conv["title"]) > 25 else "")
            if st.button(f"📄 {title}", key=f"hist_{conv['id']}", use_container_width=True):
                st.session_state.messages = load_conversation(conv["id"])
                
    st.caption("NeuralDoc SaaS v2.0")

# --- 6. MAIN CONTENT ---
if st.session_state.active_view == "💬 Chat":
    # Header actions
    c1, c2 = st.columns([8, 2])
    with c1:
        st.header("Ask your documents")
    with c2:
        if st.button("Clear Chat", use_container_width=True):
            if st.session_state.messages:
                save_conversation(st.session_state.messages)
            st.session_state.messages = []
            st.rerun()
            
    st.markdown("---")

    # Message Display
    chat_container = st.container(height=500)
    with chat_container:
        if not st.session_state.messages:
            st.info("Upload a document on the left and start asking questions.")
        
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
                
                # Render Citations
                refs = m.get("references", [])
                if refs:
                    ref_html = ""
                    for r in refs:
                        ref_html += f"<span style='font-size: 11px; background-color: rgba(99, 102, 241, 0.1); color: #6366f1; padding: 2px 6px; border-radius: 4px; margin-right: 4px;'>{r}</span>"
                    st.markdown(ref_html, unsafe_allow_html=True)
                
                # Render Refusal tags
                if m.get("refused"):
                    st.caption("⚠️ Refusal triggered: Insufficient context.")

    # Chat Input
    if prompt := st.chat_input("Ask anything about your documents..."):
        if not ready:
            st.warning("Please upload and index a PDF first.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                st.chat_message("user").write(prompt)
                
            with st.spinner("Thinking..."):
                try:
                    resp = requests.post(f"{API_BASE}/query", json={"query": prompt}, timeout=120)
                    if resp.status_code == 200:
                        d = resp.json()
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": d["answer"],
                            "references": d["references"], 
                            "refused": d["refused"],
                            "latency_ms": d["latency_ms"]
                        })
                        record_query(query=prompt, latency_ms=d["latency_ms"], refused=d["refused"])
                        st.rerun()
                    else:
                        st.error("API error.")
                except Exception:
                    st.error("API offline.")

elif st.session_state.active_view == "📊 Analytics":
    st.header("Live Observability")
    st.markdown("---")
    
    stats = get_stats()
    
    # KPIs
    st.subheader("Query Analytics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Queries", stats["total_queries"])
    with col2:
        st.metric("Answered", stats["answered"])
    with col3:
        st.metric("Refusal Rate", f"{stats['refusal_rate']:.1f}%")
    with col4:
        st.metric("Avg Latency", f"{stats['avg_latency_ms']:.0f} ms")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # System Status
    st.subheader("System Status")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.info(f"**Backend**: {'Online' if api_ok else 'Offline'}")
    with sc2:
        st.info(f"**Pipeline**: {'Ready' if ready else 'No documents'}")
    with sc3:
        st.info(f"**Indexed**: {chunks} chunks")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent Queries Grid
    st.subheader("Recent Queries")
    if stats["recent"]:
        for q in stats["recent"][:10]:
            icon = "🔴" if q["refused"] else "🟢"
            with st.container():
                st.markdown(f"**{icon} {q['query'][:80]}...**")
                st.caption(f"Latency: {q['latency_ms']} ms")
                st.divider()
    else:
        st.info("No queries recorded yet.")