import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.express as px

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
    # --- Visualisasi
    st.subheader("📈 Visualisasi Proyeksi")
    hist_series = (
        df[["Tahun", response]]
        .sort_values("Tahun")
        .rename(columns={response: "Nilai"})
    )
    hist_series["Skenario"] = "Aktual"

    proj_long = (
        proj_df.reset_index()
        .rename(columns={"index": "Tahun"})
        .melt(id_vars="Tahun", var_name="Skenario", value_name="Nilai")
    )

    if not hist_series.empty and not proj_long.empty:
        last_year = int(hist_series["Tahun"].max())
        last_value = float(
            hist_series.loc[hist_series["Tahun"] == last_year, "Nilai"].iloc[0]
        )
        bridge_rows = [
            {"Tahun": last_year, "Skenario": scen, "Nilai": last_value}
            for scen in proj_long["Skenario"].unique()
        ]
        proj_long = pd.concat([pd.DataFrame(bridge_rows), proj_long], ignore_index=True)

    combined_chart = pd.concat([hist_series, proj_long], ignore_index=True)
    combined_chart = combined_chart.sort_values(["Tahun", "Skenario"])

    fig = px.line(
        combined_chart,
        x="Tahun",
        y="Nilai",
        color="Skenario",
        markers=True,
        title=f"Proyeksi {response} 2018-2026 ({predictor} sebagai prediktor)",
    )

    line_dash_map = {"Aktual": "solid"}
    for scen in proj_long["Skenario"].unique():
        line_dash_map.setdefault(scen, "dash")

    for trace in fig.data:
        trace.update(line=dict(dash=line_dash_map.get(trace.name, "dash")))

    fig.update_layout(
        template="plotly_white",
        xaxis=dict(tickmode="array", tickvals=list(range(2018, 2027))),
        yaxis=dict(rangemode="tozero"),
    )
    st.plotly_chart(fig, use_container_width=True)


def app():
    show_projection_page()


if __name__ == "__main__":
    app()
