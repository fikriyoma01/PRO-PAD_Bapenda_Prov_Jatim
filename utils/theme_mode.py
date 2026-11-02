"""
Theme Mode Utilities
Harmonisasi dark mode / light mode mengikuti tema bawaan browser client
(prefers-color-scheme), dengan opsi paksa light/dark.

Mode:
- "auto"  : mengikuti tema Chrome/OS client (default)
- "light" : paksa light
- "dark"  : paksa dark

Pemakaian di app.py:
    from utils.theme_mode import apply_theme_mode, render_theme_toggle
    apply_theme_mode()          # setelah load_custom_css()
    render_theme_toggle()       # di dalam st.sidebar
"""

from pathlib import Path

import streamlit as st

DARK_CSS_FILE = Path(__file__).resolve().parent.parent / "assets" / "dark_theme.css"

MODE_LABELS = {
    "auto": "🌗 Auto (ikuti tema browser)",
    "light": "☀️ Light",
    "dark": "🌙 Dark",
}


def get_theme_mode() -> str:
    """Get current theme mode from session state (default: auto)."""
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "auto"
    return st.session_state.theme_mode


def render_theme_toggle():
    """Render selectbox pemilih mode tema. Panggil di dalam st.sidebar."""
    options = list(MODE_LABELS)
    current = get_theme_mode()
    choice = st.selectbox(
        "Tema tampilan",
        options=options,
        index=options.index(current),
        format_func=lambda m: MODE_LABELS[m],
        key="theme_mode_select",
    )
    if choice != st.session_state.theme_mode:
        st.session_state.theme_mode = choice
        st.rerun()


def apply_theme_mode():
    """
    Inject CSS dark theme sesuai mode aktif.
    - "light": tidak inject apa-apa (base tema light dari config.toml)
    - "dark":  inject dark_theme.css langsung
    - "auto":  inject dark_theme.css dibungkus @media (prefers-color-scheme: dark)
               sehingga mengikuti tema bawaan Chrome/OS client (live, tanpa reload)
    Catatan: Streamlit 1.45 men-strip <script> di st.markdown, jadi seluruh
    theming (termasuk chart Plotly) dilakukan via CSS.
    """
    mode = get_theme_mode()
    if mode == "light":
        return

    if not DARK_CSS_FILE.exists():
        return
    css = DARK_CSS_FILE.read_text()

    if mode == "auto":
        css = "@media (prefers-color-scheme: dark) {\n" + css + "\n}"

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
