import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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
    fig.update_yaxes(rangemode='tozero')
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

    # --- Correlation Heatmap
    st.markdown("---")
    st.subheader("🔥 Correlation Heatmap - Analisis Hubungan Antar Variabel")

    with st.expander("ℹ️ Apa itu Correlation Heatmap?", expanded=False):
        st.markdown("""
        **Correlation Heatmap** menunjukkan seberapa kuat hubungan antar variabel dalam dataset.

        **Cara Membaca:**
        - **+1.0** (Merah Gelap): Korelasi positif sempurna - kedua variabel bergerak searah
        - **0.0** (Putih): Tidak ada korelasi linear
        - **-1.0** (Biru Gelap): Korelasi negatif sempurna - kedua variabel bergerak berlawanan arah

        **Contoh Interpretasi:**
        - Jika PKB dan PDRB memiliki korelasi +0.85, artinya ketika PDRB naik, PKB cenderung naik juga
        - Jika BBNKB dan TPT memiliki korelasi -0.60, artinya ketika TPT naik, BBNKB cenderung turun

        **Multicollinearity Warning**: Jika dua variabel makro memiliki korelasi > 0.8 atau < -0.8,
        ini menunjukkan multicollinearity yang dapat menyebabkan model regresi tidak stabil.
        """)

    # Pilih variabel untuk correlation analysis
    all_vars = ["PKB", "BBNKB"] + macro_vars
    corr_df = df[all_vars].corr()

    # Create heatmap
    fig_corr = go.Figure(data=go.Heatmap(
        z=corr_df.values,
        x=corr_df.columns,
        y=corr_df.columns,
        colorscale='RdBu_r',  # Red-White-Blue reversed
        zmid=0,  # Center at 0
        text=corr_df.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(
            title="Korelasi",
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=['-1.0<br>Negatif<br>Kuat', '-0.5', '0.0<br>Tidak ada', '+0.5', '+1.0<br>Positif<br>Kuat']
        ),
        hoverongaps=False,
        hovertemplate='%{y} vs %{x}<br>Korelasi: %{z:.3f}<extra></extra>'
    ))

    fig_corr.update_layout(
        title="Correlation Matrix: PKB, BBNKB & Variabel Makroekonomi<br><sub>Dataset 2018-2024 (n=7 tahun)</sub>",
        xaxis=dict(
            tickangle=-45,
            side='bottom',
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            tickfont=dict(size=10)
        ),
        width=800,
        height=700,
        template="plotly_white"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    # Highlight strong correlations
    st.subheader("🔍 Temuan Korelasi Signifikan")

    # Find strong correlations with PKB and BBNKB
    pkb_corr = corr_df['PKB'].drop('PKB').sort_values(ascending=False)
    bbnkb_corr = corr_df['BBNKB'].drop('BBNKB').sort_values(ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**📊 Korelasi dengan PKB:**")
        for var, corr_val in pkb_corr.items():
            if var != 'BBNKB':  # Skip BBNKB
                emoji = "🔴" if corr_val > 0.5 else "🔵" if corr_val < -0.5 else "⚪"
                strength = "Kuat" if abs(corr_val) > 0.7 else "Sedang" if abs(corr_val) > 0.4 else "Lemah"
                direction = "positif" if corr_val > 0 else "negatif"
                st.write(f"{emoji} **{var}**: {corr_val:.3f} ({strength} {direction})")

    with col2:
        st.markdown("**📊 Korelasi dengan BBNKB:**")
        for var, corr_val in bbnkb_corr.items():
            if var != 'PKB':  # Skip PKB
                emoji = "🔴" if corr_val > 0.5 else "🔵" if corr_val < -0.5 else "⚪"
                strength = "Kuat" if abs(corr_val) > 0.7 else "Sedang" if abs(corr_val) > 0.4 else "Lemah"
                direction = "positif" if corr_val > 0 else "negatif"
                st.write(f"{emoji} **{var}**: {corr_val:.3f} ({strength} {direction})")

    # Multicollinearity warning
    st.markdown("---")
    st.markdown("**⚠️ Multicollinearity Check (Variabel Makro)**")

    high_corr_pairs = []
    for i in range(len(macro_vars)):
        for j in range(i+1, len(macro_vars)):
            corr_value = corr_df.loc[macro_vars[i], macro_vars[j]]
            if abs(corr_value) > 0.7:
                high_corr_pairs.append((macro_vars[i], macro_vars[j], corr_value))

    if high_corr_pairs:
        st.warning("🚨 **Multicollinearity Detected!** Pasangan variabel berikut memiliki korelasi tinggi (>0.7):")
        for var1, var2, corr_val in high_corr_pairs:
            st.write(f"- **{var1}** ↔ **{var2}**: {corr_val:.3f}")
        st.caption("⚡ High multicollinearity dapat menyebabkan koefisien regresi tidak stabil. Pertimbangkan untuk tidak menggunakan kedua variabel bersamaan dalam model yang sama.")
    else:
        st.success("✅ Tidak ada multicollinearity yang signifikan terdeteksi (threshold: 0.7)")


def app():
    show_dataset_page()


if __name__ == "__main__":
    app()
