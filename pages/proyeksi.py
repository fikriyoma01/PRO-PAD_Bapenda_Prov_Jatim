import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from data_loader import load_pad_historis

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

    # --- Input nilai makro (default dari prediksi, tapi bisa diubah manual)
    st.subheader("📥 Input Proyeksi Variabel Makro")
    val_2025 = st.number_input(f"{predictor} Tahun 2025", value=float(pred_2025))
    val_2026 = st.number_input(f"{predictor} Tahun 2026", value=float(pred_2026))

    # Jalankan regresi sederhana
    model = run_regression(response, predictor)

    # --- Prediksi 2025 & 2026 untuk respon dengan confidence intervals
    proj = {}
    ci_data = {}  # Untuk menyimpan confidence intervals

    for tahun, val in zip([2025, 2026], [val_2025, val_2026]):
        # Prediksi nilai
        pred_input = np.array([[1, val]])
        pred = model.predict(pred_input)[0]

        # Hitung confidence interval (95%)
        pred_summary = model.get_prediction(pred_input)
        ci = pred_summary.conf_int(alpha=0.05)[0]  # 95% CI

        proj[tahun] = {
            "Pesimis (Batas Atas)": pred * 1.05,
            "Moderat (Rata-rata)": pred,
            "Optimis (Batas Bawah)": pred * 0.95
        }

        ci_data[tahun] = {
            "lower": ci[0],
            "upper": ci[1],
            "mean": pred
        }

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
        sedangkan skenario menggunakan perkalian ±5% dari prediksi tengah.
        """)


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

    # Optimis
    optimis_values = [last_value, proj[2025]["Optimis (Batas Bawah)"], proj[2026]["Optimis (Batas Bawah)"]]
    fig.add_trace(go.Scatter(
        x=proj_years,
        y=optimis_values,
        mode='lines+markers',
        name='Optimis (Batas Bawah)',
        line=dict(color='#4caf50', width=2, dash='dot'),
        marker=dict(size=7)
    ))

    # Pesimis
    pesimis_values = [last_value, proj[2025]["Pesimis (Batas Atas)"], proj[2026]["Pesimis (Batas Atas)"]]
    fig.add_trace(go.Scatter(
        x=proj_years,
        y=pesimis_values,
        mode='lines+markers',
        name='Pesimis (Batas Atas)',
        line=dict(color='#f57c00', width=2, dash='dot'),
        marker=dict(size=7)
    ))

    # Layout
    fig.update_layout(
        title=f"Proyeksi {response} 2018-2026 ({predictor} sebagai prediktor)<br><sub>Area abu-abu = Confidence Interval 95%</sub>",
        xaxis=dict(
            title="Tahun",
            tickmode="array",
            tickvals=list(range(2018, 2027))
        ),
        yaxis=dict(
            title=f"{response} (Miliar Rupiah)",
            rangemode="tozero"
        ),
        template="plotly_white",
        hovermode='x unified',
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


def app():
    show_projection_page()


if __name__ == "__main__":
    app()
