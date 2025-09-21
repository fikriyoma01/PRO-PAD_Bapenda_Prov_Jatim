import streamlit as st
import plotly.express as px

from data_loader import load_pad_historis


def local_css():
    st.markdown(
        """
        <style>
            .metric-card {
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.08);
                transition: transform 0.2s ease;
            }
            .metric-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 6px 14px rgba(0,0,0,0.15);
            }
            .metric-low {
                background: linear-gradient(135deg, #fff3e0, #ffe0b2);
                border-left: 6px solid #ff9800;
            }
            .metric-avg {
                background: linear-gradient(135deg, #e3f2fd, #bbdefb);
                border-left: 6px solid #1e88e5;
            }
            .metric-high {
                background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
                border-left: 6px solid #43a047;
            }
            .metric-card h4 {
                margin: 0;
                font-size: 1.1rem;
            }
            .metric-card p {
                margin: 0;
                font-size: 1.3rem;
                font-weight: bold;
            }

            div[data-baseweb="select"] > div {
                border-radius: 8px !important;
                border: 2px solid #1a5fb4 !important;
                background-color: #f0f6ff !important;
            }
            div[data-baseweb="select"] > div:hover {
                border-color: #0d47a1 !important;
                background-color: #e3f2fd !important;
            }

            [data-testid="stDataFrame"] td,
            [data-testid="stDataFrame"] th {
                text-align: center !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Fungsi format Rupiah
def format_rupiah(val):
    return "Rp {:,}".format(int(val)).replace(",", ".")


def show_dataset_page():
    df = load_pad_historis()
    local_css()

    st.markdown(
        """
        <div style='background: linear-gradient(90deg, #1a5fb4, #3584e4);
                    padding: 18px; border-radius: 12px; margin-bottom: 25px;'>
            <h1 style='color: white; margin: 0;'>📑 Dataset Historis 2018-2024</h1>
            <p style='color: #f1f1f1; margin: 0;'>PKB, BBNKB, dan variabel makroekonomi</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("💰 Ringkasan PKB & BBNKB")
    for var in ["PKB", "BBNKB"]:
        st.markdown(f"### 📌 {var}")
        lowest_val = df[var].min()
        lowest_year = df.loc[df[var].idxmin(), "Tahun"]
        average_val = df[var].mean()
        highest_val = df[var].max()
        highest_year = df.loc[df[var].idxmax(), "Tahun"]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div class='metric-card metric-low'>
                    <h4>🔻 Nilai Terendah</h4>
                    <p>{format_rupiah(lowest_val)}<br><span style='font-size:1rem;'>({lowest_year})</span></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(f"""
            <div class='metric-card metric-avg'>
                <h4>📊 Rata-rata</h4>
                <p>{format_rupiah(average_val)}<br><span style="font-size:1rem;">(2018–2024)</span></p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class='metric-card metric-high'>
                <h4>🔺 Nilai Tertinggi</h4>
                <p>{format_rupiah(highest_val)}<br><span style="font-size:1rem;">({highest_year})</span></p>
            </div>
            """, unsafe_allow_html=True)

    # --- Data Lengkap
    st.subheader("📂 Data Lengkap")
    st.dataframe(df, use_container_width=True)

    # --- Visualisasi Tren PKB & BBNKB
    st.subheader("📈 Tren PKB & BBNKB")
    fig = px.line(
        df,
        x="Tahun",
        y=["PKB", "BBNKB"],
        markers=True,
        line_shape="spline",
        labels={"value": "Rupiah", "variable": "Jenis Pajak"},
        title="Tren PKB & BBNKB (2018-2024)",
        color_discrete_map={"PKB": "#1e88e5", "BBNKB": "#43a047"},
    )
    fig.update_layout(template="plotly_white", yaxis_tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    # --- Visualisasi Makro
    st.subheader("📊 Variabel Makroekonomi")
    macro_vars = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]
    selected = st.selectbox("Pilih variabel makro untuk divisualisasikan", macro_vars)

    fig2 = px.bar(
        df,
        x="Tahun",
        y=selected,
        text=selected,
        title=f"Perkembangan {selected} (2018-2024)",
        color=selected,
        color_continuous_scale="Blues",
    )
    fig2.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig2.update_layout(template="plotly_white", yaxis_title=selected)
    st.plotly_chart(fig2, use_container_width=True)


def app():
    show_dataset_page()


if __name__ == "__main__":
    app()
