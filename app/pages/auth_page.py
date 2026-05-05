"""
Styled Sign In / Sign Up page for NeuralDoc.
Renders a light-themed auth page matching the landing page aesthetic.
"""
from __future__ import annotations

import streamlit as st

from app.auth import login, signup


def render_auth_page() -> None:
    """Render the login/signup page with light theme matching NeuralDoc landing."""

    st.html("""<style>
    /* Show labels on the auth page */
    .stTextInput label{display:block!important;color:var(--t2)!important;
      font-weight:600!important;font-size:12px!important;
      letter-spacing:0.04em!important;text-transform:uppercase!important;
      font-family:'Plus Jakarta Sans',sans-serif!important;margin-bottom:4px!important;}
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"]{background:transparent!important;
      border-bottom:1.5px solid var(--bd2)!important;gap:0!important;justify-content:center!important;}
    .stTabs [data-baseweb="tab"]{
      background:transparent!important;color:var(--t3)!important;
      font-family:'Plus Jakarta Sans',sans-serif!important;font-weight:600!important;
      font-size:14px!important;padding:10px 32px!important;border:none!important;
      transition:color 0.2s!important;}
    .stTabs [data-baseweb="tab"]:hover{color:var(--v)!important;}
    .stTabs [aria-selected="true"]{color:var(--v)!important;
      border-bottom:2.5px solid var(--v)!important;}
    </style>""")

    # Centered layout
    _, col, _ = st.columns([1.3, 1, 1.3])
    with col:
        # Logo + tagline
        st.html("""<div style="text-align:center;padding:60px 0 10px;animation:fU 0.6s ease both;">
          <div style="display:inline-flex;align-items:center;gap:10px;margin-bottom:8px;">
            <div style="width:10px;height:10px;border-radius:50%;background:var(--v);
              animation:pulse 2.5s ease-in-out infinite;"></div>
            <span style="font-family:'Instrument Serif',serif;font-size:32px;color:var(--t1);
              letter-spacing:-0.5px;">NeuralDoc</span>
          </div>
          <div style="font-size:14px;color:var(--t3);margin-top:2px;">
            Sign in to access the full application</div>
        </div>""")

        # Auth card
        st.html("""<div style="background:var(--s);border:1px solid var(--bd2);
          border-radius:var(--r2);padding:24px 28px 20px;margin-top:16px;
          box-shadow:var(--sh2);animation:fU 0.6s ease 0.1s both;"></div>""")

        tab_signin, tab_signup = st.tabs(["Sign In", "Sign Up"])

        with tab_signin:
            st.html('<div style="height:8px;"></div>')
            si_user = st.text_input("Username", key="_si_user", placeholder="Enter your username")
            si_pass = st.text_input("Password", type="password", key="_si_pass", placeholder="Enter your password")
            st.html('<div style="height:4px;"></div>')
            if st.button("Sign In →", key="_si_btn", use_container_width=True):
                ok, msg = login(si_user, si_pass)
                if ok:
                    st.session_state["_auth"] = True
                    st.session_state["_username"] = msg
                    st.session_state["page"] = "app"
                    st.session_state["active_tab"] = "chat"
                    st.rerun()
                else:
                    st.error(msg)

        with tab_signup:
            st.html('<div style="height:8px;"></div>')
            su_user = st.text_input("Choose a username", key="_su_user", placeholder="At least 3 characters")
            su_pass = st.text_input("Choose a password", type="password", key="_su_pass", placeholder="At least 6 characters")
            su_pass2 = st.text_input("Confirm password", type="password", key="_su_pass2", placeholder="Re-enter password")
            st.html('<div style="height:4px;"></div>')
            if st.button("Create Account →", key="_su_btn", use_container_width=True):
                if su_pass != su_pass2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = signup(su_user, su_pass)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.html("""<div style="text-align:center;margin-top:18px;font-size:11px;color:var(--t3);
          animation:fU 0.6s ease 0.2s both;">
          Secured with local authentication</div>""")

        if st.button("← Back to Home", key="_auth_back_home", use_container_width=True):
            st.session_state.page = "landing"
            st.rerun()
