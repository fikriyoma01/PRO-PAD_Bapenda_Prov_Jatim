"""
Interactive Scenario Builder — Simulasi What-If Variabel Makroekonomi
Mengatur asumsi 7 indikator makroekonomi secara real-time dan membandingkan skenario kebijakan.
"""

import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st

from data_loader import load_pad_historis
from utils.audit_utils import log_scenario_save
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact, format_rupiah_full

MACRO_VARS = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]


def run_regression(df: pd.DataFrame, response: str, predictor: str):
    X = sm.add_constant(df[[predictor]])
    y = df[response]
    return sm.OLS(y, X).fit()


def predict_macro_linear(df: pd.DataFrame, var: str, year: int) -> float:
    X = sm.add_constant(df[["Tahun"]])
    y = df[var]
    model = sm.OLS(y, X).fit()
    return float(model.predict([1, year])[0])


def calculate_projection(df: pd.DataFrame, response: str, macro_vars: list[str], macro_values: dict, year: int) -> dict:
    impacts = {}
    total_impact = 0.0

    baseline = {var: float(df.iloc[-1][var]) for var in macro_vars}

    for var in macro_vars:
        model = run_regression(df, response, var)
        beta = float(model.params[var])
        delta = float(macro_values[var]) - baseline[var]
        impact = beta * delta

        impacts[var] = {
            "baseline": baseline[var],
            "scenario": float(macro_values[var]),
            "delta": delta,
            "beta": beta,
            "impact": impact,
        }
        total_impact += impact

    X = sm.add_constant(df[["Tahun"]])
    base_model = sm.OLS(df[response], X).fit()
    base_prediction = float(base_model.predict([1, year])[0])
    final_projection = base_prediction + total_impact

    return {
        "base_prediction": base_prediction,
        "total_impact": total_impact,
        "final_projection": final_projection,
        "impacts": impacts,
    }


