"""
Halaman Metodologi Proyeksi PAD
Dokumentasi komprehensif arsitektur model, formula matematis, dekomposisi objek pajak, HKPD, serta batasan statistik.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_info_box,
    render_page_header,
)


def _create_pipeline_figure() -> go.Figure:
    steps = [
        (1, "1. Ekstrapolasi\nIndikator Makro", "#1a5fb4"),
        (2, "2. Estimasi OLS &\nTime-Series", "#0ea5e9"),
        (3, "3. Integrasi\nDekomposisi Objek", "#10b981"),
        (4, "4. Skenario, CI 95%\n& Bagi Hasil HKPD", "#f59e0b"),
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[s[0] for s in steps],
            y=[1, 1, 1, 1],
            mode="markers+text",
            marker=dict(
                size=78,
                color=[s[2] for s in steps],
                line=dict(width=3, color="rgba(255,255,255,0.85)"),
            ),
            text=[s[1].replace("\n", "<br>") for s in steps],
            textposition="bottom center",
            textfont=dict(size=12),
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[s[0] for s in steps],
            y=[1, 1, 1, 1],
            mode="text",
            text=["🌐", "📐", "⚖️", "🏛️"],
            textfont=dict(size=26),
            hoverinfo="skip",
        )
    )
    for i in range(1, 4):
        fig.add_annotation(
            x=i + 0.62,
            y=1,
            ax=i + 0.38,
            ay=1,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=2.5,
            arrowcolor="rgba(148, 163, 184, 0.85)",
        )

    apply_plotly_theme(
        fig,
        title="Alur Arsitektur Hibrida Proyeksi PRO-PAD",
        height=250,
        show_legend=False,
        margin=dict(l=24, r=24, t=58, b=48),
    )
    fig.update_xaxes(visible=False, range=[0.4, 4.6])
    fig.update_yaxes(visible=False, range=[0.45, 1.35])
    return fig


def show_metodologi_page() -> None:
    render_page_header(
        title="Metodologi & Dokumentasi Teknis PRO-PAD",
        subtitle="Landasan ekonometrika, rumus perhitungan skenario, struktur dekomposisi objek pajak, dan tata kelola validasi",
        icon="📚",
    )

    tabs = st.tabs(
        [
            "📊 Ikhtisar & Sumber Data",
            "🔬 Arsitektur & Formula",
            "⚖️ Dekomposisi & HKPD",
            "⚠️ Asumsi & Keterbatasan",
            "✅ Validasi & Referensi",
        ]
    )

    # TAB 1: Overview & Data Sources
    with tabs[0]:
        create_header_with_icon("Pendekatan Hibrida Proyeksi PAD", "📊")
        with st.container(border=True):
            st.markdown(
                """
                Sistem **PRO-PAD Bapenda Provinsi Jawa Timur** mengintegrasikan **empat pilar metodologi** agar hasil proyeksi tidak hanya kuat secara statistik, tetapi juga berpijak pada realitas administrasi pemungutan pajak daerah:
                1. **Regresi Linear Sederhana (OLS)**: Mengukur elastisitas dan besaran dampak Rupiah dari perubahan indikator makroekonomi terhadap penerimaan PKB & BBNKB.
                2. **Ensemble Time-Series (OLS + ARIMA + Exponential Smoothing)**: Menyediakan pembanding deret waktu murni guna meredam bias model tunggal.
                3. **Dekomposisi Struktural Objek Pajak**: Menghitung komponen riil penambahan kendaraan baru (Roda 4 & Roda 2), pencairan tunggakan, mutasi masuk/keluar, tidak daftar ulang (TDR), serta pembebasan pajak.
                4. **Simulasi Skenario & HKPD (UU 1/2022)**: Menyajikan rentang kepercayaan 95% (*Confidence Interval*), tiga skenario perencanaan, serta distribusi porsi Provinsi vs Kabupaten/Kota.
                """
            )
            st.plotly_chart(_create_pipeline_figure(), use_container_width=True)

        create_header_with_icon("Katalog Sumber Data Resmi", "📁")
        sources_df = pd.DataFrame(
            [
                ("PKB & BBNKB (2018–2024)", "Bapenda Prov. Jawa Timur", "Rupiah Penuh", "Realisasi tahunan audited pajak kendaraan bermotor"),
                ("Pertumbuhan PDRB", "BPS Provinsi Jawa Timur", "% (YoY)", "Laju pertumbuhan ekonomi regional harga konstan"),
                ("Rasio Gini", "BPS Provinsi Jawa Timur", "Indeks (0–1)", "Ukuran ketimpangan distribusi pengeluaran penduduk"),
                ("IPM", "BPS Provinsi Jawa Timur", "Indeks (0–100)", "Indeks Pembangunan Manusia Provinsi Jawa Timur"),
                ("TPT", "BPS Provinsi Jawa Timur", "%", "Tingkat Pengangguran Terbuka angkatan kerja"),
                ("Kemiskinan", "BPS Provinsi Jawa Timur", "%", "Persentase penduduk miskin daerah"),
                ("Inflasi", "BPS / Bank Indonesia", "% (YoY)", "Inflasi tahunan gabungan kota IHK Jawa Timur"),
                ("Suku Bunga Acuan", "Bank Indonesia", "%", "BI 7-Day Reverse Repo Rate / BI-Rate"),
                ("Input Dekomposisi 2025–2026", "Bidang Perencanaan Bapenda", "Rupiah Penuh", "Target R-APBD, potensi kendaraan baru, TDR, mutasi & pembebasan"),
            ],
            columns=["Variabel / Dataset", "Instansi Sumber", "Satuan", "Keterangan"],
        )
        st.dataframe(sources_df, use_container_width=True, hide_index=True)

    # TAB 2: Model Architecture & Formulas
    with tabs[1]:
        create_header_with_icon("Spesifikasi Matematis & Formula Skenario", "🔬")

        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("#### Tahap 1 — Ekstrapolasi Tren Indikator Makro")
                st.caption("Digunakan sebagai nilai awal (baseline) proyeksi indikator makroekonomi tahun 2025 & 2026:")
                st.markdown(
                    '<div class="formula-box">X<sub>m,t</sub> = γ<sub>0</sub> + γ<sub>1</sub> · Tahun<sub>t</sub> + u<sub>t</sub></div>',
                    unsafe_allow_html=True,
                )

                st.markdown("#### Tahap 2 — Regresi Linear Terhadap Pajak Daerah")
                st.caption("Estimasi hubungan linear antara masing-masing indikator makro terhadap PKB atau BBNKB:")
                st.markdown(
                    '<div class="formula-box">Y<sub>t</sub> = β<sub>0</sub> + β<sub>1</sub> · X<sub>m,t</sub> + ε<sub>t</sub></div>',
                    unsafe_allow_html=True,
                )

        with c2:
            with st.container(border=True):
                st.markdown("#### Tahap 3 — Transmisi Dampak Makroekonomi (Δ Rupiah)")
                st.caption("Mengonversi selisih perubahan indikator makro dari baseline menjadi nilai Rupiah:")
                st.markdown(
                    '<div class="formula-box">Dampak<sub>m,t</sub> (Rp) = β<sub>1,m</sub> × (X̂<sub>m,t</sub> − X<sub>m,t−1</sub>)</div>',
                    unsafe_allow_html=True,
                )

                st.markdown("#### Tahap 4 — Perhitungan Rentang Tiga Skenario")
                st.caption("Rumus batas atas (Optimis), tengah (Moderat), dan batas bawah (Pesimis):")
                st.markdown(
                    """
                    <div class="formula-box">
                        Optimis (Batas Atas) &nbsp;= Prediksi × 1,05 &nbsp;(atau Ensemble Upper Bound)<br>
                        Moderat (Baseline) &nbsp;&nbsp;&nbsp;= Prediksi × 1,00<br>
                        Pesimis (Batas Bawah) = Prediksi × 0,95 &nbsp;(atau Ensemble Lower Bound)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        render_info_box(
            "Pada mode <strong>Data-Driven (Recommended)</strong>, batas Optimis dan Pesimis dihitung secara adaptif "
            "dari rata-rata tiga pendekatan: (1) <em>Historical Volatility</em>, (2) <em>95% Confidence Interval OLS</em>, "
            "dan (3) <em>Empirical Growth Percentiles</em>.",
            box_type="info",
        )

    # TAB 3: Decomposition & HKPD
    with tabs[2]:
        create_header_with_icon("Struktur Dekomposisi Objek Pajak & Bagi Hasil HKPD", "⚖️")

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            with st.container(border=True):
                st.markdown("#### 🚗 Formula Dekomposisi PKB (2025 & 2026)")
                st.markdown(
                    """
                    <div class="formula-box">
                        <strong>Total Potensi PKB</strong> =<br>
                        &nbsp;&nbsp;+ Potensi Awal Tahun<br>
                        &nbsp;&nbsp;+ Potensi Kendaraan Baru Roda 4 &amp; Roda 2<br>
                        &nbsp;&nbsp;+ Prediksi Pencairan Tunggakan<br>
                        &nbsp;&nbsp;+ Prediksi Mutasi Masuk<br>
                        &nbsp;&nbsp;− Proyeksi Tidak Daftar Ulang (TDR)<br>
                        &nbsp;&nbsp;− Proyeksi Mutasi Keluar<br>
                        &nbsp;&nbsp;− Potensi Pembebasan Pajak Daerah<br>
                        &nbsp;&nbsp;± Dampak Bersih Variabel Makroekonomi
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col_d2:
            with st.container(border=True):
                st.markdown("#### 📝 Formula Dekomposisi BBNKB & Skema HKPD")
                st.markdown(
                    """
                    <div class="formula-box">
                        <strong>Total Potensi BBNKB</strong> =<br>
                        &nbsp;&nbsp;+ Potensi Kendaraan Baru Roda 4 &amp; Roda 2<br>
                        &nbsp;&nbsp;− Pengurang Kebijakan BBN II (khusus 2026)<br>
                        &nbsp;&nbsp;± Dampak Bersih Variabel Makroekonomi
                    </div>
                    <div class="formula-box">
                        <strong>Porsi Provinsi (HKPD)</strong> = Total Potensi × Rasio_Provinsi<br>
                        <strong>Bagian Kab/Kota</strong> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= Total Potensi × (1 − Rasio_Provinsi)
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption("Rasio efektif default Provinsi Jawa Timur pada modul simulasi HKPD ditetapkan sebesar 60,24%.")

    # TAB 4: Assumptions & Limitations
    with tabs[3]:
        create_header_with_icon("Asumsi Statistik, Keterbatasan Sampel & Mitigasi", "⚠️")

        render_info_box(
            "<strong>Transparansi Metodologis:</strong> Rentang data tahunan mencakup <strong>7 observasi (2018–2024)</strong> "
            "termasuk periode pandemi COVID-19 (2020–2021). Oleh sebab itu, hasil ekonometrika wajib dibaca berdampingan "
            "dengan dekomposisi objek pajak teknis dan pertimbangan ahli (*expert judgment*) Bapenda.",
            box_type="warning",
        )

        l1, l2 = st.columns(2)
        with l1:
            with st.container(border=True):
                st.markdown("#### 1. Ukuran Sampel Tahunan Terbatas (`n = 7`)")
                st.markdown(
                    "- **Implikasi**: Derajat bebas (*degrees of freedom*) rendah membuat interval kepercayaan 95% menjadi lebih lebar dan sensitif terhadap pencilan (*outlier*).\n"
                    "- **Mitigasi Sistem**: Menyediakan validasi silang **Leave-One-Out (LOOCV)**, **Backtesting 2023–2024**, dan rata-rata **Ensemble**."
                )
            with st.container(border=True):
                st.markdown("#### 2. Multikolinearitas Antar-Indikator Makro")
                st.markdown(
                    "- **Implikasi**: Indikator struktural seperti IPM, Kemiskinan, dan PDRB sering berkorelasi kuat (`|r| > 0.70`).\n"
                    "- **Mitigasi Sistem**: Evaluasi regresi dilakukan secara bivariat per prediktor disertai peringatan multikolinearitas otomatis pada halaman Dataset."
                )

        with l2:
            with st.container(border=True):
                st.markdown("#### 3. Asumsi Linearitas & Stabilitas Parameter")
                st.markdown(
                    "- **Implikasi**: Regresi OLS mengasumsikan elastisitas konstan sepanjang periode observasi hingga tahun proyeksi.\n"
                    "- **Mitigasi Sistem**: Modul **Scenario Builder** dan **Policy Settings** mengizinkan simulasi intervensi non-historis secara fleksibel."
                )
            with st.container(border=True):
                st.markdown("#### 4. Guncangan Eksternal & Perubahan Regulasi")
                st.markdown(
                    "- **Implikasi**: Perubahan regulasi perpajakan daerah (seperti implementasi penuh UU HKPD dan penghapusan BBN II) tidak tercermin pada tren masa lalu.\n"
                    "- **Mitigasi Sistem**: Diakomodasi secara eksplisit melalui variabel pengurang struktural di modul **Dekomposisi** dan rasio **HKPD**."
                )

    # TAB 5: Validation, Changelog & References
    with tabs[4]:
        create_header_with_icon("Kerangka Validasi Model & Riwayat Pembaruan", "✅")

        val_df = pd.DataFrame(
            [
                ("RMSE & MAE", "Rata-rata kesalahan absolut dalam satuan Rupiah", "Aktif pada halaman Pemodelan"),
                ("MAPE (%)", "Persentase kesalahan absolut rata-rata (< 10% sangat baik)", "Aktif pada halaman Pemodelan"),
                ("LOOCV (Cross-Validation)", "Uji stabilitas out-of-sample dengan menyisihkan 1 tahun bergantian", "Aktif pada halaman Pemodelan"),
                ("Backtesting Historis", "Pelatihan 2018–2022 untuk menguji akurasi prediksi 2023–2024", "Aktif pada halaman Pemodelan"),
                ("Tornado & Elasticity", "Peringkat sensitivitas dampak guncangan ±10% tiap variabel makro", "Aktif pada halaman Pemodelan"),
                ("Ensemble Multi-Model", "Komparasi OLS Regression, ARIMA(1,1,1), dan Exponential Smoothing", "Aktif pada halaman Proyeksi"),
            ],
            columns=["Instrumen Validasi", "Fungsi Evaluasi", "Status Implementasi"],
        )
        st.dataframe(val_df, use_container_width=True, hide_index=True)

        create_header_with_icon("Riwayat Versi & Referensi Regulasi", "📝")
        c_ref1, c_ref2 = st.columns(2)
        with c_ref1:
            changelog_df = pd.DataFrame(
                {
                    "Versi": ["2.0", "1.5", "1.0"],
                    "Tanggal": ["2025", "2025-01", "2024-12"],
                    "Pembaruan Utama": [
                        "Modernisasi UI Bapenda Jatim (Light/Dark), LOOCV, Backtesting, Ensemble, Scenario Builder, Decision Support & Audit Trail",
                        "Penambahan Confidence Interval 95%, Correlation Heatmap, Waterfall Dekomposisi, dan Ekspor Excel Multi-Sheet",
                        "Rilis perdana proyeksi PKB & BBNKB berbasis regresi makro dan simulasi HKPD",
                    ],
                }
            )
            st.dataframe(changelog_df, use_container_width=True, hide_index=True)

        with c_ref2:
            with st.container(border=True):
                st.markdown("#### 📚 Landasan Regulasi & Literatur")
                st.markdown(
                    "- **UU Nomor 1 Tahun 2022** tentang Hubungan Keuangan antara Pemerintah Pusat dan Pemerintahan Daerah (HKPD).\n"
                    "- **PP Nomor 35 Tahun 2023** tentang Ketentuan Umum Pajak Daerah dan Retribusi Daerah.\n"
                    "- **Perda Provinsi Jawa Timur Nomor 8 Tahun 2023** tentang Pajak Daerah dan Retribusi Daerah.\n"
                    "- Wooldridge, J. M. (2020). *Introductory Econometrics: A Modern Approach*.\n"
                    "- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice* (3rd ed.)."
                )


def app() -> None:
    show_metodologi_page()


if __name__ == "__main__":
    app()
