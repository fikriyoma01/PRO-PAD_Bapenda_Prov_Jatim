import streamlit as st
import pandas as pd
import statsmodels.api as sm

from data_loader import load_pad_historis, get_pkb_inputs, get_bbnkb_inputs, map_inputs

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


def coef_pkb_vs(var: str) -> float:
    """Koefisien beta dari regresi PKB ~ var (2018-2024)."""
    X = sm.add_constant(df_hist[[var]])
    y = df_hist["PKB"]
    model = sm.OLS(y, X).fit()
    return float(model.params[var])


def compute_macro_impact(year: int, baseline_macro: dict) -> tuple[pd.DataFrame, float, float, dict]:
    """Hitung prediksi makro dan dampak rupiah ke PKB untuk tahun tertentu."""
    rows = []
    total_plus, total_minus = 0.0, 0.0
    pred_macro = {}

    for var in MACROS:
        base_val = baseline_macro[var]
        pred_val = predict_macro_linear(var, year)
        beta = coef_pkb_vs(var)
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


def rupiah_style(df: pd.DataFrame, colmap: dict):
    """Helper apply style format per kolom agar aman dari kolom string."""
    return df.style.format(colmap)


def dekomposisi_pkb_with_macro(year: int, inputs_df: pd.DataFrame, baseline_macro: dict) -> tuple[pd.DataFrame, float, pd.DataFrame, dict]:
    """Buat tabel dekomposisi PKB lengkap dengan dampak makro."""
    values = map_inputs(inputs_df)
    total_penambah = inputs_df[inputs_df["kategori"] == "penambah"]["nilai"].sum()
    total_pengurang = inputs_df[inputs_df["kategori"] == "pengurang"]["nilai"].sum()

    df_macro, dampak_plus, dampak_minus, pred_macro = compute_macro_impact(year, baseline_macro)
    total_potensi = total_penambah - total_pengurang + dampak_plus + dampak_minus

    faktor = [
        "Potensi Awal Tahun",
        "RODA 4 (Jan–Des)",
        "RODA 2 (Jan–Des)",
        "Prediksi Pencairan Tunggakan",
        "Prediksi Mutasi Masuk (Jan–Des)",
        "TOTAL PENAMBAH",
        "Proyeksi tidak daftar ulang (Jan–Des)",
        "Proyeksi Mutasi Keluar (Jan–Des)",
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


def dekomposisi_bbnkb_table(year: int, inputs_df: pd.DataFrame) -> pd.DataFrame:
    """Tabel BBNKB sesuai format Excel."""
    values = map_inputs(inputs_df)

    if year == 2025:
        faktor = [
            "RODA 4 (Jan–Des)",
            "RODA 2 (Jan–Des)",
            "TOTAL POTENSI BBN I TAHUN 2025",
            "TOTAL POTENSI BBNKB TAHUN 2025",
            "TARGET R-APBD 2025",
            "SISA POTENSI",
        ]
        rupiah = [
            values.get("R4", 0),
            values.get("R2", 0),
            values.get("Total", 0),
            values.get("Total", 0),
            values.get("Target", 0),
            values.get("Total", 0) - values.get("Target", 0),
        ]
    else:
        total = values.get("Total", 0)
        pengurang = values.get("Pengurang", 0)
        neto = total - pengurang
        faktor = [
            "Roda 4 (Jan–Des 2026)",
            "Roda 2 (Jan–Des 2026)",
            "Total Potensi Kendaraan Baru Tahun 2026",
            "Potensi BBN II Tidak Dipungut",
            "Total Pengurang",
            "Total Potensi BBNKB Tahun 2026",
            "Target BBNKB pada R-APBD 2026",
            "Sisa Potensi",
        ]
        rupiah = [
            values.get("R4", 0),
            values.get("R2", 0),
            total,
            pengurang,
            pengurang,
            neto,
            values.get("Target", 0),
            neto - values.get("Target", 0),
        ]

    return pd.DataFrame({"Faktor": faktor, "Rupiah": rupiah})


# =========================
# PAGE RENDER
# =========================
def show_decomposition_tab():
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
    df_pkb25, total_pkb25, df_macro25, pred_macro25 = dekomposisi_pkb_with_macro(2025, pkb_inputs_2025, baseline_2024)

    baseline_2025_for_2026 = {k: float(v) for k, v in pred_macro25.items()}
    df_pkb26, total_pkb26, df_macro26, _ = dekomposisi_pkb_with_macro(2026, pkb_inputs_2026, baseline_2025_for_2026)

    bbn_vals_2025 = map_inputs(bbn_inputs_2025)
    bbn_vals_2026 = map_inputs(bbn_inputs_2026)
    bbn_total_2026 = bbn_vals_2026.get("Total", 0) - bbn_vals_2026.get("Pengurang", 0)

    ringkas = pd.DataFrame(
        {
            "Tahun": [2025, 2025, 2026, 2026],
            "Jenis": ["PKB", "BBNKB", "PKB", "BBNKB"],
            "Total Potensi": [
                total_pkb25,
                bbn_vals_2025.get("Total", 0),
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

    st.subheader("B. Prediksi Variabel Makro & Dampak ke PKB (2025)")
    st.caption("Baseline = nilai aktual 2024; Prediksi dihitung dari regresi linear variabel ~ Tahun (2018–2024)")
    st.dataframe(
        rupiah_style(
            df_macro25.rename(columns={"Baseline": "Baseline 2024"}),
            {"Baseline 2024": "{:,.2f}", "Prediksi 2025": "{:,.2f}",
             "Δ Selisih": "{:,.2f}", "Dampak (Rp)": "Rp{:,.0f}"}
        ),
        use_container_width=True,
    )

    st.subheader("C. Dekomposisi BBNKB 2025")
    df_bbn25 = dekomposisi_bbnkb_table(2025, bbn_inputs_2025)
    st.dataframe(rupiah_style(df_bbn25, {"Rupiah": "Rp{:,.0f}"}), use_container_width=True)

    st.markdown("---")

    # ====== DETAIL 2026 ======
    st.header("📅 Tahun 2026")

    st.subheader("A. Dekomposisi PKB 2026 (termasuk dampak makro)")
    st.dataframe(rupiah_style(df_pkb26, {"Rupiah": "Rp{:,.0f}"}), use_container_width=True)

    st.subheader("B. Prediksi Variabel Makro & Dampak ke PKB (2026)")
    st.caption("Baseline 2026 = hasil prediksi makro 2025 (bukan 2024) • Prediksi 2026 dihitung dari regresi variabel ~ Tahun (2018-2025)")
    st.dataframe(
        rupiah_style(
            df_macro26.rename(columns={"Baseline": "Baseline 2025"}),
            {"Baseline 2025": "{:,.2f}", "Prediksi 2026": "{:,.2f}",
             "Δ Selisih": "{:,.2f}", "Dampak (Rp)": "Rp{:,.0f}"}
        ),
        use_container_width=True,
    )

    st.subheader("C. Dekomposisi BBNKB 2026")
    df_bbn26 = dekomposisi_bbnkb_table(2026, bbn_inputs_2026)
    st.dataframe(rupiah_style(df_bbn26, {"Rupiah": "Rp{:,.0f}"}), use_container_width=True)


def app():
    show_decomposition_tab()


if __name__ == "__main__":
    app()
