import base64
import importlib
from pathlib import Path

import streamlit as st

from utils.audit_utils import initialize_session
from utils.theme_mode import apply_theme_mode, render_theme_toggle
from utils.ui_components import load_custom_css
from utils.ui_theme_utils import get_ui_theme

BASE_DIR = Path(__file__).resolve().parent
LOGO_PATH = BASE_DIR / "img" / "logo_bapenda.png"

# --- Konfigurasi halaman utama
_theme_pref = get_ui_theme()
_initial_sidebar = (
    "collapsed"
    if _theme_pref.get("layout", {}).get("sidebar_width") == "collapsed"
    else "expanded"
)

st.set_page_config(
    page_title="PRO-PAD | Bapenda Provinsi Jawa Timur",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "📊",
    layout="wide",
    initial_sidebar_state=_initial_sidebar,
)

# --- Inisialisasi sesi audit & CSS dasar
initialize_session()
load_custom_css()

# --- Struktur Navigasi Terkelompok (15 Halaman)
NAV_GROUPS = {
    "Ikhtisar & Data": {
        "🏠 Beranda": "home",
        "📄 Dataset Historis": "datasets",
        "📝 Editor Data": "data_editor",
    },
    "Pemodelan & Proyeksi": {
        "📊 Pemodelan Regresi": "pemodelan",
        "📈 Proyeksi 2025–2026": "proyeksi",
        "⚖️ Dekomposisi PAD": "dekomposisi",
        "🧭 Insight Terpadu": "insight",
    },
    "Simulasi & Keputusan": {
        "📘 Skenario HKPD": "hkpd",
        "🎯 Scenario Builder": "scenario_builder",
        "🏛️ Decision Support": "decision_support",
    },
    "Konfigurasi & Tata Kelola": {
        "⚙️ Pengaturan Kebijakan": "policy_settings",
        "🗂️ Manajemen Variabel": "variable_manager",
        "🎨 Kustomisasi UI": "ui_customization",
        "📚 Metodologi": "metodologi",
        "📋 Audit Trail": "audit",
    },
}

# Flat mapping (label -> slug) & reverse mapping (slug -> label)
PAGES = {
    label: slug
    for group_items in NAV_GROUPS.values()
    for label, slug in group_items.items()
}
SLUG_TO_LABEL = {slug: label for label, slug in PAGES.items()}


@st.cache_data(show_spinner=False)
def _get_logo_base64() -> str:
    if LOGO_PATH.exists():
        return base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return ""


# --- Inisialisasi halaman aktif
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Beranda"
elif st.session_state.current_page in SLUG_TO_LABEL:
    st.session_state.current_page = SLUG_TO_LABEL[st.session_state.current_page]
elif st.session_state.current_page not in PAGES:
    st.session_state.current_page = "🏠 Beranda"


def render_sidebar() -> None:
    logo_b64 = _get_logo_base64()
    logo_tag = (
        f'<img src="data:image/png;base64,{logo_b64}" alt="Logo Pemprov Jatim" class="sidebar-brand-logo">'
        if logo_b64
        else '<span style="font-size:2rem;">🏛️</span>'
    )

    st.sidebar.markdown(
        f"""
        <div class="sidebar-brand">
            {logo_tag}
            <div>
                <div class="sidebar-brand-title">PRO-PAD</div>
                <div class="sidebar-brand-sub">BAPENDA PROV. JATIM</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_theme_toggle()

    active_label = st.session_state.current_page
    for group_title, items in NAV_GROUPS.items():
        st.sidebar.markdown(
            f'<div class="sidebar-group-label">{group_title}</div>',
            unsafe_allow_html=True,
        )
        for label in items:
            is_active = label == active_label
            if st.sidebar.button(
                label,
                key=f"nav_{items[label]}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                if not is_active:
                    st.session_state.current_page = label
                    st.rerun()

    st.sidebar.markdown(
        """
        <div class="sidebar-footer">
            <div style="font-weight: 600; color: rgba(248,250,252,0.85);">🏛️ Bapenda Prov. Jawa Timur</div>
            <div style="margin-top: 2px;">Sistem Analitik PAD v2.0 • © 2025</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --- Render Sidebar & Konten Halaman Aktif
render_sidebar()

try:
    active_slug = PAGES[st.session_state.current_page]
    module = importlib.import_module(f"pages.{active_slug}")
    module.app()

    # Inject CSS dark mode paling akhir agar menang di cascade atas CSS lokal halaman
    apply_theme_mode()

except ImportError as e:
    st.error(f"⚠️ Gagal memuat modul halaman: {e}")
    st.info(
        "Pastikan seluruh modul tersedia di direktori `pages/`: "
        + ", ".join(f"`{slug}.py`" for slug in PAGES.values())
    )
