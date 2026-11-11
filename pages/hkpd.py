"""
Implementasi Skenario HKPD Page (UU Nomor 1 Tahun 2022)
Simulasi pembagian porsi penerimaan PKB & BBNKB antara Pemerintah Provinsi dan Kabupaten/Kota.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import get_bbnkb_inputs, get_pkb_inputs, load_pad_historis, map_inputs
from pages import dekomposisi as dekom
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact, format_rupiah_full

DEFAULT_RATIO = 0.6024


def compute_future_totals():
    hist = load_pad_historis()

    pkb_inputs_2025 = get_pkb_inputs(2025)
    baseline_2024 = {var: float(hist.iloc[-1][var]) for var in dekom.MACROS if var in hist.columns}
    _, total_pkb25, _, pred_macro25 = dekom.dekomposisi_pkb_with_macro(
        2025, pkb_inputs_2025, baseline_2024, df=hist
    )

    baseline_2025 = {k: float(v) for k, v in pred_macro25.items()}
    pkb_inputs_2026 = get_pkb_inputs(2026)
    _, total_pkb26, _, _ = dekom.dekomposisi_pkb_with_macro(
        2026, pkb_inputs_2026, baseline_2025, df=hist
    )

    bbn_inputs_2025 = get_bbnkb_inputs(2025)
    bbn_inputs_2026 = get_bbnkb_inputs(2026)

    _, bbn_plus25, bbn_minus25, _ = dekom.compute_macro_impact(
        2025, baseline_2024, response_col="BBNKB", df=hist
    )
    _, bbn_plus26, bbn_minus26, _ = dekom.compute_macro_impact(
        2026, baseline_2025, response_col="BBNKB", df=hist
    )

    bbn_vals_2025 = map_inputs(bbn_inputs_2025)
    bbn_total_2025 = float(bbn_vals_2025.get("Total", 0.0)) + bbn_plus25 + bbn_minus25

    bbn_vals_2026 = map_inputs(bbn_inputs_2026)
    bbn_net_2026 = float(bbn_vals_2026.get("Total", 0.0)) - float(bbn_vals_2026.get("Pengurang", 0.0))
    bbn_total_2026 = bbn_net_2026 + bbn_plus26 + bbn_minus26

    return hist, total_pkb25, total_pkb26, bbn_total_2025, bbn_total_2026


def build_hkpd_series(
    hist: pd.DataFrame,
    pkb2025: float,
    pkb2026: float,
    bbn2025: float,
    bbn2026: float,
    factor: float,
) -> pd.DataFrame:
    records = []

    for row in hist.itertuples(index=False):
        records.append(
            {
                "Tahun": int(row.Tahun),
                "Status": "Aktual",
                "PKB Bruto": float(row.PKB),
                "BBNKB Bruto": float(row.BBNKB),
            }
        )

    for year, pkb_val, bbn_val in [(2025, pkb2025, bbn2025), (2026, pkb2026, bbn2026)]:
        records.append(
            {
                "Tahun": year,
                "Status": "Proyeksi",
                "PKB Bruto": float(pkb_val),
                "BBNKB Bruto": float(bbn_val),
            }
        )

    df = pd.DataFrame(records)
    df["PKB Porsi Provinsi"] = df["PKB Bruto"] * factor
    df["PKB Opsen/Kab-Kota"] = df["PKB Bruto"] * (1.0 - factor)
    df["BBNKB Porsi Provinsi"] = df["BBNKB Bruto"] * factor
    df["BBNKB Opsen/Kab-Kota"] = df["BBNKB Bruto"] * (1.0 - factor)
    return df


def app() -> None:
    render_page_header(
        title="Simulasi Skenario HKPD",
        subtitle="Analisis dampak porsi pembagian penerimaan PKB & BBNKB antara Pemerintah Provinsi dan Kabupaten/Kota (2018–2026)",
        icon="📘",
    )

    with st.expander("ℹ️ Tentang Skema HKPD (Hubungan Keuangan antara Pemerintah Pusat dan Pemerintahan Daerah)", expanded=False):
        st.markdown(
            """
            Berdasarkan **UU Nomor 1 Tahun 2022 tentang HKPD**, skema opsen pajak daerah mengatur proporsi penerimaan
            antara **Pemerintah Provinsi** dan **Pemerintah Kabupaten/Kota**:
            - **Porsi Provinsi Default (`60.24%`)**: Menggambarkan hak bersih penerimaan Provinsi Jawa Timur.
            - **Porsi Kabupaten/Kota (`39.76%`)**: Menggambarkan bagian opsen/bagi hasil untuk Kabupaten/Kota.
            - Gunakan pengatur di bawah untuk menguji sensitivitas fiskal Provinsi pada berbagai rasio efektif.
            """
        )

    if "ratio_value" not in st.session_state:
        st.session_state.ratio_value = round(DEFAULT_RATIO * 100, 2)

    def update_from_slider() -> None:
        st.session_state.ratio_value = float(st.session_state.ratio_slider)

    def update_from_number() -> None:
        st.session_state.ratio_value = float(st.session_state.ratio_number)

    def reset_default_ratio() -> None:
        st.session_state.ratio_value = round(DEFAULT_RATIO * 100, 2)
        st.session_state.ratio_slider = round(DEFAULT_RATIO * 100, 2)
        st.session_state.ratio_number = round(DEFAULT_RATIO * 100, 2)

    # --- Panel Kontrol Rasio HKPD ---
    with st.container(border=True):
        c_sl, c_num, c_btn = st.columns([2.6, 1, 1])
        with c_sl:
            st.slider(
                "⚖️ Porsi Penerimaan Provinsi — HKPD (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                key="ratio_slider",
                value=float(st.session_state.ratio_value),
                on_change=update_from_slider,
            )
        with c_num:
            st.number_input(
                "Input Presisi (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f",
                key="ratio_number",
                value=float(st.session_state.ratio_value),
                on_change=update_from_number,
            )
        with c_btn:
            st.markdown("<div style='height: 1.65rem;'></div>", unsafe_allow_html=True)
            st.button(
                "🔄 Default (60.24%)",
                on_click=reset_default_ratio,
                use_container_width=True,
            )

        ratio_input = float(st.session_state.ratio_value)
        factor = ratio_input / 100.0
        kab_pct = 100.0 - ratio_input
        st.caption(
            f"Proporsi simulasi aktif: **Pemerintah Provinsi {ratio_input:.2f}%** | **Kabupaten/Kota {kab_pct:.2f}%**"
        )

    hist, pkb25, pkb26, bbn25, bbn26 = compute_future_totals()
    scenario_df = build_hkpd_series(hist, pkb25, pkb26, bbn25, bbn26, factor)

    latest = scenario_df[scenario_df["Tahun"] == 2026].iloc[0]
    prev = scenario_df[scenario_df["Tahun"] == 2025].iloc[0]

    # --- KPI Skenario Tahun 2026 ---
    create_header_with_icon(
        f"Estimasi Distribusi HKPD Tahun 2026 (Porsi Provinsi {ratio_input:.2f}%)",
        "🏛️",
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        diff_pkb = float(latest["PKB Porsi Provinsi"] - prev["PKB Porsi Provinsi"])
        render_kpi_card(
            label="PKB Porsi Provinsi (2026)",
            value=format_rupiah_compact(latest["PKB Porsi Provinsi"], respect_privacy=True),
            delta=f"{format_rupiah_compact(diff_pkb, signed=True)} vs 2025",
            delta_positive=diff_pkb >= 0,
            subtitle=format_rupiah_full(latest["PKB Porsi Provinsi"]),
            icon="🚗",
            variant="primary",
        )
    with k2:
        render_kpi_card(
            label="PKB Bagian Kab/Kota (2026)",
            value=format_rupiah_compact(latest["PKB Opsen/Kab-Kota"], respect_privacy=True),
            delta=f"Porsi {kab_pct:.2f}%",
            delta_positive=None,
            subtitle=format_rupiah_full(latest["PKB Opsen/Kab-Kota"]),
            icon="🏘️",
            variant="indigo",
        )
    with k3:
        diff_bbn = float(latest["BBNKB Porsi Provinsi"] - prev["BBNKB Porsi Provinsi"])
        render_kpi_card(
            label="BBNKB Porsi Provinsi (2026)",
            value=format_rupiah_compact(latest["BBNKB Porsi Provinsi"], respect_privacy=True),
            delta=f"{format_rupiah_compact(diff_bbn, signed=True)} vs 2025",
            delta_positive=diff_bbn >= 0,
            subtitle=format_rupiah_full(latest["BBNKB Porsi Provinsi"]),
            icon="📝",
            variant="success",
        )
    with k4:
        render_kpi_card(
            label="BBNKB Bagian Kab/Kota (2026)",
            value=format_rupiah_compact(latest["BBNKB Opsen/Kab-Kota"], respect_privacy=True),
            delta=f"Porsi {kab_pct:.2f}%",
            delta_positive=None,
            subtitle=format_rupiah_full(latest["BBNKB Opsen/Kab-Kota"]),
            icon="🏘️",
            variant="warning",
        )

    render_section_divider()

    # --- Visualisasi Grafik HKPD ---
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        create_header_with_icon("Tren Porsi Provinsi (HKPD)", "📈")
        with st.container(border=True):
            chart_df = scenario_df.melt(
                id_vars=["Tahun", "Status"],
                value_vars=["PKB Porsi Provinsi", "BBNKB Porsi Provinsi"],
                var_name="Komponen",
                value_name="Nilai",
            )
            fig = px.line(
                chart_df,
                x="Tahun",
                y="Nilai",
                color="Komponen",
                line_dash="Status",
                markers=True,
                category_orders={"Status": ["Aktual", "Proyeksi"]},
                color_discrete_map={
                    "PKB Porsi Provinsi": "#1a5fb4",
                    "BBNKB Porsi Provinsi": "#10b981",
                },
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            apply_plotly_theme(
                fig,
                title=f"Penerimaan Bersih Provinsi ({ratio_input:.2f}%)",
                height=420,
                xaxis_title="Tahun",
                yaxis_title="Nilai (Rupiah)",
                is_currency=True,
            )
            fig.update_yaxes(rangemode="tozero")
            fig.update_xaxes(dtick=1)
            fig.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_c2:
        create_header_with_icon("Bruto vs Porsi Provinsi", "⚖️")
        with st.container(border=True):
            compare_df = pd.concat(
                [
                    scenario_df[["Tahun", "Status", "PKB Bruto"]]
                    .rename(columns={"PKB Bruto": "Nilai"})
                    .assign(Komponen="PKB", Skema="Bruto (100%)"),
                    scenario_df[["Tahun", "Status", "PKB Porsi Provinsi"]]
                    .rename(columns={"PKB Porsi Provinsi": "Nilai"})
                    .assign(Komponen="PKB", Skema=f"Provinsi ({ratio_input:.2f}%)"),
                    scenario_df[["Tahun", "Status", "BBNKB Bruto"]]
                    .rename(columns={"BBNKB Bruto": "Nilai"})
                    .assign(Komponen="BBNKB", Skema="Bruto (100%)"),
                    scenario_df[["Tahun", "Status", "BBNKB Porsi Provinsi"]]
                    .rename(columns={"BBNKB Porsi Provinsi": "Nilai"})
                    .assign(Komponen="BBNKB", Skema=f"Provinsi ({ratio_input:.2f}%)"),
                ],
                ignore_index=True,
            )
            fig_compare = px.line(
                compare_df,
                x="Tahun",
                y="Nilai",
                color="Komponen",
                line_dash="Skema",
                markers=True,
                color_discrete_map={"PKB": "#1a5fb4", "BBNKB": "#f59e0b"},
            )
            fig_compare.update_traces(line=dict(width=2.8), marker=dict(size=7))
            apply_plotly_theme(
                fig_compare,
                title="Perbandingan Total Bruto vs Porsi Provinsi",
                height=420,
                xaxis_title="Tahun",
                yaxis_title="Nilai (Rupiah)",
                is_currency=True,
            )
            fig_compare.update_yaxes(rangemode="tozero")
            fig_compare.update_xaxes(dtick=1)
            fig_compare.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_compare, use_container_width=True)

    render_section_divider()

    # --- Tabel Ringkasan Lengkap ---
    create_header_with_icon(
        "Tabel Simulasi Nilai Bruto, Porsi Provinsi & Kab/Kota",
        "📋",
    )
    st.dataframe(
        scenario_df.style.format(
            {
                "PKB Bruto": "Rp {:,.0f}",
                "PKB Porsi Provinsi": "Rp {:,.0f}",
                "PKB Opsen/Kab-Kota": "Rp {:,.0f}",
                "BBNKB Bruto": "Rp {:,.0f}",
                "BBNKB Porsi Provinsi": "Rp {:,.0f}",
                "BBNKB Opsen/Kab-Kota": "Rp {:,.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    app()
