"""
Dataset Historis Page — Eksplorasi Data PAD & Variabel Makroekonomi (2018–2024)
"""

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_pad_historis
from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_kpi_card,
    render_page_header,
    render_section_divider,
)
from utils.ui_theme_utils import format_rupiah_compact, format_rupiah_full

MACRO_VARS = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]


def show_dataset_page() -> None:
    df = load_pad_historis()
    min_year = int(df["Tahun"].min())
    max_year = int(df["Tahun"].max())

    render_page_header(
        title=f"Dataset Historis ({min_year}–{max_year})",
        subtitle="Eksplorasi realisasi PKB, BBNKB, 7 indikator makroekonomi Jawa Timur, serta matriks korelasi antarvariabel",
        icon="📄",
    )

    if st.session_state.get("use_custom_data", False):
        st.info("📝 Saat ini menggunakan **Dataset Kustom** hasil penyuntingan dari menu Editor Data.")

    # --- Ringkasan Statistik PKB & BBNKB ---
    create_header_with_icon(
        "Ringkasan Statistik PKB & BBNKB",
        "💰",
        subtitle=f"Nilai minimum, rata-rata historis, dan capaian tertinggi sepanjang periode {min_year}–{max_year}",
    )

    for var, icon in [("PKB", "🚗"), ("BBNKB", "📝")]:
        lowest_val = float(df[var].min())
        lowest_year = int(df.loc[df[var].idxmin(), "Tahun"])
        average_val = float(df[var].mean())
        highest_val = float(df[var].max())
        highest_year = int(df.loc[df[var].idxmax(), "Tahun"])

        st.markdown(
            f"<h4 style='color: var(--heading-accent); margin: 0.9rem 0 0.5rem 0; font-weight: 700;'>{icon} {var}</h4>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            render_kpi_card(
                label=f"{var} Terendah ({lowest_year})",
                value=format_rupiah_compact(lowest_val),
                subtitle=format_rupiah_full(lowest_val),
                icon="🔻",
                variant="warning",
            )
        with col2:
            render_kpi_card(
                label=f"Rata-rata {var} ({min_year}–{max_year})",
                value=format_rupiah_compact(average_val),
                subtitle=format_rupiah_full(average_val),
                icon="📊",
                variant="primary",
            )
        with col3:
            render_kpi_card(
                label=f"{var} Tertinggi ({highest_year})",
                value=format_rupiah_compact(highest_val),
                subtitle=format_rupiah_full(highest_val),
                icon="🔺",
                variant="success",
            )

    render_section_divider()

    # --- Tabel Data Lengkap ---
    create_header_with_icon(
        "Tabel Data Lengkap",
        "📂",
        subtitle="Seluruh variabel penerimaan pajak daerah dan indikator makroekonomi tahunan",
    )

    format_map = {
        "Tahun": "{:.0f}",
        "PKB": "Rp {:,.0f}",
        "BBNKB": "Rp {:,.0f}",
        "PDRB": "{:.2f}%",
        "Rasio Gini": "{:.3f}",
        "IPM": "{:.2f}",
        "TPT": "{:.2f}%",
        "Kemiskinan": "{:.2f}%",
        "Inflasi": "{:.2f}%",
        "Suku Bunga": "{:.2f}%",
    }
    active_fmt = {k: v for k, v in format_map.items() if k in df.columns}
    st.dataframe(df.style.format(active_fmt), use_container_width=True, hide_index=True)

    render_section_divider()

    # --- Visualisasi Tren PKB & BBNKB ---
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        create_header_with_icon("Tren PKB & BBNKB", "📈")
        with st.container(border=True):
            fig = px.line(
                df,
                x="Tahun",
                y=["PKB", "BBNKB"],
                markers=True,
                line_shape="spline",
                labels={"value": "Rupiah", "variable": "Jenis Pajak"},
                color_discrete_map={"PKB": "#1a5fb4", "BBNKB": "#10b981"},
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            apply_plotly_theme(
                fig,
                title=f"Tren PKB & BBNKB ({min_year}–{max_year})",
                height=420,
                xaxis_title="Tahun",
                yaxis_title="Nilai Penerimaan (Rupiah)",
                is_currency=True,
            )
            fig.update_yaxes(rangemode="tozero")
            fig.update_xaxes(dtick=1)
            fig.update_layout(
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        create_header_with_icon("Indikator Makroekonomi", "📊")
        with st.container(border=True):
            available_macros = [m for m in MACRO_VARS if m in df.columns]
            selected = st.selectbox("Pilih indikator makroekonomi:", available_macros)

            fig2 = px.bar(
                df,
                x="Tahun",
                y=selected,
                text=selected,
                color=selected,
                color_continuous_scale="Blues",
            )
            fig2.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
            apply_plotly_theme(
                fig2,
                title=f"Perkembangan {selected} ({min_year}–{max_year})",
                height=352,
                xaxis_title="Tahun",
                yaxis_title=selected,
                show_legend=False,
            )
            fig2.update_layout(coloraxis_showscale=False)
            fig2.update_xaxes(dtick=1)
            st.plotly_chart(fig2, use_container_width=True)

    render_section_divider()

    # --- Correlation Heatmap ---
    create_header_with_icon(
        "Correlation Heatmap — Hubungan Antarvariabel",
        "🔥",
        subtitle="Kekuatan dan arah korelasi Pearson antara penerimaan pajak dan indikator makroekonomi",
    )

    with st.expander("ℹ️ Panduan Membaca Correlation Heatmap", expanded=False):
        st.markdown(
            """
            **Correlation Heatmap** mengukur kekuatan hubungan linear antar dua variabel pada rentang **-1.0 hingga +1.0**:
            - **+0.70 s.d. +1.00** (Merah Tua): Korelasi positif kuat — variabel bergerak searah.
            - **-0.30 s.d. +0.30** (Putih/Netral): Korelasi lemah atau tidak signifikan secara linear.
            - **-0.70 s.d. -1.00** (Biru Tua): Korelasi negatif kuat — variabel bergerak berlawanan arah.

            **Peringatan Multikolinearitas**: Apabila dua variabel makroekonomi memiliki korelasi `|r| > 0.70`, hindari
            memasukkan keduanya secara bersamaan ke dalam satu model regresi berganda agar koefisien tetap stabil.
            """
        )

    available_macros = [m for m in MACRO_VARS if m in df.columns]
    all_vars = ["PKB", "BBNKB"] + available_macros
    corr_df = df[all_vars].corr()

    with st.container(border=True):
        fig_corr = go.Figure(
            data=go.Heatmap(
                z=corr_df.values,
                x=corr_df.columns,
                y=corr_df.columns,
                colorscale="RdBu_r",
                zmin=-1,
                zmax=1,
                zmid=0,
                text=corr_df.values,
                texttemplate="%{text:.2f}",
                textfont={"size": 11},
                colorbar=dict(
                    title="Korelasi (r)",
                    tickvals=[-1, -0.5, 0, 0.5, 1],
                    ticktext=["-1.0 (Negatif)", "-0.5", "0.0", "+0.5", "+1.0 (Positif)"],
                ),
                hoverongaps=False,
                hovertemplate="<b>%{y} vs %{x}</b><br>Korelasi Pearson: %{z:.3f}<extra></extra>",
            )
        )
        apply_plotly_theme(
            fig_corr,
            title=f"Matriks Korelasi PKB, BBNKB & Indikator Makroekonomi ({min_year}–{max_year}, n={len(df)})",
            height=520,
            margin=dict(l=90, r=60, t=72, b=90),
        )
        fig_corr.update_xaxes(tickangle=-35, showgrid=False)
        fig_corr.update_yaxes(showgrid=False, autorange="reversed")
        st.plotly_chart(fig_corr, use_container_width=True)

    # --- Temuan Korelasi Signifikan ---
    create_header_with_icon("Temuan Korelasi Utama", "🔍")

    pkb_corr = corr_df["PKB"].drop(["PKB", "BBNKB"], errors="ignore").sort_values(ascending=False)
    bbnkb_corr = corr_df["BBNKB"].drop(["PKB", "BBNKB"], errors="ignore").sort_values(ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("#### 🚗 Korelasi Indikator Makro terhadap PKB")
            for var, corr_val in pkb_corr.items():
                badge = "🔴" if corr_val > 0.5 else "🔵" if corr_val < -0.5 else "⚪"
                strength = "Kuat" if abs(corr_val) > 0.7 else "Sedang" if abs(corr_val) > 0.4 else "Lemah"
                direction = "positif" if corr_val > 0 else "negatif"
                st.markdown(f"- {badge} **{var}**: `{corr_val:+.3f}` — *{strength} ({direction})*")

    with col2:
        with st.container(border=True):
            st.markdown("#### 📝 Korelasi Indikator Makro terhadap BBNKB")
            for var, corr_val in bbnkb_corr.items():
                badge = "🔴" if corr_val > 0.5 else "🔵" if corr_val < -0.5 else "⚪"
                strength = "Kuat" if abs(corr_val) > 0.7 else "Sedang" if abs(corr_val) > 0.4 else "Lemah"
                direction = "positif" if corr_val > 0 else "negatif"
                st.markdown(f"- {badge} **{var}**: `{corr_val:+.3f}` — *{strength} ({direction})*")

    # --- Multicollinearity Check ---
    high_corr_pairs = []
    for i in range(len(available_macros)):
        for j in range(i + 1, len(available_macros)):
            corr_value = float(corr_df.loc[available_macros[i], available_macros[j]])
            if abs(corr_value) > 0.7:
                high_corr_pairs.append((available_macros[i], available_macros[j], corr_value))

    if high_corr_pairs:
        pairs_md = "\n".join(
            f"- **{v1}** ↔ **{v2}**: `{val:+.3f}`" for v1, v2, val in high_corr_pairs
        )
        st.warning(
            f"⚠️ **Deteksi Multikolinearitas (`|r| > 0.70`)** pada pasangan indikator makro berikut:\n\n{pairs_md}\n\n"
            "Disarankan menggunakan regresi sederhana per prediktor atau memilih salah satu variabel yang paling relevan secara ekonomi."
        )
    else:
        st.success("✅ Tidak terdeteksi multikolinearitas tinggi antar indikator makroekonomi (`|r| <= 0.70`).")


def app() -> None:
    show_dataset_page()


if __name__ == "__main__":
    app()
