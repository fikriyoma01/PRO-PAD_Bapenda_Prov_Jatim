"""
Audit Trail Viewer Page
Catatan kronologis aktivitas pemodelan, proyeksi, penyuntingan data, penyimpanan skenario, dan ekspor laporan.
"""

from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.audit_utils import (
    clear_audit_log,
    format_audit_log_df,
    get_audit_log,
    get_audit_statistics,
    initialize_session,
)
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)


def show_audit_page() -> None:
    initialize_session()

    if "confirm_clear_audit" not in st.session_state:
        st.session_state.confirm_clear_audit = False

    render_page_header(
        title="Audit Trail & Log Aktivitas Sistem",
        subtitle="Rekam jejak kronologis eksekusi model, proyeksi, perubahan data, dan pengunduhan laporan untuk akuntabilitas tata kelola",
        icon="📋",
    )

    with st.expander("ℹ️ Tentang Sistem Audit Trail PRO-PAD", expanded=False):
        st.markdown(
            """
            **Audit Trail** mencatat aktivitas penting selama penggunaan aplikasi untuk mendukung transparansi dan kepatuhan internal:
            - `model_run` — Eksekusi estimasi parameter regresi linear OLS.
            - `projection` — Perhitungan skenario proyeksi tahun 2025–2026.
            - `scenario_save` — Penyimpanan skenario simulasi pada Scenario Builder.
            - `data_edit` — Penyimpanan perubahan dataset historis kustom.
            - `export` — Pengunduhan dokumen laporan Excel / HTML Eksekutif.
            - `session_start` — Inisialisasi sesi kerja pengguna.
            """
        )

    stats = get_audit_statistics()

    if stats["total_events"] == 0:
        st.info("📭 Belum terdapat entri aktivitas pada log audit.")
        return

    # --- KPI Statistik Audit ---
    create_header_with_icon(
        "Ringkasan Statistik Aktivitas",
        "📊",
        subtitle=f"Rentang pencatatan: {stats['first_event']} s.d. {stats['last_event']}",
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            label="Total Aktivitas Tercatat",
            value=f"{stats['total_events']:,}",
            icon="📝",
            variant="primary",
        )
    with k2:
        render_kpi_card(
            label="Pengguna Unik",
            value=str(stats["unique_users"]),
            icon="👤",
            variant="success",
        )
    with k3:
        render_kpi_card(
            label="Total Sesi Kerja",
            value=str(stats["unique_sessions"]),
            icon="🔑",
            variant="indigo",
        )
    with k4:
        render_kpi_card(
            label="Kategori Event",
            value=str(len(stats["event_types"])),
            icon="🏷️",
            variant="warning",
        )

    # --- Distribusi Event (Side-by-Side Pie & Bar) ---
    if stats["event_types"]:
        create_header_with_icon("Proporsi & Frekuensi Berdasarkan Tipe Event", "📈")
        c_chart1, c_chart2 = st.columns(2)

        with c_chart1:
            with st.container(border=True):
                fig_pie = px.pie(
                    names=list(stats["event_types"].keys()),
                    values=list(stats["event_types"].values()),
                    hole=0.45,
                    color_discrete_sequence=["#1a5fb4", "#10b981", "#f59e0b", "#6366f1", "#0ea5e9", "#ef4444"],
                )
                fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                apply_plotly_theme(fig_pie, title="Proporsi Kategori Aktivitas", height=370)
                st.plotly_chart(fig_pie, use_container_width=True)

        with c_chart2:
            with st.container(border=True):
                fig_bar = go.Figure(
                    go.Bar(
                        x=list(stats["event_types"].keys()),
                        y=list(stats["event_types"].values()),
                        marker_color="#1a5fb4",
                        text=list(stats["event_types"].values()),
                        textposition="outside",
                        cliponaxis=False,
                    )
                )
                apply_plotly_theme(
                    fig_bar,
                    title="Jumlah Aktivitas per Tipe Event",
                    height=370,
                    xaxis_title="Tipe Event",
                    yaxis_title="Jumlah Tercatat",
                    show_legend=False,
                )
                st.plotly_chart(fig_bar, use_container_width=True)

    render_section_divider()

    # --- Tabel Penelusuran Log ---
    create_header_with_icon("Penelusuran Rincian Log Audit", "🔍")

    with st.container(border=True):
        f1, f2, f3 = st.columns([1.8, 1, 1.2])
        with f1:
            event_type_filter = st.selectbox(
                "Filter berdasarkan Tipe Event",
                ["Semua Tipe"] + list(stats["event_types"].keys()),
            )
        with f2:
            limit = st.number_input(
                "Batas Jumlah Baris",
                min_value=10,
                max_value=1000,
                value=100,
                step=10,
            )

        log_data = (
            get_audit_log(limit=int(limit))
            if event_type_filter == "Semua Tipe"
            else get_audit_log(event_type=event_type_filter, limit=int(limit))
        )

        with f3:
            st.markdown("<div style='height: 1.65rem;'></div>", unsafe_allow_html=True)
            if log_data:
                log_df = format_audit_log_df(log_data)
                st.download_button(
                    label="📥 Unduh Log Audit (.csv)",
                    data=log_df.to_csv(index=False).encode("utf-8"),
                    file_name=f"pro_pad_audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    type="primary",
                    use_container_width=True,
                )

        if log_data:
            st.dataframe(log_df, use_container_width=True, hide_index=True, height=380)
        else:
            st.info("📭 Tidak ditemukan catatan aktivitas untuk filter yang dipilih.")

    # --- Linimasa Aktivitas ---
    if log_data and len(log_data) > 1:
        create_header_with_icon("Pola Waktu Aktivitas", "⏱️")
        df_timeline = pd.DataFrame(log_data)
        df_timeline["timestamp"] = pd.to_datetime(df_timeline["timestamp"], errors="coerce")
        df_timeline = df_timeline.dropna(subset=["timestamp"])

        if not df_timeline.empty:
            df_timeline["date"] = df_timeline["timestamp"].dt.date
            df_timeline["hour"] = df_timeline["timestamp"].dt.hour

            t1, t2 = st.columns(2)
            with t1:
                with st.container(border=True):
                    daily_counts = df_timeline.groupby("date").size().reset_index(name="count")
                    fig_timeline = px.line(daily_counts, x="date", y="count", markers=True)
                    fig_timeline.update_traces(line=dict(color="#1a5fb4", width=3), marker=dict(size=8))
                    apply_plotly_theme(
                        fig_timeline,
                        title="Tren Aktivitas Harian",
                        height=350,
                        xaxis_title="Tanggal",
                        yaxis_title="Jumlah Event",
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)

            with t2:
                with st.container(border=True):
                    hourly_counts = df_timeline.groupby("hour").size().reset_index(name="count")
                    fig_hourly = px.bar(hourly_counts, x="hour", y="count")
                    fig_hourly.update_traces(marker_color="#10b981")
                    apply_plotly_theme(
                        fig_hourly,
                        title="Distribusi Aktivitas per Jam (00–23)",
                        height=350,
                        xaxis_title="Jam (WIB)",
                        yaxis_title="Jumlah Event",
                    )
                    st.plotly_chart(fig_hourly, use_container_width=True)

    render_section_divider()

    # --- Tindakan Administrasi (Fixed Confirmation) ---
    create_header_with_icon("Administrasi Log", "🔧")
    with st.container(border=True):
        a1, a2 = st.columns(2)
        with a1:
            if st.button("🔄 Muat Ulang Statistik Log", use_container_width=True):
                st.rerun()
        with a2:
            if st.button("🗑️ Bersihkan Seluruh Audit Log", use_container_width=True):
                st.session_state.confirm_clear_audit = True

        if st.session_state.confirm_clear_audit:
            st.warning("⚠️ Tindakan ini akan menghapus seluruh riwayat catatan audit secara permanen. Pastikan Anda telah mengunduh salinan CSV terlebih dahulu.")
            c_ok, c_cancel = st.columns(2)
            with c_ok:
                if st.button("✅ Ya, Hapus Seluruh Log", type="primary", use_container_width=True):
                    if clear_audit_log():
                        st.session_state.confirm_clear_audit = False
                        st.rerun()
                    else:
                        st.error("❌ Gagal menghapus berkas audit log.")
            with c_cancel:
                if st.button("✖ Batal", use_container_width=True):
                    st.session_state.confirm_clear_audit = False
                    st.rerun()


def app() -> None:
    show_audit_page()


if __name__ == "__main__":
    app()
