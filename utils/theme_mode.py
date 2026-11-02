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


def _chart_theme_js(mode: str) -> str:
    """
    JS client-side: re-tema chart Plotly (template plotly_white) ke dark
    saat mode aktif dark. Mengamati DOM untuk chart baru (MutationObserver).
    Pada mode auto, reload saat tema OS/browser berubah agar sinkron.
    """
    mode_js = "auto" if mode == "auto" else "dark"
    return f"""<script>
(function () {{
    if (window.__padChartThemer) return;
    window.__padChartThemer = true;
    var MODE = "{mode_js}";
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    function isDark() {{
        return MODE === "dark" || (MODE === "auto" && mq.matches);
    }}
    function themeCharts() {{
        if (!isDark() || !window.Plotly) return;
        document.querySelectorAll(".js-plotly-plot .plotly").forEach(function (div) {{
            try {{
                if (div.data) {{
                    Plotly.relayout(div, {{
                        paper_bgcolor: "rgba(0,0,0,0)",
                        plot_bgcolor: "rgba(0,0,0,0)",
                        font: {{ color: "#d6dae3" }}
                    }});
                }}
            }} catch (e) {{ /* ignore */ }}
        }});
    }}
    var obs = new MutationObserver(function () {{
        setTimeout(themeCharts, 150);
    }});
    obs.observe(document.body, {{ childList: true, subtree: true }});
    if (MODE === "auto") {{
        mq.addEventListener("change", function () {{
            window.location.reload();
        }});
    }}
    setTimeout(themeCharts, 800);
}})();
</script>"""


def apply_theme_mode():
    """
    Inject CSS dark theme sesuai mode aktif.
    - "light": tidak inject apa-apa (base tema light dari config.toml)
    - "dark":  inject dark_theme.css langsung
    - "auto":  inject dark_theme.css dibungkus @media (prefers-color-scheme: dark)
               sehingga mengikuti tema bawaan Chrome/OS client
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
    st.markdown(_chart_theme_js(mode), unsafe_allow_html=True)
