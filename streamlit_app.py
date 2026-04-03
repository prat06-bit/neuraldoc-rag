import streamlit as st
import hashlib
import json
import os
import time
import random
from datetime import datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuralDoc",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── User Store (flat JSON file, swap for SQLite in prod) ───────────────────
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    # seed a demo account
    demo = {"demo": hash_pw("demo1234"), "admin": hash_pw("admin123")}
    save_users(demo)
    return demo

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_user(username, password):
    users = load_users()
    return users.get(username) == hash_pw(password)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_pw(password)
    save_users(users)
    return True

# ─── Session State Init ──────────────────────────────────────────────────────
def init_session():
    defaults = {
        "logged_in": False,
        "username": "",
        "page": "login",         # login | home | chat | analytics
        "theme": "dark",
        "chat_messages": [],
        "query_log": [],
        "chunks": 0,
        "doc_ready": False,
        "auth_tab": "login",     # login | register
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ─── Global CSS ─────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

    /* ── Reset & Base ──────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    html, body, [data-testid="stApp"] {
        background: #08091a !important;
        color: #e2e8f0 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px;
        min-height: 100vh;
    }

    /* animated mesh background */
    [data-testid="stApp"]::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 80% 60% at 20% 10%, rgba(99,102,241,0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 80%, rgba(139,92,246,0.10) 0%, transparent 55%),
            radial-gradient(ellipse 50% 40% at 60% 30%, rgba(59,130,246,0.07) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
        animation: meshShift 12s ease-in-out infinite alternate;
    }

    @keyframes meshShift {
        0%   { opacity: 0.8; filter: hue-rotate(0deg); }
        100% { opacity: 1;   filter: hue-rotate(20deg); }
    }

    /* hide streamlit chrome */
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    .stDeployButton { display: none !important; }

    /* kill default padding */
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ── Typography ────────────────────────────────── */
    h1, h2, h3, .nd-display {
        font-family: 'Syne', sans-serif !important;
        letter-spacing: -0.03em;
    }

    /* ── Glassmorphism Card ─────────────────────────── */
    .glass {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
    }

    /* ── Navbar ─────────────────────────────────────── */
    .nd-navbar {
        position: sticky;
        top: 0;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 28px;
        height: 52px;
        background: rgba(8,9,26,0.85);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .nd-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'Syne', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #e2e8f0;
        text-decoration: none;
    }
    .nd-logo-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: linear-gradient(135deg,#818cf8,#a78bfa);
        box-shadow: 0 0 8px rgba(129,140,248,0.8);
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%,100% { box-shadow: 0 0 8px rgba(129,140,248,0.8); }
        50%      { box-shadow: 0 0 16px rgba(167,139,250,1); }
    }

    .nd-nav-left  { display: flex; align-items: center; gap: 16px; }
    .nd-nav-center{ display: flex; align-items: center; gap: 4px; }
    .nd-nav-right { display: flex; align-items: center; gap: 12px; }

    .nd-home-btn {
        padding: 5px 12px;
        font-size: 12px;
        font-weight: 500;
        color: rgba(226,232,240,0.65);
        background: transparent;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
        font-family: 'DM Sans', sans-serif;
        white-space: nowrap;
    }
    .nd-home-btn:hover {
        color: #e2e8f0;
        background: rgba(255,255,255,0.06);
        box-shadow: 0 0 10px rgba(129,140,248,0.2);
    }

    /* toggle pill */
    .nd-toggle-pill {
        display: flex;
        align-items: center;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 3px;
        gap: 2px;
    }
    .nd-toggle-opt {
        padding: 4px 14px;
        font-size: 12px;
        font-weight: 500;
        border-radius: 7px;
        cursor: pointer;
        transition: all 0.2s;
        color: rgba(226,232,240,0.5);
        font-family: 'DM Sans', sans-serif;
    }
    .nd-toggle-opt.active {
        background: linear-gradient(135deg,#6366f1,#8b5cf6);
        color: #fff;
        box-shadow: 0 2px 12px rgba(99,102,241,0.4);
    }
    .nd-toggle-opt:hover:not(.active) {
        color: #e2e8f0;
        background: rgba(255,255,255,0.06);
    }

    /* icon button */
    .nd-icon-btn {
        width: 30px; height: 30px;
        display: flex; align-items: center; justify-content: center;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        background: transparent;
        cursor: pointer;
        font-size: 14px;
        transition: all 0.2s;
        color: rgba(226,232,240,0.6);
    }
    .nd-icon-btn:hover {
        background: rgba(255,255,255,0.07);
        color: #e2e8f0;
        box-shadow: 0 0 10px rgba(129,140,248,0.2);
    }

    /* user chip */
    .nd-user-chip {
        display: flex; align-items: center; gap: 6px;
        padding: 4px 10px;
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 20px;
        font-size: 12px;
        color: #a5b4fc;
    }
    .nd-user-chip .avatar {
        width: 20px; height: 20px; border-radius: 50%;
        background: linear-gradient(135deg,#6366f1,#8b5cf6);
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: 700; color: #fff;
    }

    /* ── Page Wrapper ───────────────────────────────── */
    .nd-page {
        padding: 32px 36px;
        animation: fadeIn 0.4s ease;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Metric Cards ──────────────────────────────── */
    .nd-metrics-row {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    .nd-metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 20px 20px 16px;
        transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
        position: relative;
        overflow: hidden;
    }
    .nd-metric-card::before {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 14px;
        padding: 1px;
        background: linear-gradient(135deg, var(--c1), var(--c2));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: destination-out;
        mask-composite: exclude;
        opacity: 0.5;
        transition: opacity 0.25s;
    }
    .nd-metric-card:hover { transform: translateY(-4px); box-shadow: 0 12px 30px rgba(0,0,0,0.3); }
    .nd-metric-card:hover::before { opacity: 1; }

    .nd-metric-icon {
        font-size: 20px;
        margin-bottom: 10px;
        display: block;
    }
    .nd-metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 32px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 4px;
    }
    .nd-metric-label {
        font-size: 11px;
        font-weight: 500;
        color: rgba(226,232,240,0.45);
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .nd-metric-sub {
        font-size: 11px;
        margin-top: 6px;
    }

    /* ── Bottom Grid ────────────────────────────────── */
    .nd-grid-2 {
        display: grid;
        grid-template-columns: 1fr 380px;
        gap: 16px;
    }

    /* ── Panel ──────────────────────────────────────── */
    .nd-panel {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        overflow: hidden;
    }
    .nd-panel-header {
        padding: 14px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .nd-panel-title {
        font-family: 'Syne', sans-serif;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: rgba(226,232,240,0.6);
    }
    .nd-panel-body { padding: 20px; }

    /* empty state */
    .nd-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 48px 20px;
        gap: 12px;
        border: 1px dashed rgba(255,255,255,0.1);
        border-radius: 10px;
        background: rgba(255,255,255,0.02);
    }
    .nd-empty-icon { font-size: 36px; opacity: 0.35; }
    .nd-empty-text { font-size: 13px; color: rgba(226,232,240,0.4); }

    /* ── Status Pill ────────────────────────────────── */
    .nd-status-list { display: flex; flex-direction: column; gap: 12px; }
    .nd-status-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        background: rgba(255,255,255,0.025);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .nd-status-left { display: flex; align-items: center; gap: 10px; font-size: 13px; }
    .nd-status-icon { font-size: 16px; }
    .nd-dot {
        width: 7px; height: 7px; border-radius: 50%;
        display: inline-block; margin-right: 2px;
    }
    .nd-dot.green { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
    .nd-dot.red   { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
    .nd-dot.yellow{ background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }

    .nd-pill {
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.04em;
    }
    .nd-pill.green  { background: rgba(34,197,94,0.12);  color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
    .nd-pill.red    { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
    .nd-pill.yellow { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
    .nd-pill.blue   { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }

    /* ── Alert Card ─────────────────────────────────── */
    .nd-alert-card {
        padding: 16px 18px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(239,68,68,0.06));
        border: 1px solid rgba(245,158,11,0.2);
    }
    .nd-alert-head {
        display: flex; align-items: center; gap: 8px;
        font-size: 12px; font-weight: 600; color: #fbbf24;
        margin-bottom: 10px; letter-spacing: 0.05em; text-transform: uppercase;
    }
    .nd-alert-item {
        font-size: 12px;
        color: rgba(226,232,240,0.6);
        padding: 4px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        display: flex; align-items: flex-start; gap: 6px;
    }
    .nd-alert-item:last-child { border-bottom: none; }

    /* ── Section Label ──────────────────────────────── */
    .nd-section-label {
        font-family: 'Syne', sans-serif;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: rgba(99,102,241,0.8);
        margin-bottom: 4px;
    }
    .nd-section-title {
        font-family: 'Syne', sans-serif;
        font-size: 26px;
        font-weight: 800;
        margin-bottom: 20px;
        color: #e2e8f0;
    }
    .nd-section-title em {
        font-style: italic;
        background: linear-gradient(135deg,#818cf8,#a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ── Login Page ─────────────────────────────────── */
    .nd-auth-wrapper {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px;
        position: relative;
        overflow: hidden;
    }
    .nd-auth-card {
        width: 100%;
        max-width: 420px;
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(30px);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 20px;
        padding: 40px 36px 36px;
        position: relative;
        z-index: 1;
        animation: fadeIn 0.5s ease;
    }
    .nd-auth-card::before {
        content: '';
        position: absolute;
        inset: -1px;
        border-radius: 21px;
        background: linear-gradient(135deg,rgba(99,102,241,0.3),rgba(139,92,246,0.15),transparent 60%);
        z-index: -1;
    }

    .nd-auth-logo {
        display: flex; align-items: center; gap: 10px;
        font-family: 'Syne', sans-serif;
        font-size: 20px; font-weight: 800;
        margin-bottom: 28px;
    }
    .nd-auth-logo .dot {
        width: 10px; height: 10px; border-radius: 50%;
        background: linear-gradient(135deg,#818cf8,#a78bfa);
        box-shadow: 0 0 10px rgba(129,140,248,0.9);
        animation: pulse 2s ease-in-out infinite;
    }

    .nd-auth-tabs {
        display: flex;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 3px;
        margin-bottom: 24px;
    }
    .nd-auth-tab {
        flex: 1; text-align: center;
        padding: 7px; font-size: 13px; font-weight: 500;
        border-radius: 7px; cursor: pointer;
        transition: all 0.2s;
        color: rgba(226,232,240,0.5);
        font-family: 'DM Sans', sans-serif;
    }
    .nd-auth-tab.active {
        background: linear-gradient(135deg,#6366f1,#8b5cf6);
        color: #fff;
        box-shadow: 0 2px 12px rgba(99,102,241,0.4);
    }

    /* form inputs via Streamlit */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        padding: 10px 14px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(99,102,241,0.6) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: rgba(226,232,240,0.3) !important; }
    label[data-testid="stWidgetLabel"] p {
        color: rgba(226,232,240,0.65) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        font-family: 'DM Sans', sans-serif !important;
        letter-spacing: 0.03em;
    }

    /* primary buttons */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99,102,241,0.5) !important;
        filter: brightness(1.05) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* secondary / ghost buttons */
    .nd-ghost-btn > button {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: none !important;
        color: rgba(226,232,240,0.7) !important;
    }
    .nd-ghost-btn > button:hover {
        background: rgba(255,255,255,0.08) !important;
        box-shadow: 0 0 10px rgba(129,140,248,0.15) !important;
        color: #e2e8f0 !important;
    }

    /* ── Chat Page ──────────────────────────────────── */
    .nd-chat-layout {
        display: grid;
        grid-template-columns: 1fr 340px;
        gap: 16px;
        height: calc(100vh - 52px - 64px);
    }
    .nd-chat-container {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .nd-chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 16px;
        scrollbar-width: thin;
        scrollbar-color: rgba(99,102,241,0.3) transparent;
    }
    .nd-msg {
        display: flex;
        gap: 10px;
        animation: fadeIn 0.3s ease;
    }
    .nd-msg.user { flex-direction: row-reverse; }

    .nd-msg-avatar {
        width: 30px; height: 30px;
        border-radius: 50%;
        flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; font-weight: 700;
    }
    .nd-msg.user .nd-msg-avatar {
        background: linear-gradient(135deg,#6366f1,#8b5cf6);
        color: #fff;
    }
    .nd-msg.assistant .nd-msg-avatar {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        color: #818cf8;
    }
    .nd-msg-bubble {
        max-width: 72%;
        padding: 12px 16px;
        border-radius: 14px;
        font-size: 13px;
        line-height: 1.6;
    }
    .nd-msg.user .nd-msg-bubble {
        background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.18));
        border: 1px solid rgba(99,102,241,0.3);
        border-bottom-right-radius: 4px;
        color: #e2e8f0;
    }
    .nd-msg.assistant .nd-msg-bubble {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.07);
        border-bottom-left-radius: 4px;
        color: #cbd5e1;
    }
    .nd-msg-time {
        font-size: 10px;
        color: rgba(226,232,240,0.3);
        margin-top: 4px;
        align-self: flex-end;
    }

    /* chat input row */
    .nd-chat-input-row {
        padding: 12px 16px;
        border-top: 1px solid rgba(255,255,255,0.06);
        display: flex;
        gap: 10px;
        align-items: flex-end;
    }

    /* upload panel */
    .nd-upload-panel {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }

    /* file uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.02) !important;
        border: 2px dashed rgba(99,102,241,0.25) !important;
        border-radius: 12px !important;
        transition: border-color 0.2s !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99,102,241,0.5) !important;
    }

    /* text area */
    .stTextArea textarea {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        resize: none !important;
    }
    .stTextArea textarea:focus {
        border-color: rgba(99,102,241,0.5) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    }

    /* ── Home / Landing ─────────────────────────────── */
    .nd-hero {
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        text-align: center;
        padding: 80px 20px 60px;
        gap: 20px;
    }
    .nd-hero-badge {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 5px 14px;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 20px;
        font-size: 11px; font-weight: 600;
        color: #818cf8; letter-spacing: 0.07em;
        text-transform: uppercase;
    }
    .nd-hero-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(36px, 6vw, 64px);
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.03em;
        color: #e2e8f0;
    }
    .nd-hero-title span {
        background: linear-gradient(135deg,#818cf8 0%,#a78bfa 50%,#c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .nd-hero-sub {
        max-width: 520px;
        font-size: 15px;
        line-height: 1.7;
        color: rgba(226,232,240,0.55);
    }
    .nd-hero-btns { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }

    .nd-btn-primary {
        padding: 11px 26px;
        background: linear-gradient(135deg,#6366f1,#8b5cf6);
        color: #fff;
        border: none;
        border-radius: 10px;
        font-family: 'DM Sans', sans-serif;
        font-size: 14px; font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 4px 16px rgba(99,102,241,0.35);
        text-decoration: none;
    }
    .nd-btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(99,102,241,0.5);
    }
    .nd-btn-ghost {
        padding: 11px 26px;
        background: rgba(255,255,255,0.05);
        color: rgba(226,232,240,0.75);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        font-family: 'DM Sans', sans-serif;
        font-size: 14px; font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
    }
    .nd-btn-ghost:hover {
        background: rgba(255,255,255,0.08);
        color: #e2e8f0;
        box-shadow: 0 0 12px rgba(129,140,248,0.15);
    }

    /* feature cards */
    .nd-feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        max-width: 900px;
        margin: 0 auto 48px;
    }
    .nd-feature-card {
        padding: 24px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        transition: all 0.25s;
    }
    .nd-feature-card:hover {
        background: rgba(255,255,255,0.05);
        transform: translateY(-3px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.2);
        border-color: rgba(99,102,241,0.2);
    }
    .nd-feature-icon { font-size: 28px; margin-bottom: 12px; }
    .nd-feature-title {
        font-family: 'Syne', sans-serif;
        font-size: 15px; font-weight: 700;
        margin-bottom: 6px; color: #e2e8f0;
    }
    .nd-feature-desc { font-size: 13px; color: rgba(226,232,240,0.5); line-height: 1.6; }

    /* ── Spinner / typing indicator ─────────────────── */
    .nd-typing { display: flex; align-items: center; gap: 4px; padding: 10px 14px; }
    .nd-typing span {
        width: 6px; height: 6px; border-radius: 50%;
        background: #818cf8;
        animation: typingBounce 1.2s ease-in-out infinite;
    }
    .nd-typing span:nth-child(2) { animation-delay: 0.2s; }
    .nd-typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typingBounce {
        0%,60%,100% { transform: translateY(0); opacity: 0.4; }
        30%          { transform: translateY(-6px); opacity: 1; }
    }

    /* ── Scrollbar ──────────────────────────────────── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,0.5); }

    /* ── Divider ────────────────────────────────────── */
    .nd-divider {
        height: 1px;
        background: linear-gradient(90deg,transparent,rgba(255,255,255,0.08),transparent);
        margin: 8px 0;
    }

    /* hide streamlit form border */
    [data-testid="stForm"] { border: none !important; padding: 0 !important; }

    /* selectbox */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }

    /* ── Tip box ────────────────────────────────────── */
    .nd-tip-box {
        background: rgba(99,102,241,0.06);
        border: 1px solid rgba(99,102,241,0.15);
        border-radius: 12px;
        padding: 14px 16px;
    }
    .nd-tip-head {
        font-size: 11px; font-weight: 600; letter-spacing: 0.06em;
        text-transform: uppercase; color: #818cf8; margin-bottom: 8px;
    }
    .nd-tip-item {
        font-size: 12px; color: rgba(226,232,240,0.55);
        padding: 3px 0;
        display: flex; align-items: flex-start; gap: 6px;
    }

    /* doc status badge */
    .nd-doc-badge {
        display: inline-flex; align-items: center; gap: 5px;
        padding: 3px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600;
    }
    .nd-doc-badge.ready   { background: rgba(34,197,94,0.12);  color: #4ade80; border: 1px solid rgba(34,197,94,0.25); }
    .nd-doc-badge.not-ready { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }
    .nd-doc-badge.processing { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }

    /* suggestion pills */
    .nd-suggestions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; }
    .nd-sugg-pill {
        padding: 6px 14px;
        background: rgba(99,102,241,0.1);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 20px;
        font-size: 12px; color: #a5b4fc;
        cursor: pointer;
        transition: all 0.2s;
        font-family: 'DM Sans', sans-serif;
    }
    .nd-sugg-pill:hover {
        background: rgba(99,102,241,0.2);
        border-color: rgba(99,102,241,0.4);
        color: #c4b5fd;
    }

    /* chunk badge */
    .nd-chunk-badge {
        display: inline-flex; align-items: center; gap: 5px;
        padding: 3px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600;
        background: rgba(99,102,241,0.12);
        color: #818cf8;
        border: 1px solid rgba(99,102,241,0.25);
    }

    </style>
    """, unsafe_allow_html=True)

inject_css()

# ─── Navbar Component ────────────────────────────────────────────────────────
def render_navbar(show_toggle: bool = True):
    page = st.session_state.page
    username = st.session_state.username

    chat_active   = "active" if page == "chat"      else ""
    analyt_active = "active" if page == "analytics" else ""

    user_chip = f"""
    <div class="nd-user-chip">
        <div class="avatar">{username[0].upper() if username else "U"}</div>
        {username}
    </div>
    """ if username else ""

    toggle_html = f"""
    <div class="nd-toggle-pill">
        <div class="nd-toggle-opt {chat_active}"
             onclick="window.parent.document.querySelector('[data-testid=stApp]').dispatchEvent(
                 new CustomEvent('nd-nav', {{detail:'chat'}}))">
             Chat
        </div>
        <div class="nd-toggle-opt {analyt_active}"
             onclick="window.parent.document.querySelector('[data-testid=stApp]').dispatchEvent(
                 new CustomEvent('nd-nav', {{detail:'analytics'}}))">
             Analytics
        </div>
    </div>
    """ if show_toggle else "<div></div>"

    st.markdown(f"""
    <div class="nd-navbar">
        <div class="nd-nav-left">
            <a class="nd-logo" href="#">
                <div class="nd-logo-dot"></div>
                NeuralDoc
            </a>
        </div>
        <div class="nd-nav-center">
            {toggle_html}
        </div>
        <div class="nd-nav-right">
            {user_chip}
            <div class="nd-icon-btn" title="Toggle theme">🌙</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Streamlit-native nav buttons (hidden visually but functional)
    if show_toggle and st.session_state.logged_in:
        nav_cols = st.columns([1, 1, 1, 8, 1])
        with nav_cols[0]:
            if st.button("⬅ Home", key="nav_home", help="Go home"):
                st.session_state.page = "home"
                st.rerun()
        with nav_cols[1]:
            if st.button("💬 Chat", key="nav_chat"):
                st.session_state.page = "chat"
                st.rerun()
        with nav_cols[2]:
            if st.button("📊 Analytics", key="nav_analytics"):
                st.session_state.page = "analytics"
                st.rerun()
        with nav_cols[4]:
            if st.button("Logout", key="nav_logout"):
                st.session_state.logged_in = False
                st.session_state.username  = ""
                st.session_state.page      = "login"
                st.rerun()

        # style the nav helper row to be subtle
        st.markdown("""
        <style>
        /* Make the helper nav compact */
        div[data-testid="column"]:has(button[kind="secondary"]) {
            min-width: 0 !important;
        }
        </style>""", unsafe_allow_html=True)

# ─── LOGIN PAGE ──────────────────────────────────────────────────────────────
def page_login():
    st.markdown("""
    <div class="nd-auth-wrapper">
        <div style="position:fixed;inset:0;
            background:radial-gradient(ellipse 70% 60% at 30% 20%,rgba(99,102,241,0.15),transparent 60%),
                       radial-gradient(ellipse 50% 50% at 70% 70%,rgba(139,92,246,0.12),transparent 55%);
            pointer-events:none;z-index:0;">
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Center card using columns
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("""
        <div class="nd-auth-card">
            <div class="nd-auth-logo">
                <div class="dot"></div>
                NeuralDoc
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Tab toggle
        tab_col1, tab_col2 = st.columns(2)
        with tab_col1:
            if st.button("Sign In", key="tab_login"):
                st.session_state.auth_tab = "login"
                st.rerun()
        with tab_col2:
            if st.button("Register", key="tab_register"):
                st.session_state.auth_tab = "register"
                st.rerun()

        st.markdown("<div class='nd-divider'></div>", unsafe_allow_html=True)

        if st.session_state.auth_tab == "login":
            st.markdown("<p style='color:rgba(226,232,240,0.5);font-size:13px;margin-bottom:16px;'>Welcome back — sign in to continue.</p>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="your_username", key="login_user")
            password = st.text_input("Password", placeholder="••••••••", type="password", key="login_pass")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Sign In →", key="do_login"):
                    if verify_user(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username  = username
                        st.session_state.page      = "home"
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
            with col_b:
                st.markdown("<div class='nd-ghost-btn'>", unsafe_allow_html=True)
                if st.button("Demo →", key="demo_login"):
                    st.session_state.logged_in = True
                    st.session_state.username  = "demo"
                    st.session_state.page      = "home"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<p style='text-align:center;font-size:11px;color:rgba(226,232,240,0.3);margin-top:12px;'>Demo credentials: demo / demo1234</p>", unsafe_allow_html=True)

        else:  # register
            st.markdown("<p style='color:rgba(226,232,240,0.5);font-size:13px;margin-bottom:16px;'>Create your account.</p>", unsafe_allow_html=True)
            new_user = st.text_input("Username", placeholder="choose_username", key="reg_user")
            new_pass = st.text_input("Password", placeholder="min 6 characters", type="password", key="reg_pass")
            conf_pass = st.text_input("Confirm Password", placeholder="repeat password", type="password", key="reg_conf")

            if st.button("Create Account →", key="do_register"):
                if len(new_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_pass != conf_pass:
                    st.error("Passwords do not match.")
                elif not new_user.strip():
                    st.error("Username cannot be empty.")
                elif register_user(new_user.strip(), new_pass):
                    st.success("Account created! Sign in now.")
                    st.session_state.auth_tab = "login"
                    st.rerun()
                else:
                    st.error("Username already exists.")

# ─── HOME PAGE ───────────────────────────────────────────────────────────────
def page_home():
    render_navbar(show_toggle=False)

    st.markdown(f"""
    <div class="nd-hero">
        <div class="nd-hero-badge">⚡ RAG-Powered Document Intelligence</div>
        <div class="nd-hero-title">
            Ask your<br><span>documents anything</span>
        </div>
        <p class="nd-hero-sub">
            Upload PDFs, get instant cited answers. Powered by a production-grade
            Retrieval-Augmented Generation pipeline.
        </p>
        <div class="nd-hero-btns">
            <a class="nd-btn-primary" href="#">Start Chatting →</a>
            <a class="nd-btn-ghost" href="#">View Analytics</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA streamlit buttons
    _, c1, c2, _ = st.columns([2, 1, 1, 2])
    with c1:
        if st.button("💬 Open Chat", key="home_chat"):
            st.session_state.page = "chat"
            st.rerun()
    with c2:
        if st.button("📊 Analytics", key="home_analytics"):
            st.session_state.page = "analytics"
            st.rerun()

    st.markdown("""
    <div style='max-width:900px;margin:0 auto;'>
    <div class="nd-feature-grid">
        <div class="nd-feature-card">
            <div class="nd-feature-icon">📄</div>
            <div class="nd-feature-title">Semantic Search</div>
            <p class="nd-feature-desc">Vector embeddings find the most relevant chunks across all your documents instantly.</p>
        </div>
        <div class="nd-feature-card">
            <div class="nd-feature-icon">🔗</div>
            <div class="nd-feature-title">Inline Citations</div>
            <p class="nd-feature-desc">Every answer includes source references so you can verify the context directly.</p>
        </div>
        <div class="nd-feature-card">
            <div class="nd-feature-icon">🛡️</div>
            <div class="nd-feature-title">Refusal Guard</div>
            <p class="nd-feature-desc">Unanswerable queries return a clear refusal — not a hallucinated guess.</p>
        </div>
        <div class="nd-feature-card">
            <div class="nd-feature-icon">⚡</div>
            <div class="nd-feature-title">Low Latency</div>
            <p class="nd-feature-desc">FastAPI backend + async pipeline keeps response times under 2 seconds.</p>
        </div>
        <div class="nd-feature-card">
            <div class="nd-feature-icon">📊</div>
            <div class="nd-feature-title">Live Analytics</div>
            <p class="nd-feature-desc">Track query volume, success rate, latency, and system health in real time.</p>
        </div>
        <div class="nd-feature-card">
            <div class="nd-feature-icon">🔒</div>
            <div class="nd-feature-title">Secure Auth</div>
            <p class="nd-feature-desc">Session-based login with password hashing. Your data stays private.</p>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

# ─── CHAT PAGE ───────────────────────────────────────────────────────────────
def page_chat():
    render_navbar(show_toggle=True)

    st.markdown("<div class='nd-page' style='padding-top:16px;'>", unsafe_allow_html=True)

    # Header row
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("""
        <div class='nd-section-label'>Document QA</div>
        <div class='nd-section-title'>Ask your <em>documents</em></div>
        """, unsafe_allow_html=True)
    with h2:
        badge_class = "ready" if st.session_state.doc_ready else "not-ready"
        badge_text  = "✓ Ready" if st.session_state.doc_ready else "✗ Not Ready"
        chunks = st.session_state.chunks
        st.markdown(f"""
        <div style='display:flex;gap:8px;align-items:center;justify-content:flex-end;padding-top:20px;'>
            <div class='nd-chunk-badge'>📦 {chunks} chunks</div>
            <div class='nd-doc-badge {badge_class}'>{badge_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # Two-column layout
    chat_col, upload_col = st.columns([1.6, 1])

    # ── Chat Column ──────────────────────────────────────────
    with chat_col:
        st.markdown("<div class='nd-chat-container'>", unsafe_allow_html=True)

        # Messages
        st.markdown("<div class='nd-chat-messages' id='chat-scroll'>", unsafe_allow_html=True)
        messages = st.session_state.chat_messages

        if not messages:
            st.markdown("""
            <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
                        padding:48px 20px;gap:12px;text-align:center;'>
                <div style='font-size:40px;opacity:0.3;'>💬</div>
                <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:rgba(226,232,240,0.5);'>
                    Ask anything
                </div>
                <div style='font-size:13px;color:rgba(226,232,240,0.35);max-width:280px;line-height:1.6;'>
                    Upload a PDF on the right, then start asking questions. Every answer is cited.
                </div>
            </div>
            <div class='nd-suggestions'>
                <div class='nd-sugg-pill'>📋 What is the main finding?</div>
                <div class='nd-sugg-pill'>📝 Summarise section 3</div>
                <div class='nd-sugg-pill'>⚠️ What are the key risks?</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            uname = st.session_state.username or "U"
            for msg in messages:
                role  = msg["role"]
                text  = msg["text"]
                ts    = msg.get("time", "")
                if role == "user":
                    st.markdown(f"""
                    <div class='nd-msg user'>
                        <div>
                            <div class='nd-msg-bubble'>{text}</div>
                            <div class='nd-msg-time' style='text-align:right;'>{ts}</div>
                        </div>
                        <div class='nd-msg-avatar'>{uname[0].upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='nd-msg assistant'>
                        <div class='nd-msg-avatar'>⚡</div>
                        <div>
                            <div class='nd-msg-bubble'>{text}</div>
                            <div class='nd-msg-time'>{ts}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # end chat-messages

        # Input row
        st.markdown("<div class='nd-chat-input-row'>", unsafe_allow_html=True)
        inp_col, btn_col = st.columns([5, 1])
        with inp_col:
            user_input = st.text_input(
                label="",
                placeholder="Ask anything about your documents…",
                key="chat_input",
                label_visibility="collapsed",
            )
        with btn_col:
            send = st.button("Send ↗", key="chat_send")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # end chat-container

        # Handle send
        if send and user_input.strip():
            ts = datetime.now().strftime("%H:%M")
            st.session_state.chat_messages.append({
                "role": "user", "text": user_input.strip(), "time": ts
            })
            # Simulate typing & response
            with st.spinner(""):
                time.sleep(0.8)
            demo_responses = [
                "Based on the document, the main finding indicates that [placeholder — connect your RAG API here]. <em style='color:rgba(226,232,240,0.4);font-size:11px;'>[Source: page 3, §2.1]</em>",
                "The document does not contain enough information to answer this precisely. Please rephrase or upload a more relevant file.",
                "According to section 3 of the uploaded PDF, the analysis shows [placeholder]. <em style='color:rgba(226,232,240,0.4);font-size:11px;'>[Source: page 7]</em>",
            ]
            reply = random.choice(demo_responses)
            st.session_state.chat_messages.append({
                "role": "assistant", "text": reply, "time": datetime.now().strftime("%H:%M")
            })

            # Log to analytics
            st.session_state.query_log.append({
                "query": user_input.strip(),
                "status": "answered",
                "latency": random.randint(220, 980),
                "time": datetime.now().strftime("%H:%M:%S"),
            })
            st.rerun()

    # ── Upload Column ────────────────────────────────────────
    with upload_col:
        st.markdown("""
        <div class='nd-upload-panel'>
        <div class='nd-panel-header'>
            <span class='nd-panel-title'>📚 Knowledge Base</span>
        </div>
        <div class='nd-panel-body' style='display:flex;flex-direction:column;gap:14px;'>
        """, unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Drop your PDF below",
            type=["pdf"],
            label_visibility="collapsed",
            key="pdf_upload",
        )

        if uploaded:
            with st.spinner("Parsing → Chunking → Embedding…"):
                time.sleep(1.5)
            st.session_state.doc_ready = True
            st.session_state.chunks    = random.randint(48, 240)
            st.success(f"✓ Indexed {uploaded.name}")

        col_clear, _ = st.columns([1, 2])
        with col_clear:
            if st.button("🗑 Clear", key="clear_docs"):
                st.session_state.doc_ready = False
                st.session_state.chunks    = 0
                st.rerun()

        st.markdown("""
        <div class='nd-tip-box'>
            <div class='nd-tip-head'>💡 Tips</div>
            <div class='nd-tip-item'><span>→</span> Clear before switching documents</div>
            <div class='nd-tip-item'><span>→</span> Ask precise questions for best citation accuracy</div>
            <div class='nd-tip-item'><span>→</span> Unanswerable queries return a refusal</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # nd-page

# ─── ANALYTICS PAGE ──────────────────────────────────────────────────────────
def page_analytics():
    render_navbar(show_toggle=True)

    logs = st.session_state.query_log
    total    = len(logs)
    answered = sum(1 for q in logs if q["status"] == "answered")
    refused  = total - answered
    success  = f"{int(answered/total*100)}%" if total else "—"
    avg_lat  = f"{int(sum(q['latency'] for q in logs)/total)}ms" if total else "0ms"
    lat_label= "Fast" if total == 0 or int(sum(q['latency'] for q in logs)/max(total,1)) < 500 else "Moderate"

    st.markdown("<div class='nd-page'>", unsafe_allow_html=True)

    st.markdown("""
    <div class='nd-section-label'>Live Observability</div>
    <div class='nd-section-title'>Query <em>Analytics</em></div>
    """, unsafe_allow_html=True)

    # Metric cards
    st.markdown(f"""
    <div class="nd-metrics-row">
        <div class="nd-metric-card" style="--c1:#6366f1;--c2:#8b5cf6;">
            <span class="nd-metric-icon">🔍</span>
            <div class="nd-metric-value" style="color:#818cf8;">{total}</div>
            <div class="nd-metric-label">Total Queries</div>
        </div>
        <div class="nd-metric-card" style="--c1:#22c55e;--c2:#16a34a;">
            <span class="nd-metric-icon">✅</span>
            <div class="nd-metric-value" style="color:#4ade80;">{answered}</div>
            <div class="nd-metric-label">Answered</div>
        </div>
        <div class="nd-metric-card" style="--c1:#ef4444;--c2:#dc2626;">
            <span class="nd-metric-icon">🚫</span>
            <div class="nd-metric-value" style="color:#f87171;">{refused}</div>
            <div class="nd-metric-label">Refused</div>
        </div>
        <div class="nd-metric-card" style="--c1:#f59e0b;--c2:#d97706;">
            <span class="nd-metric-icon">📈</span>
            <div class="nd-metric-value" style="color:#fbbf24;">{success}</div>
            <div class="nd-metric-label">Success Rate</div>
            <div class="nd-metric-sub" style="color:rgba(226,232,240,0.4);">{"Good" if success != "—" else "No data"}</div>
        </div>
        <div class="nd-metric-card" style="--c1:#06b6d4;--c2:#0891b2;">
            <span class="nd-metric-icon">⚡</span>
            <div class="nd-metric-value" style="color:#22d3ee;">{avg_lat}</div>
            <div class="nd-metric-label">Avg Latency</div>
            <div class="nd-metric-sub" style="color:rgba(226,232,240,0.4);">{lat_label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Bottom grid
    left_col, right_col = st.columns([2.4, 1])

    with left_col:
        st.markdown("""
        <div class="nd-panel" style="height:100%;">
            <div class="nd-panel-header">
                <span class="nd-panel-title">📋 Recent Queries</span>
            </div>
            <div class="nd-panel-body">
        """, unsafe_allow_html=True)

        if not logs:
            st.markdown("""
            <div class="nd-empty">
                <div class="nd-empty-icon">🔎</div>
                <div class="nd-empty-text">No queries yet — start chatting to see data here</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Table header
            st.markdown("""
            <div style="display:grid;grid-template-columns:1fr 100px 80px 80px;
                        gap:8px;padding:8px 12px;
                        font-size:11px;font-weight:600;letter-spacing:0.05em;
                        text-transform:uppercase;color:rgba(226,232,240,0.35);
                        border-bottom:1px solid rgba(255,255,255,0.05);">
                <span>Query</span><span>Time</span><span>Status</span><span>Latency</span>
            </div>
            """, unsafe_allow_html=True)
            for q in reversed(logs[-20:]):
                status_cls = "green" if q["status"] == "answered" else "red"
                st.markdown(f"""
                <div style="display:grid;grid-template-columns:1fr 100px 80px 80px;
                            gap:8px;padding:10px 12px;
                            font-size:12px;color:rgba(226,232,240,0.7);
                            border-bottom:1px solid rgba(255,255,255,0.03);
                            transition:background 0.15s;"
                     onmouseover="this.style.background='rgba(255,255,255,0.03)'"
                     onmouseout="this.style.background='transparent'">
                    <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                          title="{q['query']}">{q['query'][:60]}{'…' if len(q['query'])>60 else ''}</span>
                    <span style="color:rgba(226,232,240,0.4);">{q['time']}</span>
                    <span><span class="nd-pill {status_cls}">{q['status']}</span></span>
                    <span style="color:rgba(226,232,240,0.4);">{q['latency']}ms</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    with right_col:
        # System Status
        st.markdown("""
        <div class="nd-panel" style="margin-bottom:14px;">
            <div class="nd-panel-header">
                <span class="nd-panel-title">🖥 System Status</span>
            </div>
            <div class="nd-panel-body">
                <div class="nd-status-list">
                    <div class="nd-status-item">
                        <div class="nd-status-left">
                            <span class="nd-status-icon">⚡</span>
                            <span>FastAPI</span>
                        </div>
                        <span class="nd-pill red">Offline</span>
                    </div>
                    <div class="nd-status-item">
                        <div class="nd-status-left">
                            <span class="nd-status-icon">🔗</span>
                            <span>RAG Pipeline</span>
                        </div>
                        <span class="nd-pill yellow">Standby</span>
                    </div>
                    <div class="nd-status-item">
                        <div class="nd-status-left">
                            <span class="nd-status-icon">📂</span>
                            <span>Indexed Files</span>
                        </div>
        """, unsafe_allow_html=True)

        idx_count = 1 if st.session_state.doc_ready else 0
        idx_cls   = "green" if idx_count > 0 else "red"
        idx_text  = f"{idx_count} doc" if idx_count > 0 else "No docs"

        st.markdown(f"""
                        <span class="nd-pill {idx_cls}">{idx_text}</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Ops Notes alert
        st.markdown("""
        <div class="nd-panel">
            <div class="nd-panel-header">
                <span class="nd-panel-title">⚠️ Ops Notes</span>
            </div>
            <div class="nd-panel-body">
                <div class="nd-alert-card">
                    <div class="nd-alert-head">⚠ Recommendations</div>
                    <div class="nd-alert-item">
                        <span>→</span>
                        <span>Refusal &gt; 25%: threshold may be too strict</span>
                    </div>
                    <div class="nd-alert-item">
                        <span>→</span>
                        <span>Latency &gt; 5s: try GPU or GPT-4o mini</span>
                    </div>
                    <div class="nd-alert-item">
                        <span>→</span>
                        <span>Rolling window: last 200 queries</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # nd-page

# ─── Router ──────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    page_login()
else:
    p = st.session_state.page
    if p == "home":
        page_home()
    elif p == "chat":
        page_chat()
    elif p == "analytics":
        page_analytics()
    else:
        page_home()