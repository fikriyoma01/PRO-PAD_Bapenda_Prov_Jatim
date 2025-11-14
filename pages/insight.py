import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

from data_loader import (
    load_pad_historis,
    get_pkb_inputs,
    get_bbnkb_inputs,
    map_inputs,
)

MACROS = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]

def local_css():
    st.markdown(
        """
        <style>
            .insight-header {
                background: linear-gradient(90deg, #1a5fb4, #3584e4);
                padding: 18px;
                border-radius: 12px;
                margin-bottom: 25px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            }
            .insight-header h1 {
                color: #ffffff;
                margin: 0;
                font-size: 2.2rem;
                font-weight: 700;
            }
            .insight-header p {
                color: #f1f1f1;
                margin: 0;
                font-size: 1.05rem;
            }
            .insight-section-title {
                font-size: 1.35rem;
                font-weight: 700;
                color: #1e3c72;
                margin: 32px 0 16px;
                border-left: 5px solid #ffd700;
                padding-left: 12px;
            }
            .insight-divider {
                margin: 24px 0;
                border: none;
                border-top: 1px solid rgba(30, 60, 114, 0.15);
            }
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


def render_section_title(text: str) -> None:
    st.markdown(
        f"<div class='insight-section-title'>{text}</div>",
        unsafe_allow_html=True,
    )


def render_divider() -> None:
    st.markdown("<hr class='insight-divider'>", unsafe_allow_html=True)



def format_rupiah(value: float, signed: bool = False) -> str:
    formatted = f"Rp {abs(value):,.0f}".replace(",", ".")
    if signed:
        prefix = "+" if value >= 0 else "-"
        return f"{prefix}{formatted}"
    return formatted


def build_macro_models(hist: pd.DataFrame):
    X_year = sm.add_constant(hist["Tahun"])
    trend_params = {}
    beta_coeffs = {"PKB": {}, "BBNKB": {}}
    for var in MACROS:
        trend_model = sm.OLS(hist[var], X_year).fit()
        trend_params[var] = {
            "const": float(trend_model.params["const"]),
            "tahun": float(trend_model.params["Tahun"]),
        }
        for response_col in ("PKB", "BBNKB"):
            beta_model = sm.OLS(hist[response_col], sm.add_constant(hist[[var]])).fit()
            beta_coeffs[response_col][var] = float(beta_model.params[var])
    return trend_params, beta_coeffs


def compute_macro_effects(
    year: int,
    baseline: dict,
    trend_params: dict,
    beta_coeffs: dict,
    response: str = "PKB",
):
    rows = []
    total_plus = 0.0
    total_minus = 0.0
    predictions = {}

    beta_map = beta_coeffs
    if isinstance(beta_coeffs, dict) and response in beta_coeffs:
        beta_map = beta_coeffs[response]

    for var in MACROS:
        params = trend_params[var]
        predicted = params["const"] + params["tahun"] * year
        delta = predicted - baseline[var]
        impact = beta_map.get(var, 0.0) * delta
        predictions[var] = predicted

        if impact >= 0:
            total_plus += impact
        else:
            total_minus += impact

        rows.append(
            {
                "Variabel": var,
                "Baseline": baseline[var],
                f"Prediksi {year}": predicted,
                "Selisih": delta,
                "Dampak (Rp)": impact,
            }
        )

    df_macro = pd.DataFrame(rows)
    return df_macro, total_plus, total_minus, predictions

def compute_pkb_summary(hist: pd.DataFrame, trend_params: dict, beta_coeffs: dict, year: int, baseline: dict):
    inputs = get_pkb_inputs(year)
    values = map_inputs(inputs)

    penambah = inputs.loc[inputs["kategori"] == "penambah", "nilai"].sum()
    pengurang = inputs.loc[inputs["kategori"] == "pengurang", "nilai"].sum()

    macro_df, macro_plus, macro_minus, predicted_macro = compute_macro_effects(
        year, baseline, trend_params, beta_coeffs, response="PKB"
    )

    total = penambah - pengurang + macro_plus + macro_minus

    return {
        "inputs": inputs,
        "values": values,
        "penambah": penambah,
        "pengurang": pengurang,
        "macro_plus": macro_plus,
        "macro_minus": macro_minus,
        "macro_df": macro_df,
        "predicted_macro": predicted_macro,
        "total": total,
        "target": values.get("Target", 0.0),
    }


def compute_bbnkb_summary(
    hist: pd.DataFrame,
    trend_params: dict,
    beta_coeffs: dict,
    year: int,
    baseline: dict,
):
    inputs = get_bbnkb_inputs(year)
    values = map_inputs(inputs)

    structural_total = values.get("Total", 0.0)
    pengurang = inputs.loc[inputs["kategori"] == "pengurang", "nilai"].sum()

    macro_df, macro_plus, macro_minus, predicted_macro = compute_macro_effects(
        year,
        baseline,
        trend_params,
        beta_coeffs,
        response="BBNKB",
    )

    net_structural = structural_total - pengurang
    total = net_structural + macro_plus + macro_minus

    return {
        "inputs": inputs,
        "values": values,
        "structural_total": structural_total,
        "pengurang": pengurang,
        "macro_plus": macro_plus,
        "macro_minus": macro_minus,
        "macro_df": macro_df,
        "predicted_macro": predicted_macro,
        "neto": net_structural,
        "total": total,
        "target": values.get("Target", 0.0),
    }
def build_combined_time_series(hist: pd.DataFrame, pkb25: dict, pkb26: dict, bbn25: dict, bbn26: dict) -> pd.DataFrame:
    actual = hist[["Tahun", "PKB", "BBNKB"]].melt("Tahun", var_name="Jenis", value_name="Nilai")
    actual["Status"] = "Aktual"

    projections = pd.DataFrame(
        [
            {"Tahun": 2025, "Jenis": "PKB", "Nilai": pkb25["total"], "Status": "Proyeksi"},
            {"Tahun": 2026, "Jenis": "PKB", "Nilai": pkb26["total"], "Status": "Proyeksi"},
            {"Tahun": 2025, "Jenis": "BBNKB", "Nilai": bbn25["total"], "Status": "Proyeksi"},
            {"Tahun": 2026, "Jenis": "BBNKB", "Nilai": bbn26["total"], "Status": "Proyeksi"},
        ]
    )

    last_year = hist["Tahun"].max()
    bridge_rows = []
    last_row = hist.loc[hist["Tahun"] == last_year]
    if not last_row.empty:
        for jenis in ["PKB", "BBNKB"]:
            bridge_rows.append(
                {
                    "Tahun": int(last_year),
                    "Jenis": jenis,
                    "Nilai": float(last_row[jenis].iloc[0]),
                    "Status": "Proyeksi",
                }
            )
    if bridge_rows:
        projections = pd.concat([pd.DataFrame(bridge_rows), projections], ignore_index=True)

    combined = pd.concat([actual, projections], ignore_index=True)
    combined = combined.sort_values(["Jenis", "Tahun", "Status"]).reset_index(drop=True)
    return combined


def build_macro_series(hist: pd.DataFrame, pkb25: dict, pkb26: dict) -> pd.DataFrame:
    base = hist[["Tahun"] + MACROS].copy()
    future_rows = []
    for year, pred in [(2025, pkb25["predicted_macro"]), (2026, pkb26["predicted_macro"])]:
        row = {"Tahun": year}
        row.update({var: float(pred[var]) for var in MACROS})
        future_rows.append(row)

    future = pd.DataFrame(future_rows)
    combined = pd.concat([base, future], ignore_index=True)
    combined["Status"] = combined["Tahun"].apply(lambda x: "Aktual" if x <= 2024 else "Proyeksi")
    long_df = combined.melt(id_vars=["Tahun", "Status"], var_name="Variabel", value_name="Nilai")
    return long_df


def build_pkb_contribution(pkb25: dict, pkb26: dict) -> pd.DataFrame:
    rows = []
    for year, data in [(2025, pkb25), (2026, pkb26)]:
        rows.extend(
            [
                {"Tahun": year, "Kategori": "Total Penambah", "Nilai": data["penambah"]},
                {"Tahun": year, "Kategori": "Total Pengurang", "Nilai": -data["pengurang"]},
                {"Tahun": year, "Kategori": "Dampak Makro (+)", "Nilai": data["macro_plus"]},
                {"Tahun": year, "Kategori": "Dampak Makro (-)", "Nilai": data["macro_minus"]},
            ]
        )
    return pd.DataFrame(rows)


def build_bbnkb_overview(bbn25: dict, bbn26: dict) -> pd.DataFrame:
    rows = []
    for year, data in [(2025, bbn25), (2026, bbn26)]:
        rows.extend(
            [
                {"Tahun": year, "Komponen": "Total Potensi", "Nilai": data["total"]},
                {"Tahun": year, "Komponen": "Total Pengurang", "Nilai": data["pengurang"]},
                {"Tahun": year, "Komponen": "Potensi Neto", "Nilai": data["neto"]},
                {"Tahun": year, "Komponen": "Target", "Nilai": data["target"]},
            ]
        )
    return pd.DataFrame(rows)


def app():
    local_css()
    st.markdown(
        """
        <div class="insight-header">
            <h1>📊 Insight Terpadu PAD 2018-2026</h1>
            <p>🧭 Ringkasan interaktif yang menyatukan tren historis, pemodelan regresi, proyeksi, dan dekomposisi untuk PKB dan BBNKB.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hist = load_pad_historis()
    trend_params, beta_coeffs = build_macro_models(hist)

    baseline_2024 = {var: float(hist.iloc[-1][var]) for var in MACROS}
    baseline_2024 = {var: float(hist.iloc[-1][var]) for var in MACROS}
    pkb25 = compute_pkb_summary(hist, trend_params, beta_coeffs, 2025, baseline_2024)
    baseline_pkb_2026 = {var: float(pkb25["predicted_macro"][var]) for var in MACROS}
    pkb26 = compute_pkb_summary(hist, trend_params, beta_coeffs, 2026, baseline_pkb_2026)

    bbn25 = compute_bbnkb_summary(hist, trend_params, beta_coeffs, 2025, baseline_2024)
    baseline_bbn_2026 = {var: float(bbn25["predicted_macro"][var]) for var in MACROS}
    bbn26 = compute_bbnkb_summary(hist, trend_params, beta_coeffs, 2026, baseline_bbn_2026)

    combined_series = build_combined_time_series(hist, pkb25, pkb26, bbn25, bbn26)
    macro_series = build_macro_series(hist, pkb25, pkb26)
    pkb_contrib = build_pkb_contribution(pkb25, pkb26)
    bbn_overview = build_bbnkb_overview(bbn25, bbn26)

    render_section_title("📈 Tren PAD 2018-2026")
    fig_trend = px.line(
        combined_series,
        x="Tahun",
        y="Nilai",
        color="Jenis",
        line_dash="Status",
        markers=True,
        template="plotly_white",
        labels={"Nilai": "Rupiah"},
        title="📈 PKB dan BBNKB: Aktual vs Proyeksi",
        category_orders={"Status": ["Aktual", "Proyeksi"]},
    )
    fig_trend.update_layout(
        yaxis=dict(
            tickformat=",.0f",
            title="Nilai (Rupiah)"
        ),
        xaxis=dict(
            title="Tahun",
            dtick=1
        ),
        hovermode='x unified',
        height=550,
        autosize=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "🚗 PKB 2025 Potensi",
        format_rupiah(pkb25["total"]),
        delta=f"{format_rupiah(pkb25['total'] - pkb25['target'], signed=True)} vs target",
    )
    col2.metric(
        "🚗 PKB 2026 Potensi",
        format_rupiah(pkb26["total"]),
        delta=f"{format_rupiah(pkb26['total'] - pkb26['target'], signed=True)} vs target",
    )
    col3.metric(
        "🔁 BBNKB 2026 Neto",
        format_rupiah(bbn26["total"]),
        delta=f"{format_rupiah(bbn26['total'] - bbn26['target'], signed=True)} vs target",
    )

    render_divider()
    render_section_title("🌐 Dinamika Variabel Makro")
    selected_macros = st.multiselect(
        "🌐 Pilih variabel makro",
        MACROS,
        default=["PDRB", "Inflasi", "Suku Bunga"],
    )
    filtered_macro = macro_series[macro_series["Variabel"].isin(selected_macros)]
    if not filtered_macro.empty:
        fig_macro = px.line(
            filtered_macro,
            x="Tahun",
            y="Nilai",
            color="Variabel",
            line_dash="Status",
            markers=True,
            template="plotly_white",
            title="🌐 Pergerakan Variabel Makro 2018-2026",
        )
        fig_macro.update_layout(
            yaxis=dict(
                title="Nilai",
                tickformat=".2f"
            ),
            xaxis=dict(
                title="Tahun",
                dtick=1
            ),
            hovermode='x unified',
            height=550,
            autosize=True
        )
        st.plotly_chart(fig_macro, use_container_width=True)
    else:
        st.warning("⚠️ Silakan pilih minimal satu variabel makro untuk ditampilkan.")

    render_divider()
    render_section_title("🧪 Insight Pemodelan Regresi")
    response = st.selectbox("🎯 Variabel respon", ["PKB", "BBNKB"], index=0)
    predictor = st.selectbox("🧭 Variabel makro", MACROS, index=0)

    model = sm.OLS(hist[response], sm.add_constant(hist[[predictor]])).fit()
    coef = float(model.params[predictor])
    intercept = float(model.params["const"])
    p_value = float(model.pvalues[predictor])
    r_squared = float(model.rsquared)

    future_points = []
    for year, macro_pred in [(2025, pkb25["predicted_macro"].get(predictor)), (2026, pkb26["predicted_macro"].get(predictor))]:
        if macro_pred is None:
            continue
        predicted_response = float(model.predict([1, macro_pred])[0])
        future_points.append(
            {
                "Tahun": year,
                predictor: macro_pred,
                response: predicted_response,
                "Status": "Proyeksi",
            }
        )

    modeling_df = hist[["Tahun", predictor, response]].copy()
    modeling_df["Status"] = "Aktual"
    modeling_df = pd.concat([modeling_df, pd.DataFrame(future_points)], ignore_index=True)

    fig_model = px.scatter(
        modeling_df,
        x=predictor,
        y=response,
        color="Status",
        symbol="Status",
        text="Tahun",
        hover_data=["Tahun"],
        template="plotly_white",
        title=f"🧪 {response} vs {predictor}",
    )
    x_axis = pd.Series(sorted(hist[predictor]))
    line_df = pd.DataFrame({predictor: x_axis})
    line_df.insert(0, "const", 1.0)
    reg_line = model.predict(line_df)
    fig_model.add_trace(
        go.Scatter(
            x=x_axis,
            y=reg_line,
            mode="lines",
            name="📏 Regresi",
            line=dict(color="#636EFA", width=2, dash='dash'),
            showlegend=True,
        )
    )
    fig_model.update_traces(textposition="top center", selector=dict(mode='markers+text'))
    fig_model.update_layout(
        xaxis_title=predictor,
        yaxis_title=response,
        yaxis=dict(tickformat=",.0f"),
        hovermode='closest',
        height=550,
        autosize=True
    )
    st.plotly_chart(fig_model, use_container_width=True)

    col_a, col_b, col_c = st.columns(3)
    col_a.markdown(f"<div class=\"metric-box metric-koef\">📐 Koefisien<span>{coef:,.2f}</span></div>", unsafe_allow_html=True)
    col_b.markdown(f"<div class=\"metric-box metric-r2\">📊 R²<span>{r_squared:.3f}</span></div>", unsafe_allow_html=True)
    col_c.markdown(f"<div class=\"metric-box metric-pval\">🧪 p-value<span>{p_value:.3f}</span></div>", unsafe_allow_html=True)
    
    # Persamaan Regresi
    st.subheader("📑 Persamaan Regresi")
    st.info(f"**{response} = {intercept:.3f} + {coef:.3f} × {predictor}**")

    # Interpretasi
    arah = "penambah 📈" if coef > 0 else "pengurang 📉"
    if p_value < 0.05:
        st.success(f"✅ {predictor} signifikan sebagai faktor **{arah}** terhadap {response}.")
    else:
        st.warning(f"⚠️ {predictor} tidak signifikan, namun bisa sebagai faktor **{arah}**.")

    render_divider()
    render_section_title("🧩 Ringkasan Dekomposisi Potensi")
    fig_contrib = px.bar(
        pkb_contrib,
        x="Tahun",
        y="Nilai",
        color="Kategori",
        template="plotly_white",
        title="🧩 Kontributor Potensi PKB 2025-2026",
        barmode="group",
        hover_data={"Nilai": ":,.0f"},
    )
    fig_contrib.update_layout(
        legend_title="Kategori",
        bargap=0.25,
        hovermode="x unified",
        xaxis=dict(
            title="Tahun",
            tickmode="linear",
            tick0=2025,
            dtick=1
        ),
        yaxis=dict(
            title="Nilai (Rupiah)",
            tickformat=",.0f"
        ),
        height=550,
        autosize=True
    )
    st.plotly_chart(fig_contrib, use_container_width=True)

    render_section_title("🧾 Tabel Ringkas Potensi vs Target")
    st.dataframe(
        pd.DataFrame(
            {
                "Tahun": [2025, 2026],
                "PKB Potensi": [pkb25["total"], pkb26["total"]],
                "PKB Target": [pkb25["target"], pkb26["target"]],
                "BBNKB Potensi": [bbn25["total"], bbn26["total"]],
                "BBNKB Target": [bbn25["target"], bbn26["target"]],
            }
        ).style.format({
            "PKB Potensi": "Rp{:,.0f}",
            "PKB Target": "Rp{:,.0f}",
            "BBNKB Potensi": "Rp{:,.0f}",
            "BBNKB Target": "Rp{:,.0f}",
        }),
        use_container_width=True,
    )


if __name__ == "__main__":
    app()

