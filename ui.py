"""Small shared UI helpers: page setup, theme CSS, headers and disclaimers."""
import streamlit as st

import config
import database

CSS = """
<style>
html, body, [class*="css"] { font-family: "Segoe UI", system-ui, -apple-system, sans-serif; }
h1, h2, h3 { color: #3B3470; letter-spacing: -0.01em; }
.me-hero { background: linear-gradient(135deg, #E7E2F8 0%, #DCEBFA 55%, #DDF3EA 100%);
           border-radius: 22px; padding: 2rem 2.2rem; margin-bottom: 1.2rem; color: #26283B; }
.me-hero h1 { margin: 0 0 .4rem 0; font-size: 2.2rem; }
.me-card { background: #FFFFFF; border: 1px solid #D9D4EE; border-radius: 16px;
           padding: 1rem 1.2rem; margin-bottom: .8rem; color: #26283B; }
.me-card h4 { margin: 0 0 .3rem 0; color: #3B3470; }
.me-note { background: #EEF6FD; border-left: 5px solid #4A7FB5; border-radius: 10px;
           padding: .7rem 1rem; margin: .5rem 0 1rem 0; color: #1F2D3D; }
.me-tag { display: inline-block; padding: 1px 10px; border-radius: 999px; font-size: .8rem;
          border: 1px solid #8A7F2B; background: #FFF8D6; color: #4D4510; }
.me-tag-ok { border-color: #2F7D5B; background: #DFF5EA; color: #14452F; }
button:focus-visible, input:focus-visible, textarea:focus-visible { outline: 3px solid #5B50A0 !important; }
@media (max-width: 640px) { .me-hero { padding: 1.2rem; } .me-hero h1 { font-size: 1.6rem; } }
</style>
"""

SHORT_DISCLAIMER = ("MindEase AI offers general wellness support only. It is not a medical service, cannot "
                    "diagnose, and is not monitored in real time. In an emergency contact local emergency services.")


def setup_page(title: str, icon: str = "🌿"):
    """Must be the first Streamlit call on every page."""
    st.set_page_config(page_title=f"{title} · {config.APP_NAME}", page_icon=icon, layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    database.init_db(config.get_db_path())
    with st.sidebar:
        st.markdown(f"### 🌿 {config.APP_NAME}")
        if config.is_public_demo():
            st.warning("Public demo: your entries are private to this browser session and are deleted when "
                       "the session or server ends. Please do not enter real personal details.")
        st.caption(SHORT_DISCLAIMER)
        st.page_link("pages/6_Help_and_Support.py", label="Need support now?", icon="🆘")


def page_header(title: str, subtitle: str = ""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def note(text: str):
    st.markdown(f'<div class="me-note">{text}</div>', unsafe_allow_html=True)


def card(title: str, body: str):
    st.markdown(f'<div class="me-card"><h4>{title}</h4>{body}</div>', unsafe_allow_html=True)


def empty_state(message: str, hint: str = ""):
    st.info(f"**Nothing here yet.** {message}" + (f"\n\n{hint}" if hint else ""))
