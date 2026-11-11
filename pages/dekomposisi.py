"""
Dekomposisi PAD & Dampak Makroekonomi Page (2025–2026)
Menggabungkan perhitungan potensi teknis objek pajak PKB & BBNKB dengan estimasi dampak makroekonomi.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st

from data_loader import get_bbnkb_inputs, get_pkb_inputs, load_pad_historis, map_inputs
from utils.audit_utils import log_export
from utils.export_utils import create_comprehensive_excel_report
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    create_target_gauge,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact, format_rupiah_full

MACROS = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]


def _get_hist_df(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    return df if df is not None else load_pad_historis()


def predict_macro_linear(var: str, year: int, df: Optional[pd.DataFrame] = None) -> float:
    """Prediksi indikator makro dengan regresi linear sederhana: var ~ Tahun."""
    hist = _get_hist_df(df)
    X = sm.add_constant(hist[["Tahun"]])
    y = hist[var]
    model = sm.OLS(y, X).fit()
    return float(model.predict([1, year])[0])


def coef_vs(response_col: str, var: str, df: Optional[pd.DataFrame] = None) -> float:
    """Koefisien beta dari regresi linear sederhana response_col ~ var."""
    hist = _get_hist_df(df)
    X = sm.add_constant(hist[[var]])
    y = hist[response_col]
    model = sm.OLS(y, X).fit()
    return float(model.params[var])


def compute_macro_impact(
    year: int,
    baseline_macro: dict,
    response_col: str = "PKB",
    df: Optional[pd.DataFrame] = None,
) -> tuple[pd.DataFrame, float, float, dict]:
    """Hitung prediksi makro dan dampak Rupiah terhadap PKB atau BBNKB."""
    hist = _get_hist_df(df)
    rows = []
    total_plus, total_minus = 0.0, 0.0
    pred_macro = {}

    for var in MACROS:
        if var not in hist.columns or var not in baseline_macro:
            continue
        base_val = float(baseline_macro[var])
        pred_val = predict_macro_linear(var, year, df=hist)
        beta = coef_vs(response_col, var, df=hist)
        delta_val = pred_val - base_val
        impact_rp = beta * delta_val

        if impact_rp >= 0:
            total_plus += impact_rp
        else:
            total_minus += impact_rp

        pred_macro[var] = pred_val
        rows.append(
            {
                "Variabel": var,
                "Baseline": base_val,
                f"Prediksi {year}": pred_val,
                "Δ Selisih": delta_val,
                "Dampak (Rp)": impact_rp,
            }
        )

    df_macro = pd.DataFrame(rows)
    return df_macro, total_plus, total_minus, pred_macro


def create_waterfall_chart(df_dekom: pd.DataFrame, title: str) -> go.Figure:
    """Buat Waterfall Chart dekomposisi dengan skala Triliun/Miliar yang akurat & adaptif."""
    labels = df_dekom["Faktor"].tolist()
    values = [float(v) for v in df_dekom["Rupiah"].tolist()]

    measures = []
    text_values = []

    for label, value in zip(labels, values):
        label_upper = label.upper()
        is_total = any(
            kw in label_upper
            for kw in ["TOTAL POTENSI", "TARGET", "SISA", "TOTAL PENAMBAH", "TOTAL PENGURANG", "POTENSI NETO"]
        )
        measures.append("total" if is_total else "relative")
        text_values.append(format_rupiah_compact(value, signed=not is_total))

    fig = go.Figure(
        go.Waterfall(
            name="Dekomposisi",
            orientation="v",
            measure=measures,
            x=labels,
            textposition="outside",
            text=text_values,
            y=values,
            cliponaxis=False,
            connector={"line": {"color": "rgba(148, 163, 184, 0.65)", "width": 1.8}},
            decreasing={"marker": {"color": "#ef4444", "line": {"color": "#b91c1c", "width": 1}}},
            increasing={"marker": {"color": "#10b981", "line": {"color": "#047857", "width": 1}}},
            totals={"marker": {"color": "#1a5fb4", "line": {"color": "#0f3d7a", "width": 1}}},
            hovertemplate="<b>%{x}</b><br>Nilai: Rp %{y:,.0f}<extra></extra>",
        )
    )

    apply_plotly_theme(
        fig,
        title=title,
        height=500,
        xaxis_title="Komponen Dekomposisi",
        yaxis_title="Nilai (Rupiah)",
        is_currency=True,
        show_legend=False,
        margin=dict(l=72, r=40, t=78, b=145),
    )
    fig.update_xaxes(tickangle=-32, tickfont=dict(size=10))
    return fig


def rupiah_style(df: pd.DataFrame, colmap: dict):
    """Terapkan pemformatan per kolom yang tersedia pada DataFrame."""
    valid_map = {k: v for k, v in colmap.items() if k in df.columns}
    return df.style.format(valid_map)


def dekomposisi_pkb_with_macro(
    year: int,
    inputs_df: pd.DataFrame,
    baseline_macro: dict,
    df: Optional[pd.DataFrame] = None,
) -> tuple[pd.DataFrame, float, pd.DataFrame, dict]:
    """Bangun tabel dekomposisi PKB lengkap beserta dampak makroekonomi."""
    hist = _get_hist_df(df)
    values = map_inputs(inputs_df)
    total_penambah = float(inputs_df[inputs_df["kategori"] == "penambah"]["nilai"].sum())
    total_pengurang = float(inputs_df[inputs_df["kategori"] == "pengurang"]["nilai"].sum())

    df_macro, dampak_plus, dampak_minus, pred_macro = compute_macro_impact(
        year, baseline_macro, response_col="PKB", df=hist
    )
    total_potensi = total_penambah - total_pengurang + dampak_plus + dampak_minus
    target_val = float(values.get("Target", 0.0))

    faktor = [
        "Potensi Awal Tahun",
        "RODA 4 (Jan-Des)",
        "RODA 2 (Jan-Des)",
        "Prediksi Pencairan Tunggakan",
        "Prediksi Mutasi Masuk (Jan-Des)",
        "TOTAL PENAMBAH",
        "Proyeksi Tidak Daftar Ulang (Jan-Des)",
        "Proyeksi Mutasi Keluar (Jan-Des)",
        "Potensi Pembebasan Pajak Daerah",
        "TOTAL PENGURANG",
        "Dampak Makro (+)",
        "Dampak Makro (-)",
        f"TOTAL POTENSI PKB TAHUN {year}",
        f"TARGET R-APBD {year}",
        "SISA POTENSI",
    ]

    rupiah = [
        float(values.get("Potensi Awal", 0.0)),
        float(values.get("R4", 0.0)),
        float(values.get("R2", 0.0)),
        float(values.get("Tunggakan", 0.0)),
        float(values.get("Mutasi Masuk", 0.0)),
        total_penambah,
        -float(values.get("TDR", 0.0)),
        -float(values.get("Mutasi Keluar", 0.0)),
        -float(values.get("Pembebasan", 0.0)),
        -total_pengurang,
        dampak_plus,
        dampak_minus,
        total_potensi,
        target_val,
        total_potensi - target_val,
    ]

    df_dekom = pd.DataFrame({"Faktor": faktor, "Rupiah": rupiah})
    return df_dekom, total_potensi, df_macro, pred_macro


def dekomposisi_bbnkb_table(
    year: int,
    inputs_df: pd.DataFrame,
    macro_plus: float = 0.0,
    macro_minus: float = 0.0,
) -> pd.DataFrame:
    """Bangun tabel dekomposisi BBNKB termasuk dampak makroekonomi."""
    values = map_inputs(inputs_df)

    if year == 2025:
        total_struktural = float(values.get("Total", 0.0))
        target = float(values.get("Target", 0.0))
        total_potensi = total_struktural + macro_plus + macro_minus

        faktor = [
            "RODA 4 (Jan-Des)",
            "RODA 2 (Jan-Des)",
            "TOTAL POTENSI BBN I TAHUN 2025",
            "Dampak Makro (+)",
            "Dampak Makro (-)",
            "TOTAL POTENSI BBNKB TAHUN 2025",
            "TARGET R-APBD 2025",
            "SISA POTENSI",
        ]
        rupiah = [
            float(values.get("R4", 0.0)),
            float(values.get("R2", 0.0)),
            total_struktural,
            macro_plus,
            macro_minus,
            total_potensi,
            target,
            total_potensi - target,
        ]
    else:
        total = float(values.get("Total", 0.0))
        pengurang = float(values.get("Pengurang", 0.0))
        target = float(values.get("Target", 0.0))
        neto = total - pengurang
        total_potensi = neto + macro_plus + macro_minus

        faktor = [
            "Roda 4 (Jan-Des 2026)",
            "Roda 2 (Jan-Des 2026)",
            "Total Potensi Kendaraan Baru Tahun 2026",
            "Potensi BBN II Tidak Dipungut",
            "Potensi Neto Setelah Pengurang",
            "Dampak Makro (+)",
            "Dampak Makro (-)",
            "Total Potensi BBNKB Tahun 2026",
            "Target BBNKB pada R-APBD 2026",
            "Sisa Potensi",
        ]
        rupiah = [
            float(values.get("R4", 0.0)),
            float(values.get("R2", 0.0)),
            total,
            -pengurang,
            neto,
            macro_plus,
            macro_minus,
            total_potensi,
            target,
            total_potensi - target,
        ]

    return pd.DataFrame({"Faktor": faktor, "Rupiah": rupiah})


def _render_target_status(potensi: float, target: float) -> None:
    pct = (potensi / target * 100) if target > 0 else 0.0
    gap = potensi - target
    if pct >= 100:
        st.success(
            f"✅ Capaian Potensi **{pct:.1f}%** dari Target (Surplus **{format_rupiah_compact(gap, signed=True)}**)"
        )
    elif pct >= 92:
        st.info(
            f"💡 Capaian Potensi **{pct:.1f}%** mendekati Target (Selisih **{format_rupiah_compact(gap, signed=True)}**)"
        )
    else:
        st.warning(
            f"⚠️ Capaian Potensi **{pct:.1f}%** di bawah Target (Defisit **{format_rupiah_compact(gap, signed=True)}**)"
        )


def show_decomposition_tab() -> None:
    df_hist = load_pad_historis()

    render_page_header(
        title="Dekomposisi PAD & Dampak Makro (2025–2026)",
        subtitle="Integrasi komponen potensi teknis objek pajak (Roda 4, Roda 2, Tunggakan, Mutasi) dengan dampak variabel makroekonomi",
        icon="⚖️",
    )

    pkb_inputs_2025 = get_pkb_inputs(2025)
    pkb_inputs_2026 = get_pkb_inputs(2026)
    bbn_inputs_2025 = get_bbnkb_inputs(2025)
    bbn_inputs_2026 = get_bbnkb_inputs(2026)

    baseline_2024 = {v: float(df_hist.iloc[-1][v]) for v in MACROS if v in df_hist.columns}
    df_pkb25, total_pkb25, df_macro_pkb25, pred_macro25 = dekomposisi_pkb_with_macro(
        2025, pkb_inputs_2025, baseline_2024, df=df_hist
    )

    baseline_2025_for_2026 = {k: float(v) for k, v in pred_macro25.items()}
    df_pkb26, total_pkb26, df_macro_pkb26, _ = dekomposisi_pkb_with_macro(
        2026, pkb_inputs_2026, baseline_2025_for_2026, df=df_hist
    )

    df_macro_bbn25, bbn_macro_plus25, bbn_macro_minus25, _ = compute_macro_impact(
        2025, baseline_2024, response_col="BBNKB", df=df_hist
    )
    df_macro_bbn26, bbn_macro_plus26, bbn_macro_minus26, _ = compute_macro_impact(
        2026, baseline_2025_for_2026, response_col="BBNKB", df=df_hist
    )

    bbn_vals_2025 = map_inputs(bbn_inputs_2025)
    bbn_vals_2026 = map_inputs(bbn_inputs_2026)
    bbn_total_2025 = float(bbn_vals_2025.get("Total", 0.0)) + bbn_macro_plus25 + bbn_macro_minus25
    bbn_net_2026 = float(bbn_vals_2026.get("Total", 0.0)) - float(bbn_vals_2026.get("Pengurang", 0.0))
    bbn_total_2026 = bbn_net_2026 + bbn_macro_plus26 + bbn_macro_minus26

    pkb_target_2025 = float(map_inputs(pkb_inputs_2025).get("Target", 0.0))
    pkb_target_2026 = float(map_inputs(pkb_inputs_2026).get("Target", 0.0))
    bbn_target_2025 = float(bbn_vals_2025.get("Target", 0.0))
    bbn_target_2026 = float(bbn_vals_2026.get("Target", 0.0))

    df_bbn25 = dekomposisi_bbnkb_table(2025, bbn_inputs_2025, bbn_macro_plus25, bbn_macro_minus25)
    df_bbn26 = dekomposisi_bbnkb_table(2026, bbn_inputs_2026, bbn_macro_plus26, bbn_macro_minus26)

    # --- KPI Ringkasan 4 Komponen ---
    create_header_with_icon(
        "Ringkasan Potensi vs Target R-APBD",
        "📌",
        subtitle="Perbandingan total potensi hasil dekomposisi terhadap target R-APBD Tahun 2025 dan 2026",
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        gap = total_pkb25 - pkb_target_2025
        render_kpi_card(
            label="Potensi PKB 2025",
            value=format_rupiah_compact(total_pkb25, respect_privacy=True),
            delta=f"{format_rupiah_compact(gap, signed=True)} vs Target",
            delta_positive=gap >= 0,
            subtitle=f"Target: {format_rupiah_compact(pkb_target_2025)}",
            icon="🚗",
            variant="primary",
        )
    with k2:
        gap = bbn_total_2025 - bbn_target_2025
        render_kpi_card(
            label="Potensi BBNKB 2025",
            value=format_rupiah_compact(bbn_total_2025, respect_privacy=True),
            delta=f"{format_rupiah_compact(gap, signed=True)} vs Target",
            delta_positive=gap >= 0,
            subtitle=f"Target: {format_rupiah_compact(bbn_target_2025)}",
            icon="📝",
            variant="warning",
        )
    with k3:
        gap = total_pkb26 - pkb_target_2026
        render_kpi_card(
            label="Potensi PKB 2026",
            value=format_rupiah_compact(total_pkb26, respect_privacy=True),
            delta=f"{format_rupiah_compact(gap, signed=True)} vs Target",
            delta_positive=gap >= 0,
            subtitle=f"Target: {format_rupiah_compact(pkb_target_2026)}",
            icon="🚗",
            variant="success",
        )
    with k4:
        gap = bbn_total_2026 - bbn_target_2026
        render_kpi_card(
            label="Potensi BBNKB 2026",
            value=format_rupiah_compact(bbn_total_2026, respect_privacy=True),
            delta=f"{format_rupiah_compact(gap, signed=True)} vs Target",
            delta_positive=gap >= 0,
            subtitle=f"Target: {format_rupiah_compact(bbn_target_2026)}",
            icon="📝",
            variant="indigo",
        )

    ringkas = pd.DataFrame(
        {
            "Tahun": [2025, 2025, 2026, 2026],
            "Jenis Pajak": ["PKB", "BBNKB", "PKB", "BBNKB"],
            "Total Potensi": [total_pkb25, bbn_total_2025, total_pkb26, bbn_total_2026],
            "Target R-APBD": [pkb_target_2025, bbn_target_2025, pkb_target_2026, bbn_target_2026],
        }
    )
    ringkas["Sisa Potensi (Surplus/Defisit)"] = ringkas["Total Potensi"] - ringkas["Target R-APBD"]
    ringkas["Capaian (%)"] = (ringkas["Total Potensi"] / ringkas["Target R-APBD"]) * 100

    st.dataframe(
        rupiah_style(
            ringkas,
            {
                "Total Potensi": "Rp {:,.0f}",
                "Target R-APBD": "Rp {:,.0f}",
                "Sisa Potensi (Surplus/Defisit)": "Rp {:+,.0f}",
                "Capaian (%)": "{:.2f}%",
            },
        ),
        use_container_width=True,
        hide_index=True,
    )

    render_section_divider()

    # --- Gauge Pencapaian Target ---
    create_header_with_icon(
        "Indikator Ketercapaian Target (Gauge)",
        "🎯",
        subtitle="Visualisasi posisi potensi terhadap ambang batas target R-APBD dalam satuan Triliun Rupiah",
    )

    g_col1, g_col2 = st.columns(2)
    with g_col1:
        with st.container(border=True):
            st.plotly_chart(
                create_target_gauge(total_pkb25, pkb_target_2025, "PKB Tahun 2025", bar_color="#1a5fb4"),
                use_container_width=True,
            )
            _render_target_status(total_pkb25, pkb_target_2025)
    with g_col2:
        with st.container(border=True):
            st.plotly_chart(
                create_target_gauge(bbn_total_2025, bbn_target_2025, "BBNKB Tahun 2025", bar_color="#10b981"),
                use_container_width=True,
            )
            _render_target_status(bbn_total_2025, bbn_target_2025)

    g_col3, g_col4 = st.columns(2)
    with g_col3:
        with st.container(border=True):
            st.plotly_chart(
                create_target_gauge(total_pkb26, pkb_target_2026, "PKB Tahun 2026", bar_color="#1a5fb4"),
                use_container_width=True,
            )
            _render_target_status(total_pkb26, pkb_target_2026)
    with g_col4:
        with st.container(border=True):
            st.plotly_chart(
                create_target_gauge(bbn_total_2026, bbn_target_2026, "BBNKB Tahun 2026", bar_color="#10b981"),
                use_container_width=True,
            )
            _render_target_status(bbn_total_2026, bbn_target_2026)

    render_section_divider()

    # --- Detail Tahun 2025 & 2026 dalam Tabs ---
    create_header_with_icon(
        "Rincian Komponen Dekomposisi & Waterfall per Tahun",
        "📊",
        subtitle="Pilih tab tahun untuk meninjau rincian penambah, pengurang, waterfall chart, serta kontribusi tiap variabel makro",
    )

    tab_2025, tab_2026 = st.tabs(["📅 Detail Tahun 2025", "📅 Detail Tahun 2026"])

    with tab_2025:
        st.markdown("#### A. Dekomposisi PKB Tahun 2025")
        st.dataframe(rupiah_style(df_pkb25, {"Rupiah": "Rp {:,.0f}"}), use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.plotly_chart(
                create_waterfall_chart(df_pkb25, "Waterfall Dekomposisi PKB Tahun 2025"),
                use_container_width=True,
            )
            st.caption("🟢 Hijau = Penambah | 🔴 Merah = Pengurang | 🔵 Biru = Komponen Akumulasi / Total")

        st.markdown("#### B. Prediksi Indikator Makro & Dampak ke PKB (2025)")
        st.caption("Baseline menggunakan realisasi aktual 2024; prediksi 2025 dihitung melalui tren linear historis.")
        st.dataframe(
            rupiah_style(
                df_macro_pkb25.rename(columns={"Baseline": "Baseline 2024"}),
                {
                    "Baseline 2024": "{:,.2f}",
                    "Prediksi 2025": "{:,.2f}",
                    "Δ Selisih": "{:+,.2f}",
                    "Dampak (Rp)": "Rp {:+,.0f}",
                },
            ),
            use_container_width=True,
            hide_index=True,
        )

        render_section_divider()

        st.markdown("#### C. Dekomposisi BBNKB Tahun 2025")
        st.dataframe(rupiah_style(df_bbn25, {"Rupiah": "Rp {:,.0f}"}), use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.plotly_chart(
                create_waterfall_chart(df_bbn25, "Waterfall Dekomposisi BBNKB Tahun 2025"),
                use_container_width=True,
            )
            st.caption("🟢 Hijau = Penambah | 🔴 Merah = Pengurang | 🔵 Biru = Komponen Akumulasi / Total")

        st.markdown("#### D. Prediksi Indikator Makro & Dampak ke BBNKB (2025)")
        st.dataframe(
            rupiah_style(
                df_macro_bbn25.rename(columns={"Baseline": "Baseline 2024"}),
                {
                    "Baseline 2024": "{:,.2f}",
                    "Prediksi 2025": "{:,.2f}",
                    "Δ Selisih": "{:+,.2f}",
                    "Dampak (Rp)": "Rp {:+,.0f}",
                },
            ),
            use_container_width=True,
            hide_index=True,
        )
        net_bbn25 = bbn_macro_plus25 + bbn_macro_minus25
        st.info(
            f"💡 **Dampak Makro Bersih ke BBNKB 2025**: **{format_rupiah_compact(net_bbn25, signed=True)}** ({format_rupiah_full(net_bbn25, signed=True)})"
        )

    with tab_2026:
        st.markdown("#### A. Dekomposisi PKB Tahun 2026")
        st.dataframe(rupiah_style(df_pkb26, {"Rupiah": "Rp {:,.0f}"}), use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.plotly_chart(
                create_waterfall_chart(df_pkb26, "Waterfall Dekomposisi PKB Tahun 2026"),
                use_container_width=True,
            )
            st.caption("🟢 Hijau = Penambah | 🔴 Merah = Pengurang | 🔵 Biru = Komponen Akumulasi / Total")

        st.markdown("#### B. Prediksi Indikator Makro & Dampak ke PKB (2026)")
        st.caption("Baseline 2026 menggunakan nilai proyeksi makro tahun 2025.")
        st.dataframe(
            rupiah_style(
                df_macro_pkb26.rename(columns={"Baseline": "Baseline 2025"}),
                {
                    "Baseline 2025": "{:,.2f}",
                    "Prediksi 2026": "{:,.2f}",
                    "Δ Selisih": "{:+,.2f}",
                    "Dampak (Rp)": "Rp {:+,.0f}",
                },
            ),
            use_container_width=True,
            hide_index=True,
        )

        render_section_divider()

        st.markdown("#### C. Dekomposisi BBNKB Tahun 2026")
        st.dataframe(rupiah_style(df_bbn26, {"Rupiah": "Rp {:,.0f}"}), use_container_width=True, hide_index=True)

        with st.container(border=True):
            st.plotly_chart(
                create_waterfall_chart(df_bbn26, "Waterfall Dekomposisi BBNKB Tahun 2026"),
                use_container_width=True,
            )
            st.caption("🟢 Hijau = Penambah | 🔴 Merah = Pengurang | 🔵 Biru = Komponen Akumulasi / Total")

        st.markdown("#### D. Prediksi Indikator Makro & Dampak ke BBNKB (2026)")
        st.dataframe(
            rupiah_style(
                df_macro_bbn26.rename(columns={"Baseline": "Baseline 2025"}),
                {
                    "Baseline 2025": "{:,.2f}",
                    "Prediksi 2026": "{:,.2f}",
                    "Δ Selisih": "{:+,.2f}",
                    "Dampak (Rp)": "Rp {:+,.0f}",
                },
            ),
            use_container_width=True,
            hide_index=True,
        )
        net_bbn26 = bbn_macro_plus26 + bbn_macro_minus26
        st.info(
            f"💡 **Dampak Makro Bersih ke BBNKB 2026**: **{format_rupiah_compact(net_bbn26, signed=True)}** ({format_rupiah_full(net_bbn26, signed=True)})"
        )

    render_section_divider()

    # --- Ekspor Laporan Excel Komprehensif ---
    create_header_with_icon(
        "Unduh Laporan Komprehensif (Excel Multi-Sheet)",
        "📥",
        subtitle="Mencakup metadata eksekutif, metodologi, data historis, rincian dekomposisi 2025–2026, serta glosarium teknis",
    )

    df_proyeksi_summary = pd.DataFrame(
        {
            "Tahun": [2025, 2026],
            "PKB Proyeksi": [total_pkb25, total_pkb26],
            "BBNKB Proyeksi": [bbn_total_2025, bbn_total_2026],
            "PKB Target": [pkb_target_2025, pkb_target_2026],
            "BBNKB Target": [bbn_target_2025, bbn_target_2026],
        }
    )

    with st.container(border=True):
        try:
            excel_bytes = create_comprehensive_excel_report(
                df_historis=df_hist,
                df_proyeksi=df_proyeksi_summary,
                df_pkb_2025=df_pkb25,
                df_pkb_2026=df_pkb26,
                df_bbnkb_2025=df_bbn25,
                df_bbnkb_2026=df_bbn26,
                model_metrics={
                    "Total Proyeksi PKB 2025": format_rupiah_full(total_pkb25),
                    "Total Proyeksi PKB 2026": format_rupiah_full(total_pkb26),
                    "Total Proyeksi BBNKB 2025": format_rupiah_full(bbn_total_2025),
                    "Total Proyeksi BBNKB 2026": format_rupiah_full(bbn_total_2026),
                    "Cakupan Historis": f"{len(df_hist)} tahun ({int(df_hist['Tahun'].min())}–{int(df_hist['Tahun'].max())})",
                    "Metodologi": "Dekomposisi Objek Pajak + Regresi Linear Dampak Makro",
                },
            )
            filename = f"PRO_PAD_Comprehensive_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"

            def _record_excel_export() -> None:
                log_export(
                    export_type="Excel Report",
                    filename=filename,
                    details={
                        "total_pkb_2025": float(total_pkb25),
                        "total_pkb_2026": float(total_pkb26),
                        "total_bbnkb_2025": float(bbn_total_2025),
                        "total_bbnkb_2026": float(bbn_total_2026),
                        "file_size_bytes": len(excel_bytes),
                    },
                )

            col_dl1, col_dl2 = st.columns([2, 1])
            with col_dl1:
                st.markdown(
                    "**Isi Workbook Excel (.xlsx):**\n"
                    "- `Metadata & Info` • `Methodology` • `Historical Data` • `Projections 2025-2026`\n"
                    "- `PKB 2025` • `PKB 2026` • `BBNKB 2025` • `BBNKB 2026` • `Glossary`"
                )
            with col_dl2:
                st.download_button(
                    label="📥 Unduh Laporan Excel (.xlsx)",
                    data=excel_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    on_click=_record_excel_export,
                    type="primary",
                    use_container_width=True,
                )
        except Exception as e:
            st.error(f"❌ Gagal menyiapkan berkas laporan Excel: {e}")


def app() -> None:
    show_decomposition_tab()


if __name__ == "__main__":
    app()
