import streamlit as st
import importlib
from utils.audit_utils import initialize_session
from utils.ui_components import load_custom_css

# --- Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Proyeksi PAD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize audit trail session
initialize_session()

# --- Load custom CSS
load_custom_css()

# --- Daftar halaman
PAGES = {
    "🏠 Home": "home",
    "📄 Dataset": "datasets",
    "📊 Pemodelan": "pemodelan",
    "📈 Proyeksi": "proyeksi",
    "⚖️ Dekomposisi": "dekomposisi",
    "🧭 Insight Terpadu": "insight",
    "📘 Implementasi Skenario HKPD": "hkpd",
    "🎯 Scenario Builder": "scenario_builder",
    "⚙️ Policy Settings": "policy_settings",
    "📝 Data Editor": "data_editor",
    "📚 Metodologi": "metodologi",
    "📋 Audit Trail": "audit"
}

# --- Inisialisasi session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# --- Enhanced Sidebar Styling & Render
def render_sidebar():
    st.sidebar.markdown(
        """
        <style>
            /* Enhanced Sidebar background with gradient */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
                box-shadow: 4px 0 20px rgba(0,0,0,0.15) !important;
            }

            /* Sidebar title with glow effect */
            .sidebar-title {
                color: #ffffff !important;
                font-size: 1.8rem !important;
                font-weight: 800 !important;
                margin: 1rem 0 2rem 0 !important;
                text-align: center;
                font-family: 'Segoe UI', sans-serif;
                text-shadow: 0 0 20px rgba(255,215,0,0.5);
                letter-spacing: 1px;
            }

            .sidebar-subtitle {
                color: rgba(255,255,255,0.8) !important;
                font-size: 0.9rem !important;
                text-align: center;
                margin-bottom: 2rem !important;
                font-style: italic;
            }

            /* Modern navigation buttons */
            section[data-testid="stSidebar"] .stButton > button {
                background: rgba(255, 255, 255, 0.95) !important;
                color: #0f2027 !important;
                border-radius: 12px !important;
                height: 52px !important;
                width: 100% !important;
                margin: 6px 0 !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
                transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
                border: 2px solid transparent !important;
                position: relative;
                overflow: hidden;
            }

            /* Hover effect with gradient */
            section[data-testid="stSidebar"] .stButton > button:hover {
                background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%) !important;
                color: #0f2027 !important;
                transform: translateX(5px) scale(1.02);
                box-shadow: 0 6px 20px rgba(255,215,0,0.4) !important;
                border-color: #ffd700 !important;
            }

            /* Active/Selected state */
            section[data-testid="stSidebar"] .stButton > button[aria-pressed="true"] {
                background: linear-gradient(135deg, #ff9800 0%, #ff6f00 100%) !important;
                color: #ffffff !important;
                font-weight: 700 !important;
                box-shadow: 0 8px 24px rgba(255,152,0,0.5) !important;
                border-color: #ff9800 !important;
            }

            /* Button click animation */
            section[data-testid="stSidebar"] .stButton > button:active {
                transform: scale(0.98);
            }

            /* Add icon spacing */
            section[data-testid="stSidebar"] .stButton > button::before {
                margin-right: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('''
    <div class="sidebar-title">📊 PAD Dashboard</div>
    <div class="sidebar-subtitle">Proyeksi & Analisis</div>
    ''', unsafe_allow_html=True)

    for label in PAGES:
        if st.sidebar.button(label, key=f"nav_{label}"):
            st.session_state.current_page = label
            st.rerun()

    # Add footer to sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.6); font-size: 0.8rem; padding: 1rem 0;">
        <p style="margin: 0;">🏛️ Bapenda Prov. Jatim</p>
        <p style="margin: 0.5rem 0 0 0;">v2.0 © 2025</p>
    </div>
    """, unsafe_allow_html=True)

# --- Main container styling
st.markdown("""
<style>
    .main-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        animation: fadeIn 0.4s ease-in-out;
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(8px);}
        to {opacity: 1; transform: translateY(0);}
    }
</style>
""", unsafe_allow_html=True)

# --- Render
render_sidebar()

try:
    module_name = f"pages.{PAGES[st.session_state.current_page]}"
    module = importlib.import_module(module_name)

    with st.container():
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        module.app()
        st.markdown('</div>', unsafe_allow_html=True)

except ImportError as e:
    st.error(f"⚠️ Failed to load page module: {e}")
    st.error("Pastikan folder `pages/` berisi file berikut:")
    for page in PAGES.values():
        st.error(f"- pages/{page}.py")
