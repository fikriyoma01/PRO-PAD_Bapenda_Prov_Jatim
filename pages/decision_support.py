"""
Decision Support System — Ringkasan Eksekutif, Penilaian Risiko, Rekomendasi Strategis & Ekspor Laporan
"""

from __future__ import annotations

import html
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_loader import get_bbnkb_inputs, get_pkb_inputs, load_pad_historis, map_inputs
from pages import dekomposisi as dekom
from utils.audit_utils import log_export
from utils.export_utils import create_comprehensive_excel_report
from utils.policy_utils import get_policy_settings
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_info_box,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact, format_rupiah_full


def calculate_risk_score(volatility_pct: float, shortfall_pct: float, sample_size: int) -> tuple[float, str, str]:
    """Hitung skor risiko komposit (0–100) dari volatilitas historis, gap target, dan ukuran sampel."""
    sample_penalty = max(0.0, (12 - sample_size) * 3.5)
    vol_component = min(40.0, volatility_pct * 2.8)
    gap_component = min(35.0, max(0.0, shortfall_pct) * 2.5)
    score = round(min(100.0, sample_penalty + vol_component + gap_component), 1)

    if score < 35:
        return score, "RENDAH (LOW)", "#10b981"
    if score < 65:
        return score, "MENENGAH (MEDIUM)", "#f59e0b"
    return score, "TINGGI (HIGH)", "#ef4444"


def create_risk_matrix() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Kategori Risiko": "Keterbatasan Sampel Model (n=7)",
                "Probabilitas": "Medium",
                "Dampak": "High",
                "Strategi Mitigasi": "Gunakan kombinasi Dekomposisi Objek Pajak, LOOCV, dan Ensemble Multi-Model",
            },
            {
                "Kategori Risiko": "Perlambatan Ekonomi & Daya Beli",
                "Probabilitas": "Low",
                "Dampak": "High",
                "Strategi Mitigasi": "Siapkan cadangan fiskal mengacu pada Skenario Pesimis",
            },
            {
                "Kategori Risiko": "Transisi Kebijakan Opsen HKPD",
                "Probabilitas": "Medium",
                "Dampak": "Medium",
                "Strategi Mitigasi": "Sinkronisasi rekonsiliasi bagi hasil Provinsi & Kab/Kota secara bulanan",
            },
            {
                "Kategori Risiko": "Ketidakpatuhan Daftar Ulang (TDR)",
                "Probabilitas": "Medium",
                "Dampak": "High",
                "Strategi Mitigasi": "Perluas kanal pembayaran digital e-Samsat, pengingat WhatsApp, dan operasi gabungan",
            },
            {
                "Kategori Risiko": "Fluktuasi Penjualan Kendaraan Baru",
                "Probabilitas": "Medium",
                "Dampak": "Medium",
                "Strategi Mitigasi": "Pantau data Gaikindo/AISI triwulanan sebagai indikator dini BBNKB",
            },
        ]
    )


def _compute_real_projections(df: pd.DataFrame) -> dict:
    pkb_in_25 = get_pkb_inputs(2025)
    pkb_in_26 = get_pkb_inputs(2026)
    bbn_in_25 = get_bbnkb_inputs(2025)
    bbn_in_26 = get_bbnkb_inputs(2026)

    base_24 = {v: float(df.iloc[-1][v]) for v in dekom.MACROS if v in df.columns}
    df_pkb25, total_pkb25, _, pred_m25 = dekom.dekomposisi_pkb_with_macro(2025, pkb_in_25, base_24, df=df)
    base_25 = {k: float(v) for k, v in pred_m25.items()}
    df_pkb26, total_pkb26, _, _ = dekom.dekomposisi_pkb_with_macro(2026, pkb_in_26, base_25, df=df)

    _, bbn_p25, bbn_m25, _ = dekom.compute_macro_impact(2025, base_24, response_col="BBNKB", df=df)
    _, bbn_p26, bbn_m26, _ = dekom.compute_macro_impact(2026, base_25, response_col="BBNKB", df=df)

    bbn_v25 = map_inputs(bbn_in_25)
    bbn_v26 = map_inputs(bbn_in_26)
    total_bbn25 = float(bbn_v25.get("Total", 0.0)) + bbn_p25 + bbn_m25
    net_bbn26 = float(bbn_v26.get("Total", 0.0)) - float(bbn_v26.get("Pengurang", 0.0))
    total_bbn26 = net_bbn26 + bbn_p26 + bbn_m26

    df_bbn25 = dekom.dekomposisi_bbnkb_table(2025, bbn_in_25, bbn_p25, bbn_m25)
    df_bbn26 = dekom.dekomposisi_bbnkb_table(2026, bbn_in_26, bbn_p26, bbn_m26)

    return {
        "pkb_2025": total_pkb25,
        "pkb_2026": total_pkb26,
        "bbnkb_2025": total_bbn25,
        "bbnkb_2026": total_bbn26,
        "apbd_targets": {
            "pkb_2025": float(map_inputs(pkb_in_25).get("Target", 0.0)),
            "pkb_2026": float(map_inputs(pkb_in_26).get("Target", 0.0)),
            "bbnkb_2025": float(bbn_v25.get("Target", 0.0)),
            "bbnkb_2026": float(bbn_v26.get("Target", 0.0)),
        },
        "tables": {
            "df_pkb25": df_pkb25,
            "df_pkb26": df_pkb26,
            "df_bbn25": df_bbn25,
            "df_bbn26": df_bbn26,
        },
    }


