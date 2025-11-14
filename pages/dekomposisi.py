import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go
from datetime import datetime

from data_loader import load_pad_historis, get_pkb_inputs, get_bbnkb_inputs, map_inputs
from utils.export_utils import create_comprehensive_excel_report

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
    
# =========================
# Data historis 2018-2024
# =========================
df_hist = load_pad_historis()
MACROS = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]


# ============== Util ==============
def predict_macro_linear(var: str, year: int) -> float:
    """Prediksi makro dengan regresi linier sederhana: var ~ Tahun (2018-2024)."""
    X = sm.add_constant(df_hist[["Tahun"]])
    y = df_hist[var]
    model = sm.OLS(y, X).fit()
    return float(model.predict([1, year])[0])


def coef_vs(response_col: str, var: str) -> float:
    """Koefisien beta dari regresi linier sederhana response_col ~ var."""
    X = sm.add_constant(df_hist[[var]])
    y = df_hist[response_col]
    model = sm.OLS(y, X).fit()
    return float(model.params[var])


def compute_macro_impact(year: int, baseline_macro: dict, response_col: str = "PKB") -> tuple[pd.DataFrame, float, float, dict]:
    """Hitung prediksi makro dan dampak rupiah ke variabel tertentu."""
    rows = []
    total_plus, total_minus = 0.0, 0.0
    pred_macro = {}

    for var in MACROS:
        base_val = baseline_macro[var]
        pred_val = predict_macro_linear(var, year)
        beta = coef_vs(response_col, var)
        delta_val = pred_val - base_val
        impact_rp = beta * delta_val

        if impact_rp >= 0:
            total_plus += impact_rp
        else:
            total_minus += impact_rp

        pred_macro[var] = pred_val
        rows.append({
            "Variabel": var,
            "Baseline": base_val,
            f"Prediksi {year}": pred_val,
            "Δ Selisih": delta_val,
            "Dampak (Rp)": impact_rp
        })

    df_macro = pd.DataFrame(rows)
    return df_macro, total_plus, total_minus, pred_macro


def create_waterfall_chart(df_dekom: pd.DataFrame, title: str, year: int) -> go.Figure:
    """Buat waterfall chart dari DataFrame dekomposisi."""
    # Extract data dari DataFrame
    labels = df_dekom["Faktor"].tolist()
    values = df_dekom["Rupiah"].tolist()

    # Tentukan tipe measure untuk setiap bar
    measures = []
    text_values = []

    for i, (label, value) in enumerate(zip(labels, values)):
        # Format text
        if value >= 0:
            text_values.append(f"+{value/1e9:.2f}T")
        else:
            text_values.append(f"{value/1e9:.2f}T")

        # Tentukan measure type
        if "TOTAL POTENSI" in label.upper():
            measures.append("total")
        elif "TARGET" in label.upper():
            measures.append("total")
        elif "SISA" in label.upper():
            measures.append("total")
        elif "TOTAL PENAMBAH" in label.upper():
            measures.append("total")
        elif "TOTAL PENGURANG" in label.upper():
            measures.append("total")
        else:
            measures.append("relative")

    # Create waterfall chart
    fig = go.Figure(go.Waterfall(
        name="Decomposition",
        orientation="v",
        measure=measures,
        x=labels,
        textposition="outside",
        text=text_values,
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#ef5350"}},  # Red for negative
        increasing={"marker": {"color": "#66bb6a"}},  # Green for positive
        totals={"marker": {"color": "#42a5f5"}},  # Blue for totals
    ))

    fig.update_layout(
        title=f"{title}<br><sub>Nilai dalam Miliar Rupiah</sub>",
        showlegend=False,
        height=500,
        xaxis=dict(
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="Nilai (Rupiah)",
            tickformat=",.0f"
        ),
        template="plotly_white"
    )

    return fig


def rupiah_style(df: pd.DataFrame, colmap: dict):
    """Helper apply style format per kolom agar aman dari kolom string."""
    return df.style.format(colmap)


def format_rupiah_value(value: float) -> str:
    prefix = "-" if value < 0 else ""
    formatted = f"Rp{abs(value):,.0f}".replace(",", ".")
    return f"{prefix}{formatted}"


