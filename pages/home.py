"""
Home Page — Dashboard PRO-PAD Bapenda Provinsi Jawa Timur
Halaman utama ikhtisar capaian historis, tren PAD, fitur unggulan, dan navigasi cepat.
"""

import plotly.graph_objects as go
import streamlit as st

from data_loader import load_pad_historis
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_feature_card,
    render_info_box,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact, format_rupiah_full


def show_home_page() -> None:
    render_page_header(
        title="Dashboard Proyeksi PAD Jawa Timur",
        subtitle="Sistem Analisis, Simulasi Kebijakan HKPD, dan Proyeksi Pendapatan Asli Daerah Berbasis Data Science",
        icon="🏛️",
    )

    # Ringkasan pengantar institusional
    st.markdown(
        """
        <div class="modern-card fade-in" style="padding: 1.5rem 1.75rem;">
            <h3 style="color: var(--heading-accent); margin: 0 0 0.55rem 0; font-size: 1.2rem; font-weight: 700;">
                Selamat Datang di Sistem Analitik PRO-PAD Bapenda Provinsi Jawa Timur
            </h3>
            <p style="font-size: 0.98rem; color: var(--text-secondary); line-height: 1.7; margin: 0;">
                Platform ini menyajikan pemantauan realisasi historis, pemodelan ekonometrika, simulasi skenario makroekonomi,
                serta dukungan keputusan strategis untuk <strong>PKB (Pajak Kendaraan Bermotor)</strong> dan
                <strong>BBNKB (Bea Balik Nama Kendaraan Bermotor)</strong> secara transparan dan terukur.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Muat data historis terkini (mendukung dataset kustom apabila diaktifkan)
    df = load_pad_historis()
    min_year = int(df["Tahun"].min())
    latest_year = int(df["Tahun"].max())
    latest_pkb = float(df.loc[df["Tahun"] == latest_year, "PKB"].iloc[0])
    latest_bbnkb = float(df.loc[df["Tahun"] == latest_year, "BBNKB"].iloc[0])
    total_pad = latest_pkb + latest_bbnkb

    if len(df) >= 2:
        prev_df = df.sort_values("Tahun")
        prev_pkb = float(prev_df["PKB"].iloc[-2])
        prev_bbnkb = float(prev_df["BBNKB"].iloc[-2])
        prev_total = prev_pkb + prev_bbnkb
        pkb_growth = ((latest_pkb - prev_pkb) / prev_pkb * 100) if prev_pkb else 0.0
        bbnkb_growth = ((latest_bbnkb - prev_bbnkb) / prev_bbnkb * 100) if prev_bbnkb else 0.0
        total_growth = ((total_pad - prev_total) / prev_total * 100) if prev_total else 0.0
    else:
        pkb_growth = 0.0
        bbnkb_growth = 0.0
        total_growth = 0.0

    # --- KPI Utama ---
    create_header_with_icon(
        "Ringkasan Realisasi Terkini",
        "📊",
        subtitle=f"Posisi capaian tahun terakhir ({latest_year}) dibandingkan tahun sebelumnya",
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card(
            label=f"Realisasi PKB {latest_year}",
            value=format_rupiah_compact(latest_pkb, respect_privacy=True),
            delta=f"{pkb_growth:+.2f}% YoY",
            delta_positive=pkb_growth >= 0,
            subtitle=format_rupiah_full(latest_pkb),
            icon="🚗",
            variant="primary",
        )
    with col2:
        render_kpi_card(
            label=f"Realisasi BBNKB {latest_year}",
            value=format_rupiah_compact(latest_bbnkb, respect_privacy=True),
            delta=f"{bbnkb_growth:+.2f}% YoY",
            delta_positive=bbnkb_growth >= 0,
            subtitle=format_rupiah_full(latest_bbnkb),
            icon="📝",
            variant="warning",
        )
    with col3:
        render_kpi_card(
            label=f"Total PKB + BBNKB {latest_year}",
            value=format_rupiah_compact(total_pad, respect_privacy=True),
            delta=f"{total_growth:+.2f}% YoY",
            delta_positive=total_growth >= 0,
            subtitle=format_rupiah_full(total_pad),
            icon="💰",
            variant="success",
        )
    with col4:
        render_kpi_card(
            label="Cakupan Observasi",
            value=f"{min_year}–{latest_year}",
            delta=f"{len(df)} Tahun Data",
            delta_positive=None,
            subtitle="7 Indikator Makroekonomi",
            icon="📅",
            variant="indigo",
        )

    render_section_divider()

    # --- Tren Historis PAD ---
    create_header_with_icon(
        "Tren Historis PKB & BBNKB",
        "📈",
        subtitle=f"Perkembangan penerimaan pajak kendaraan bermotor Provinsi Jawa Timur ({min_year}–{latest_year})",
    )

    with st.container(border=True):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["Tahun"],
                y=df["PKB"],
                mode="lines+markers",
                name="PKB",
                line=dict(color="#1a5fb4", width=3.5, shape="spline"),
                marker=dict(size=9, symbol="circle", line=dict(width=2, color="#ffffff")),
                hovertemplate="<b>PKB</b><br>Tahun: %{x}<br>Realisasi: Rp %{y:,.0f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["Tahun"],
                y=df["BBNKB"],
                mode="lines+markers",
                name="BBNKB",
                line=dict(color="#f59e0b", width=3.5, shape="spline"),
                marker=dict(size=9, symbol="diamond", line=dict(width=2, color="#ffffff")),
                hovertemplate="<b>BBNKB</b><br>Tahun: %{x}<br>Realisasi: Rp %{y:,.0f}<extra></extra>",
            )
        )

        apply_plotly_theme(
            fig,
            title=f"Tren Realisasi PKB & BBNKB ({min_year}–{latest_year})",
            height=440,
            xaxis_title="Tahun",
            yaxis_title="Nilai Penerimaan (Rupiah)",
            is_currency=True,
        )
        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_xaxes(dtick=1)
        st.plotly_chart(fig, use_container_width=True)

    render_section_divider()

    # --- Fitur Unggulan ---
    create_header_with_icon(
        "Kapabilitas Utama Sistem",
        "✨",
        subtitle="Arsitektur analitik komprehensif dari eksplorasi data hingga rekomendasi kebijakan",
    )

    row1 = st.columns(3)
    with row1[0]:
        render_feature_card(
            icon="📊",
            title="Eksplorasi & Korelasi Makro",
            description="Visualisasi realisasi historis, matriks korelasi 9 variabel, serta deteksi otomatis multikolinearitas.",
        )
    with row1[1]:
        render_feature_card(
            icon="🔮",
            title="Proyeksi Ensemble & CI 95%",
            description="Kombinasi model OLS, ARIMA, dan Exponential Smoothing lengkap dengan rentang kepercayaan statistik 95%.",
        )
    with row1[2]:
        render_feature_card(
            icon="⚖️",
            title="Dekomposisi & Simulasi HKPD",
            description="Perhitungan berbasis objek pajak riil, proyeksi bagi hasil Provinsi vs Kab/Kota (UU 1/2022), dan analisis waterfall.",
        )

    row2 = st.columns(3)
    with row2[0]:
        render_feature_card(
            icon="📈",
            title="Validasi & Backtesting",
            description="Evaluasi akurasi model menggunakan RMSE, MAE, MAPE, Leave-One-Out Cross-Validation (LOOCV), dan uji historis.",
        )
    with row2[1]:
        render_feature_card(
            icon="🌪️",
            title="Analisis Sensitivitas & Skenario",
            description="Tornado chart, koefisien elastisitas, serta simulasi what-if interaktif lintas 7 indikator makroekonomi.",
        )
    with row2[2]:
        render_feature_card(
            icon="🏛️",
            title="Executive Decision Support",
            description="Penilaian risiko pencapaian target, rekomendasi tindakan prioritas, audit trail, dan ekspor laporan eksekutif.",
        )

    render_section_divider()

    # --- Navigasi Cepat Interaktif ---
    create_header_with_icon(
        "Navigasi Cepat",
        "🧭",
        subtitle="Akses langsung ke modul analitik utama",
    )

    quick_links = [
        (
            "📄 Dataset Historis",
            "datasets",
            "#1a5fb4",
            "Tinjau data 2018–2024, perkembangan indikator makro, dan heatmap korelasi.",
        ),
        (
            "📊 Pemodelan Regresi",
            "pemodelan",
            "#10b981",
            "Uji signifikansi prediktor makro, LOOCV, backtesting, dan tornado chart.",
        ),
        (
            "📈 Proyeksi 2025–2026",
            "proyeksi",
            "#f59e0b",
            "Bandingkan skenario Optimis/Moderat/Pesimis dan model ensemble.",
        ),
        (
            "🎯 Scenario Builder",
            "scenario_builder",
            "#6366f1",
            "Jalankan simulasi what-if interaktif dan simpan skenario kebijakan kustom.",
        ),
    ]

    nav_cols = st.columns(4)
    for col, (title, slug, accent, desc) in zip(nav_cols, quick_links):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="border-top: 3px solid {accent}; padding-top: 0.65rem; min-height: 112px;">
                        <h4 style="color: var(--heading-accent); margin: 0 0 0.45rem 0; font-size: 1.02rem; font-weight: 700;">
                            {title}
                        </h4>
                        <p style="color: var(--text-muted); margin: 0; font-size: 0.88rem; line-height: 1.5;">
                            {desc}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Buka Halaman →", key=f"quick_nav_{slug}", use_container_width=True):
                    st.session_state.current_page = slug
                    st.rerun()

    render_section_divider()

    render_info_box(
        "<strong>Alur Kerja yang Disarankan:</strong> Mulailah dari <strong>Dataset Historis</strong> untuk meninjau tren dasar, "
        "lanjutkan ke <strong>Pemodelan Regresi</strong> & <strong>Proyeksi 2025–2026</strong> untuk melihat estimasi berbasis makro, "
        "lalu gunakan <strong>Dekomposisi PAD</strong> dan <strong>Decision Support</strong> untuk penetapan target operasional.",
        box_type="info",
    )

    st.markdown(
        """
        <div style="text-align: center; padding: 1.5rem 1rem 0.5rem 1rem; color: var(--text-muted); font-size: 0.86rem;">
            <p style="margin: 0; font-weight: 600; color: var(--text-secondary);">
                PRO-PAD — Sistem Proyeksi Pendapatan Asli Daerah v2.0
            </p>
            <p style="margin: 0.3rem 0 0 0;">
                Badan Pendapatan Daerah Provinsi Jawa Timur • © 2025 Pemerintah Provinsi Jawa Timur
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def app() -> None:
    show_home_page()


if __name__ == "__main__":
    app()
