import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import (
    load_pad_historis,
    get_pkb_inputs,
    get_bbnkb_inputs,
    map_inputs,
)
from pages import dekomposisi as dekom

DEFAULT_RATIO = 0.6024


def local_css():
    st.markdown(
        """
        <style>
            .hkpd-header {
                background: linear-gradient(90deg, #1a5fb4, #3584e4);
                padding: 18px;
                border-radius: 12px;
                margin-bottom: 25px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            }
            .hkpd-header h1 {
                color: #ffffff;
                margin: 0;
                font-size: 2.2rem;
                font-weight: 700;
            }
            .hkpd-header p {
                color: #f1f1f1;
                margin: 0;
                font-size: 1.05rem;
            }
            .section-title {
                font-size: 1.35rem;
                font-weight: 700;
                color: #1e3c72;
                margin: 32px 0 16px;
                border-left: 5px solid #ffd700;
                padding-left: 12px;
            }
            .hkpd-divider {
                margin: 24px 0;
                border: none;
                border-top: 1px solid rgba(30, 60, 114, 0.15);
            }
            div[data-testid="metric-container"] {
                background: linear-gradient(135deg, #f0f6ff, #dce9ff);
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                padding: 16px;
            }
            div[data-testid="metric-container"] label {
                color: #1e3c72;
                font-weight: 600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(text: str) -> None:
    st.markdown(f"<div class='section-title'>{text}</div>", unsafe_allow_html=True)


def render_divider() -> None:
    st.markdown("<hr class='hkpd-divider'>", unsafe_allow_html=True)


def format_rupiah(value: float) -> str:
    prefix = "-" if value < 0 else ""
    return f"{prefix}Rp{abs(value):,.0f}".replace(",", ".")


def compute_future_totals():
    hist = load_pad_historis()

    pkb_inputs_2025 = get_pkb_inputs(2025)
    baseline_2024 = {var: float(hist.iloc[-1][var]) for var in dekom.MACROS}
    _, total_pkb25, _, pred_macro25 = dekom.dekomposisi_pkb_with_macro(2025, pkb_inputs_2025, baseline_2024)

    baseline_2025 = {k: float(v) for k, v in pred_macro25.items()}
    pkb_inputs_2026 = get_pkb_inputs(2026)
    _, total_pkb26, _, _ = dekom.dekomposisi_pkb_with_macro(2026, pkb_inputs_2026, baseline_2025)

    bbn_inputs_2025 = get_bbnkb_inputs(2025)
    bbn_inputs_2026 = get_bbnkb_inputs(2026)

    df_macro_bbn25, bbn_plus25, bbn_minus25, _ = dekom.compute_macro_impact(2025, baseline_2024, response_col="BBNKB")
    df_macro_bbn26, bbn_plus26, bbn_minus26, _ = dekom.compute_macro_impact(2026, baseline_2025, response_col="BBNKB")

    bbn_vals_2025 = map_inputs(bbn_inputs_2025)
    bbn_total_2025 = bbn_vals_2025.get("Total", 0.0) + bbn_plus25 + bbn_minus25

    bbn_vals_2026 = map_inputs(bbn_inputs_2026)
    bbn_net_2026 = bbn_vals_2026.get("Total", 0.0) - bbn_vals_2026.get("Pengurang", 0.0)
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
                "PKB": float(row.PKB),
                "BBNKB": float(row.BBNKB),
            }
        )

    for year, pkb_val, bbn_val in [(2025, pkb2025, bbn2025), (2026, pkb2026, bbn2026)]:
        records.append(
            {
                "Tahun": year,
                "Status": "Proyeksi",
                "PKB": float(pkb_val),
                "BBNKB": float(bbn_val),
            }
        )

    df = pd.DataFrame(records)
    df["PKB Skenario"] = df["PKB"] * factor
    df["BBNKB Skenario"] = df["BBNKB"] * factor
    return df


def app():
    local_css()
    st.markdown(
        """
        <div class="hkpd-header">
            <h1>📘 Implementasi Skenario HKPD</h1>
            <p>⚖️ Menyajikan PKB dan BBNKB yang disesuaikan dengan faktor HKPD untuk periode 2018-2026.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Inisialisasi nilai awal di session_state (sekali saja)
    if "ratio_value" not in st.session_state:
        st.session_state.ratio_value = DEFAULT_RATIO * 100


    # Callback untuk slider
    def update_from_slider():
        st.session_state.ratio_value = st.session_state.ratio_slider


    # Callback untuk number_input
    def update_from_number():
        st.session_state.ratio_value = st.session_state.ratio_number


    col1, col2 = st.columns([3, 1])

    with col1:
        st.slider(
            "Porsi HKPD (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            key="ratio_slider",
            value=st.session_state.ratio_value,
            on_change=update_from_slider,
        )

    with col2:
        st.number_input(
            " ",
            min_value=0.0,
            max_value=100.0,
            step=0.01,
            format="%.2f",
            key="ratio_number",
            value=st.session_state.ratio_value,
            on_change=update_from_number,
        )

    # Ambil nilai sinkron
    ratio_input = st.session_state.ratio_value
    factor = ratio_input / 100.0

    st.caption("Faktor HKPD yang digunakan dapat disesuaikan.")

    hist, pkb25, pkb26, bbn25, bbn26 = compute_future_totals()
    scenario_df = build_hkpd_series(hist, pkb25, pkb26, bbn25, bbn26, factor)

    latest = scenario_df[scenario_df["Tahun"] == 2026].iloc[0]
    prev = scenario_df[scenario_df["Tahun"] == 2025].iloc[0]

    col1, col2 = st.columns(2)
    col1.metric(
        "PKB 2026 (skenario)",
        format_rupiah(latest["PKB Skenario"]),
        delta=f"{format_rupiah(latest['PKB Skenario'] - prev['PKB Skenario'])} vs 2025",
    )
    col2.metric(
        "BBNKB 2026 (skenario)",
        format_rupiah(latest["BBNKB Skenario"]),
        delta=f"{format_rupiah(latest['BBNKB Skenario'] - prev['BBNKB Skenario'])} vs 2025",
    )

    render_divider()
    render_section_title("Ringkasan Nilai PKB & BBNKB")

    summary_df = scenario_df[[
        "Tahun",
        "Status",
        "PKB",
        "PKB Skenario",
        "BBNKB",
        "BBNKB Skenario",
    ]]
    st.dataframe(
        summary_df.style.format(
            {
                "PKB": "Rp{:,.0f}",
                "PKB Skenario": "Rp{:,.0f}",
                "BBNKB": "Rp{:,.0f}",
                "BBNKB Skenario": "Rp{:,.0f}",
            }
        ),
        use_container_width=True,
    )

    render_divider()
    render_section_title("Visualisasi Skenario HKPD")

    chart_df = scenario_df.melt(
        id_vars=["Tahun", "Status"],
        value_vars=["PKB Skenario", "BBNKB Skenario"],
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
        template="plotly_white",
        labels={"Nilai": "Skenario (Rp)"},
        title="Tren PKB & BBNKB Skenario HKPD",
    )
    fig.update_yaxes(rangemode='tozero')
    st.plotly_chart(fig, use_container_width=True)

    render_divider()
    render_section_title("Perbandingan Aktual vs Skenario")

    compare_df = pd.concat(
        [
            scenario_df[["Tahun", "Status", "PKB"]]
            .rename(columns={"PKB": "Nilai"})
            .assign(Komponen="PKB", Jenis="Aktual"),
            scenario_df[["Tahun", "Status", "PKB Skenario"]]
            .rename(columns={"PKB Skenario": "Nilai"})
            .assign(Komponen="PKB", Jenis="Skenario"),
            scenario_df[["Tahun", "Status", "BBNKB"]]
            .rename(columns={"BBNKB": "Nilai"})
            .assign(Komponen="BBNKB", Jenis="Aktual"),
            scenario_df[["Tahun", "Status", "BBNKB Skenario"]]
            .rename(columns={"BBNKB Skenario": "Nilai"})
            .assign(Komponen="BBNKB", Jenis="Skenario"),
        ],
        ignore_index=True,
    )

    fig_compare = px.line(
        compare_df,
        x="Tahun",
        y="Nilai",
        color="Komponen",
        line_dash="Jenis",
        markers=True,
        category_orders={"Status": ["Aktual", "Proyeksi"], "Jenis": ["Aktual", "Skenario"]},
        template="plotly_white",
        labels={"Nilai": "Nilai (Rp)"},
        title="Aktual vs Skenario HKPD",
    )
    fig_compare.update_yaxes(rangemode='tozero')
    st.plotly_chart(fig_compare, use_container_width=True)


if __name__ == "__main__":
    app()