def dekomposisi_pkb_with_macro(year: int, inputs_df: pd.DataFrame, baseline_macro: dict) -> tuple[pd.DataFrame, float, pd.DataFrame, dict]:
    """Buat tabel dekomposisi PKB lengkap dengan dampak makro."""
    values = map_inputs(inputs_df)
    total_penambah = inputs_df[inputs_df["kategori"] == "penambah"]["nilai"].sum()
    total_pengurang = inputs_df[inputs_df["kategori"] == "pengurang"]["nilai"].sum()

    df_macro, dampak_plus, dampak_minus, pred_macro = compute_macro_impact(year, baseline_macro)
    total_potensi = total_penambah - total_pengurang + dampak_plus + dampak_minus

    faktor = [
        "Potensi Awal Tahun",
        "RODA 4 (Jan-Des)",
        "RODA 2 (Jan-Des)",
        "Prediksi Pencairan Tunggakan",
        "Prediksi Mutasi Masuk (Jan-Des)",
        "TOTAL PENAMBAH",
        "Proyeksi tidak daftar ulang (Jan-Des)",
        "Proyeksi Mutasi Keluar (Jan-Des)",
        "Potensi Pembebasan Pajak Daerah",
        "TOTAL PENGURANG",
        "Dampak Makro (+)",
        "Dampak Makro (-)",
        f"TOTAL POTENSI PKB TAHUN {year}",
        f"TARGET R-APBD {year}",
        "SISA POTENSI",
    ]

    rupiah = [
        values.get("Potensi Awal", 0),
        values.get("R4", 0),
        values.get("R2", 0),
        values.get("Tunggakan", 0),
        values.get("Mutasi Masuk", 0),
        total_penambah,
        -values.get("TDR", 0),
        -values.get("Mutasi Keluar", 0),
        -values.get("Pembebasan", 0),
        -total_pengurang,
        dampak_plus,
        dampak_minus,
        total_potensi,
        values.get("Target", 0),
        total_potensi - values.get("Target", 0),
    ]

    df_dekom = pd.DataFrame({"Faktor": faktor, "Rupiah": rupiah})
    return df_dekom, total_potensi, df_macro, pred_macro


def dekomposisi_bbnkb_table(
    year: int,
    inputs_df: pd.DataFrame,
    macro_plus: float = 0.0,
    macro_minus: float = 0.0,
) -> pd.DataFrame:
    """Bangun tabel dekomposisi BBNKB termasuk dampak makro."""
    values = map_inputs(inputs_df)

    if year == 2025:
        total_struktural = values.get("Total", 0.0)
        target = values.get("Target", 0.0)
        total_potensi = total_struktural + macro_plus + macro_minus

        faktor = [
            "RODA 4 (Jan-Des)",
            "RODA 2 (Jan-Des)",
            "TOTAL POTENSI BBN I TAHUN 2025",
            "Dampak Makro (+)",
            "Dampak Makro (-)",
            "TOTAL POTENSI BBNKB TAHUN 2025",
            "TARGET R-APBD 2025",
            "SISA POTENSI",
        ]
        rupiah = [
            values.get("R4", 0.0),
            values.get("R2", 0.0),
            total_struktural,
            macro_plus,
            macro_minus,
            total_potensi,
            target,
            total_potensi - target,
        ]
    else:
        total = values.get("Total", 0.0)
        pengurang = values.get("Pengurang", 0.0)
        target = values.get("Target", 0.0)
        neto = total - pengurang
        total_potensi = neto + macro_plus + macro_minus

        faktor = [
            "Roda 4 (Jan-Des 2026)",
            "Roda 2 (Jan-Des 2026)",
            "Total Potensi Kendaraan Baru Tahun 2026",
            "Potensi BBN II Tidak Dipungut",
            "Total Pengurang",
            "Potensi Neto Setelah Pengurang",
            "Dampak Makro (+)",
            "Dampak Makro (-)",
            "Total Potensi BBNKB Tahun 2026",
            "Target BBNKB pada R-APBD 2026",
            "Sisa Potensi",
        ]
        rupiah = [
            values.get("R4", 0.0),
            values.get("R2", 0.0),
            total,
            pengurang,
            pengurang,
            neto,
            macro_plus,
            macro_minus,
            total_potensi,
            target,
            total_potensi - target,
        ]

    return pd.DataFrame({"Faktor": faktor, "Rupiah": rupiah})

