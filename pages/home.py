"""
Home Page - Dashboard PAD Landing
Modern, engaging landing page with overview and quick stats
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_loader import load_pad_historis
from utils.ui_components import (
    render_gradient_header,
    render_metric_card,
    render_info_box,
    render_section_divider,
    render_feature_card,
    create_header_with_icon
)


def show_home_page():
    # Main Header
    render_gradient_header(
        title="Dashboard Proyeksi PAD Jawa Timur",
        subtitle="Sistem Analisis & Proyeksi Pendapatan Asli Daerah Berbasis Data Science",
        icon="🏛️"
    )

    # Welcome message
    st.markdown("""
    <div class="modern-card fade-in" style="text-align: center; padding: 2rem;">
        <h2 style="color: #1a5fb4; margin-bottom: 1rem;">Selamat Datang di Dashboard PAD Jawa Timur</h2>
        <p style="font-size: 1.1rem; color: #6c757d; line-height: 1.8;">
            Dashboard ini menyediakan analisis mendalam dan proyeksi akurat untuk
            <strong>PKB (Pajak Kendaraan Bermotor)</strong> dan <strong>BBNKB (Bea Balik Nama Kendaraan Bermotor)</strong>
            menggunakan metodologi statistik dan machine learning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Load data for quick stats
    df = load_pad_historis()
    latest_year = int(df['Tahun'].max())
    latest_pkb = df.loc[df['Tahun'] == latest_year, 'PKB'].iloc[0]
    latest_bbnkb = df.loc[df['Tahun'] == latest_year, 'BBNKB'].iloc[0]

    # Calculate growth if possible
    if len(df) >= 2:
        prev_year = latest_year - 1
        prev_pkb = df.loc[df['Tahun'] == prev_year, 'PKB'].iloc[0]
        prev_bbnkb = df.loc[df['Tahun'] == prev_year, 'BBNKB'].iloc[0]
        pkb_growth = ((latest_pkb - prev_pkb) / prev_pkb * 100)
        bbnkb_growth = ((latest_bbnkb - prev_bbnkb) / prev_bbnkb * 100)
    else:
        pkb_growth = 0
        bbnkb_growth = 0

    # Quick Stats Section
    create_header_with_icon("📊 Ringkasan Data Terkini", "📈")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card(
            label=f"PKB {latest_year}",
            value=f"Rp {latest_pkb/1e9:.2f}T",
            delta=f"{pkb_growth:+.1f}%",
            delta_positive=pkb_growth > 0
        )

    with col2:
        render_metric_card(
            label=f"BBNKB {latest_year}",
            value=f"Rp {latest_bbnkb/1e9:.2f}T",
            delta=f"{bbnkb_growth:+.1f}%",
            delta_positive=bbnkb_growth > 0
        )

    with col3:
        total_pad = latest_pkb + latest_bbnkb
        render_metric_card(
            label=f"Total PAD {latest_year}",
            value=f"Rp {total_pad/1e9:.2f}T",
            delta=None
        )

    with col4:
        render_metric_card(
            label="Data Range",
            value=f"{int(df['Tahun'].min())}-{latest_year}",
            delta=f"{len(df)} Years"
        )

    render_section_divider()

    # Trend visualization
    create_header_with_icon("📈 Tren Historis PAD", "📉")

    st.markdown("""
    <div class="modern-card">
    """, unsafe_allow_html=True)

    # Create beautiful line chart
    fig = go.Figure()

    # PKB line
    fig.add_trace(go.Scatter(
        x=df['Tahun'],
        y=df['PKB'],
        mode='lines+markers',
        name='PKB',
        line=dict(color='#1a5fb4', width=4, shape='spline'),
        marker=dict(size=10, symbol='circle', line=dict(width=2, color='white')),
        hovertemplate='<b>PKB</b><br>Tahun: %{x}<br>Nilai: Rp %{y:,.0f}<extra></extra>'
    ))

    # BBNKB line
    fig.add_trace(go.Scatter(
        x=df['Tahun'],
        y=df['BBNKB'],
        mode='lines+markers',
        name='BBNKB',
        line=dict(color='#ff9800', width=4, shape='spline'),
        marker=dict(size=10, symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate='<b>BBNKB</b><br>Tahun: %{x}<br>Nilai: Rp %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': '<b>Tren PKB & BBNKB (2018-2024)</b>',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50'}
        },
        xaxis=dict(
            title='<b>Tahun</b>',
            tickmode='linear',
            tick0=df['Tahun'].min(),
            dtick=1,
            gridcolor='#e9ecef',
            showgrid=True
        ),
        yaxis=dict(
            title='<b>Nilai (Rupiah)</b>',
            tickformat=',.0f',
            gridcolor='#e9ecef',
            showgrid=True
        ),
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#e9ecef",
            borderwidth=2
        ),
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    render_section_divider()

    # Features Grid
    create_header_with_icon("✨ Fitur Unggulan Dashboard", "🎯")

    col1, col2, col3 = st.columns(3)

    with col1:
        render_feature_card(
            icon="📊",
            title="Analisis Mendalam",
            description="Visualisasi data historis, correlation heatmap, dan analisis statistik komprehensif"
        )

    with col2:
        render_feature_card(
            icon="🔮",
            title="Proyeksi Akurat",
            description="Model ensemble (OLS, ARIMA, Exp Smoothing) dengan confidence intervals 95%"
        )

    with col3:
        render_feature_card(
            icon="🎯",
            title="Scenario Planning",
            description="Interactive what-if analysis dengan 7 variabel makroekonomi"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        render_feature_card(
            icon="📈",
            title="Model Validation",
            description="RMSE, MAPE, cross-validation, dan backtesting untuk akurasi terjamin"
        )

    with col2:
        render_feature_card(
            icon="🔬",
            title="Sensitivity Analysis",
            description="Tornado chart dan elasticity analysis untuk risk assessment"
        )

    with col3:
        render_feature_card(
            icon="📋",
            title="Audit Trail",
            description="Tracking lengkap semua aktivitas untuk transparansi dan compliance"
        )

    render_section_divider()

    # Quick Navigation
    create_header_with_icon("🧭 Navigasi Cepat", "🚀")

    st.markdown("""
    <div class="modern-card">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
            <div style="padding: 1.5rem; border-left: 4px solid #1a5fb4; background: #f8f9fa; border-radius: 8px;">
                <h3 style="color: #1a5fb4; margin: 0 0 0.5rem 0;">📄 Dataset</h3>
                <p style="color: #6c757d; margin: 0; font-size: 0.95rem;">Lihat data historis, correlation heatmap, dan statistik deskriptif</p>
            </div>
            <div style="padding: 1.5rem; border-left: 4px solid #4caf50; background: #f8f9fa; border-radius: 8px;">
                <h3 style="color: #4caf50; margin: 0 0 0.5rem 0;">📊 Pemodelan</h3>
                <p style="color: #6c757d; margin: 0; font-size: 0.95rem;">Regresi, validation metrics, dan sensitivity analysis</p>
            </div>
            <div style="padding: 1.5rem; border-left: 4px solid #ff9800; background: #f8f9fa; border-radius: 8px;">
                <h3 style="color: #ff9800; margin: 0 0 0.5rem 0;">📈 Proyeksi</h3>
                <p style="color: #6c757d; margin: 0; font-size: 0.95rem;">Proyeksi 2025-2026 dengan CI dan ensemble models</p>
            </div>
            <div style="padding: 1.5rem; border-left: 4px solid #8e24aa; background: #f8f9fa; border-radius: 8px;">
                <h3 style="color: #8e24aa; margin: 0 0 0.5rem 0;">🎯 Scenario Builder</h3>
                <p style="color: #6c757d; margin: 0; font-size: 0.95rem;">What-if analysis interaktif dengan multiple scenarios</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Info boxes at bottom
    render_section_divider()

    render_info_box(
        "💡 <strong>Tips Penggunaan:</strong> Mulai dari halaman <strong>Dataset</strong> untuk memahami data, "
        "lalu ke <strong>Pemodelan</strong> untuk melihat analisis statistik, dan <strong>Proyeksi</strong> untuk melihat hasil forecasting.",
        box_type="info"
    )

    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #6c757d; font-size: 0.9rem;">
        <p style="margin: 0;">Dashboard PAD Jawa Timur v2.0</p>
        <p style="margin: 0.5rem 0 0 0;">Developed with ❤️ by Claude AI | © 2025 Bapenda Prov. Jatim</p>
    </div>
    """, unsafe_allow_html=True)


def app():
    show_home_page()


if __name__ == "__main__":
    app()
