import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from data_loader import load_pad_historis
from utils.scenario_utils import (
    calculate_ensemble_scenario_bounds,
    format_scenario_comparison,
    explain_scenario_method
)
from utils.audit_utils import log_projection
from utils.ensemble_models import (
    ensemble_forecast,
    compare_models,
    explain_model
)

# Data historis (2018-2024) dari layer CSV
df = load_pad_historis()

def local_css():
    st.markdown(
        """
        <style>
            .metric-box {
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                font-weight: bold;
                font-size: 1.2rem;
                color: white;
                margin: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            .metric-koef {
                background: linear-gradient(135deg, #64b5f6, #1976d2);
            }
            .metric-r2 {
                background: linear-gradient(135deg, #81c784, #388e3c);
            }
            .metric-pval {
                background: linear-gradient(135deg, #ffb74d, #f57c00);
            }
            .metric-box span {
                display: block;
                font-size: 1.8rem;
                margin-top: 6px;
            }
            .note-box {
                background: #fff8e1;
                border-left: 6px solid #fbc02d;
                border-radius: 10px;
                padding: 1rem;
                margin: 1rem 0;
                font-size: 0.95rem;
                color: #4e342e;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            .note-box strong {
                color: #e65100;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_regression(response: str, predictor: str):
    X = sm.add_constant(df[[predictor]])
    y = df[response]
    return sm.OLS(y, X).fit()


def show_projection_page():
    local_css()
    st.markdown("""
    <div style='background: linear-gradient(90deg, #1a5fb4, #3584e4); 
                padding: 15px; border-radius: 10px; margin-bottom: 25px;'>
        <h1 style='color: white; margin: 0;'>🔮 Proyeksi 2025–2026</h1>
        <p style='color: #f1f1f1; margin: 0;'>PKB & BBNKB dengan 3 skenario</p>
    </div>
    """, unsafe_allow_html=True)

    # Pilih respon & prediktor
    response = st.selectbox("Pilih Variabel Respon", ["PKB", "BBNKB"])
    predictors = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]
    predictor = st.selectbox("Pilih Variabel Prediktor untuk Proyeksi", predictors)

    # --- Prediksi otomatis nilai makro 2025 & 2026 (linear trend terhadap tahun)
    X_tahun = sm.add_constant(df["Tahun"])
    y_var = df[predictor]
    trend_model = sm.OLS(y_var, X_tahun).fit()
    pred_2025 = trend_model.predict([1, 2025])[0]
    pred_2026 = trend_model.predict([1, 2026])[0]

    # --- Scenario Method Selection
    st.subheader("⚙️ Konfigurasi Skenario")

    scenario_method = st.radio(
        "Metode Perhitungan Skenario",
        ["Traditional (±5%)", "Data-Driven (Recommended)"],
        help="Traditional menggunakan ±5% fixed, Data-Driven menggunakan historical volatility & CI"
    )

    if scenario_method == "Data-Driven (Recommended)":
        with st.expander("ℹ️ Tentang Data-Driven Scenarios"):
            st.markdown("""
            **Data-Driven Scenarios** menghitung bounds berdasarkan:
            1. **Historical Volatility**: Standar deviasi dari returns historis
            2. **Confidence Intervals**: Prediction intervals dari model regresi
            3. **Percentiles**: Distribusi empiris dari growth rates

            **Ensemble Method** (default) mengambil rata-rata dari 3 metode di atas untuk hasil yang lebih robust.

            **Keuntungan**: Bounds mencerminkan ketidakpastian aktual dalam data, bukan arbitrary ±5%
            """)

    # --- Input nilai makro (default dari prediksi, tapi bisa diubah manual)
    st.subheader("📥 Input Proyeksi Variabel Makro")
    val_2025 = st.number_input(f"{predictor} Tahun 2025", value=float(pred_2025))
    val_2026 = st.number_input(f"{predictor} Tahun 2026", value=float(pred_2026))

    # Jalankan regresi sederhana
    model = run_regression(response, predictor)

    # --- Prediksi 2025 & 2026 untuk respon dengan confidence intervals
    proj = {}
    ci_data = {}  # Untuk menyimpan confidence intervals
    all_scenario_methods = {}  # Untuk perbandingan metode

    for tahun, val in zip([2025, 2026], [val_2025, val_2026]):
        # Prediksi nilai
        pred_input = np.array([[1, val]])
        pred = model.predict(pred_input)[0]

        # Hitung confidence interval (95%)
        pred_summary = model.get_prediction(pred_input)
        ci = pred_summary.conf_int(alpha=0.05)[0]  # 95% CI

        ci_data[tahun] = {
            "lower": ci[0],
            "upper": ci[1],
            "mean": pred
        }

        # Pilih metode skenario berdasarkan user input
        if scenario_method == "Data-Driven (Recommended)":
            # Hitung ensemble scenario bounds
            scenarios = calculate_ensemble_scenario_bounds(
                df=df,
                model=model,
                response=response,
                X_pred=pred_input,
                prediction=pred,
                method='average'
            )

            # Gunakan ensemble method
            opt, mod, pes = scenarios['ensemble']

            # Simpan semua metode untuk perbandingan
            all_scenario_methods[tahun] = scenarios

            proj[tahun] = {
                "Optimis (Batas Atas)": opt,
                "Moderat (Rata-rata)": mod,
                "Pesimis (Batas Bawah)": pes
            }
        else:
            # Traditional ±5%
            proj[tahun] = {
                "Optimis (Batas Atas)": pred * 1.05,
                "Moderat (Rata-rata)": pred,
                "Pesimis (Batas Bawah)": pred * 0.95
            }

        # Log projection to audit trail
        log_projection(
            response=response,
            year=tahun,
            value=float(proj[tahun]["Moderat (Rata-rata)"]),
            scenario=scenario_method,
            details={
                'predictor': predictor,
                'predictor_value': float(val),
                'optimistic': float(proj[tahun]["Optimis (Batas Atas)"]),
                'pessimistic': float(proj[tahun]["Pesimis (Batas Bawah)"])
            }
        )

    # --- Tabel hasil proyeksi
    st.subheader("📊 Hasil Proyeksi")
    proj_df = pd.DataFrame(proj).T

    # Tambahkan confidence intervals ke tabel
    ci_df = pd.DataFrame(ci_data).T
    ci_df.columns = ['CI Lower (95%)', 'CI Upper (95%)', 'Prediksi Tengah']
    ci_df = ci_df[['Prediksi Tengah', 'CI Lower (95%)', 'CI Upper (95%)']]

    # Gabungkan dengan proyeksi skenario
    combined_df = pd.concat([proj_df, ci_df], axis=1)
    st.dataframe(combined_df.style.format("{:,.0f}"), use_container_width=True)

    # Penjelasan Confidence Interval
    with st.expander("ℹ️ Apa itu Confidence Interval (CI)?"):
        st.markdown("""
        **Confidence Interval (CI) 95%** menunjukkan rentang di mana kita yakin 95% bahwa nilai sebenarnya akan berada.

        - **CI Lower**: Batas bawah interval kepercayaan (lebih konservatif)
        - **CI Upper**: Batas atas interval kepercayaan (lebih optimis)
        - **Prediksi Tengah**: Nilai prediksi paling mungkin

        Semakin lebar interval CI, semakin tinggi ketidakpastian proyeksi. Dengan hanya 7 tahun data (2018-2024),
        interval CI cenderung lebih lebar dibanding jika kita memiliki lebih banyak data historis.

        **Catatan**: CI berbeda dengan skenario Optimis/Moderat/Pesimis. CI dihitung berdasarkan statistik model,
        sedangkan skenario dapat dihitung dengan metode Traditional (±5%) atau Data-Driven (berbasis volatilitas historis).
        """)

    # --- Perbandingan Metode Skenario (untuk Data-Driven)
    if scenario_method == "Data-Driven (Recommended)" and all_scenario_methods:
        st.markdown("---")
        st.subheader("🔬 Perbandingan Metode Perhitungan Skenario")

        # Pilih tahun untuk ditampilkan
        compare_year = st.selectbox(
            "Pilih tahun untuk perbandingan detail:",
            [2025, 2026],
            key="compare_year_scenarios"
        )

        scenarios = all_scenario_methods[compare_year]

        # Format comparison table
        comparison_df = format_scenario_comparison(scenarios)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        # Penjelasan metode yang dipilih
        tabs = st.tabs(["Volatility", "Confidence Interval", "Percentile", "Ensemble"])

        with tabs[0]:
            st.markdown(explain_scenario_method('volatility'))

        with tabs[1]:
            st.markdown(explain_scenario_method('confidence_interval'))

        with tabs[2]:
            st.markdown(explain_scenario_method('percentile'))

        with tabs[3]:
            st.markdown(explain_scenario_method('ensemble'))

        # Recommendation
        st.info("💡 **Rekomendasi**: Metode **Ensemble** digunakan secara default karena menggabungkan kekuatan dari ketiga metode dan lebih robust terhadap outliers.")

    # --- Visualisasi dengan Confidence Intervals
    st.subheader("📈 Visualisasi Proyeksi dengan Confidence Intervals")

    # Create figure using graph_objects for better control
    fig = go.Figure()

    # 1. Data Historis (Aktual)
    hist_years = df["Tahun"].values
    hist_values = df[response].values
    fig.add_trace(go.Scatter(
        x=hist_years,
        y=hist_values,
        mode='lines+markers',
        name='Aktual',
        line=dict(color='#1976d2', width=3),
        marker=dict(size=8)
    ))

    # 2. Confidence Interval Band (Shaded Area)
    last_year = int(df["Tahun"].max())
    last_value = float(df.loc[df["Tahun"] == last_year, response].iloc[0])

    ci_years = [last_year, 2025, 2026]
    ci_upper = [last_value, ci_data[2025]['upper'], ci_data[2026]['upper']]
    ci_lower = [last_value, ci_data[2025]['lower'], ci_data[2026]['lower']]

    # Upper bound
    fig.add_trace(go.Scatter(
        x=ci_years,
        y=ci_upper,
        mode='lines',
        name='CI Upper (95%)',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Lower bound with fill
    fig.add_trace(go.Scatter(
        x=ci_years,
        y=ci_lower,
        mode='lines',
        name='Confidence Interval 95%',
        line=dict(width=0),
        fillcolor='rgba(68, 68, 68, 0.15)',
        fill='tonexty',
        hovertemplate='CI: %{y:,.0f}<extra></extra>'
    ))

    # 3. Skenario Proyeksi
    proj_years = [last_year, 2025, 2026]

    # Moderat (Prediksi Tengah)
    moderat_values = [last_value, proj[2025]["Moderat (Rata-rata)"], proj[2026]["Moderat (Rata-rata)"]]
    fig.add_trace(go.Scatter(
        x=proj_years,
        y=moderat_values,
        mode='lines+markers',
        name='Moderat (Rata-rata)',
        line=dict(color='#388e3c', width=2, dash='dash'),
        marker=dict(size=8, symbol='diamond')
    ))

    # Optimis (Batas Atas = nilai lebih tinggi)
    optimis_values = [last_value, proj[2025]["Optimis (Batas Atas)"], proj[2026]["Optimis (Batas Atas)"]]
    fig.add_trace(go.Scatter(
        x=proj_years,
        y=optimis_values,
        mode='lines+markers',
        name='Optimis (Batas Atas)',
        line=dict(color='#4caf50', width=2, dash='dot'),
        marker=dict(size=7)
    ))

    # Pesimis (Batas Bawah = nilai lebih rendah)
    pesimis_values = [last_value, proj[2025]["Pesimis (Batas Bawah)"], proj[2026]["Pesimis (Batas Bawah)"]]
    fig.add_trace(go.Scatter(
        x=proj_years,
        y=pesimis_values,
        mode='lines+markers',
        name='Pesimis (Batas Bawah)',
        line=dict(color='#f57c00', width=2, dash='dot'),
        marker=dict(size=7)
    ))

    # Layout
    fig.update_layout(
        title=f"Proyeksi {response} 2018-2026 ({predictor} sebagai prediktor)<br><sub>Area abu-abu = Confidence Interval 95%</sub>",
        xaxis=dict(
            title="Tahun",
            tickmode="array",
            tickvals=list(range(2018, 2027)),
            dtick=1
        ),
        yaxis=dict(
            title=f"{response} (Rupiah)",
            tickformat=",.0f"
        ),
        template="plotly_white",
        hovermode='x unified',
        height=650,
        autosize=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)"
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Catatan tambahan
    st.info("💡 **Area abu-abu** menunjukkan Confidence Interval 95%, yaitu rentang di mana nilai aktual kemungkinan besar akan berada berdasarkan model statistik.")

    # --- Ensemble Models Comparison (Advanced) ---
    st.markdown("---")
    st.header("🔬 Advanced: Model Comparison")

    with st.expander("ℹ️ Tentang Model Ensemble"):
        st.markdown("""
        ### 📚 Apa itu Model Ensemble?

        **Model Ensemble** menggabungkan prediksi dari beberapa model berbeda untuk menghasilkan proyeksi yang lebih robust.

        **Model yang tersedia:**
        1. **OLS Regression**: Model utama yang sudah digunakan (berbasis variabel makro)
        2. **ARIMA**: Time series model yang melihat pola historis tanpa prediktor eksternal
        3. **Exponential Smoothing**: Model sederhana yang memberikan bobot lebih pada data terbaru

        **Keuntungan Ensemble:**
        - Mengurangi risiko dari single model bias
        - Memberikan perspektif berbeda (time series vs regression)
        - Rata-rata dari multiple models lebih stabil
        - Useful untuk uncertainty assessment

        **Keterbatasan dengan 7 data point:**
        - ARIMA membutuhkan lebih banyak data untuk hasil optimal
        - Model time series mungkin tidak reliable dengan sample kecil
        - Gunakan sebagai **referensi tambahan**, bukan pengganti OLS
        """)

    if st.checkbox("🔍 Tampilkan Perbandingan Model Ensemble", value=False):
        st.subheader("📊 Perbandingan Beberapa Model Forecasting")

        # Run ensemble forecast
        with st.spinner("Running multiple models..."):
            ensemble_results = ensemble_forecast(
                df=df,
                response=response,
                predictor=predictor,
                forecast_predictor_values=[val_2025, val_2026],
                models_to_use=['ols', 'arima', 'exp_smoothing'],
                arima_order=(1, 1, 1),
                forecast_steps=2
            )

        # Display comparison table
        comparison_df = compare_models(ensemble_results)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        # Show detailed results for each model
        tabs = st.tabs(["OLS Regression", "ARIMA", "Exponential Smoothing", "Ensemble Average"])

        for idx, (tab, model_key) in enumerate(zip(tabs, ['ols', 'arima', 'exp_smoothing', 'ensemble'])):
            with tab:
                if model_key in ensemble_results:
                    model_result = ensemble_results[model_key]

                    if model_result.get('success', False):
                        # Explanation
                        st.markdown(explain_model(model_key))

                        # Forecast values
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(
                                "Proyeksi 2025",
                                f"Rp {model_result['forecast'][0]/1e9:.2f}T"
                            )
                        with col2:
                            if len(model_result['forecast']) > 1:
                                st.metric(
                                    "Proyeksi 2026",
                                    f"Rp {model_result['forecast'][1]/1e9:.2f}T"
                                )

                        # Confidence intervals
                        st.caption(f"**95% CI 2025**: Rp {model_result['forecast_lower'][0]/1e9:.2f}T - Rp {model_result['forecast_upper'][0]/1e9:.2f}T")
                        if len(model_result['forecast']) > 1:
                            st.caption(f"**95% CI 2026**: Rp {model_result['forecast_lower'][1]/1e9:.2f}T - Rp {model_result['forecast_upper'][1]/1e9:.2f}T")

                        # Model-specific metrics
                        if 'aic' in model_result:
                            st.caption(f"**AIC**: {model_result['aic']:.2f}")
                        if 'r_squared' in model_result:
                            st.caption(f"**R²**: {model_result['r_squared']:.3f}")
                        if 'models_used' in model_result:
                            st.caption(f"**Models Combined**: {', '.join([m.upper() for m in model_result['models_used']])}")

                    else:
                        st.error(f"❌ Model gagal: {model_result.get('error', 'Unknown error')}")
                else:
                    st.warning("Model tidak tersedia dalam hasil ensemble")

        # Visualization comparing all models
        st.subheader("📈 Visualisasi Perbandingan Model")

        fig_compare = go.Figure()

        # Historical data
        fig_compare.add_trace(go.Scatter(
            x=df["Tahun"].values,
            y=df[response].values,
            mode='lines+markers',
            name='Aktual (Historis)',
            line=dict(color='#1976d2', width=3),
            marker=dict(size=8)
        ))

        # Add forecasts from each model
        colors = {'ols': '#388e3c', 'arima': '#f57c00', 'exp_smoothing': '#8e24aa', 'ensemble': '#e91e63'}
        last_year = int(df["Tahun"].max())
        last_value = float(df.loc[df["Tahun"] == last_year, response].iloc[0])

        for model_key, color in colors.items():
            if model_key in ensemble_results and ensemble_results[model_key].get('success', False):
                model_result = ensemble_results[model_key]
                forecast_years = [last_year, 2025, 2026]
                forecast_values = [last_value] + list(model_result['forecast'])

                fig_compare.add_trace(go.Scatter(
                    x=forecast_years,
                    y=forecast_values,
                    mode='lines+markers',
                    name=model_result.get('model', model_key.upper()),
                    line=dict(color=color, width=2, dash='dash'),
                    marker=dict(size=7)
                ))

        fig_compare.update_layout(
            title=f"Perbandingan Proyeksi {response} dari Multiple Models",
            xaxis=dict(
                title="Tahun",
                tickmode="array",
                tickvals=list(range(2018, 2027)),
                dtick=1
            ),
            yaxis=dict(
                title=f"{response} (Rupiah)",
                tickformat=",.0f"
            ),
            template="plotly_white",
            hovermode='x unified',
            height=650,
            autosize=True,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255, 255, 255, 0.9)"
            )
        )

        st.plotly_chart(fig_compare, use_container_width=True)

        # Insights
        st.markdown("### 💡 Interpretasi")

        successful_models = {k: v for k, v in ensemble_results.items()
                           if v.get('success', False) and k != 'ensemble'}

        if len(successful_models) > 1:
            # Calculate variance across models
            forecasts_2025 = [m['forecast'][0] for m in successful_models.values()]
            avg_2025 = np.mean(forecasts_2025)
            std_2025 = np.std(forecasts_2025)
            cv_2025 = (std_2025 / avg_2025) * 100

            st.info(f"""
            📊 **Konsistensi Proyeksi 2025:**
            - Rata-rata: Rp {avg_2025/1e9:.2f}T
            - Standar Deviasi: Rp {std_2025/1e9:.2f}T
            - Coefficient of Variation: {cv_2025:.1f}%

            {'✅ Model cukup konsisten (CV < 10%)' if cv_2025 < 10 else '⚠️ Ada perbedaan signifikan antar model (CV > 10%)'}
            """)

            if 'ensemble' in ensemble_results:
                st.success(f"🎯 **Rekomendasi Ensemble**: Gunakan proyeksi ensemble (Rp {ensemble_results['ensemble']['forecast'][0]/1e9:.2f}T) sebagai **best estimate** karena mengurangi bias dari single model.")
        else:
            st.warning("⚠️ Hanya 1 model berhasil. Ensemble tidak tersedia.")


def app():
    show_projection_page()


if __name__ == "__main__":
    app()
