"""
Insight Terpadu PAD 2018–2026 Page
Menyatukan tren historis, dinamika makroekonomi, pemodelan regresi, dan dekomposisi potensi.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st

from data_loader import get_bbnkb_inputs, get_pkb_inputs, load_pad_historis, map_inputs
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact

MACROS = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]


def build_macro_models(hist: pd.DataFrame):
    X_year = sm.add_constant(hist["Tahun"])
    trend_params = {}
    beta_coeffs = {"PKB": {}, "BBNKB": {}}
    for var in MACROS:
        if var not in hist.columns:
            continue
        trend_model = sm.OLS(hist[var], X_year).fit()
        trend_params[var] = {
            "const": float(trend_model.params["const"]),
            "tahun": float(trend_model.params["Tahun"]),
        }
        for response_col in ("PKB", "BBNKB"):
            beta_model = sm.OLS(hist[response_col], sm.add_constant(hist[[var]])).fit()
            beta_coeffs[response_col][var] = float(beta_model.params[var])
    return trend_params, beta_coeffs


def compute_macro_effects(
    year: int,
    baseline: dict,
    trend_params: dict,
    beta_coeffs: dict,
    response: str = "PKB",
):
    rows = []
    total_plus = 0.0
    total_minus = 0.0
    predictions = {}

    beta_map = beta_coeffs.get(response, beta_coeffs) if isinstance(beta_coeffs, dict) else {}

    for var, params in trend_params.items():
        predicted = params["const"] + params["tahun"] * year
        delta = predicted - baseline[var]
        impact = beta_map.get(var, 0.0) * delta
        predictions[var] = predicted

        if impact >= 0:
            total_plus += impact
        else:
            total_minus += impact

        rows.append(
            {
                "Variabel": var,
                "Baseline": baseline[var],
                f"Prediksi {year}": predicted,
                "Selisih": delta,
                "Dampak (Rp)": impact,
            }
        )

    return pd.DataFrame(rows), total_plus, total_minus, predictions


def compute_pkb_summary(hist: pd.DataFrame, trend_params: dict, beta_coeffs: dict, year: int, baseline: dict):
    inputs = get_pkb_inputs(year)
    values = map_inputs(inputs)

    penambah = float(inputs.loc[inputs["kategori"] == "penambah", "nilai"].sum())
    pengurang = float(inputs.loc[inputs["kategori"] == "pengurang", "nilai"].sum())

    macro_df, macro_plus, macro_minus, predicted_macro = compute_macro_effects(
        year, baseline, trend_params, beta_coeffs, response="PKB"
    )
    total = penambah - pengurang + macro_plus + macro_minus

    return {
        "inputs": inputs,
        "values": values,
        "penambah": penambah,
        "pengurang": pengurang,
        "macro_plus": macro_plus,
        "macro_minus": macro_minus,
        "macro_df": macro_df,
        "predicted_macro": predicted_macro,
        "total": total,
        "target": float(values.get("Target", 0.0)),
    }


def compute_bbnkb_summary(
    hist: pd.DataFrame,
    trend_params: dict,
    beta_coeffs: dict,
    year: int,
    baseline: dict,
):
    inputs = get_bbnkb_inputs(year)
    values = map_inputs(inputs)

    structural_total = float(values.get("Total", 0.0))
    pengurang = float(inputs.loc[inputs["kategori"] == "pengurang", "nilai"].sum())

    macro_df, macro_plus, macro_minus, predicted_macro = compute_macro_effects(
        year, baseline, trend_params, beta_coeffs, response="BBNKB"
    )

    net_structural = structural_total - pengurang
    total = net_structural + macro_plus + macro_minus

    return {
        "inputs": inputs,
        "values": values,
        "structural_total": structural_total,
        "pengurang": pengurang,
        "macro_plus": macro_plus,
        "macro_minus": macro_minus,
        "macro_df": macro_df,
        "predicted_macro": predicted_macro,
        "neto": net_structural,
        "total": total,
        "target": float(values.get("Target", 0.0)),
    }


def build_combined_time_series(hist: pd.DataFrame, pkb25: dict, pkb26: dict, bbn25: dict, bbn26: dict) -> pd.DataFrame:
    actual = hist[["Tahun", "PKB", "BBNKB"]].melt("Tahun", var_name="Jenis", value_name="Nilai")
    actual["Status"] = "Aktual"

    projections = pd.DataFrame(
        [
            {"Tahun": 2025, "Jenis": "PKB", "Nilai": pkb25["total"], "Status": "Proyeksi"},
            {"Tahun": 2026, "Jenis": "PKB", "Nilai": pkb26["total"], "Status": "Proyeksi"},
            {"Tahun": 2025, "Jenis": "BBNKB", "Nilai": bbn25["total"], "Status": "Proyeksi"},
            {"Tahun": 2026, "Jenis": "BBNKB", "Nilai": bbn26["total"], "Status": "Proyeksi"},
        ]
    )

    last_year = int(hist["Tahun"].max())
    last_row = hist.loc[hist["Tahun"] == last_year]
    if not last_row.empty:
        bridge_rows = [
            {
                "Tahun": last_year,
                "Jenis": jenis,
                "Nilai": float(last_row[jenis].iloc[0]),
                "Status": "Proyeksi",
            }
            for jenis in ["PKB", "BBNKB"]
        ]
        projections = pd.concat([pd.DataFrame(bridge_rows), projections], ignore_index=True)

    combined = pd.concat([actual, projections], ignore_index=True)
    return combined.sort_values(["Jenis", "Tahun", "Status"]).reset_index(drop=True)


def build_macro_series(hist: pd.DataFrame, pkb25: dict, pkb26: dict, active_macros: list[str]) -> pd.DataFrame:
    base = hist[["Tahun"] + active_macros].copy()
    future_rows = []
    for year, pred in [(2025, pkb25["predicted_macro"]), (2026, pkb26["predicted_macro"])]:
        row = {"Tahun": year}
        row.update({var: float(pred[var]) for var in active_macros})
        future_rows.append(row)

    combined = pd.concat([base, pd.DataFrame(future_rows)], ignore_index=True)
    last_hist_year = int(hist["Tahun"].max())
    combined["Status"] = combined["Tahun"].apply(lambda x: "Aktual" if x <= last_hist_year else "Proyeksi")
    return combined.melt(id_vars=["Tahun", "Status"], var_name="Variabel", value_name="Nilai")


def build_pkb_contribution(pkb25: dict, pkb26: dict) -> pd.DataFrame:
    rows = []
    for year, data in [(2025, pkb25), (2026, pkb26)]:
        rows.extend(
            [
                {"Tahun": str(year), "Kategori": "Total Penambah", "Nilai": data["penambah"]},
                {"Tahun": str(year), "Kategori": "Total Pengurang", "Nilai": -data["pengurang"]},
                {"Tahun": str(year), "Kategori": "Dampak Makro (+)", "Nilai": data["macro_plus"]},
                {"Tahun": str(year), "Kategori": "Dampak Makro (-)", "Nilai": data["macro_minus"]},
            ]
        )
    return pd.DataFrame(rows)


def app() -> None:
    render_page_header(
        title="Insight Terpadu PAD (2018–2026)",
        subtitle="Sintesis eksekutif yang menyatukan realisasi historis, dinamika makroekonomi, pemodelan regresi, dan dekomposisi potensi",
        icon="🧭",
    )

    hist = load_pad_historis()
    active_macros = [m for m in MACROS if m in hist.columns]
    trend_params, beta_coeffs = build_macro_models(hist)

    baseline_2024 = {var: float(hist.iloc[-1][var]) for var in active_macros}
    pkb25 = compute_pkb_summary(hist, trend_params, beta_coeffs, 2025, baseline_2024)
    baseline_pkb_2026 = {var: float(pkb25["predicted_macro"][var]) for var in active_macros}
    pkb26 = compute_pkb_summary(hist, trend_params, beta_coeffs, 2026, baseline_pkb_2026)

    bbn25 = compute_bbnkb_summary(hist, trend_params, beta_coeffs, 2025, baseline_2024)
    baseline_bbn_2026 = {var: float(bbn25["predicted_macro"][var]) for var in active_macros}
    bbn26 = compute_bbnkb_summary(hist, trend_params, beta_coeffs, 2026, baseline_bbn_2026)

    combined_series = build_combined_time_series(hist, pkb25, pkb26, bbn25, bbn26)
    macro_series = build_macro_series(hist, pkb25, pkb26, active_macros)
    pkb_contrib = build_pkb_contribution(pkb25, pkb26)

    # --- KPI Ikhtisar 2025 & 2026 ---
    create_header_with_icon("Ikhtisar Potensi Terpadu vs Target", "🎯")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        gap = pkb25["total"] - pkb25["target"]
        render_kpi_card(
            label="Potensi PKB 2025",
            value=format_rupiah_compact(pkb25["total"], respect_privacy=True),
            delta=f"{format_rupiah_compact(gap, signed=True)} vs Target",
            delta_positive=gap >= 0,
            subtitle=f"Target: {format_rupiah_compact(pkb25['target'])}",
            icon="🚗",
            variant="primary",
        )
    with k2:
        gap = pkb26["total"] - pkb26["target"]
        render_kpi_card(
            label="Potensi PKB 2026",
            value=format_rupiah_compact(pkb26["total"], respect_privacy=True),
            delta=f"{format_rupiah_compact(gap, signed=True)} vs Target",
            delta_positive=gap >= 0,
            subtitle=f"Target: {format_rupiah_compact(pkb26['target'])}",
            icon="🚗",
            variant="success",
        )
    with k3:
        gap = bbn25["total"] - bbn25["target"]
        render_kpi_card(
            label="Potensi BBNKB 2025",
            value=format_rupiah_compact(bbn25["total"], respect_privacy=True),
            delta=f"{format_rupiah_compact(gap, signed=True)} vs Target",
            delta_positive=gap >= 0,
            subtitle=f"Target: {format_rupiah_compact(bbn25['target'])}",
            icon="📝",
            variant="warning",
        )
    with k4:
        gap = bbn26["total"] - bbn26["target"]
        render_kpi_card(
            label="Potensi BBNKB 2026",
            value=format_rupiah_compact(bbn26["total"], respect_privacy=True),
            delta=f"{format_rupiah_compact(gap, signed=True)} vs Target",
            delta_positive=gap >= 0,
            subtitle=f"Target: {format_rupiah_compact(bbn26['target'])}",
            icon="📝",
            variant="indigo",
        )

    # --- Tren PAD 2018-2026 ---
    create_header_with_icon(
        "Lintasan Historis & Proyeksi PAD (2018–2026)",
        "📈",
        subtitle="Garis utuh menampilkan realisasi aktual; garis putus-putus menampilkan proyeksi berbasis dekomposisi & makro",
    )

    with st.container(border=True):
        fig_trend = px.line(
            combined_series,
            x="Tahun",
            y="Nilai",
            color="Jenis",
            line_dash="Status",
            markers=True,
            labels={"Nilai": "Rupiah", "Jenis": "Jenis Pajak"},
            color_discrete_map={"PKB": "#1a5fb4", "BBNKB": "#f59e0b"},
            category_orders={"Status": ["Aktual", "Proyeksi"]},
        )
        fig_trend.update_traces(line=dict(width=3.2), marker=dict(size=8))
        apply_plotly_theme(
            fig_trend,
            title="PKB & BBNKB: Realisasi Aktual vs Proyeksi (2018–2026)",
            height=440,
            xaxis_title="Tahun",
            yaxis_title="Nilai Penerimaan (Rupiah)",
            is_currency=True,
        )
        fig_trend.update_xaxes(dtick=1)
        fig_trend.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    render_section_divider()

    # --- Dinamika Variabel Makro ---
    create_header_with_icon(
        "Dinamika Indikator Makroekonomi (2018–2026)",
        "🌐",
        subtitle="Pilih indikator makroekonomi untuk meninjau arah tren historis dan ekstrapolasi hingga 2026",
    )

    with st.container(border=True):
        default_sel = [m for m in ["PDRB", "Inflasi", "Suku Bunga"] if m in active_macros]
        selected_macros = st.multiselect(
            "Pilih indikator makroekonomi:",
            active_macros,
            default=default_sel,
        )
        filtered_macro = macro_series[macro_series["Variabel"].isin(selected_macros)]
        if not filtered_macro.empty:
            fig_macro = px.line(
                filtered_macro,
                x="Tahun",
                y="Nilai",
                color="Variabel",
                line_dash="Status",
                markers=True,
                category_orders={"Status": ["Aktual", "Proyeksi"]},
            )
            fig_macro.update_traces(line=dict(width=2.8), marker=dict(size=7))
            apply_plotly_theme(
                fig_macro,
                title="Pergerakan Indikator Makroekonomi (2018–2026)",
                height=420,
                xaxis_title="Tahun",
                yaxis_title="Nilai Indikator",
            )
            fig_macro.update_xaxes(dtick=1)
            fig_macro.update_yaxes(tickformat=".2f")
            fig_macro.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_macro, use_container_width=True)
        else:
            st.warning("⚠️ Pilih minimal satu indikator makroekonomi untuk ditampilkan.")

    render_section_divider()

    # --- Insight Pemodelan Regresi Interaktif ---
    create_header_with_icon(
        "Eksplorasi Hubungan Regresi Aktual & Proyeksi",
        "🧪",
        subtitle="Posisi titik proyeksi 2025–2026 di sepanjang garis regresi historis",
    )

    with st.container(border=True):
        c_sel1, c_sel2 = st.columns(2)
        with c_sel1:
            response = st.selectbox("🎯 Variabel Respon", ["PKB", "BBNKB"], index=0)
        with c_sel2:
            predictor = st.selectbox("🧭 Variabel Prediktor Makro", active_macros, index=0)

        model = sm.OLS(hist[response], sm.add_constant(hist[[predictor]])).fit()
        coef = float(model.params[predictor])
        intercept = float(model.params["const"])
        p_value = float(model.pvalues[predictor])
        r_squared = float(model.rsquared)

        future_points = []
        for year, macro_pred in [
            (2025, pkb25["predicted_macro"].get(predictor)),
            (2026, pkb26["predicted_macro"].get(predictor)),
        ]:
            if macro_pred is not None:
                predicted_response = float(model.predict([1, macro_pred])[0])
                future_points.append(
                    {
                        "Tahun": year,
                        predictor: macro_pred,
                        response: predicted_response,
                        "Status": "Proyeksi",
                    }
                )

        modeling_df = hist[["Tahun", predictor, response]].copy()
        modeling_df["Status"] = "Aktual"
        modeling_df = pd.concat([modeling_df, pd.DataFrame(future_points)], ignore_index=True)

        fig_model = px.scatter(
            modeling_df,
            x=predictor,
            y=response,
            color="Status",
            symbol="Status",
            text="Tahun",
            hover_data=["Tahun"],
            color_discrete_map={"Aktual": "#1a5fb4", "Proyeksi": "#f59e0b"},
        )
        x_axis = pd.Series(sorted(modeling_df[predictor]))
        line_df = pd.DataFrame({"const": 1.0, predictor: x_axis})
        reg_line = model.predict(line_df)
        fig_model.add_trace(
            go.Scatter(
                x=x_axis,
                y=reg_line,
                mode="lines",
                name="Garis Regresi OLS",
                line=dict(color="#10b981", width=2.5, dash="dash"),
            )
        )
        fig_model.update_traces(marker=dict(size=10), selector=dict(mode="markers+text"))
        fig_model.update_traces(textposition="top center", selector=dict(mode="markers+text"))
        apply_plotly_theme(
            fig_model,
            title=f"Hubungan {response} vs {predictor} (Aktual & Proyeksi)",
            height=430,
            xaxis_title=predictor,
            yaxis_title=f"{response} (Rupiah)",
            is_currency=True,
        )
        fig_model.update_layout(
            hovermode="closest",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_model, use_container_width=True)

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            render_kpi_card(
                label="Koefisien (β₁)",
                value=format_rupiah_compact(coef, signed=True),
                subtitle=f"Dampak per +1 unit {predictor}",
                variant="primary",
            )
        with m_col2:
            render_kpi_card(
                label="Koefisien Determinasi (R²)",
                value=f"{r_squared:.3f}",
                subtitle=f"{r_squared * 100:.1f}% variasi dijelaskan",
                variant="success" if r_squared >= 0.5 else "warning",
            )
        with m_col3:
            render_kpi_card(
                label="p-value",
                value=f"{p_value:.4f}",
                subtitle="Signifikan (< 0.05)" if p_value < 0.05 else "Tidak Signifikan (≥ 0.05)",
                variant="success" if p_value < 0.05 else "warning",
            )

        sign_str = "+" if coef >= 0 else "-"
        st.markdown(
            f'<div class="formula-box"><strong>Persamaan:</strong> {response} = {intercept:,.0f} {sign_str} {abs(coef):,.0f} × ({predictor})</div>',
            unsafe_allow_html=True,
        )

    render_section_divider()

    # --- Komponen Kontributor & Tabel Ringkas ---
    col_b1, col_b2 = st.columns([1.35, 1])

    with col_b1:
        create_header_with_icon("Komposisi Kontributor Potensi PKB", "🧩")
        with st.container(border=True):
            fig_contrib = px.bar(
                pkb_contrib,
                x="Tahun",
                y="Nilai",
                color="Kategori",
                barmode="group",
                color_discrete_map={
                    "Total Penambah": "#10b981",
                    "Total Pengurang": "#ef4444",
                    "Dampak Makro (+)": "#1a5fb4",
                    "Dampak Makro (-)": "#f59e0b",
                },
            )
            apply_plotly_theme(
                fig_contrib,
                title="Komponen Penambah, Pengurang & Makro PKB (2025–2026)",
                height=400,
                xaxis_title="Tahun",
                yaxis_title="Nilai (Rupiah)",
                is_currency=True,
            )
            fig_contrib.update_layout(
                bargap=0.25,
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_contrib, use_container_width=True)

    with col_b2:
        create_header_with_icon("Matriks Potensi vs Target", "🧾")
        with st.container(border=True):
            summary_tbl = pd.DataFrame(
                {
                    "Tahun": [2025, 2026],
                    "PKB Potensi": [pkb25["total"], pkb26["total"]],
                    "PKB Target": [pkb25["target"], pkb26["target"]],
                    "BBNKB Potensi": [bbn25["total"], bbn26["total"]],
                    "BBNKB Target": [bbn25["target"], bbn26["target"]],
                }
            )
            st.dataframe(
                summary_tbl.style.format(
                    {
                        "PKB Potensi": "Rp {:,.0f}",
                        "PKB Target": "Rp {:,.0f}",
                        "BBNKB Potensi": "Rp {:,.0f}",
                        "BBNKB Target": "Rp {:,.0f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(
                "Potensi menggabungkan proyeksi objek pajak struktural (Roda 4, Roda 2, mutasi, tunggakan) dengan dampak perubahan makroekonomi."
            )


if __name__ == "__main__":
    app()
