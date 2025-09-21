import streamlit as st
from PIL import Image

def local_css():
    """
    Menerapkan tema kustom untuk Dashboard Proyeksi PAD.
    """
    st.markdown("""
    <style>
        .info-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 0.8rem;
            border-left: 5px solid #FFD700;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            height: 100%;
        }

        .info-card h3 {
            color: #1e3c72;
            margin-top: 0;
        }

        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 1rem;
            color: #1e3c72;
            font-size: 0.9rem;
            border-top: 1px solid #FFD700;
        }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    """
    Header dengan logo di kiri dan judul di kanan.
    """
    col1, col2 = st.columns([1, 5])

    # Logo di kiri
    with col1:
        try:
            logo = Image.open("img/bapendajatim_logo.png")
            st.image(logo, use_container_width=True)
        except FileNotFoundError:
            st.error("Logo tidak ditemukan di folder img/")

    # Kotak judul di kanan
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            color: white;
            display:flex;
            flex-direction:column;
            justify-content:center;
        ">
            <h1 style="margin:0; font-size:2.3rem; font-weight:700;">
                Dashboard Proyeksi Pendapatan Asli Daerah
            </h1>
            <p style="margin:0; font-size:1.2rem; opacity:0.95;">
                Badan Pendapatan Daerah Provinsi Jawa Timur
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_info_cards():
    """
    Bagian intro / informasi awal.
    """
    st.markdown("## 🎯 Tujuan Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>📈 Analisis Historis</h3>
            <p>Menampilkan tren penerimaan PKB & BBNKB periode 2018–2024.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>🔮 Proyeksi</h3>
            <p>Memberikan prediksi 2025–2026 berdasarkan variabel makroekonomi 
            dengan 3 skenario: Optimis, Moderat, Pesimis.</p>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>🧮 Pemodelan</h3>
            <p>Menganalisis hubungan PKB dan BBNKB dengan variabel makroekonomi 
            menggunakan regresi sederhana untuk mengetahui faktor penambah dan pengurang.</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="info-card">
            <h3>⚖️ Faktor Penambah & Pengurang</h3>
            <p>Menyajikan dekomposisi komponen penambah dan pengurang dalam rupiah.</p>
        </div>
        """, unsafe_allow_html=True)


def show_footer():
    st.markdown("""
    <div class="footer">
        © 2025 Bapenda Provinsi Jawa Timur | Dashboard Proyeksi PAD
    </div>
    """, unsafe_allow_html=True)


def app():
    local_css()
    show_header()
    show_info_cards()
    show_footer()


if __name__ == "__main__":
    app()