# =========================
# PAGE RENDER
# =========================
def show_decomposition_tab():
    local_css()
    st.markdown("""
    <div style='background:linear-gradient(90deg,#1a5fb4,#3584e4);
                padding:15px;border-radius:10px;margin-bottom:20px;'>
        <h1 style='color:white;margin:0;'>⚖️ Dekomposisi & Prediksi Makro – PKB & BBNKB (2025–2026)</h1>
        <p style='color:#eef; margin:0;'>Menggabungkan komponen teknis + dampak variabel makro ke rupiah</p>
    </div>
    """, unsafe_allow_html=True)

    pkb_inputs_2025 = get_pkb_inputs(2025)
    pkb_inputs_2026 = get_pkb_inputs(2026)
    bbn_inputs_2025 = get_bbnkb_inputs(2025)
    bbn_inputs_2026 = get_bbnkb_inputs(2026)

    baseline_2024 = {v: float(df_hist.iloc[-1][v]) for v in MACROS}
    df_pkb25, total_pkb25, df_macro_pkb25, pred_macro25 = dekomposisi_pkb_with_macro(2025, pkb_inputs_2025, baseline_2024)

    baseline_2025_for_2026 = {k: float(v) for k, v in pred_macro25.items()}
    df_pkb26, total_pkb26, df_macro_pkb26, _ = dekomposisi_pkb_with_macro(2026, pkb_inputs_2026, baseline_2025_for_2026)

    df_macro_bbn25, bbn_macro_plus25, bbn_macro_minus25, _ = compute_macro_impact(2025, baseline_2024, response_col="BBNKB")
    df_macro_bbn26, bbn_macro_plus26, bbn_macro_minus26, _ = compute_macro_impact(2026, baseline_2025_for_2026, response_col="BBNKB")

    bbn_vals_2025 = map_inputs(bbn_inputs_2025)
    bbn_vals_2026 = map_inputs(bbn_inputs_2026)
    bbn_total_2025 = bbn_vals_2025.get("Total", 0.0) + bbn_macro_plus25 + bbn_macro_minus25
    bbn_net_2026 = bbn_vals_2026.get("Total", 0.0) - bbn_vals_2026.get("Pengurang", 0.0)
    bbn_total_2026 = bbn_net_2026 + bbn_macro_plus26 + bbn_macro_minus26

    ringkas = pd.DataFrame(
        {
            "Tahun": [2025, 2025, 2026, 2026],
            "Jenis": ["PKB", "BBNKB", "PKB", "BBNKB"],
            "Total Potensi": [
                total_pkb25,
                bbn_total_2025,
                total_pkb26,
                bbn_total_2026,
            ],
            "Target": [
                map_inputs(pkb_inputs_2025).get("Target", 0),
                bbn_vals_2025.get("Target", 0),
                map_inputs(pkb_inputs_2026).get("Target", 0),
                bbn_vals_2026.get("Target", 0),
            ],
        }
    )
    ringkas["Sisa Potensi"] = ringkas["Total Potensi"] - ringkas["Target"]

    st.subheader("📌 Ringkasan Total & Target")
    st.dataframe(
        rupiah_style(
            ringkas,
            {
                "Total Potensi": "Rp{:,.0f}",
                "Target": "Rp{:,.0f}",
                "Sisa Potensi": "Rp{:,.0f}",
            },
        ),
        use_container_width=True,
    )

    # Highlight cepat
    for _, row in ringkas.iterrows():
        tag = "✅" if row["Sisa Potensi"] >= 0 else "⚠️"
        st.write(f"{tag} **{row['Jenis']} {int(row['Tahun'])}**: Sisa Potensi **Rp{row['Sisa Potensi']:,.0f}**")

    st.markdown("---")

    # ====== DETAIL 2025 ======
    st.header("📅 Tahun 2025")

    st.subheader("A. Dekomposisi PKB 2025 (termasuk dampak makro)")
    st.dataframe(
        rupiah_style(df_pkb25, {"Rupiah": "Rp{:,.0f}"}),
        use_container_width=True
    )

    # Waterfall Chart untuk PKB 2025
    with st.expander("📊 Lihat Waterfall Chart - Visualisasi Dekomposisi PKB 2025", expanded=True):
        fig_pkb25 = create_waterfall_chart(df_pkb25, "Waterfall Dekomposisi PKB 2025", 2025)
        st.plotly_chart(fig_pkb25, use_container_width=True)
        st.caption("🟢 Hijau = Penambah | 🔴 Merah = Pengurang | 🔵 Biru = Total")

    st.subheader("B. Prediksi Variabel Makro & Dampak ke PKB (2025)")
    st.caption("Baseline = nilai aktual 2024; Prediksi dihitung dari regresi linear variabel ~ Tahun (2018–2024)")
    st.dataframe(
        rupiah_style(
            df_macro_pkb25.rename(columns={"Baseline": "Baseline 2024"}),
            {
                "Baseline 2024": "{:,.2f}",
                "Prediksi 2025": "{:,.2f}",
                "Selisih": "{:,.2f}",
                "Dampak (Rp)": "Rp{:,.0f}",
            },
        ),
        use_container_width=True,
    )

    st.subheader("C. Dekomposisi BBNKB 2025 (termasuk dampak makro)")
    df_bbn25 = dekomposisi_bbnkb_table(2025, bbn_inputs_2025, bbn_macro_plus25, bbn_macro_minus25)
    st.dataframe(rupiah_style(df_bbn25, {"Rupiah": "Rp{:,.0f}"}), use_container_width=True)

    # Waterfall Chart untuk BBNKB 2025
    with st.expander("📊 Lihat Waterfall Chart - Visualisasi Dekomposisi BBNKB 2025", expanded=True):
        fig_bbn25 = create_waterfall_chart(df_bbn25, "Waterfall Dekomposisi BBNKB 2025", 2025)
        st.plotly_chart(fig_bbn25, use_container_width=True)
        st.caption("🟢 Hijau = Penambah | 🔴 Merah = Pengurang | 🔵 Biru = Total")

    st.subheader("D. Prediksi Variabel Makro & Dampak ke BBNKB (2025)")
    st.caption("Baseline = nilai aktual 2024; prediksi makro menggunakan pendekatan yang sama seperti PKB.")
    st.dataframe(
        rupiah_style(
            df_macro_bbn25.rename(columns={"Baseline": "Baseline 2024"}),
            {
                "Baseline 2024": "{:,.2f}",
                "Prediksi 2025": "{:,.2f}",
                "Selisih": "{:,.2f}",
                "Dampak (Rp)": "Rp{:,.0f}",
            },
        ),
        use_container_width=True,
    )
    st.info(f"Dampak makro bersih ke BBNKB 2025: {format_rupiah_value(bbn_macro_plus25 + bbn_macro_minus25)}")

    st.markdown("---")

    # ====== DETAIL 2026 ======
    st.header("📅 Tahun 2026")

    st.subheader("A. Dekomposisi PKB 2026 (termasuk dampak makro)")
    st.dataframe(rupiah_style(df_pkb26, {"Rupiah": "Rp{:,.0f}"}), use_container_width=True)

    # Waterfall Chart untuk PKB 2026
    with st.expander("📊 Lihat Waterfall Chart - Visualisasi Dekomposisi PKB 2026", expanded=True):
        fig_pkb26 = create_waterfall_chart(df_pkb26, "Waterfall Dekomposisi PKB 2026", 2026)
        st.plotly_chart(fig_pkb26, use_container_width=True)
        st.caption("🟢 Hijau = Penambah | 🔴 Merah = Pengurang | 🔵 Biru = Total")

    st.subheader("B. Prediksi Variabel Makro & Dampak ke PKB (2026)")
    st.caption("Baseline 2026 = hasil prediksi makro 2025 (bukan 2024) • Prediksi 2026 dihitung dari regresi variabel ~ Tahun (2018-2025)")
    st.dataframe(
        rupiah_style(
            df_macro_pkb26.rename(columns={"Baseline": "Baseline 2025"}),
            {
                "Baseline 2025": "{:,.2f}",
                "Prediksi 2026": "{:,.2f}",
                "Selisih": "{:,.2f}",
                "Dampak (Rp)": "Rp{:,.0f}",
            },
        ),
        use_container_width=True,
    )

    st.subheader("C. Dekomposisi BBNKB 2026 (termasuk dampak makro)")
    df_bbn26 = dekomposisi_bbnkb_table(2026, bbn_inputs_2026, bbn_macro_plus26, bbn_macro_minus26)
    st.dataframe(rupiah_style(df_bbn26, {"Rupiah": "Rp{:,.0f}"}), use_container_width=True)

    # Waterfall Chart untuk BBNKB 2026
    with st.expander("📊 Lihat Waterfall Chart - Visualisasi Dekomposisi BBNKB 2026", expanded=True):
        fig_bbn26 = create_waterfall_chart(df_bbn26, "Waterfall Dekomposisi BBNKB 2026", 2026)
        st.plotly_chart(fig_bbn26, use_container_width=True)
        st.caption("🟢 Hijau = Penambah | 🔴 Merah = Pengurang | 🔵 Biru = Total")

    st.subheader("D. Prediksi Variabel Makro & Dampak ke BBNKB (2026)")
    st.caption("Baseline 2026 = hasil prediksi makro 2025; prediksi mengikuti pendekatan PKB.")
    st.dataframe(
        rupiah_style(
            df_macro_bbn26.rename(columns={"Baseline": "Baseline 2025"}),
            {
                "Baseline 2025": "{:,.2f}",
                "Prediksi 2026": "{:,.2f}",
                "Selisih": "{:,.2f}",
                "Dampak (Rp)": "Rp{:,.0f}",
            },
        ),
        use_container_width=True,
    )
    st.info(f"Dampak makro bersih ke BBNKB 2026: {format_rupiah_value(bbn_macro_plus26 + bbn_macro_minus26)}")

    # ====== EXPORT TO EXCEL ======
    st.markdown("---")
    st.header("📥 Download Comprehensive Report")

    st.markdown("""
    **Download laporan lengkap dalam format Excel** yang mencakup:
    - ✅ Metadata & Informasi Report
    - ✅ Metodologi & Assumptions
    - ✅ Data Historis 2018-2024
    - ✅ Dekomposisi PKB & BBNKB 2025-2026
    - ✅ Prediksi Variabel Makroekonomi
    - ✅ Glossary Istilah Teknis

    File Excel akan memiliki multiple sheets dengan formatting profesional.
    """)

    # Create projection summary for export
    df_proyeksi_summary = pd.DataFrame({
        'Tahun': [2025, 2026],
        'PKB Proyeksi': [total_pkb25, total_pkb26],
        'BBNKB Proyeksi': [bbn_total_2025, bbn_total_2026],
        'PKB Target': [
            map_inputs(pkb_inputs_2025).get("Target", 0),
            map_inputs(pkb_inputs_2026).get("Target", 0)
        ],
        'BBNKB Target': [
            bbn_vals_2025.get("Target", 0),
            bbn_vals_2026.get("Target", 0)
        ]
    })

    # Generate Excel report
    try:
        excel_bytes = create_comprehensive_excel_report(
            df_historis=df_hist,
            df_proyeksi=df_proyeksi_summary,
            df_pkb_2025=df_pkb25,
            df_pkb_2026=df_pkb26,
            df_bbnkb_2025=df_bbn25,
            df_bbnkb_2026=df_bbn26,
            model_metrics={
                'Total Proyeksi PKB 2025': f"Rp {total_pkb25:,.0f}",
                'Total Proyeksi PKB 2026': f"Rp {total_pkb26:,.0f}",
                'Total Proyeksi BBNKB 2025': f"Rp {bbn_total_2025:,.0f}",
                'Total Proyeksi BBNKB 2026': f"Rp {bbn_total_2026:,.0f}",
                'Dataset Size': '7 years (2018-2024)',
                'Methodology': 'Linear Regression + Macroeconomic Impact'
            }
        )

        # Download button
        filename = f"PAD_Comprehensive_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        st.download_button(
            label="📥 Download Excel Report (Comprehensive)",
            data=excel_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download comprehensive PAD analysis report with all data, methodology, and projections"
        )

        st.success("✅ Report siap untuk di-download! Klik button di atas untuk mengunduh.")

    except Exception as e:
        st.error(f"❌ Error generating Excel report: {str(e)}")
        st.caption("Mohon hubungi administrator jika error terus berlanjut.")


def app():
    show_decomposition_tab()


if __name__ == "__main__":
    app()
