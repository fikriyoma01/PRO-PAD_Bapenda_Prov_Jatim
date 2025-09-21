import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.express as px

from data_loader import load_pad_historis

# Data historis (2018-2024) dari layer CSV
df = load_pad_historis()


def run_regression(response: str, predictor: str):
    X = sm.add_constant(df[[predictor]])
    y = df[response]
    return sm.OLS(y, X).fit()


def show_projection_page():
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

    # --- Prediksi 2025 & 2026 untuk respon
    proj = {}
    for tahun, val in zip([2025, 2026], [val_2025, val_2026]):
        pred = model.predict([1, val])[0]
        proj[tahun] = {
            "Pesimis (Batas Atas)": pred * 1.05,
            "Moderat (Rata-rata)": pred,
            "Optimis (Batas Bawah)": pred * 0.95
        }

    # --- Tabel hasil proyeksi
    st.subheader("📊 Hasil Proyeksi")
    proj_df = pd.DataFrame(proj).T
    st.dataframe(proj_df.style.format("{:,.0f}"), use_container_width=True)

    # --- Visualisasi
    st.subheader("📈 Visualisasi Proyeksi")
    fig = px.line(
        proj_df.reset_index().melt(id_vars="index", var_name="Skenario", value_name="Proyeksi"),
        x="index", y="Proyeksi", color="Skenario", markers=True,
        title=f"Proyeksi {response} 2025–2026 ({predictor} sebagai prediktor)"
    )
    fig.update_layout(
        xaxis=dict(tickmode="array", tickvals=[2025, 2026], ticktext=["2025", "2026"]),
        template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)


def app():
    show_projection_page()


if __name__ == "__main__":
    app()
