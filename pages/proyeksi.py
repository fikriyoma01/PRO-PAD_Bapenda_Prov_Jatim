"""
Proyeksi 2025–2026 Page — Peramalan Skenario, Confidence Interval 95%, dan Ensemble Multi-Model
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st

from data_loader import load_pad_historis
from utils.audit_utils import log_projection
from utils.ensemble_models import compare_models, ensemble_forecast, explain_model
from utils.scenario_utils import (
    calculate_ensemble_scenario_bounds,
    explain_scenario_method,
    format_scenario_comparison,
)
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact, format_rupiah_full

PREDICTORS = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]


def run_regression(df: pd.DataFrame, response: str, predictor: str):
    X = sm.add_constant(df[[predictor]])
    y = df[response]
    return sm.OLS(y, X).fit()


def show_projection_page() -> None:
    df = load_pad_historis()
    available_predictors = [p for p in PREDICTORS if p in df.columns]

    render_page_header(
        title="Proyeksi PAD Tahun 2025–2026",
        subtitle="Estimasi PKB & BBNKB dengan 3 skenario (Optimis, Moderat, Pesimis), Confidence Interval 95%, dan komparasi Ensemble",
        icon="📈",
    )

    # --- Panel Konfigurasi Proyeksi ---
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            response = st.selectbox("📌 Pilih Variabel Respon", ["PKB", "BBNKB"])
        with c2:
            predictor = st.selectbox("📌 Pilih Variabel Prediktor Makro", available_predictors)

        # Estimasi tren linear otomatis untuk default nilai prediktor 2025 & 2026
        X_tahun = sm.add_constant(df["Tahun"])
        trend_model = sm.OLS(df[predictor], X_tahun).fit()
        pred_2025 = float(trend_model.predict([1, 2025])[0])
        pred_2026 = float(trend_model.predict([1, 2026])[0])

        st.markdown("##### ⚙️ Metode Skenario & Asumsi Nilai Makro")
        m1, m2, m3 = st.columns([1.4, 1, 1])
        with m1:
            scenario_method = st.radio(
                "Metode Perhitungan Batas Skenario",
                ["Data-Driven (Recommended)", "Traditional (±5%)"],
                help="Data-Driven menghitung rentang berdasarkan volatilitas historis, CI model, dan persentil pertumbuhan.",
            )
        with m2:
            val_2025 = st.number_input(
                f"Asumsi {predictor} 2025",
                value=round(pred_2025, 3),
                step=0.1,
                format="%.3f",
            )
        with m3:
            val_2026 = st.number_input(
                f"Asumsi {predictor} 2026",
                value=round(pred_2026, 3),
                step=0.1,
                format="%.3f",
            )

    model = run_regression(df, response, predictor)

    proj = {}
    ci_data = {}
    all_scenario_methods = {}

    for tahun, val in zip([2025, 2026], [val_2025, val_2026]):
        pred_input = np.array([[1.0, float(val)]])
        pred = float(model.predict(pred_input)[0])
        ci = model.get_prediction(pred_input).conf_int(alpha=0.05)[0]

        ci_data[tahun] = {
            "lower": float(ci[0]),
            "upper": float(ci[1]),
            "mean": pred,
        }

        if scenario_method == "Data-Driven (Recommended)":
            scenarios = calculate_ensemble_scenario_bounds(
                df=df,
                model=model,
                response=response,
                X_pred=pred_input,
                prediction=pred,
                method="average",
            )
            opt, mod, pes = scenarios["ensemble"]
            all_scenario_methods[tahun] = scenarios
            proj[tahun] = {
                "Optimis (Batas Atas)": float(opt),
                "Moderat (Rata-rata)": float(mod),
                "Pesimis (Batas Bawah)": float(pes),
            }
        else:
            proj[tahun] = {
                "Optimis (Batas Atas)": pred * 1.05,
                "Moderat (Rata-rata)": pred,
                "Pesimis (Batas Bawah)": pred * 0.95,
            }

        log_projection(
            response=response,
            year=tahun,
            value=float(proj[tahun]["Moderat (Rata-rata)"]),
            scenario=scenario_method,
            details={
                "predictor": predictor,
                "predictor_value": float(val),
                "optimistic": float(proj[tahun]["Optimis (Batas Atas)"]),
                "pessimistic": float(proj[tahun]["Pesimis (Batas Bawah)"]),
            },
        )

    # --- KPI Ringkasan Proyeksi ---
    create_header_with_icon(
        f"Ringkasan Proyeksi {response} (2025–2026)",
        "🎯",
        subtitle=f"Berdasarkan prediktor {predictor} dan metode {scenario_method}",
    )

    last_year = int(df["Tahun"].max())
    last_actual = float(df.loc[df["Tahun"] == last_year, response].iloc[0])
    mod_2025 = proj[2025]["Moderat (Rata-rata)"]
    mod_2026 = proj[2026]["Moderat (Rata-rata)"]
    g_2025 = ((mod_2025 - last_actual) / last_actual * 100) if last_actual else 0.0
    g_2026 = ((mod_2026 - mod_2025) / mod_2025 * 100) if mod_2025 else 0.0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            label=f"Moderat {response} 2025",
            value=format_rupiah_compact(mod_2025, respect_privacy=True),
            delta=f"{g_2025:+.2f}% vs {last_year}",
            delta_positive=g_2025 >= 0,
            subtitle=format_rupiah_full(mod_2025),
            icon="📅",
            variant="primary",
        )
    with k2:
        render_kpi_card(
            label=f"Moderat {response} 2026",
            value=format_rupiah_compact(mod_2026, respect_privacy=True),
            delta=f"{g_2026:+.2f}% vs 2025",
            delta_positive=g_2026 >= 0,
            subtitle=format_rupiah_full(mod_2026),
            icon="🚀",
            variant="success",
        )
    with k3:
        render_kpi_card(
            label="Rentang Skenario 2025",
            value=f"{format_rupiah_compact(proj[2025]['Pesimis (Batas Bawah)'], respect_privacy=True)} – {format_rupiah_compact(proj[2025]['Optimis (Batas Atas)'], respect_privacy=True)}",
            subtitle="Pesimis s.d. Optimis 2025",
            icon="↔️",
            variant="warning",
        )
    with k4:
        render_kpi_card(
            label="Rentang Skenario 2026",
            value=f"{format_rupiah_compact(proj[2026]['Pesimis (Batas Bawah)'], respect_privacy=True)} – {format_rupiah_compact(proj[2026]['Optimis (Batas Atas)'], respect_privacy=True)}",
            subtitle="Pesimis s.d. Optimis 2026",
            icon="↔️",
            variant="indigo",
        )

    # --- Tabel Detail Proyeksi & CI ---
    create_header_with_icon("Tabel Proyeksi & Confidence Interval (95%)", "📋")

    proj_df = pd.DataFrame(proj).T
    ci_df = pd.DataFrame(ci_data).T[["mean", "lower", "upper"]]
    ci_df.columns = ["Prediksi Tengah (OLS)", "CI Lower (95%)", "CI Upper (95%)"]
    combined_df = pd.concat([proj_df, ci_df], axis=1)
    combined_df.index.name = "Tahun"

    st.dataframe(
        combined_df.style.format("Rp {:,.0f}"),
        use_container_width=True,
    )

    with st.expander("ℹ️ Perbedaan Skenario Proyeksi vs Confidence Interval (CI) 95%"):
        st.markdown(
            """
            - **Confidence Interval (CI) 95%** merupakan interval statistik regresi OLS di mana nilai rata-rata populasi diestimasi berada pada tingkat keyakinan 95%.
            - **Skenario Optimis / Moderat / Pesimis** menerjemahkan ketidakpastian ke dalam perencanaan target fiskal:
              - *Data-Driven* menggabungkan volatilitas historis, lebar CI model, dan persentil pertumbuhan historis.
              - *Traditional (±5%)* menerapkan deviasi tetap `+5%` (Optimis) dan `-5%` (Pesimis) dari prediksi tengah.
            """
        )

    # --- Visualisasi Grafik Proyeksi + CI ---
    create_header_with_icon(
        "Visualisasi Lintasan Proyeksi & Confidence Interval",
        "📈",
        subtitle=f"Realisasi aktual 2018–{last_year} dilanjutkan proyeksi 2025–2026 beserta pita kepercayaan 95%",
    )

    with st.container(border=True):
        fig = go.Figure()

        # 1. Historis Aktual
        fig.add_trace(
            go.Scatter(
                x=df["Tahun"].values,
                y=df[response].values,
                mode="lines+markers",
                name="Realisasi Aktual",
                line=dict(color="#1a5fb4", width=3.5),
                marker=dict(size=8),
                hovertemplate="Tahun %{x}<br>Aktual: Rp %{y:,.0f}<extra></extra>",
            )
        )

        # 2. Pita Confidence Interval 95%
        ci_years = [last_year, 2025, 2026]
        ci_upper = [last_actual, ci_data[2025]["upper"], ci_data[2026]["upper"]]
        ci_lower = [last_actual, ci_data[2025]["lower"], ci_data[2026]["lower"]]

        fig.add_trace(
            go.Scatter(
                x=ci_years,
                y=ci_upper,
                mode="lines",
                name="CI Upper (95%)",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=ci_years,
                y=ci_lower,
                mode="lines",
                name="Confidence Interval 95%",
                line=dict(width=0),
                fillcolor="rgba(59, 130, 246, 0.18)",
                fill="tonexty",
                hovertemplate="Batas CI 95%: Rp %{y:,.0f}<extra></extra>",
            )
        )

        # 3. Tiga Skenario Proyeksi
        proj_years = [last_year, 2025, 2026]
        fig.add_trace(
            go.Scatter(
                x=proj_years,
                y=[last_actual, proj[2025]["Optimis (Batas Atas)"], proj[2026]["Optimis (Batas Atas)"]],
                mode="lines+markers",
                name="Optimis (Batas Atas)",
                line=dict(color="#10b981", width=2.5, dash="dot"),
                marker=dict(size=8, symbol="triangle-up"),
                hovertemplate="Optimis %{x}: Rp %{y:,.0f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=proj_years,
                y=[last_actual, proj[2025]["Moderat (Rata-rata)"], proj[2026]["Moderat (Rata-rata)"]],
                mode="lines+markers",
                name="Moderat (Utama)",
                line=dict(color="#0ea5e9", width=3, dash="dash"),
                marker=dict(size=9, symbol="diamond"),
                hovertemplate="Moderat %{x}: Rp %{y:,.0f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=proj_years,
                y=[last_actual, proj[2025]["Pesimis (Batas Bawah)"], proj[2026]["Pesimis (Batas Bawah)"]],
                mode="lines+markers",
                name="Pesimis (Batas Bawah)",
                line=dict(color="#f59e0b", width=2.5, dash="dot"),
                marker=dict(size=8, symbol="triangle-down"),
                hovertemplate="Pesimis %{x}: Rp %{y:,.0f}<extra></extra>",
            )
        )

        apply_plotly_theme(
            fig,
            title=f"Proyeksi {response} 2018–2026 (Prediktor: {predictor})",
            height=480,
            xaxis_title="Tahun",
            yaxis_title=f"{response} (Rupiah)",
            is_currency=True,
        )
        fig.update_xaxes(tickvals=list(range(int(df["Tahun"].min()), 2027)), dtick=1)
        fig.update_layout(
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Rincian Metode Data-Driven ---
    if scenario_method == "Data-Driven (Recommended)" and all_scenario_methods:
        with st.expander("🔬 Lihat Rincian Komparasi 4 Metode Skenario Data-Driven", expanded=False):
            compare_year = st.selectbox(
                "Pilih tahun proyeksi:",
                [2025, 2026],
                key="compare_year_scenarios",
            )
            comparison_df = format_scenario_comparison(all_scenario_methods[compare_year])
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

            m_tabs = st.tabs(["Volatility", "Confidence Interval", "Percentile", "Ensemble"])
            for tab, m_key in zip(m_tabs, ["volatility", "confidence_interval", "percentile", "ensemble"]):
                with tab:
                    st.markdown(explain_scenario_method(m_key))

    render_section_divider()

    # --- Perbandingan Ensemble Multi-Model ---
    create_header_with_icon(
        "Komparasi Ensemble Multi-Model (OLS, ARIMA & Exponential Smoothing)",
        "🔬",
        subtitle="Bandingkan peramalan berbasis indikator makro (OLS) dengan peramalan deret waktu murni",
    )

    show_ensemble = st.toggle("Tampilkan Analisis & Grafik Perbandingan Multi-Model", value=True)

    if show_ensemble:
        with st.spinner("Menjalankan model OLS, ARIMA, dan Exponential Smoothing..."):
            ensemble_results = ensemble_forecast(
                df=df,
                response=response,
                predictor=predictor,
                forecast_predictor_values=[val_2025, val_2026],
                models_to_use=["ols", "arima", "exp_smoothing"],
                arima_order=(1, 1, 1),
                forecast_steps=2,
            )

        comparison_df = compare_models(ensemble_results)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        tabs = st.tabs(["OLS Regression", "ARIMA", "Exponential Smoothing", "Ensemble Average"])
        for tab, model_key in zip(tabs, ["ols", "arima", "exp_smoothing", "ensemble"]):
            with tab:
                model_result = ensemble_results.get(model_key, {})
                if model_result.get("success", False):
                    c_m1, c_m2 = st.columns(2)
                    with c_m1:
                        render_kpi_card(
                            label=f"Proyeksi 2025 ({model_result.get('model', model_key.upper())})",
                            value=format_rupiah_compact(model_result["forecast"][0], respect_privacy=True),
                            subtitle=(
                                f"95% CI: {format_rupiah_compact(model_result['forecast_lower'][0])} – "
                                f"{format_rupiah_compact(model_result['forecast_upper'][0])}"
                            ),
                            variant="primary",
                        )
                    with c_m2:
                        if len(model_result["forecast"]) > 1:
                            render_kpi_card(
                                label=f"Proyeksi 2026 ({model_result.get('model', model_key.upper())})",
                                value=format_rupiah_compact(model_result["forecast"][1], respect_privacy=True),
                                subtitle=(
                                    f"95% CI: {format_rupiah_compact(model_result['forecast_lower'][1])} – "
                                    f"{format_rupiah_compact(model_result['forecast_upper'][1])}"
                                ),
                                variant="success",
                            )
                    with st.expander(f"ℹ️ Penjelasan Metodologi {model_result.get('model', model_key.upper())}"):
                        st.markdown(explain_model(model_key))
                else:
                    st.warning(f"⚠️ Model `{model_key}` tidak dapat dijalankan: {model_result.get('error', 'Unknown error')}")

        with st.container(border=True):
            fig_compare = go.Figure()
            fig_compare.add_trace(
                go.Scatter(
                    x=df["Tahun"].values,
                    y=df[response].values,
                    mode="lines+markers",
                    name="Aktual (Historis)",
                    line=dict(color="#1a5fb4", width=3.5),
                    marker=dict(size=8),
                )
            )

            model_colors = {
                "ols": "#10b981",
                "arima": "#f59e0b",
                "exp_smoothing": "#6366f1",
                "ensemble": "#ef4444",
            }
            for model_key, color in model_colors.items():
                res = ensemble_results.get(model_key, {})
                if res.get("success", False):
                    fig_compare.add_trace(
                        go.Scatter(
                            x=[last_year, 2025, 2026],
                            y=[last_actual] + list(res["forecast"]),
                            mode="lines+markers",
                            name=res.get("model", model_key.upper()),
                            line=dict(
                                color=color,
                                width=3 if model_key == "ensemble" else 2.2,
                                dash="solid" if model_key == "ensemble" else "dash",
                            ),
                            marker=dict(size=8),
                            hovertemplate=f"<b>{res.get('model', model_key.upper())}</b> (%{{x}}): Rp %{{y:,.0f}}<extra></extra>",
                        )
                    )

            apply_plotly_theme(
                fig_compare,
                title=f"Perbandingan Lintasan Proyeksi {response} Lintas Model",
                height=460,
                xaxis_title="Tahun",
                yaxis_title=f"{response} (Rupiah)",
                is_currency=True,
            )
            fig_compare.update_xaxes(tickvals=list(range(int(df["Tahun"].min()), 2027)), dtick=1)
            fig_compare.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_compare, use_container_width=True)

        successful_models = {
            k: v for k, v in ensemble_results.items() if v.get("success", False) and k != "ensemble"
        }
        if len(successful_models) > 1:
            forecasts_2025 = [float(m["forecast"][0]) for m in successful_models.values()]
            avg_2025 = float(np.mean(forecasts_2025))
            std_2025 = float(np.std(forecasts_2025))
            cv_2025 = (std_2025 / avg_2025 * 100) if avg_2025 else 0.0
            consistency_msg = (
                "✅ Konsistensi antar-model sangat baik (`CV < 10%`)."
                if cv_2025 < 10
                else "⚠️ Terdapat deviasi cukup lebar antar-model (`CV ≥ 10%`); gunakan rata-rata Ensemble untuk memitigasi bias."
            )
            ens_val = format_rupiah_compact(ensemble_results["ensemble"]["forecast"][0], respect_privacy=True)
            st.info(
                f"📊 **Konsistensi Proyeksi 2025**: Rata-rata **{format_rupiah_compact(avg_2025, respect_privacy=True)}** | "
                f"Simpangan Baku **{format_rupiah_compact(std_2025)}** | CV **{cv_2025:.1f}%** — {consistency_msg}\n\n"
                f"🎯 **Estimasi Terbaik (Ensemble 2025)**: **{ens_val}**"
            )


def app() -> None:
    show_projection_page()


if __name__ == "__main__":
    app()
