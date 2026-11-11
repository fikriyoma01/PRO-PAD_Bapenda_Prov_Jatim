"""
Pemodelan Regresi Sederhana — Evaluasi Statistik, Validasi LOOCV, Backtesting & Sensitivitas
"""

import warnings as _warnings

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st

from data_loader import load_pad_historis
from utils.audit_utils import log_model_run
from utils.sensitivity_utils import (
    calculate_sensitivity_all_vars,
    create_elasticity_chart,
    create_tornado_chart,
    format_sensitivity_table,
    interpret_sensitivity,
)
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_info_box,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact
from utils.validation_utils import (
    backtest_model,
    calculate_all_metrics,
    interpret_mape,
    interpret_r2,
    leave_one_out_cross_validation,
)

PREDICTORS = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]


def run_regression(df: pd.DataFrame, response: str, predictor: str):
    """Jalankan regresi OLS menggunakan matriks numpy agar konsisten di seluruh prediksi."""
    X = df[[predictor]].values
    y = df[response].values
    X_with_const = np.column_stack([np.ones(len(X)), X])
    return sm.OLS(y, X_with_const).fit()


def show_modeling_page() -> None:
    df = load_pad_historis()
    min_year = int(df["Tahun"].min())
    max_year = int(df["Tahun"].max())

    render_page_header(
        title="Pemodelan Regresi & Validasi",
        subtitle=f"Analisis hubungan ekonometrika PKB & BBNKB terhadap indikator makroekonomi ({min_year}–{max_year})",
        icon="📊",
    )

    available_predictors = [p for p in PREDICTORS if p in df.columns]

    # --- Konfigurasi Model ---
    with st.container(border=True):
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            response = st.selectbox("📌 Pilih Variabel Respon (Pajak Daerah)", ["PKB", "BBNKB"])
        with col_sel2:
            predictor = st.selectbox("📌 Pilih Variabel Prediktor (Makroekonomi)", available_predictors)

    model = run_regression(df, response, predictor)
    intercept = float(model.params[0])
    coef = float(model.params[1])
    pval = float(model.pvalues[1])
    r2 = float(model.rsquared)

    log_model_run(
        response=response,
        predictor=predictor,
        r2=r2,
        details={
            "coefficient": coef,
            "intercept": intercept,
            "p_value": pval,
        },
    )

    # --- Ringkasan Parameter Regresi ---
    create_header_with_icon(
        f"Hasil Estimasi OLS: {response} terhadap {predictor}",
        "📐",
        subtitle="Parameter model regresi linear sederhana beserta tingkat signifikansi statistik",
    )

    k1, k2, k3 = st.columns(3)
    with k1:
        render_kpi_card(
            label="Koefisien Regresi (β₁)",
            value=format_rupiah_compact(coef, signed=True),
            delta="Arah Positif" if coef >= 0 else "Arah Negatif",
            delta_positive=coef >= 0,
            subtitle=f"Perubahan per +1 unit {predictor}",
            icon="📈",
            variant="primary",
        )
    with k2:
        r2_label = "Kuat" if r2 >= 0.7 else "Sedang" if r2 >= 0.4 else "Lemah"
        render_kpi_card(
            label="Koefisien Determinasi (R²)",
            value=f"{r2:.3f} ({r2 * 100:.1f}%)",
            delta=f"Daya Jelas {r2_label}",
            delta_positive=r2 >= 0.4,
            subtitle="Proporsi variasi yang dijelaskan model",
            icon="🎯",
            variant="success" if r2 >= 0.5 else "warning",
        )
    with k3:
        sig = pval < 0.05
        render_kpi_card(
            label="Signifikansi (p-value)",
            value=f"{pval:.4f}",
            delta="Signifikan (p < 0.05)" if sig else "Tidak Signifikan (p ≥ 0.05)",
            delta_positive=sig,
            subtitle="Uji hipotesis dua arah pada α = 5%",
            icon="🔬",
            variant="success" if sig else "warning",
        )

    # Persamaan & Interpretasi
    sign_str = "+" if coef >= 0 else "-"
    st.markdown(
        f"""
        <div class="formula-box">
            <strong>Persamaan Regresi:</strong>&nbsp;
            {response} = {intercept:,.0f} {sign_str} {abs(coef):,.0f} × ({predictor})
        </div>
        """,
        unsafe_allow_html=True,
    )

    arah = "penambah (positif)" if coef > 0 else "pengurang (negatif)"
    if pval < 0.05:
        st.success(
            f"✅ Secara statistik **{predictor}** berpengaruh signifikan (`p = {pval:.4f} < 0.05`) sebagai faktor **{arah}** terhadap **{response}**."
        )
    else:
        st.warning(
            f"⚠️ Pengaruh **{predictor}** terhadap **{response}** belum signifikan pada α = 5% (`p = {pval:.4f}`), dengan kecenderungan arah **{arah}**."
        )

    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        with st.expander("ℹ️ Panduan Membaca Parameter Regresi"):
            st.markdown(
                f"""
                - **Koefisien (β₁)**: Setiap kenaikan 1 satuan `{predictor}` berasosiasi dengan perubahan `{response}` sebesar **{format_rupiah_compact(coef, signed=True)}**.
                - **R² ({r2:.3f})**: Sebesar **{r2 * 100:.1f}%** variasi historis `{response}` dapat dijelaskan oleh pergerakan `{predictor}`.
                - **p-value ({pval:.4f})**: Nilai di bawah `0.05` menandakan hubungan linear kecil kemungkinannya terjadi secara kebetulan.
                """
            )
    with col_exp2:
        with st.expander("🔍 Detail Statistik Lengkap (Statsmodels OLS Summary)"):
            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore")
                st.code(model.summary().as_text(), language="text")

    render_info_box(
        f"<strong>Catatan Metodologis Sampel Terbatas:</strong> Observasi mencakup <strong>{len(df)} tahun ({min_year}–{max_year})</strong>. "
        "Gunakan hasil uji signifikansi bersama metrik validasi silang (LOOCV) dan dekomposisi objek pajak agar terhindar dari risiko overfitting.",
        box_type="warning",
    )

    # --- Visualisasi Scatterplot + Garis Regresi ---
    create_header_with_icon(
        "Visualisasi Regresi Linear",
        "📉",
        subtitle=f"Sebaran observasi aktual {min_year}–{max_year} beserta garis estimasi OLS",
    )

    df_sorted = df.sort_values(predictor).copy()
    X_sorted = df_sorted[[predictor]].values
    X_sorted_with_const = np.column_stack([np.ones(len(X_sorted)), X_sorted])
    df_sorted["pred"] = model.predict(X_sorted_with_const)

    with st.container(border=True):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df[predictor],
                y=df[response],
                mode="markers+text",
                name="Observasi Aktual",
                text=df["Tahun"],
                textposition="top center",
                marker=dict(size=11, color="#1a5fb4", line=dict(width=2, color="#ffffff")),
                hovertemplate=(
                    "<b>Tahun %{text}</b><br>"
                    f"{predictor}: %{{x:.2f}}<br>"
                    f"{response}: Rp %{{y:,.0f}}<extra></extra>"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_sorted[predictor],
                y=df_sorted["pred"],
                mode="lines",
                name="Garis Estimasi OLS",
                line=dict(color="#f59e0b", width=3, dash="dash"),
                hovertemplate=f"{predictor}: %{{x:.2f}}<br>Estimasi OLS: Rp %{{y:,.0f}}<extra></extra>",
            )
        )
        apply_plotly_theme(
            fig,
            title=f"Hubungan {response} vs {predictor} (R² = {r2:.3f})",
            height=440,
            xaxis_title=predictor,
            yaxis_title=f"{response} (Rupiah)",
            is_currency=True,
        )
        fig.update_layout(
            hovermode="closest",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    render_section_divider()

    # --- Validasi Model & Performance Metrics ---
    create_header_with_icon(
        "Validasi Model & Metrik Performa",
        "✅",
        subtitle="Evaluasi akurasi in-sample (Training), out-of-sample (LOOCV), dan pengujian historis (Backtesting)",
    )

    X_full = df[[predictor]].values
    X_full_with_const = np.column_stack([np.ones(len(X_full)), X_full])
    y_fitted = model.predict(X_full_with_const)
    y_actual = df[response].values

    train_metrics = calculate_all_metrics(y_actual, y_fitted)
    cv_results = leave_one_out_cross_validation(df, response, predictor)

    col_val1, col_val2 = st.columns(2)
    with col_val1:
        with st.container(border=True):
            st.markdown("#### 📊 Training Metrics (In-Sample)")
            st.caption("Evaluasi error pada seluruh data historis yang digunakan untuk melatih model.")
            metrics_df = pd.DataFrame(
                {
                    "Metrik": list(train_metrics.keys()),
                    "Nilai": [
                        format_rupiah_compact(v) if k in ("RMSE", "MAE") else f"{v:,.3f}" if k == "R²" else f"{v:,.2f}%"
                        for k, v in train_metrics.items()
                    ],
                }
            )
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
            r2_cat, r2_desc = interpret_r2(train_metrics["R²"])
            mape_cat, mape_desc = interpret_mape(train_metrics["MAPE (%)"])
            st.info(f"**R²**: {r2_cat} — {r2_desc}\n\n**MAPE**: {mape_cat} — {mape_desc}")

    with col_val2:
        with st.container(border=True):
            st.markdown("#### 🔄 Cross-Validation (LOOCV)")
            st.caption("Melatih model n kali dengan menyisihkan 1 tahun secara bergantian sebagai data uji.")
            cv_metrics_df = pd.DataFrame(
                {
                    "Metrik": list(cv_results["metrics"].keys()),
                    "Nilai": [
                        format_rupiah_compact(v)
                        if k in ("RMSE", "MAE")
                        else f"{v:,.3f}"
                        if k == "R²"
                        else f"{v:,.2f}%"
                        for k, v in cv_results["metrics"].items()
                    ],
                }
            )
            st.dataframe(cv_metrics_df, use_container_width=True, hide_index=True)

            train_mape = train_metrics["MAPE (%)"]
            cv_mape = cv_results["metrics"]["MAPE (%)"]
            diff_pct = ((cv_mape - train_mape) / train_mape * 100) if train_mape else 0.0
            if abs(diff_pct) <= 25:
                st.success(f"✅ **Model Stabil**: Selisih MAPE LOOCV terhadap training terkendali (`{diff_pct:+.1f}%`).")
            else:
                st.warning(
                    f"⚠️ **Indikasi Sensitivitas Sampel**: MAPE LOOCV meningkat `{diff_pct:+.1f}%` dibanding in-sample."
                )

    # --- Backtesting ---
    create_header_with_icon(
        "Backtesting Historis (Train 2018–2022 → Test 2023–2024)",
        "⏮️",
        subtitle="Simulasi akurasi peramalan seandainya model dilatih hingga 2022 untuk memprediksi 2 tahun terakhir",
    )

    backtest_results = backtest_model(df, response, predictor, test_years=2)
    col_bt1, col_bt2 = st.columns([1.75, 1])

    with col_bt1:
        with st.container(border=True):
            fig_backtest = go.Figure()
            fig_backtest.add_trace(
                go.Scatter(
                    x=backtest_results["test_years"],
                    y=backtest_results["y_test"],
                    mode="lines+markers",
                    name="Realisasi Aktual",
                    line=dict(color="#1a5fb4", width=3.5),
                    marker=dict(size=10),
                    hovertemplate="Tahun %{x}<br>Aktual: Rp %{y:,.0f}<extra></extra>",
                )
            )
            fig_backtest.add_trace(
                go.Scatter(
                    x=backtest_results["test_years"],
                    y=backtest_results["y_pred"],
                    mode="lines+markers",
                    name="Prediksi Backtest",
                    line=dict(color="#f59e0b", width=3.5, dash="dash"),
                    marker=dict(size=10, symbol="diamond"),
                    hovertemplate="Tahun %{x}<br>Prediksi: Rp %{y:,.0f}<extra></extra>",
                )
            )
            apply_plotly_theme(
                fig_backtest,
                title=f"Uji Backtest {response} (Periode Uji {min(backtest_results['test_years'])}–{max(backtest_results['test_years'])})",
                height=380,
                xaxis_title="Tahun Uji",
                yaxis_title=f"{response} (Rupiah)",
                is_currency=True,
            )
            fig_backtest.update_xaxes(dtick=1)
            fig_backtest.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_backtest, use_container_width=True)

    with col_bt2:
        with st.container(border=True):
            st.markdown("#### 📋 Ringkasan Komparasi Validasi")
            comparison_df = pd.DataFrame(
                {
                    "Metrik": ["RMSE", "MAE", "MAPE (%)", "R²"],
                    "Training": [
                        format_rupiah_compact(train_metrics["RMSE"]),
                        format_rupiah_compact(train_metrics["MAE"]),
                        f"{train_metrics['MAPE (%)']:.2f}%",
                        f"{train_metrics['R²']:.3f}",
                    ],
                    "LOOCV": [
                        format_rupiah_compact(cv_results["metrics"]["RMSE"]),
                        format_rupiah_compact(cv_results["metrics"]["MAE"]),
                        f"{cv_results['metrics']['MAPE (%)']:.2f}%",
                        f"{cv_results['metrics']['R²']:.3f}",
                    ],
                    "Backtest": [
                        format_rupiah_compact(backtest_results["metrics"]["RMSE"]),
                        format_rupiah_compact(backtest_results["metrics"]["MAE"]),
                        f"{backtest_results['metrics']['MAPE (%)']:.2f}%",
                        f"{backtest_results['metrics']['R²']:.3f}",
                    ],
                }
            )
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            st.caption(
                "Catatan: R² pada 2 titik uji backtest sangat sensitif terhadap fluktuasi tahun tunggal; prioritaskan metrik MAPE & MAE."
            )

    render_section_divider()

    # --- Sensitivity Analysis ---
    create_header_with_icon(
        "Analisis Sensitivitas & Elastisitas Makro",
        "🔬",
        subtitle=f"Simulasi dampak guncangan ±10% pada masing-masing indikator makro terhadap proyeksi {response}",
    )

    base_values = {var: float(df.iloc[-1][var]) for var in available_predictors}
    sens_df = calculate_sensitivity_all_vars(
        df=df,
        response=response,
        predictors=available_predictors,
        base_values=base_values,
        variation_pct=0.1,
    )
    interpretation = interpret_sensitivity(sens_df)

    c_sens1, c_sens2 = st.columns(2)
    with c_sens1:
        st.info(f"📊 {interpretation['most_impactful']}")
    with c_sens2:
        st.info(f"📉 {interpretation['least_impactful']}")

    col_viz1, col_viz2 = st.columns(2)
    with col_viz1:
        with st.container(border=True):
            tornado_fig = create_tornado_chart(sens_df, response, variation_pct=0.1)
            tornado_fig.update_layout(height=420)
            st.plotly_chart(tornado_fig, use_container_width=True)
    with col_viz2:
        with st.container(border=True):
            elasticity_fig = create_elasticity_chart(sens_df, response)
            elasticity_fig.update_layout(height=420)
            st.plotly_chart(elasticity_fig, use_container_width=True)

    with st.expander("📋 Lihat Tabel Detail Sensitivitas & Elastisitas Semua Variabel", expanded=False):
        formatted_table = format_sensitivity_table(sens_df)
        st.dataframe(formatted_table, use_container_width=True, hide_index=True)


def app() -> None:
    show_modeling_page()


if __name__ == "__main__":
    app()
