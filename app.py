import streamlit as st
import importlib

# --- Konfigurasi halaman
st.set_page_config(page_title="Dashboard Proyeksi PAD", layout="wide")

# --- Daftar halaman
PAGES = {
    "🏠 Home": "home",
    "📄 Dataset": "datasets",
    "📊 Pemodelan": "pemodelan",
    "📈 Proyeksi": "proyeksi",
    "⚖️ Dekomposisi": "dekomposisi",
    "🧭 Insight Terpadu": "insight",
    "📘 Implementasi Skenario HKPD": "hkpd",
    "📚 Metodologi": "metodologi"
}

# --- Inisialisasi session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# --- Sidebar Styling & Render
def render_sidebar():
    st.sidebar.markdown(
        """
        <style>
            /* Sidebar background */
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1e3c72, #2a5298) !important;
                color: white !important;
            }

            /* Judul sidebar */
            .sidebar-title {
                color: #ffffff !important;
                font-size: 1.6rem !important;
                font-weight: 700 !important;
                margin-bottom: 1.5rem !important;
                text-align: center;
                font-family: 'Segoe UI', sans-serif;
            }

        /* Tombol navigasi */
        section[data-testid="stSidebar"] .stButton > button {
            background: #ffffff !important;
            color: #1e3c72 !important;
            border-radius: 8px !important;
            height: 50px !important;   /* tinggi seragam */
            width: 100% !important;    /* lebar penuh sidebar */
            margin: 8px 0 !important;  /* jarak antar tombol */
            font-weight: 600 !important;
            font-size: 1rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
            transition: all 0.3s ease !important;
            border: none !important;
        }

            /* Hover efek */
            section[data-testid="stSidebar"] .stButton > button:hover {
                background: #ffd700 !important;
                color: #1e3c72 !important;
                transform: scale(1.01);
                box-shadow: 0 4px 10px rgba(0,0,0,0.25) !important;
            }

            /* Active state */
            section[data-testid="stSidebar"] .stButton > button[aria-pressed="true"] {
                background: #ff9800 !important;
                color: #ffffff !important;
                font-weight: bold !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown('<div class="sidebar-title">📚 Navigation</div>', unsafe_allow_html=True)

    for label in PAGES:
        if st.sidebar.button(label, key=f"nav_{label}"):
            st.session_state.current_page = label
            st.rerun()

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
