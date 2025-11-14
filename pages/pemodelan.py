import streamlit as st
import statsmodels.api as sm
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data_loader import load_pad_historis
from utils.validation_utils import (
    calculate_all_metrics,
    leave_one_out_cross_validation,
    backtest_model,
    interpret_mape,
    interpret_r2
)

# Data historis dari layer CSV
df = load_pad_historis()


def run_regression(response: str, predictor: str):
    X = df[[predictor]]
    X = sm.add_constant(X)
    y = df[response]
    return sm.OLS(y, X).fit()


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


# --- Halaman Pemodelan
def show_modeling_page():
    local_css()

    # Header
    st.markdown("""
    <div style='background: linear-gradient(90deg, #1a5fb4, #3584e4); 
                padding: 18px; border-radius: 12px; margin-bottom: 25px;'>
        <h1 style='color: white; margin: 0;'>📉 Pemodelan Regresi Sederhana</h1>
        <p style='color: #f1f1f1; margin: 0;'>PKB & BBNKB terhadap variabel makro (2018–2024)</p>
    </div>
    """, unsafe_allow_html=True)

    # Pilihan Variabel
    response = st.selectbox("📌 Pilih Variabel Respon", ["PKB", "BBNKB"])
    predictors = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]
    predictor = st.selectbox("📌 Pilih Variabel Prediktor (Makroekonomi)", predictors)

    # Jalankan regresi
    model = run_regression(response, predictor)
    coef = model.params[predictor]
    intercept = model.params["const"]
    pval = model.pvalues[predictor]
    r2 = model.rsquared

    # --- Explanation Card untuk Metrics
    with st.expander("ℹ️ Panduan Memahami Metrics Regresi", expanded=False):
        st.markdown("""
        ### 📊 Penjelasan Metrics Regresi

        **1. Koefisien (β - Beta)**
        - **Definisi**: Menunjukkan seberapa besar perubahan pada variabel respon (PKB/BBNKB) jika prediktor (variabel makro) berubah 1 unit
        - **Interpretasi**:
          - Jika β = +500.000.000, maka kenaikan 1% PDRB akan meningkatkan PKB sebesar Rp 500 juta
          - Nilai positif (+): prediktor meningkatkan respon
          - Nilai negatif (-): prediktor menurunkan respon
        - **Contoh**: Koefisien PDRB terhadap PKB = 800M artinya setiap kenaikan 1% PDRB meningkatkan PKB Rp 800M

        **2. R² (R-Squared / Coefficient of Determination)**
        - **Definisi**: Persentase variasi data yang dijelaskan oleh model (0 - 1)
        - **Interpretasi**:
          - **R² > 0.7**: Model sangat baik menjelaskan data (>70%)
          - **R² 0.4 - 0.7**: Model cukup baik (40-70%)
          - **R² < 0.4**: Model lemah (<40%)
        - **Catatan**: R² tinggi ≠ model bagus untuk prediksi! Dengan hanya 7 data, R² tinggi bisa tanda overfitting
        - **Contoh**: R² = 0.85 artinya 85% variasi PKB dijelaskan oleh PDRB, sisanya 15% oleh faktor lain

        **3. p-value (Probabilitas)**
        - **Definisi**: Probabilitas bahwa hubungan yang ditemukan terjadi secara kebetulan (bukan karena pengaruh nyata)
        - **Interpretasi**:
          - **p < 0.05**: Signifikan secara statistik (hubungan kemungkinan besar nyata) ✅
          - **p > 0.05**: Tidak signifikan (hubungan mungkin kebetulan) ⚠️
        - **Catatan**: Dengan dataset kecil (n=7), p-value harus diinterpretasi hati-hati
        - **Contoh**: p-value = 0.03 artinya hanya 3% kemungkinan hubungan ini terjadi secara kebetulan

        ---
        ### ⚠️ **Peringatan Penting untuk Dataset Kecil**

        Dataset PAD hanya 7 tahun (2018-2024), yang berarti:
        - ✗ **Risiko Overfitting Tinggi**: Model bisa terlalu "pas" dengan data historis tapi gagal prediksi masa depan
        - ✗ **Power Statistik Rendah**: Sulit mendeteksi hubungan nyata karena sampel kecil
        - ✗ **Sensitivitas Outlier**: 1 data outlier dapat mengubah hasil drastis
        - ✓ **Solusi**: Gunakan ensemble modeling, cross-validation, dan interpretasi hati-hati
        """)

    # --- Kartu hasil
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-box metric-koef'>Koefisien<span>{coef:,.2f}</span></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-box metric-r2'>R²<span>{r2:.3f}</span></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-box metric-pval'>p-value<span>{pval:.3f}</span></div>", unsafe_allow_html=True)

    # Persamaan Regresi
    st.subheader("📑 Persamaan Regresi")
    st.info(f"**{response} = {intercept:.3f} + {coef:.3f} × {predictor}**")

    # Interpretasi
    arah = "penambah 📈" if coef > 0 else "pengurang 📉"
    if pval < 0.05:
        st.success(f"✅ {predictor} signifikan sebagai faktor **{arah}** terhadap {response}.")
    else:
        st.warning(f"⚠️ {predictor} tidak signifikan, namun bisa sebagai faktor **{arah}**.")
    
    # Catatan
    st.markdown("""
    <div class='note-box'>
    ⚠️ <strong>Catatan:</strong> Hasil signifikan (p-value) perlu ditafsirkan dengan hati-hati.<br>
    Dataset hanya mencakup 7 tahun (2018–2024), sehingga jumlah observasi sangat terbatas. 
    Hal ini dapat menyebabkan:
    <ul>
    <li>📑 <b>Overfitting</b> karena model menyesuaikan pola jangka pendek.</li>
    <li>🔗 <b>Multikolinearitas</b> antar variabel makro yang tinggi.</li>
    <li>📊 <b>Variabilitas tinggi</b> yang membuat koefisien tidak stabil.</li>
    </ul>
    Dengan keterbatasan ini, analisis lebih lanjut dengan data jangka panjang sangat disarankan.
    </div>
    """, unsafe_allow_html=True)

    # Detail summary
    with st.expander("🔍 Detail Summary Model"):
        st.text(model.summary())

    # Visualisasi scatter + regresi
    st.subheader("📈 Visualisasi Scatterplot dengan Garis Regresi")
    df_sorted = df.sort_values(predictor)
    df_sorted["pred"] = model.predict(sm.add_constant(df_sorted[[predictor]]))

    fig = px.scatter(df, x=predictor, y=response, text="Tahun",
                     title=f"{response} vs {predictor}",
                     color_discrete_sequence=["#1e88e5"])
    fig.add_traces(px.line(df_sorted, x=predictor, y="pred").data)
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

    # ===== MODEL VALIDATION METRICS =====
    st.markdown("---")
    st.header("✅ Validasi Model & Performance Metrics")

    st.markdown("""
    Bagian ini menampilkan metrik validasi untuk mengevaluasi kualitas prediksi model.
    Dengan dataset kecil (n=7), metrik ini membantu memahami ketidakpastian model.
    """)

    # Calculate fitted values and residuals
    y_fitted = model.predict(sm.add_constant(df[[predictor]]))
    y_actual = df[response].values

    # Training metrics
    train_metrics = calculate_all_metrics(y_actual, y_fitted.values)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Training Metrics")
        st.markdown("""
        Metrik pada data yang digunakan untuk melatih model:
        """)

        # Display metrics
        metrics_df = pd.DataFrame({
            'Metric': list(train_metrics.keys()),
            'Value': [f"{v:,.2f}" for v in train_metrics.values()]
        })
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        # Interpretations
        r2_cat, r2_desc = interpret_r2(train_metrics['R²'])
        mape_cat, mape_desc = interpret_mape(train_metrics['MAPE (%)'])

        st.info(f"""
        **R² Interpretation**: {r2_cat}
        {r2_desc}

        **MAPE Interpretation**: {mape_cat}
        {mape_desc}
        """)

        # Explanation
        with st.expander("ℹ️ Penjelasan Metrics"):
            st.markdown("""
            **RMSE (Root Mean Squared Error)**:
            - Rata-rata error dalam satuan asli (Rupiah)
            - Semakin kecil semakin baik
            - Sensitif terhadap outlier

            **MAE (Mean Absolute Error)**:
            - Rata-rata error absolut
            - Lebih robust terhadap outlier dibanding RMSE
            - Interpretasi lebih mudah

            **MAPE (Mean Absolute Percentage Error)**:
            - Error dalam bentuk persentase
            - Mudah dipahami (5% = error 5%)
            - < 10% = sangat baik, < 20% = baik

            **R² (Coefficient of Determination)**:
            - Proporsi variasi yang dijelaskan (0-1)
            - 0.7-1.0 = kuat, 0.4-0.7 = sedang, <0.4 = lemah
            """)

    with col2:
        st.subheader("🔄 Cross-Validation (LOOCV)")
        st.markdown("""
        Leave-One-Out Cross-Validation: Melatih model n kali,
        setiap kali meninggalkan 1 observasi untuk testing.
        """)

        # Perform LOOCV
        with st.spinner("Running cross-validation..."):
            cv_results = leave_one_out_cross_validation(df, response, predictor)

        # Display CV metrics
        cv_metrics_df = pd.DataFrame({
            'Metric': list(cv_results['metrics'].keys()),
            'Value': [f"{v:,.2f}" for v in cv_results['metrics'].values()]
        })
        st.dataframe(cv_metrics_df, use_container_width=True, hide_index=True)

        # Comparison
        improvement = ((train_metrics['MAPE (%)'] - cv_results['metrics']['MAPE (%)']) /
                      train_metrics['MAPE (%)'] * 100)

        if abs(improvement) < 10:
            st.success(f"✅ Model stabil! CV MAPE hanya berbeda {abs(improvement):.1f}% dari training.")
        elif improvement > 0:
            st.warning(f"⚠️ Model sedikit overfit. CV MAPE lebih buruk {abs(improvement):.1f}%.")
        else:
            st.info(f"💡 CV MAPE lebih baik {abs(improvement):.1f}%, kemungkinan kebetulan.")

    # ===== BACKTESTING =====
    st.markdown("---")
    st.subheader("⏮️ Backtesting: Train on Past, Test on Recent")

    st.markdown("""
    Backtesting melatih model pada data lama (2018-2022) dan menguji pada data baru (2023-2024).
    Ini mensimulasikan performa model jika digunakan untuk prediksi real-time.
    """)

    # Perform backtesting
    with st.spinner("Running backtest..."):
        backtest_results = backtest_model(df, response, predictor, test_years=2)

    col1, col2 = st.columns([2, 1])

    with col1:
        # Backtest visualization
        fig_backtest = go.Figure()

        # Actual values
        fig_backtest.add_trace(go.Scatter(
            x=backtest_results['test_years'],
            y=backtest_results['y_test'],
            mode='lines+markers',
            name='Actual (Test Set)',
            line=dict(color='#1976d2', width=3),
            marker=dict(size=10)
        ))

        # Predicted values
        fig_backtest.add_trace(go.Scatter(
            x=backtest_results['test_years'],
            y=backtest_results['y_pred'],
            mode='lines+markers',
            name='Predicted',
            line=dict(color='#f57c00', width=3, dash='dash'),
            marker=dict(size=10, symbol='diamond')
        ))

        fig_backtest.update_layout(
            title=f"Backtest: {response} Actual vs Predicted (2023-2024)",
            xaxis_title="Tahun",
            yaxis_title=f"{response} (Rupiah)",
            template="plotly_white",
            hovermode='x unified',
            yaxis_tickformat=",.0f"
        )

        st.plotly_chart(fig_backtest, use_container_width=True)

    with col2:
        st.markdown("**Backtest Metrics:**")
        backtest_metrics_df = pd.DataFrame({
            'Metric': list(backtest_results['metrics'].keys()),
            'Value': [f"{v:,.2f}" for v in backtest_results['metrics'].values()]
        })
        st.dataframe(backtest_metrics_df, use_container_width=True, hide_index=True)

        st.markdown("**Model Parameters:**")
        params_df = pd.DataFrame({
            'Parameter': ['Intercept', 'Coefficient', 'R²', 'p-value'],
            'Value': [
                f"{backtest_results['model_params']['intercept']:,.2f}",
                f"{backtest_results['model_params']['coefficient']:,.2f}",
                f"{backtest_results['model_params']['r2']:.3f}",
                f"{backtest_results['model_params']['p_value']:.3f}"
            ]
        })
        st.dataframe(params_df, use_container_width=True, hide_index=True)

    # Comparison table
    st.markdown("**📋 Perbandingan: Training vs CV vs Backtest**")

    comparison_df = pd.DataFrame({
        'Metric': ['RMSE', 'MAE', 'MAPE (%)', 'R²'],
        'Training': [
            f"{train_metrics['RMSE']:,.0f}",
            f"{train_metrics['MAE']:,.0f}",
            f"{train_metrics['MAPE (%)']:.2f}",
            f"{train_metrics['R²']:.3f}"
        ],
        'Cross-Val (LOOCV)': [
            f"{cv_results['metrics']['RMSE']:,.0f}",
            f"{cv_results['metrics']['MAE']:,.0f}",
            f"{cv_results['metrics']['MAPE (%)']:.2f}",
            f"{cv_results['metrics']['R²']:.3f}"
        ],
        'Backtest (2023-24)': [
            f"{backtest_results['metrics']['RMSE']:,.0f}",
            f"{backtest_results['metrics']['MAE']:,.0f}",
            f"{backtest_results['metrics']['MAPE (%)']:.2f}",
            f"{backtest_results['metrics']['R²']:.3f}"
        ]
    })

    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.warning("""
    ⚠️ **Catatan Penting**:
    Dengan hanya 7 observasi, metrik validasi memiliki **variance tinggi** dan **reliability rendah**.
    Hasil backtest hanya menggunakan 2 data point untuk testing, sehingga hasilnya sangat sensitif terhadap nilai-nilai tersebut.
    Gunakan metrik ini sebagai **indikator**, bukan **bukti definitif** kualitas model.
    """)


def app():
    show_modeling_page()


if __name__ == "__main__":
    app()