def _build_executive_html_report(
    *,
    generated_at: str,
    df: pd.DataFrame,
    proj: dict,
    targets: dict,
    risk_score: float,
    risk_category: str,
    include_summary: bool,
    include_targets: bool,
    include_risks: bool,
    include_recommendations: bool,
    include_scenarios: bool,
    hide_values: bool,
    add_watermark: bool,
) -> str:
    def _fmt(val: float, signed: bool = False) -> str:
        if hide_values:
            return "Rp [DIRAHASIAKAN]"
        return format_rupiah_compact(val, signed=signed)

    wm_html = (
        '<div style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;'
        'font-size:4rem;font-weight:800;color:rgba(15,23,42,0.06);transform:rotate(-25deg);'
        'pointer-events:none;z-index:999;">CONFIDENTIAL • BAPENDA JATIM</div>'
        if add_watermark
        else ""
    )

    sections = []
    if include_summary:
        latest_yr = int(df["Tahun"].max())
        latest_pkb = float(df.loc[df["Tahun"] == latest_yr, "PKB"].iloc[0])
        latest_bbn = float(df.loc[df["Tahun"] == latest_yr, "BBNKB"].iloc[0])
        sections.append(
            f"""
            <section>
                <h2>1. Ringkasan Eksekutif</h2>
                <div class="kpi-grid">
                    <div class="kpi"><div class="lbl">Realisasi PKB {latest_yr}</div><div class="val">{_fmt(latest_pkb)}</div></div>
                    <div class="kpi"><div class="lbl">Realisasi BBNKB {latest_yr}</div><div class="val">{_fmt(latest_bbn)}</div></div>
                    <div class="kpi"><div class="lbl">Proyeksi PKB 2025</div><div class="val">{_fmt(proj['pkb_2025'])}</div></div>
                    <div class="kpi"><div class="lbl">Proyeksi BBNKB 2025</div><div class="val">{_fmt(proj['bbnkb_2025'])}</div></div>
                </div>
            </section>
            """
        )

    if include_targets:
        rows_html = ""
        for label, key in [
            ("PKB 2025", "pkb_2025"),
            ("PKB 2026", "pkb_2026"),
            ("BBNKB 2025", "bbnkb_2025"),
            ("BBNKB 2026", "bbnkb_2026"),
        ]:
            p_val = proj[key]
            t_val = targets[key]
            gap = p_val - t_val
            pct = (p_val / t_val * 100) if t_val else 0.0
            status = "Surplus / Tercapai" if gap >= 0 else "Defisit / Perlu Mitigasi"
            rows_html += (
                f"<tr><td>{label}</td><td>{_fmt(t_val)}</td><td>{_fmt(p_val)}</td>"
                f"<td>{_fmt(gap, signed=True)}</td><td>{pct:.1f}%</td><td>{status}</td></tr>"
            )
        sections.append(
            f"""
            <section>
                <h2>2. Evaluasi Target vs Proyeksi</h2>
                <table>
                    <thead><tr><th>Komponen</th><th>Target</th><th>Proyeksi</th><th>Selisih</th><th>Capaian</th><th>Status</th></tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </section>
            """
        )

    if include_risks:
        risk_df = create_risk_matrix()
        r_rows = "".join(
            f"<tr><td>{html.escape(r['Kategori Risiko'])}</td><td>{r['Probabilitas']}</td>"
            f"<td>{r['Dampak']}</td><td>{html.escape(r['Strategi Mitigasi'])}</td></tr>"
            for _, r in risk_df.iterrows()
        )
        sections.append(
            f"""
            <section>
                <h2>3. Penilaian Risiko Fiskal</h2>
                <p><strong>Skor Risiko Komposit:</strong> {risk_score:.1f} / 100 — Status: <strong>{risk_category}</strong></p>
                <table>
                    <thead><tr><th>Kategori Risiko</th><th>Probabilitas</th><th>Dampak</th><th>Strategi Mitigasi</th></tr></thead>
                    <tbody>{r_rows}</tbody>
                </table>
            </section>
            """
        )

    if include_scenarios:
        sections.append(
            f"""
            <section>
                <h2>4. Analisis Tiga Skenario (Tahun 2025)</h2>
                <table>
                    <thead><tr><th>Skenario</th><th>Bobot Probabilitas</th><th>PKB 2025</th><th>BBNKB 2025</th><th>Total PAD Kendaraan</th></tr></thead>
                    <tbody>
                        <tr><td>Pesimis (-5%)</td><td>25%</td><td>{_fmt(proj['pkb_2025']*0.95)}</td><td>{_fmt(proj['bbnkb_2025']*0.95)}</td><td>{_fmt((proj['pkb_2025']+proj['bbnkb_2025'])*0.95)}</td></tr>
                        <tr><td>Moderat (Baseline)</td><td>50%</td><td>{_fmt(proj['pkb_2025'])}</td><td>{_fmt(proj['bbnkb_2025'])}</td><td>{_fmt(proj['pkb_2025']+proj['bbnkb_2025'])}</td></tr>
                        <tr><td>Optimis (+5%)</td><td>25%</td><td>{_fmt(proj['pkb_2025']*1.05)}</td><td>{_fmt(proj['bbnkb_2025']*1.05)}</td><td>{_fmt((proj['pkb_2025']+proj['bbnkb_2025'])*1.05)}</td></tr>
                    </tbody>
                </table>
            </section>
            """
        )

    if include_recommendations:
        sections.append(
            """
            <section>
                <h2>5. Rekomendasi Strategis Bapenda Provinsi Jawa Timur</h2>
                <ul>
                    <li><strong>Kebijakan & Kepatuhan:</strong> Perluas insentif pembayaran tepat waktu pada kanal digital e-Samsat serta intensifikasi penagihan tunggakan Roda 4 & Roda 2.</li>
                    <li><strong>Operasional HKPD:</strong> Perkuat rekonsiliasi real-time bersama Pemerintah Kabupaten/Kota guna menjaga akurasi bagi hasil/opsen.</li>
                    <li><strong>Analitik & Monitoring:</strong> Lakukan evaluasi capaian setiap triwulan dan mutakhirkan parameter makroekonomi apabila terjadi deviasi PDRB atau inflasi di atas ±0.5%.</li>
                </ul>
            </section>
            """
        )

    return f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="utf-8">