def show_scenario_builder() -> None:
    render_page_header(
        title="Interactive Scenario Builder",
        subtitle="Simulasi What-If: sesuaikan 7 indikator makroekonomi secara manual dan pantau dampaknya terhadap proyeksi PAD secara real-time",
        icon="🎯",
    )

    df = load_pad_historis()
    active_macros = [m for m in MACRO_VARS if m in df.columns]
    last_hist_year = int(df["Tahun"].max())

    with st.expander("ℹ️ Cara Menggunakan Scenario Builder", expanded=False):
        st.markdown(
            f"""
            1. **Konfigurasi Target**: Pilih tahun proyeksi (`2025` atau `2026`), jenis pajak (`PKB` atau `BBNKB`), serta nama skenario.
            2. **Atur Asumsi Makro**: Geser slider indikator makroekonomi. Nilai awal menggunakan ekstrapolasi tren linear historis.
            3. **Evaluasi Dampak Real-Time**: Sistem menghitung perubahan masing-masing indikator dibandingkan posisi aktual `{last_hist_year}`.
            4. **Simpan & Bandingkan**: Simpan beberapa skenario (mis. *Ekspansi Ekonomi*, *Tekanan Inflasi*) untuk dibandingkan berdampingan.
            """
        )

    # --- Konfigurasi Dasar ---
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            year = st.selectbox("📅 Tahun Proyeksi", [2025, 2026], key="scenario_year")
        with col2:
            response = st.selectbox("💰 Variabel Respon", ["PKB", "BBNKB"], key="scenario_response")
        with col3:
            scenario_name = st.text_input(
                "🏷️ Nama Skenario",
                value=f"Skenario_{response}_{year}",
                key="scenario_name",
            )

    # --- Pengaturan Slider Makro ---
    create_header_with_icon(
        f"Parameter Indikator Makroekonomi ({year})",
        "🎛️",
        subtitle="Nilai default merepresentasikan baseline tren linear; tombol Reset mengembalikan seluruh slider ke baseline",
    )

    def _reset_sliders_to_baseline() -> None:
        prefix = f"slider_{year}_"
        for k in list(st.session_state.keys()):
            if k.startswith(prefix):
                del st.session_state[k]

    with st.container(border=True):
        top_bar_l, top_bar_r = st.columns([3, 1])
        with top_bar_l:
            st.caption(
                f"Geser slider di bawah untuk mengubah asumsi makro tahun **{year}** (dibandingkan baseline tren linear)."
            )
        with top_bar_r:
            st.button(
                "🔄 Reset ke Baseline",
                on_click=_reset_sliders_to_baseline,
                use_container_width=True,
            )

        macro_values = {}
        cols = st.columns(2)

        for idx, var in enumerate(active_macros):
            col = cols[idx % 2]
            with col:
                baseline_val = predict_macro_linear(df, var, year)
                hist_min = float(df[var].min())
                hist_max = float(df[var].max())
                hist_range = max(hist_max - hist_min, 0.05)

                slider_min = min(hist_min - hist_range * 0.6, baseline_val * 0.7)
                slider_max = max(hist_max + hist_range * 0.6, baseline_val * 1.3)
                step_val = 0.005 if var == "Rasio Gini" else 0.01

                value = st.slider(
                    f"{var}",
                    min_value=float(round(slider_min, 3)),
                    max_value=float(round(slider_max, 3)),
                    value=float(round(baseline_val, 3)),
                    step=step_val,
                    key=f"slider_{year}_{var}",
                    help=f"Baseline tren {year}: {baseline_val:.3f} | Rentang historis: {hist_min:.2f} – {hist_max:.2f}",
                )
                macro_values[var] = value

                diff = value - baseline_val
                diff_pct = (diff / baseline_val * 100) if baseline_val != 0 else 0.0
                if abs(diff) < step_val:
                    st.caption(f"✅ Sesuai baseline tren: **{baseline_val:.2f}**")
                elif diff > 0:
                    st.caption(f"📈 **+{diff:.2f}** (`+{diff_pct:.1f}%`) di atas baseline {baseline_val:.2f}")
                else:
                    st.caption(f"📉 **{diff:.2f}** (`{diff_pct:.1f}%`) di bawah baseline {baseline_val:.2f}")

    render_section_divider()

    # --- Hasil Proyeksi Real-Time ---
    create_header_with_icon(
        f"Hasil Simulasi Proyeksi {response} Tahun {year}",
        "📊",
    )

    results = calculate_projection(df, response, active_macros, macro_values, year)
    base_pred = results["base_prediction"]
    tot_impact = results["total_impact"]
    final_proj = results["final_projection"]
    impact_pct = (tot_impact / base_pred * 100) if base_pred else 0.0

    k1, k2, k3 = st.columns(3)
    with k1:
        render_kpi_card(
            label=f"Prediksi Dasar Tren ({year})",
            value=format_rupiah_compact(base_pred, respect_privacy=True),
            subtitle=format_rupiah_full(base_pred),
            icon="📏",
            variant="primary",
        )
    with k2:
        render_kpi_card(
            label="Total Dampak Makro Bersih",
            value=format_rupiah_compact(tot_impact, signed=True, respect_privacy=True),
            delta=f"{impact_pct:+.2f}% terhadap Base",
            delta_positive=tot_impact >= 0,
            subtitle=format_rupiah_full(tot_impact, signed=True),
            icon="⚡",
            variant="success" if tot_impact >= 0 else "danger",
        )
    with k3:
        render_kpi_card(
            label=f"Proyeksi Akhir {response} {year}",
            value=format_rupiah_compact(final_proj, respect_privacy=True),
            delta=f"{impact_pct:+.2f}% vs Prediksi Dasar",
            delta_positive=final_proj >= base_pred,
            subtitle=format_rupiah_full(final_proj),
            icon="🎯",
            variant="gold",
        )

    # --- Detail Dampak & Grafik ---
    col_t, col_g = st.columns([1.15, 1])

    with col_t:
        create_header_with_icon("Rincian Kontribusi per Variabel", "🔍")
        impact_rows = []
        for var in active_macros:
            info = results["impacts"][var]
            contrib_pct = (info["impact"] / abs(tot_impact) * 100) if tot_impact != 0 else 0.0
            impact_rows.append(
                {
                    "Variabel": var,
                    f"Aktual {last_hist_year}": f"{info['baseline']:.2f}",
                    f"Skenario {year}": f"{info['scenario']:.2f}",
                    "Δ Perubahan": f"{info['delta']:+.2f}",
                    "Dampak (Rp)": format_rupiah_compact(info["impact"], signed=True),
                    "Kontribusi": f"{contrib_pct:+.1f}%",
                }
            )
        st.dataframe(pd.DataFrame(impact_rows), use_container_width=True, hide_index=True)

    with col_g:
        create_header_with_icon(" Urutan Dampak Makro", "📈")
        with st.container(border=True):
            sorted_impacts = sorted(
                [(var, results["impacts"][var]["impact"]) for var in active_macros],
                key=lambda x: abs(x[1]),
                reverse=True,
            )
            variables = [x[0] for x in sorted_impacts]
            impacts = [x[1] for x in sorted_impacts]
            colors = ["#10b981" if x >= 0 else "#ef4444" for x in impacts]

            fig = go.Figure(
                go.Bar(
                    x=variables,
                    y=impacts,
                    marker_color=colors,
                    text=[format_rupiah_compact(x, signed=True) for x in impacts],
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{x}</b><br>Dampak: Rp %{y:+,.0f}<extra></extra>",
                )
            )
            apply_plotly_theme(
                fig,
                title=f"Kontribusi Makro ke {response} {year}",
                height=390,
                xaxis_title="Indikator Makro",
                yaxis_title="Dampak (Rupiah)",
                is_currency=True,
                show_legend=False,
                margin=dict(l=64, r=28, t=68, b=80),
            )
            fig.update_xaxes(tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

    render_section_divider()

    # --- Simpan & Bandingkan Skenario ---
    create_header_with_icon(
        "Simpan & Bandingkan Skenario",
        "💾",
        subtitle="Simpan konfigurasi saat ini untuk dibandingkan dengan alternatif asumsi makro lainnya",
    )

    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = []

    with st.container(border=True):
        b_col1, b_col2 = st.columns([3, 1])
        with b_col1:
            if st.button("💾 Simpan Skenario Saat Ini", type="primary", use_container_width=True):
                clean_name = scenario_name.strip() or f"Skenario_{len(st.session_state.saved_scenarios) + 1}"
                st.session_state.saved_scenarios.append(
                    {
                        "name": clean_name,
                        "year": year,
                        "response": response,
                        "macro_values": macro_values.copy(),
                        "projection": final_proj,
                        "impact": tot_impact,
                    }
                )
                log_scenario_save(
                    scenario_name=clean_name,
                    details={
                        "year": year,
                        "response": response,
                        "projection": float(final_proj),
                        "impact": float(tot_impact),
                        "num_variables": len(macro_values),
                    },
                )
                st.success(f"✅ Skenario **{clean_name}** berhasil disimpan!")

        with b_col2:
            if st.button("🗑️ Hapus Semua", use_container_width=True):
                st.session_state.saved_scenarios = []
                st.rerun()

        if st.session_state.saved_scenarios:
            comp_rows = [
                {
                    "Nama Skenario": sc["name"],
                    "Tahun": sc["year"],
                    "Jenis Pajak": sc["response"],
                    "Proyeksi Akhir": format_rupiah_compact(sc["projection"], respect_privacy=True),
                    "Dampak Makro": format_rupiah_compact(sc["impact"], signed=True, respect_privacy=True),
                }
                for sc in st.session_state.saved_scenarios
            ]
            st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

            if len(st.session_state.saved_scenarios) > 1:
                fig_comp = go.Figure()
                palette = ["#1a5fb4", "#f59e0b", "#10b981", "#6366f1", "#ef4444", "#0ea5e9"]
                for idx, sc in enumerate(st.session_state.saved_scenarios):
                    fig_comp.add_trace(
                        go.Bar(
                            name=f"{sc['name']} ({sc['year']})",
                            x=[f"{sc['response']} {sc['year']}"],
                            y=[sc["projection"]],
                            marker_color=palette[idx % len(palette)],
                            text=[format_rupiah_compact(sc["projection"], respect_privacy=True)],
                            textposition="outside",
                            cliponaxis=False,
                            hovertemplate=f"<b>{sc['name']}</b><br>Proyeksi: Rp %{{y:,.0f}}<extra></extra>",
                        )
                    )
                apply_plotly_theme(
                    fig_comp,
                    title="Perbandingan Proyeksi Antar-Skenario Tersimpan",
                    height=420,
                    xaxis_title="Target Pajak & Tahun",
                    yaxis_title="Nilai Proyeksi (Rupiah)",
                    is_currency=True,
                )
                fig_comp.update_layout(
                    barmode="group",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.caption("Belum ada skenario yang disimpan pada sesi ini.")


def app() -> None:
    show_scenario_builder()


if __name__ == "__main__":
    app()
