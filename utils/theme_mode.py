"""
Theme Mode Utilities
Harmonisasi dark mode / light mode mengikuti tema bawaan browser client
(prefers-color-scheme), dengan opsi paksa light/dark.
"""

from pathlib import Path

import streamlit as st

DARK_CSS_FILE = Path(__file__).resolve().parent.parent / "assets" / "dark_theme.css"

MODE_LABELS = {
    "auto": "🌗 Otomatis (Ikuti Browser)",
    "light": "☀️ Mode Terang (Light)",
    "dark": "🌙 Mode Gelap (Dark)",
}


def get_theme_mode() -> str:
    """Ambil mode tema aktif dari session state (default: auto)."""
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "auto"
    return st.session_state.theme_mode


def render_theme_toggle() -> None:
    """Render pemilih mode tema yang ringkas di dalam sidebar."""
    options = list(MODE_LABELS)
    current = get_theme_mode()
    choice = st.sidebar.selectbox(
        "🎨 Mode Tampilan",
        options=options,
        index=options.index(current),
        format_func=lambda m: MODE_LABELS[m],
        key="theme_mode_select",
    )
    if choice != st.session_state.theme_mode:
        st.session_state.theme_mode = choice
        st.rerun()


def apply_theme_mode() -> None:
    """
    Inject CSS dark theme sesuai mode aktif:
    - "light": tidak inject dark override (base tema light dari config.toml)
    - "dark":  inject dark_theme.css langsung
    - "auto":  inject dark_theme.css dibungkus @media (prefers-color-scheme: dark)
               sehingga mengikuti tema bawaan Chrome/OS client secara live
    """
    mode = get_theme_mode()
    if mode == "light":
        return

    if not DARK_CSS_FILE.exists():
        return
    css = DARK_CSS_FILE.read_text(encoding="utf-8")

    if mode == "auto":
        css = "@media (prefers-color-scheme: dark) {\n" + css + "\n}"

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