<title>Laporan Eksekutif PRO-PAD — Bapenda Provinsi Jawa Timur</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; color: #0f172a; margin: 0; padding: 32px; line-height: 1.6; }}
  header {{ background: linear-gradient(135deg, #0c2d57, #1a5fb4); color: #fff; padding: 24px 28px; border-radius: 12px; border-bottom: 4px solid #ffd700; margin-bottom: 28px; }}
  header h1 {{ margin: 0; font-size: 1.65rem; }}
  header p {{ margin: 6px 0 0 0; opacity: 0.9; font-size: 0.92rem; }}
  section {{ margin-bottom: 26px; page-break-inside: avoid; }}
  h2 {{ color: #134a8e; border-left: 4px solid #f59e0b; padding-left: 10px; font-size: 1.2rem; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 12px; }}
  .kpi {{ border: 1px solid #cbd5e1; border-radius: 10px; padding: 14px; background: #f8fafc; }}
  .kpi .lbl {{ font-size: 0.78rem; color: #64748b; text-transform: uppercase; font-weight: 700; }}
  .kpi .val {{ font-size: 1.3rem; font-weight: 800; color: #0f3d7a; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem; }}
  th, td {{ border: 1px solid #cbd5e1; padding: 9px 12px; text-align: left; }}
  th {{ background: #eff6ff; color: #0f3d7a; font-weight: 700; }}
  footer {{ margin-top: 36px; padding-top: 12px; border-top: 1px solid #cbd5e1; font-size: 0.82rem; color: #64748b; text-align: center; }}
  @media print {{ body {{ padding: 12px; }} }}
</style>
</head>
<body>
{wm_html}
<header>
  <h1>LAPORAN KEPUTUSAN EKSEKUTIF PROYEKSI PAD (PRO-PAD)</h1>
  <p>Badan Pendapatan Daerah Provinsi Jawa Timur • Dicetak pada: {generated_at}</p>
</header>
{''.join(sections)}
<footer>Dokumen Resmi Sistem Analitik PRO-PAD v2.0 — Bapenda Provinsi Jawa Timur (Gunakan Ctrl+P / Print ke PDF untuk arsip cetak)</footer>
</body>
</html>"""


def show_decision_support_page() -> None:
    render_page_header(
        title="Executive Decision Support System",
        subtitle="Ringkasan eksekutif pimpinan, evaluasi ketercapaian target, matriks risiko fiskal, dan ekspor laporan keputusan",
        icon="🏛️",
    )

    df = load_pad_historis()
    policy_settings = get_policy_settings()
    real_data = _compute_real_projections(df)

    # Pilihan acuan target
    with st.container(border=True):
        c_src1, c_src2 = st.columns([1.6, 1.4])
        with c_src1:
            target_source = st.radio(
                "🎯 Sumber Acuan Target Evaluasi",
                ["Target R-APBD (Dekomposisi Resmi)", "Target Simulasi (Policy Settings)"],
                horizontal=True,
            )
        with c_src2:
            st.caption(
                "Pilih **Target R-APBD** untuk membandingkan terhadap dokumen input resmi Bapenda, atau **Policy Settings** untuk simulasi target kustom."
            )

    active_targets = (
        real_data["apbd_targets"]
        if target_source.startswith("Target R-APBD")
        else policy_settings["targets"]
    )

    # Hitung volatilitas historis PKB & skor risiko nyata
    pkb_returns = df["PKB"].pct_change().dropna() * 100
    hist_vol = float(pkb_returns.std()) if len(pkb_returns) > 1 else 5.0
    pkb25_shortfall_pct = (
        ((active_targets["pkb_2025"] - real_data["pkb_2025"]) / active_targets["pkb_2025"] * 100)
        if active_targets["pkb_2025"] > 0
        else 0.0
    )
    risk_score, risk_category, risk_color = calculate_risk_score(hist_vol, pkb25_shortfall_pct, len(df))

    tabs = st.tabs(
        [
            "📊 Ringkasan Eksekutif",
            "🎯 Target vs Proyeksi",
            "⚠️ Penilaian Risiko",
            "💡 Rekomendasi Strategis",
            "📈 Analisis Skenario",
            "📄 Ekspor Laporan",
        ]
    )

    # TAB 1: Executive Summary
    with tabs[0]:
        latest_year = int(df["Tahun"].max())
        latest_pkb = float(df.loc[df["Tahun"] == latest_year, "PKB"].iloc[0])
        latest_bbnkb = float(df.loc[df["Tahun"] == latest_year, "BBNKB"].iloc[0])

        proj_total_25 = real_data["pkb_2025"] + real_data["bbnkb_2025"]
        target_total_25 = active_targets["pkb_2025"] + active_targets["bbnkb_2025"]
        gap_total_25 = proj_total_25 - target_total_25
        ach_25 = (proj_total_25 / target_total_25 * 100) if target_total_25 else 0.0

        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_kpi_card(
                label=f"Realisasi PKB+BBNKB {latest_year}",
                value=format_rupiah_compact(latest_pkb + latest_bbnkb, respect_privacy=True),
                subtitle=f"PKB {format_rupiah_compact(latest_pkb)} • BBNKB {format_rupiah_compact(latest_bbnkb)}",
                icon="📊",
                variant="primary",
            )
        with k2:
            render_kpi_card(
                label="Proyeksi Total 2025",
                value=format_rupiah_compact(proj_total_25, respect_privacy=True),
                delta=f"{format_rupiah_compact(gap_total_25, signed=True)} vs Target",
                delta_positive=gap_total_25 >= 0,
                subtitle=format_rupiah_full(proj_total_25),
                icon="🔮",
                variant="success" if gap_total_25 >= 0 else "warning",
            )
        with k3:
            render_kpi_card(
                label="Target Total 2025",
                value=format_rupiah_compact(target_total_25, respect_privacy=True),
                subtitle=target_source.split(" (")[0],
                icon="🎯",
                variant="gold",
            )
        with k4:
            render_kpi_card(
                label="Rasio Ketercapaian 2025",
                value=f"{ach_25:.1f}%",
                delta=f"Risiko: {risk_category.split(' ')[0]}",
                delta_positive=ach_25 >= 100,
                subtitle=f"Skor Risiko {risk_score:.1f}/100",
                icon="🛡️",
                variant="success" if ach_25 >= 100 else "warning",
            )

        render_section_divider()

        c_sum1, c_sum2 = st.columns(2)
        with c_sum1:
            with st.container(border=True):
                st.markdown("#### 🔍 Temuan Kunci Eksekutif")
                pkb_gap_25 = real_data["pkb_2025"] - active_targets["pkb_2025"]
                bbn_gap_25 = real_data["bbnkb_2025"] - active_targets["bbnkb_2025"]
                avg_pkb_growth = float(pkb_returns.mean()) if len(pkb_returns) > 0 else 0.0
                st.markdown(
                    f"- **Cakupan Data**: {len(df)} tahun historis (`{int(df['Tahun'].min())}–{latest_year}`) dengan rata-rata pertumbuhan tahunan PKB **{avg_pkb_growth:+.2f}%**.\n"
                    f"- **Posisi PKB 2025**: Proyeksi **{format_rupiah_compact(real_data['pkb_2025'], respect_privacy=True)}** dibanding target **{format_rupiah_compact(active_targets['pkb_2025'])}** (`{format_rupiah_compact(pkb_gap_25, signed=True)}`).\n"
                    f"- **Posisi BBNKB 2025**: Proyeksi **{format_rupiah_compact(real_data['bbnkb_2025'], respect_privacy=True)}** dibanding target **{format_rupiah_compact(active_targets['bbnkb_2025'])}** (`{format_rupiah_compact(bbn_gap_25, signed=True)}`)."
                )
        with c_sum2:
            with st.container(border=True):
                st.markdown("#### ⚡ Fokus Perhatian Pimpinan")
                st.markdown(
                    "- **Kepatuhan Daftar Ulang**: Pengurangan potensi akibat Tidak Daftar Ulang (TDR) merupakan komponen kebocoran terbesar yang dapat ditekan melalui digitalisasi layanan.\n"
                    "- **Dinamika BBNKB 2026**: Perhatikan dampak kebijakan penghapusan BBN II terhadap struktur penerimaan bersih tahun 2026.\n"
                    "- **Mitigasi Makro**: Pantau pergerakan PDRB dan Suku Bunga BI setiap triwulan untuk kalibrasi ulang target APBD Perubahan."
                )

    # TAB 2: Target vs Projection
    with tabs[1]:
        create_header_with_icon("Evaluasi Target vs Proyeksi (2025–2026)", "🎯")

        categories = ["PKB 2025", "PKB 2026", "BBNKB 2025", "BBNKB 2026"]
        target_vals = [
            active_targets["pkb_2025"],
            active_targets["pkb_2026"],
            active_targets["bbnkb_2025"],
            active_targets["bbnkb_2026"],
        ]
        proj_vals = [
            real_data["pkb_2025"],
            real_data["pkb_2026"],
            real_data["bbnkb_2025"],
            real_data["bbnkb_2026"],
        ]

        with st.container(border=True):
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    name="Target",
                    x=categories,
                    y=target_vals,
                    marker_color="#f59e0b",
                    text=[format_rupiah_compact(v, respect_privacy=True) for v in target_vals],
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{x}</b><br>Target: Rp %{y:,.0f}<extra></extra>",
                )
            )
            fig.add_trace(
                go.Bar(
                    name="Proyeksi Dekomposisi + Makro",
                    x=categories,
                    y=proj_vals,
                    marker_color="#1a5fb4",
                    text=[format_rupiah_compact(v, respect_privacy=True) for v in proj_vals],
                    textposition="outside",
                    cliponaxis=False,
                    hovertemplate="<b>%{x}</b><br>Proyeksi: Rp %{y:,.0f}<extra></extra>",
                )
            )
            apply_plotly_theme(
                fig,
                title="Perbandingan Target vs Proyeksi PKB & BBNKB (2025–2026)",
                height=440,
                xaxis_title="Komponen & Tahun",
                yaxis_title="Nilai (Rupiah)",
                is_currency=True,
            )
            fig.update_layout(
                barmode="group",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)

        gap_rows = []
        for cat, t_val, p_val in zip(categories, target_vals, proj_vals):
            gap = p_val - t_val
            gap_pct = (gap / t_val * 100) if t_val else 0.0
            gap_rows.append(
                {
                    "Komponen": cat,
                    "Target": format_rupiah_compact(t_val, respect_privacy=True),
                    "Proyeksi": format_rupiah_compact(p_val, respect_privacy=True),
                    "Selisih (Gap)": format_rupiah_compact(gap, signed=True, respect_privacy=True),
                    "Persentase Gap": f"{gap_pct:+.2f}%",
                    "Status": "✅ Surplus / Tercapai" if gap >= 0 else "⚠️ Defisit / Perlu Intensifikasi",
                }
            )
        st.dataframe(pd.DataFrame(gap_rows), use_container_width=True, hide_index=True)

    # TAB 3: Risk Assessment
    with tabs[2]:
        create_header_with_icon("Matriks & Indeks Risiko Pencapaian PAD", "⚠️")

        c_r1, c_r2 = st.columns([1.35, 1])
        with c_r1:
            df_risks = create_risk_matrix()

            def _badge_risk(val: str) -> str:
                if val == "High":
                    return "background-color: #dc2626; color: #ffffff; font-weight: 700;"
                if val == "Medium":
                    return "background-color: #d97706; color: #ffffff; font-weight: 700;"
                return "background-color: #059669; color: #ffffff; font-weight: 700;"

            st.dataframe(
                df_risks.style.map(_badge_risk, subset=["Probabilitas", "Dampak"]),
                use_container_width=True,
                hide_index=True,
            )

        with c_r2:
            with st.container(border=True):
                fig_gauge = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=risk_score,
                        number={"suffix": " / 100", "font": {"size": 30}},
                        title={"text": f"<b>Indeks Risiko: {risk_category}</b>", "font": {"size": 16}},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": risk_color, "thickness": 0.65},
                            "bgcolor": "rgba(148, 163, 184, 0.08)",
                            "borderwidth": 1,
                            "bordercolor": "rgba(148, 163, 184, 0.25)",
                            "steps": [
                                {"range": [0, 35], "color": "rgba(16, 185, 129, 0.16)"},
                                {"range": [35, 65], "color": "rgba(245, 158, 11, 0.18)"},
                                {"range": [65, 100], "color": "rgba(239, 68, 68, 0.16)"},
                            ],
                            "threshold": {
                                "line": {"color": "#ef4444", "width": 3},
                                "thickness": 0.8,
                                "value": 65,
                            },
                        },
                    )
                )
                fig_gauge.update_layout(
                    height=290,
                    margin=dict(l=24, r=24, t=64, b=16),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

        if risk_score < 35:
            st.success("✅ **Risiko Terkendali**: Proyeksi berada pada jalur aman terhadap target. Pertahankan monitoring berkala.")
        elif risk_score < 65:
            st.warning("⚠️ **Risiko Menengah**: Terdapat sensitivitas terhadap fluktuasi makro dan ukuran sampel historis. Siapkan rencana kontinjensi triwulanan.")
        else:
            st.error("🚨 **Risiko Tinggi**: Gap terhadap target atau volatilitas cukup lebar. Evaluasi ulang target atau perkuat program intensifikasi penagihan.")

    # TAB 4: Recommendations
    with tabs[3]:
        create_header_with_icon("Rekomendasi Strategis & Peta Jalan Implementasi", "💡")

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            with st.container(border=True):
                st.markdown("#### 🎯 Kebijakan Fiskal")
                st.markdown(
                    "- Pertahankan stabilitas tarif dasar PKB sembari mengoptimalkan insentif kepatuhan tepat waktu.\n"
                    "- Perluas program keringanan denda terukur untuk mencairkan tunggakan tahun berjalan.\n"
                    "- Kawal implementasi skema bagi hasil/opsen HKPD agar arus kas daerah tetap terjaga."
                )
        with rc2:
            with st.container(border=True):
                st.markdown("#### ⚙️ Operasional Pemungutan")
                st.markdown(
                    "- Perkuat integrasi kanal pembayaran digital (QRIS, Virtual Account, marketplace, gerai modern).\n"
                    "- Optimalkan layanan Samsat Keliling dan penagihan door-to-door berbasis data objek tidak daftar ulang.\n"
                    "- Rekonsiliasi data registrasi kendaraan baru secara bulanan."
                )
        with rc3:
            with st.container(border=True):
                st.markdown("#### 🔬 Penguatan Analitik")
                st.markdown(
                    "- Kembangkan pencatatan time-series bulanan/triwulanan untuk memperbesar derajat bebas model.\n"
                    "- Tambahkan indikator jumlah armada aktif & penjualan kendaraan bermotor regional.\n"
                    "- Lakukan kalibrasi ulang proyeksi setiap akhir triwulan."
                )

        st.markdown("#### ⏰ Jadwal Tindak Lanjut Prioritas")
        timeline = pd.DataFrame(
            {
                "Prioritas": ["Tinggi", "Tinggi", "Menengah", "Menengah", "Berkelanjutan"],
                "Rencana Aksi": [
                    "Penetapan pagu target operasional PKB & BBNKB per UPT PPD",
                    "Eksekusi program intensifikasi pencairan tunggakan & penurunan TDR",
                    "Evaluasi realisasi Semester I & kalibrasi asumsi makroekonomi P-APBD",
                    "Sinkronisasi dashboard monitoring bagi hasil HKPD bersama Kab/Kota",
                    "Pengumpulan dataset frekuensi triwulanan untuk pemodelan fase berikutnya",
                ],
                "Target Waktu": ["Triwulan I", "Triwulan I–II", "Triwulan II", "Triwulan II–III", "Triwulan III–IV"],
                "Penanggung Jawab": [
                    "Kepala Bapenda & Bidang Perencanaan",
                    "Bidang Pajak Daerah & UPT PPD",
                    "Tim Analitik & Bidang Evaluasi",
                    "Bidang Pengendalian & Pembinaan",
                    "Tim Data & Sistem Informasi",
                ],
            }
        )
        st.dataframe(timeline, use_container_width=True, hide_index=True)

    # TAB 5: Scenario Comparison
    with tabs[4]:
        create_header_with_icon("Analisis Multi-Skenario & Expected Value (2025)", "📈")

        mult_opt = float(policy_settings["scenario_adjustments"].get("optimistic_multiplier", 1.05))
        mult_pes = float(policy_settings["scenario_adjustments"].get("pessimistic_multiplier", 0.95))

        sc_rows = [
            {
                "Skenario": "Pesimis",
                "Bobot Probabilitas": 0.25,
                "PKB 2025": real_data["pkb_2025"] * mult_pes,
                "BBNKB 2025": real_data["bbnkb_2025"] * mult_pes,
            },
            {
                "Skenario": "Moderat (Utama)",
                "Bobot Probabilitas": 0.50,
                "PKB 2025": real_data["pkb_2025"],
                "BBNKB 2025": real_data["bbnkb_2025"],
            },
            {
                "Skenario": "Optimis",
                "Bobot Probabilitas": 0.25,
                "PKB 2025": real_data["pkb_2025"] * mult_opt,
                "BBNKB 2025": real_data["bbnkb_2025"] * mult_opt,
            },
        ]
        df_sc = pd.DataFrame(sc_rows)
        df_sc["Total PAD 2025"] = df_sc["PKB 2025"] + df_sc["BBNKB 2025"]

        expected_pkb = float(np.sum(df_sc["PKB 2025"] * df_sc["Bobot Probabilitas"]))
        expected_total = float(np.sum(df_sc["Total PAD 2025"] * df_sc["Bobot Probabilitas"]))

        c_ev1, c_ev2 = st.columns(2)
        with c_ev1:
            render_kpi_card(
                label="Expected Value PKB 2025 (Tertimbang)",
                value=format_rupiah_compact(expected_pkb, respect_privacy=True),
                subtitle=format_rupiah_full(expected_pkb),
                icon="📐",
                variant="primary",
            )
        with c_ev2:
            render_kpi_card(
                label="Expected Value Total PKB + BBNKB 2025",
                value=format_rupiah_compact(expected_total, respect_privacy=True),
                subtitle="Probabilitas: 25% Pesimis • 50% Moderat • 25% Optimis",
                icon="💰",
                variant="success",
            )

        with st.container(border=True):
            fig_sc = go.Figure()
            fig_sc.add_trace(
                go.Bar(
                    name="PKB 2025",
                    x=df_sc["Skenario"],
                    y=df_sc["PKB 2025"],
                    marker_color="#1a5fb4",
                    text=[format_rupiah_compact(v, respect_privacy=True) for v in df_sc["PKB 2025"]],
                    textposition="inside",
                )
            )
            fig_sc.add_trace(
                go.Bar(
                    name="BBNKB 2025",
                    x=df_sc["Skenario"],
                    y=df_sc["BBNKB 2025"],
                    marker_color="#f59e0b",
                    text=[format_rupiah_compact(v, respect_privacy=True) for v in df_sc["BBNKB 2025"]],
                    textposition="inside",
                )
            )
            apply_plotly_theme(
                fig_sc,
                title="Komposisi Total Proyeksi PAD 2025 per Skenario",
                height=420,
                xaxis_title="Skenario",
                yaxis_title="Nilai (Rupiah)",
                is_currency=True,
            )
            fig_sc.update_layout(
                barmode="stack",
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_sc, use_container_width=True)

        disp_sc = pd.DataFrame(
            {
                "Skenario": df_sc["Skenario"],
                "Probabilitas": [f"{int(p * 100)}%" for p in df_sc["Bobot Probabilitas"]],
                "PKB 2025": [format_rupiah_compact(v, respect_privacy=True) for v in df_sc["PKB 2025"]],
                "BBNKB 2025": [format_rupiah_compact(v, respect_privacy=True) for v in df_sc["BBNKB 2025"]],
                "Total 2025": [format_rupiah_compact(v, respect_privacy=True) for v in df_sc["Total PAD 2025"]],
            }
        )
        st.dataframe(disp_sc, use_container_width=True, hide_index=True)

    # TAB 6: Export Report (Real HTML Print-Ready + Real Excel Multi-Sheet)
    with tabs[5]:
        create_header_with_icon("Ekspor Laporan Keputusan Eksekutif", "📄")
        render_info_box(
            "Unduh laporan eksekutif siap cetak (<strong>HTML Print-Ready / Save as PDF</strong>) maupun workbook "
            "analitik lengkap (<strong>Excel Multi-Sheet .xlsx</strong>) dengan dukungan sensor privasi dan watermark.",
            box_type="info",
        )

        with st.container(border=True):
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                st.markdown("##### 📋 Bagian yang Disertakan")
                include_summary = st.checkbox("Ringkasan Eksekutif & KPI", value=True)
                include_targets = st.checkbox("Evaluasi Target vs Proyeksi", value=True)
                include_risks = st.checkbox("Matriks & Skor Risiko Fiskal", value=True)
                include_scenarios = st.checkbox("Perbandingan Multi-Skenario", value=True)
                include_recommendations = st.checkbox("Rekomendasi Strategis", value=True)
            with col_opt2:
                st.markdown("##### 🔒 Pengaturan Kerahasiaan Dokumen")
                hide_actual_values = st.checkbox(
                    "Sembunyikan Angka Nominal (Mode Publik)",
                    value=False,
                    help="Mengganti nilai Rupiah pada laporan HTML dengan penanda [DIRAHASIAKAN].",
                )
                add_watermark = st.checkbox(
                    "Sertakan Watermark 'CONFIDENTIAL • BAPENDA JATIM'",
                    value=False,
                )

            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_tag = datetime.now().strftime("%Y%m%d")

            html_report = _build_executive_html_report(
                generated_at=now_str,
                df=df,
                proj=real_data,
                targets=active_targets,
                risk_score=risk_score,
                risk_category=risk_category,
                include_summary=include_summary,
                include_targets=include_targets,
                include_risks=include_risks,
                include_recommendations=include_recommendations,
                include_scenarios=include_scenarios,
                hide_values=hide_actual_values,
                add_watermark=add_watermark,
            )

            df_proyeksi_summary = pd.DataFrame(
                {
                    "Tahun": [2025, 2026],
                    "PKB Proyeksi": [real_data["pkb_2025"], real_data["pkb_2026"]],
                    "BBNKB Proyeksi": [real_data["bbnkb_2025"], real_data["bbnkb_2026"]],
                    "PKB Target": [active_targets["pkb_2025"], active_targets["pkb_2026"]],
                    "BBNKB Target": [active_targets["bbnkb_2025"], active_targets["bbnkb_2026"]],
                }
            )
            excel_bytes = create_comprehensive_excel_report(
                df_historis=df,
                df_proyeksi=df_proyeksi_summary,
                df_pkb_2025=real_data["tables"]["df_pkb25"],
                df_pkb_2026=real_data["tables"]["df_pkb26"],
                df_bbnkb_2025=real_data["tables"]["df_bbn25"],
                df_bbnkb_2026=real_data["tables"]["df_bbn26"],
                model_metrics={
                    "Indeks Risiko": f"{risk_score:.1f}/100 ({risk_category})",
                    "Acuan Target": target_source,
                    "Proyeksi PKB 2025": format_rupiah_full(real_data["pkb_2025"]),
                    "Proyeksi BBNKB 2025": format_rupiah_full(real_data["bbnkb_2025"]),
                },
            )

            html_filename = f"PRO_PAD_Executive_Report_{date_tag}.html"
            xlsx_filename = f"PRO_PAD_Decision_Workbook_{date_tag}.xlsx"

            st.markdown("##### 📥 Unduh Dokumen")
            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button(
                    label="📄 Unduh Laporan Eksekutif Siap Cetak (.html)",
                    data=html_report.encode("utf-8"),
                    file_name=html_filename,
                    mime="text/html",
                    type="primary",
                    use_container_width=True,
                    on_click=lambda: log_export(
                        "Executive HTML Report",
                        html_filename,
                        {"redacted": hide_actual_values, "watermark": add_watermark},
                    ),
                )
            with dl2:
                st.download_button(
                    label="📊 Unduh Workbook Keputusan Lengkap (.xlsx)",
                    data=excel_bytes,
                    file_name=xlsx_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    on_click=lambda: log_export(
                        "Decision Excel Workbook",
                        xlsx_filename,
                        {"size_bytes": len(excel_bytes)},
                    ),
                )


def app() -> None:
    show_decision_support_page()


if __name__ == "__main__":
    app()
