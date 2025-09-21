import streamlit as st
import statsmodels.api as sm
import plotly.express as px

from data_loader import load_pad_historis

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


def app():
    show_modeling_page()


if __name__ == "__main__":
    app()
