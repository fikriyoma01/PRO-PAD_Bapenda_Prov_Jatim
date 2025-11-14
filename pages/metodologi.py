"""
Halaman Metodologi - Dokumentasi lengkap metodologi proyeksi PAD
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import load_pad_historis


def local_css():
    st.markdown(
        """
        <style>
            .metodologi-header {
                background: linear-gradient(90deg, #1a5fb4, #3584e4);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            .metodologi-header h1 {
                color: white;
                margin: 0;
                font-size: 2.2rem;
            }
            .metodologi-header p {
                color: #f1f1f1;
                margin: 0;
                font-size: 1.05rem;
            }
            .section-card {
                background: white;
                border-left: 5px solid #1976d2;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            .formula-box {
                background: #f5f5f5;
                border: 2px solid #1976d2;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                font-family: 'Courier New', monospace;
                font-size: 1.1rem;
            }
            .warning-box {
                background: #fff3cd;
                border-left: 5px solid #ffc107;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
            }
            .info-box {
                background: #d1ecf1;
                border-left: 5px solid #17a2b8;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_metodologi_page():
    local_css()

    # Header
    st.markdown(
        """
        <div class="metodologi-header">
            <h1>📚 Metodologi Proyeksi PAD</h1>
            <p>Dokumentasi lengkap tentang metode, asumsi, dan keterbatasan model proyeksi</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Navigation
    st.markdown("**Navigasi Cepat:**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📊 Overview"):
            st.session_state.scroll_to = "overview"
    with col2:
        if st.button("🔬 Model Details"):
            st.session_state.scroll_to = "model"
    with col3:
        if st.button("📐 Formulas"):
            st.session_state.scroll_to = "formulas"
    with col4:
        if st.button("⚠️ Limitations"):
            st.session_state.scroll_to = "limitations"

    st.markdown("---")

    # ===== SECTION 1: OVERVIEW =====
    st.header("📊 1. Overview Metodologi")

    st.markdown("""
    Dashboard PAD Provinsi Jawa Timur menggunakan **pendekatan hybrid** yang menggabungkan:
    1. **Regresi Linear Sederhana (OLS)** untuk menangkap hubungan antara variabel makroekonomi dan PAD
    2. **Decomposition Analysis** untuk memecah komponen struktural pendapatan
    3. **Scenario Analysis** untuk memberikan rentang proyeksi (Optimis, Moderat, Pesimis)

    ### Tujuan Utama:
    - ✅ Memberikan proyeksi PAD yang **transparan dan terukur**
    - ✅ Memahami **dampak variabel makroekonomi** terhadap pendapatan daerah
    - ✅ Mengidentifikasi **komponen-komponen** yang mempengaruhi target PAD
    - ✅ Mendukung **perencanaan anggaran** yang berbasis data
    """)

    # ===== SECTION 2: DATA SOURCES =====
    st.header("📁 2. Sumber Data")

    st.markdown("""
    ### A. Data Historis PAD (2018-2024)
    **Sumber**: Bapenda Provinsi Jawa Timur

    **Variabel yang Tercakup**:
    - **PKB (Pajak Kendaraan Bermotor)**: Pendapatan dari pajak kendaraan bermotor tahunan
    - **BBNKB (Bea Balik Nama Kendaraan Bermotor)**: Pendapatan dari perpindahan kepemilikan kendaraan

    ### B. Variabel Makroekonomi (2018-2024)
    **Sumber**: BPS Jawa Timur, Bank Indonesia, Kementerian Keuangan

    | Variabel | Sumber | Satuan | Penjelasan |
    |----------|--------|--------|------------|
    | **PDRB** | BPS Jatim | % (YoY Growth) | Pertumbuhan ekonomi regional |
    | **Rasio Gini** | BPS Jatim | Indeks (0-1) | Ketimpangan pendapatan |
    | **IPM** | BPS Jatim | Indeks (0-100) | Indeks Pembangunan Manusia |
    | **TPT** | BPS Jatim | % | Tingkat Pengangguran Terbuka |
    | **Kemiskinan** | BPS Jatim | % | Persentase penduduk miskin |
    | **Inflasi** | BI / BPS | % (YoY) | Laju inflasi tahunan |
    | **Suku Bunga** | Bank Indonesia | % | BI 7-Day Reverse Repo Rate |

    ### C. Input Struktural (2025-2026)
    **Sumber**: Bapenda Provinsi Jawa Timur (Proyeksi Internal)

    - Potensi kendaraan baru (R4, R2)
    - Tunggakan yang dapat tertagih
    - Mutasi masuk/keluar
    - Pembebasan pajak
    - Target R-APBD
    """)

    # ===== SECTION 3: MODEL ARCHITECTURE =====
    st.header("🔬 3. Arsitektur Model")

    st.markdown("""
    ### A. Two-Step Regression Approach

    Model kami menggunakan pendekatan **dua tahap**:
    """)

    # Flowchart
    fig_flow = go.Figure()

    fig_flow.add_trace(go.Scatter(
        x=[1, 2, 3, 4],
        y=[2, 2, 2, 2],
        mode='markers+text',
        marker=dict(size=100, color=['#1976d2', '#388e3c', '#f57c00', '#d32f2f']),
        text=['1. Prediksi<br>Makro', '2. Prediksi<br>PAD', '3. Dampak<br>Makro', '4. Skenario<br>Final'],
        textposition='middle center',
        textfont=dict(color='white', size=12, family='Arial Black'),
        hoverinfo='skip'
    ))

    # Arrows
    for i in range(1, 4):
        fig_flow.add_annotation(
            x=i+0.5, y=2,
            ax=i, ay=2,
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=3,
            arrowcolor='gray'
        )

    fig_flow.update_layout(
        title="Pipeline Proyeksi PAD",
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0.5, 4.5]),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[1.5, 2.5]),
        height=250,
        template='plotly_white'
    )

    st.plotly_chart(fig_flow, use_container_width=True)

    st.markdown("""
    ### B. Detail Setiap Tahap

    #### **Tahap 1: Prediksi Variabel Makro (2025, 2026)**
    **Model**: Linear Trend Regression

    Setiap variabel makro diregresikan terhadap waktu (tahun):
    """)

    st.markdown("""
    <div class="formula-box">
    Variabel_Makro = β₀ + β₁ × Tahun + ε
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Contoh**:
    ```
    PDRB_2025 = 0.45 + 0.12 × 2025
    IPM_2025 = 65.3 + 0.87 × 2025
    ```

    #### **Tahap 2: Prediksi PAD Berdasarkan Makro**
    **Model**: Simple Linear Regression per variabel

    PKB/BBNKB diregresikan terhadap masing-masing variabel makro:
    """)

    st.markdown("""
    <div class="formula-box">
    PKB = α₀ + α₁ × Variabel_Makro + ε
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Contoh**:
    ```
    PKB = 2,500,000,000 + 850,000,000 × PDRB
    BBNKB = 1,200,000,000 - 120,000,000 × TPT
    ```

    #### **Tahap 3: Perhitungan Dampak Makro**
    **Formula**:
    """)

    st.markdown("""
    <div class="formula-box">
    Dampak(Rp) = α₁ × (Prediksi_Makro - Baseline_Makro)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Contoh**:
    ```
    Jika PDRB naik dari 4.5% (2024) menjadi 5.2% (2025):
    Dampak = 850,000,000 × (5.2 - 4.5) = Rp 595,000,000
    ```

    #### **Tahap 4: Scenario Bounds**
    **Formula**:
    """)

    st.markdown("""
    <div class="formula-box">
    Optimis = Prediksi × 0.95<br>
    Moderat = Prediksi × 1.00<br>
    Pesimis = Prediksi × 1.05
    </div>
    """, unsafe_allow_html=True)

    # ===== SECTION 4: DECOMPOSITION =====
    st.header("⚖️ 4. Dekomposisi Komponen")

    st.markdown("""
    ### A. Dekomposisi PKB

    Total Potensi PKB dihitung dengan formula:
    """)

    st.markdown("""
    <div class="formula-box">
    Total Potensi PKB =<br>
    &nbsp;&nbsp;+ Potensi Awal Tahun<br>
    &nbsp;&nbsp;+ RODA 4 (Jan-Des)<br>
    &nbsp;&nbsp;+ RODA 2 (Jan-Des)<br>
    &nbsp;&nbsp;+ Tunggakan Tertagih<br>
    &nbsp;&nbsp;+ Mutasi Masuk<br>
    &nbsp;&nbsp;- TDR (Tidak Daftar Ulang)<br>
    &nbsp;&nbsp;- Mutasi Keluar<br>
    &nbsp;&nbsp;- Pembebasan Pajak<br>
    &nbsp;&nbsp;+ Dampak Makro Positif<br>
    &nbsp;&nbsp;+ Dampak Makro Negatif
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### B. Dekomposisi BBNKB

    Total Potensi BBNKB (2025):
    """)

    st.markdown("""
    <div class="formula-box">
    Total Potensi BBNKB =<br>
    &nbsp;&nbsp;+ RODA 4 (Jan-Des)<br>
    &nbsp;&nbsp;+ RODA 2 (Jan-Des)<br>
    &nbsp;&nbsp;+ Dampak Makro Positif<br>
    &nbsp;&nbsp;+ Dampak Makro Negatif
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    Total Potensi BBNKB (2026):
    """)

    st.markdown("""
    <div class="formula-box">
    Total Potensi BBNKB =<br>
    &nbsp;&nbsp;+ RODA 4 (Jan-Des)<br>
    &nbsp;&nbsp;+ RODA 2 (Jan-Des)<br>
    &nbsp;&nbsp;- BBN II Tidak Dipungut<br>
    &nbsp;&nbsp;+ Dampak Makro Positif<br>
    &nbsp;&nbsp;+ Dampak Makro Negatif
    </div>
    """, unsafe_allow_html=True)

    # ===== SECTION 5: ASSUMPTIONS =====
    st.header("📐 5. Asumsi Model")

    st.markdown("""
    ### A. Asumsi Regresi Linear (OLS)

    Model regresi OLS memerlukan asumsi-asumsi berikut:

    1. **Linearitas**
       - Hubungan antara variabel independen dan dependen adalah linear
       - ⚠️ **Risiko**: Dengan dataset kecil (n=7), sulit memverifikasi asumsi ini

    2. **Independence of Errors**
       - Error terms tidak berkorelasi satu sama lain
       - ⚠️ **Risiko**: Time series data mungkin mengandung autokorelasi

    3. **Homoscedasticity**
       - Varians error konstan di semua level X
       - ⚠️ **Risiko**: Tidak diuji secara eksplisit dalam dashboard ini

    4. **Normality of Residuals**
       - Error terms berdistribusi normal
       - ⚠️ **Risiko**: Dengan n=7, asumsi normalitas sulit dipenuhi

    5. **No Multicollinearity** (ideal)
       - Variabel independen tidak berkorelasi tinggi
       - ✅ **Mitigasi**: Dashboard menyediakan correlation heatmap untuk deteksi

    ### B. Asumsi Proyeksi

    1. **Tren Linear Makro**
       - Variabel makro diasumsikan mengikuti trend linear terhadap waktu
       - **Implikasi**: Perubahan struktural ekonomi tidak tertangkap

    2. **Stabilitas Koefisien**
       - Koefisien regresi diasumsikan stabil dari 2018-2026
       - **Implikasi**: Perubahan kebijakan atau kondisi struktural diabaikan

    3. **Independensi Variabel Makro**
       - Setiap variabel makro diperlakukan independen
       - **Implikasi**: Interaksi antar variabel tidak dimodelkan

    4. **No Structural Breaks**
       - Tidak ada perubahan struktural signifikan (pandemi, krisis, dll)
       - **Implikasi**: Proyeksi mungkin bias jika ada shock ekonomi

    """)

    # ===== SECTION 6: LIMITATIONS =====
    st.header("⚠️ 6. Keterbatasan & Risiko")

    st.markdown("""
    <div class="warning-box">
    <h3>🚨 Keterbatasan Utama</h3>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 1. Dataset Terbatas (n=7)
        **Masalah**:
        - Hanya 7 observasi (2018-2024)
        - Degrees of freedom sangat rendah
        - Statistical power lemah

        **Dampak**:
        - ❌ Risiko overfitting tinggi
        - ❌ Confidence intervals sangat lebar
        - ❌ p-values tidak reliable
        - ❌ Model sensitif terhadap outlier

        **Mitigasi**:
        - ✅ Tampilkan CI untuk transparansi
        - ✅ Warning di setiap halaman
        - ✅ Gunakan multiple scenarios
        """)

        st.markdown("""
        ### 3. Multicollinearity
        **Masalah**:
        - Variabel makro saling berkorelasi tinggi
        - Contoh: PDRB vs IPM (r > 0.8)

        **Dampak**:
        - ❌ Koefisien tidak stabil
        - ❌ Interpretasi sulit
        - ❌ Variance inflation

        **Mitigasi**:
        - ✅ Correlation heatmap
        - ✅ Single predictor per model
        - ✅ Dokumentasi transparansi
        """)

    with col2:
        st.markdown("""
        ### 2. Simple Linear Model
        **Masalah**:
        - Hanya menangkap hubungan linear
        - Tidak ada interaction terms
        - Tidak ada lag effects

        **Dampak**:
        - ❌ Non-linear relationships terlewat
        - ❌ Synergy effects diabaikan
        - ❌ Time lags tidak dimodelkan

        **Mitigasi**:
        - ✅ Multiple scenarios
        - ✅ Dokumentasi asumsi
        - ⏳ Ensemble models (Phase 3)
        """)

        st.markdown("""
        ### 4. External Shocks
        **Masalah**:
        - Pandemi COVID-19 (2020-2021)
        - Perubahan regulasi
        - Krisis ekonomi

        **Dampak**:
        - ❌ Trend terputus
        - ❌ Structural breaks
        - ❌ Outliers signifikan

        **Mitigasi**:
        - ✅ User awareness
        - ✅ Scenario analysis
        - ⏳ Robust regression (future)
        """)

    st.markdown("""
    <div class="info-box">
    <h3>💡 Rekomendasi Penggunaan</h3>

    Dashboard ini **TIDAK boleh** digunakan sebagai **satu-satunya** dasar pengambilan keputusan.
    Proyeksi harus dikombinasikan dengan:

    - ✅ Expert judgment dari Tim Bapenda
    - ✅ Analisis kualitatif kondisi ekonomi
    - ✅ Pertimbangan kebijakan pemerintah
    - ✅ Data real-time dari lapangan
    - ✅ Konsultasi dengan pemangku kepentingan
    </div>
    """, unsafe_allow_html=True)

    # ===== SECTION 7: VALIDATION =====
    st.header("✅ 7. Validasi Model")

    st.markdown("""
    ### A. Metrics yang Tersedia

    Dashboard menyediakan metrics berikut untuk evaluasi model:

    | Metric | Penjelasan | Interpretasi |
    |--------|------------|--------------|
    | **R²** | Proportion of variance explained | > 0.7 = baik, < 0.4 = lemah |
    | **p-value** | Statistical significance | < 0.05 = signifikan |
    | **Koefisien** | Effect size per unit change | Magnitude dampak |
    | **CI 95%** | Confidence interval | Range ketidakpastian |

    ### B. Validasi yang Diperlukan (Future Work)

    ⏳ **Backtesting**: Bandingkan proyeksi tahun lalu vs aktual tahun ini
    ⏳ **Cross-validation**: K-fold validation (jika data lebih banyak)
    ⏳ **Residual Analysis**: Check normality, heteroscedasticity
    ⏳ **RMSE/MAPE**: Quantify prediction errors
    """)

    # ===== SECTION 8: CHANGELOG =====
    st.header("📝 8. Changelog & Version History")

    changelog_df = pd.DataFrame({
        'Version': ['1.0', '0.9', '0.8'],
        'Date': ['2025-01-14', '2024-12-15', '2024-11-10'],
        'Changes': [
            'Phase 1 Complete: CI, Waterfall, Heatmap, Tooltips, Excel Export',
            'Beta release: Basic projections with decomposition',
            'Alpha release: Initial dashboard structure'
        ],
        'Author': ['Claude AI + Team', 'Development Team', 'Development Team']
    })

    st.dataframe(changelog_df, use_container_width=True, hide_index=True)

    # ===== SECTION 9: REFERENCES =====
    st.header("📚 9. Referensi & Literatur")

    st.markdown("""
    ### Metodologi Statistik
    - Wooldridge, J.M. (2020). *Introductory Econometrics: A Modern Approach*. Cengage Learning.
    - James, G., et al. (2021). *An Introduction to Statistical Learning*. Springer.
    - Greene, W.H. (2018). *Econometric Analysis*. Pearson.

    ### Revenue Forecasting
    - Dougherty, C. (2016). *Introduction to Econometrics*. Oxford University Press.
    - Armstrong, J.S. (2001). *Principles of Forecasting*. Springer.

    ### Best Practices
    - Makridakis, S., et al. (2020). *Forecasting: Principles and Practice* (3rd ed.). OTexts.

    ### Regulasi
    - UU No. 1 Tahun 2022 tentang Hubungan Keuangan Antara Pemerintah Pusat dan Pemerintahan Daerah
    - Permendagri No. 77 Tahun 2020 tentang Pedoman Teknis Pengelolaan Keuangan Daerah
    - Pergub Jawa Timur tentang Pajak Daerah (terkini)
    """)

    # ===== SECTION 10: CONTACT =====
    st.header("📞 10. Kontak & Dukungan")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🏢 Bapenda Jawa Timur**
        - Email: dashboard@bapenda.jatimprov.go.id
        - Telp: (031) 1234-5678
        - Website: www.bapenda.jatimprov.go.id
        """)

    with col2:
        st.markdown("""
        **💻 Technical Support**
        - GitHub: [Project Repository]
        - Docs: [Documentation]
        - Issues: [Report Bug]
        """)

    with col3:
        st.markdown("""
        **📊 Data Requests**
        - Data update: setiap bulan
        - Format: CSV, Excel, JSON
        - API: (coming soon)
        """)


def app():
    show_metodologi_page()


if __name__ == "__main__":
    app()
