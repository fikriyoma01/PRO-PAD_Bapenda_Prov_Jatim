"""
Policy Settings & Configuration Page
Pengelolaan parameter tarif, target penerimaan, asumsi ekonomi, bobot model, dan ambang validasi.
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.policy_utils import get_default_settings
from utils.ui_components import (
    create_header_with_icon,
    render_info_box,
    render_kpi_card,
    render_page_header,
)
from utils.ui_theme_utils import format_rupiah_compact, format_rupiah_full

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config" / "policy_settings.json"


def load_policy_settings() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            defaults = get_default_settings()
            for k, v in defaults.items():
                if k not in loaded:
                    loaded[k] = v
                elif isinstance(v, dict) and isinstance(loaded[k], dict):
                    merged = v.copy()
                    merged.update(loaded[k])
                    loaded[k] = merged
            return loaded
        except Exception:
            return get_default_settings()
    return get_default_settings()


def save_policy_settings(settings: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    settings.setdefault("metadata", {})
    settings["metadata"]["last_modified"] = datetime.now().isoformat()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)


def show_policy_settings_page() -> None:
    render_page_header(
        title="Pengaturan Kebijakan & Parameter Model",
        subtitle="Konfigurasi target PAD simulasi, tarif pajak, asumsi makroekonomi, bobot ensemble, dan aturan validasi",
        icon="⚙️",
    )

    if "policy_settings" not in st.session_state:
        st.session_state.policy_settings = load_policy_settings()
    if "confirm_reset_policy" not in st.session_state:
        st.session_state.confirm_reset_policy = False

    settings = st.session_state.policy_settings

    render_info_box(
        "<strong>Policy Settings</strong> memungkinkan tim perencana menyesuaikan target simulasi, parameter tarif, "
        "dan bobot model yang terhubung langsung dengan modul <strong>Decision Support</strong>.",
        box_type="info",
    )

    tabs = st.tabs(
        [
            "🎯 Target PAD",
            "📋 Parameter Tarif",
            "📊 Asumsi Ekonomi",
            "🔬 Pengaturan Skenario",
            "⚖️ Bobot Ensemble",
            "✅ Aturan Validasi",
            "💾 Simpan & Kelola",
        ]
    )

    # TAB 1: Target PAD
    with tabs[0]:
        create_header_with_icon("Target Simulasi Penerimaan PAD", "🎯")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 📅 Tahun 2025")
                pkb_2025 = st.number_input(
                    "Target PKB 2025 (Rupiah)",
                    value=float(settings["targets"]["pkb_2025"]),
                    step=100_000_000_000.0,
                    format="%.0f",
                )
                bbnkb_2025 = st.number_input(
                    "Target BBNKB 2025 (Rupiah)",
                    value=float(settings["targets"]["bbnkb_2025"]),
                    step=50_000_000_000.0,
                    format="%.0f",
                )
                total_2025 = pkb_2025 + bbnkb_2025
                render_kpi_card(
                    label="Total Target Simulasi 2025",
                    value=format_rupiah_compact(total_2025),
                    subtitle=format_rupiah_full(total_2025),
                    variant="primary",
                )

            with col2:
                st.markdown("#### 📅 Tahun 2026")
                pkb_2026 = st.number_input(
                    "Target PKB 2026 (Rupiah)",
                    value=float(settings["targets"]["pkb_2026"]),
                    step=100_000_000_000.0,
                    format="%.0f",
                )
                bbnkb_2026 = st.number_input(
                    "Target BBNKB 2026 (Rupiah)",
                    value=float(settings["targets"]["bbnkb_2026"]),
                    step=50_000_000_000.0,
                    format="%.0f",
                )
                total_2026 = pkb_2026 + bbnkb_2026
                render_kpi_card(
                    label="Total Target Simulasi 2026",
                    value=format_rupiah_compact(total_2026),
                    subtitle=format_rupiah_full(total_2026),
                    variant="success",
                )

            growth_target = st.slider(
                "Target Pertumbuhan Tahunan YoY (%)",
                min_value=0.0,
                max_value=15.0,
                value=float(settings["targets"]["growth_target"]),
                step=0.1,
            )

        settings["targets"].update(
            {
                "pkb_2025": pkb_2025,
                "pkb_2026": pkb_2026,
                "bbnkb_2025": bbnkb_2025,
                "bbnkb_2026": bbnkb_2026,
                "growth_target": growth_target,
            }
        )

    # TAB 2: Parameter Kebijakan
    with tabs[1]:
        create_header_with_icon("Parameter Tarif, Insentif & Sanksi Administratif", "📋")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🚗 Tarif PKB")
                pkb_base = st.number_input(
                    "Tarif PKB Kepemilikan Pertama (%)",
                    value=float(settings["policy_parameters"]["pkb_base_rate"]),
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                )
                pkb_progressive = st.number_input(
                    "Tarif PKB Progresif Rata-rata (%)",
                    value=float(settings["policy_parameters"]["pkb_progressive_rate"]),
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                )
            with col2:
                st.markdown("#### 📝 Tarif BBNKB")
                bbnkb_first = st.number_input(
                    "Tarif BBNKB Penyerahan Pertama (%)",
                    value=float(settings["policy_parameters"]["bbnkb_rate_first"]),
                    min_value=0.0,
                    max_value=20.0,
                    step=0.5,
                )
                bbnkb_second = st.number_input(
                    "Tarif BBNKB Kedua & Seterusnya (%)",
                    value=float(settings["policy_parameters"]["bbnkb_rate_second"]),
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                )

            st.markdown("#### 💰 Insentif & Denda")
            c_i1, c_i2, c_i3 = st.columns(3)
            with c_i1:
                late_penalty = st.number_input(
                    "Denda Keterlambatan (% / bulan)",
                    value=float(settings["policy_parameters"]["late_payment_penalty"]),
                    min_value=0.0,
                    max_value=5.0,
                    step=0.1,
                )
            with c_i2:
                early_discount = st.number_input(
                    "Insentif Bayar Lebih Awal (%)",
                    value=float(settings["policy_parameters"]["discount_early_payment"]),
                    min_value=0.0,
                    max_value=20.0,
                    step=0.5,
                )
            with c_i3:
                online_discount = st.number_input(
                    "Insentif Kanal Digital / Online (%)",
                    value=float(settings["policy_parameters"]["discount_online_payment"]),
                    min_value=0.0,
                    max_value=10.0,
                    step=0.5,
                )

        settings["policy_parameters"] = {
            "pkb_base_rate": pkb_base,
            "pkb_progressive_rate": pkb_progressive,
            "bbnkb_rate_first": bbnkb_first,
            "bbnkb_rate_second": bbnkb_second,
            "late_payment_penalty": late_penalty,
            "discount_early_payment": early_discount,
            "discount_online_payment": online_discount,
        }

    # TAB 3: Asumsi Ekonomi
    with tabs[2]:
        create_header_with_icon("Asumsi Makroekonomi & Kepatuhan Pemungutan", "📊")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                inflation = st.slider(
                    "Asumsi Laju Inflasi (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=float(settings["economic_assumptions"]["inflation_assumption"]),
                    step=0.1,
                )
                gdp_growth = st.slider(
                    "Asumsi Pertumbuhan PDRB (%)",
                    min_value=-5.0,
                    max_value=15.0,
                    value=float(settings["economic_assumptions"]["gdp_growth_assumption"]),
                    step=0.1,
                )
                vehicle_growth = st.slider(
                    "Asumsi Pertumbuhan Kendaraan Baru (%)",
                    min_value=0.0,
                    max_value=12.0,
                    value=float(settings["economic_assumptions"]["vehicle_growth_assumption"]),
                    step=0.1,
                )
            with col2:
                compliance = st.slider(
                    "Tingkat Kepatuhan Wajib Pajak (%)",
                    min_value=50.0,
                    max_value=100.0,
                    value=float(settings["economic_assumptions"]["compliance_rate"]),
                    step=1.0,
                )
                efficiency = st.slider(
                    "Efisiensi Realisasi Pemungutan (%)",
                    min_value=50.0,
                    max_value=100.0,
                    value=float(settings["economic_assumptions"]["collection_efficiency"]),
                    step=1.0,
                )

        settings["economic_assumptions"] = {
            "inflation_assumption": inflation,
            "gdp_growth_assumption": gdp_growth,
            "vehicle_growth_assumption": vehicle_growth,
            "compliance_rate": compliance,
            "collection_efficiency": efficiency,
        }

    # TAB 4: Scenario Settings
    with tabs[3]:
        create_header_with_icon("Konfigurasi Rentang Skenario", "🔬")
        with st.container(border=True):
            use_data_driven = st.checkbox(
                "Gunakan Rentang Statistik Data-Driven pada Halaman Proyeksi",
                value=bool(settings["scenario_adjustments"]["use_data_driven"]),
            )
            col1, col2 = st.columns(2)
            with col1:
                optimistic = st.slider(
                    "Pengali Skenario Optimis",
                    min_value=1.00,
                    max_value=1.35,
                    value=float(settings["scenario_adjustments"]["optimistic_multiplier"]),
                    step=0.01,
                    format="%.2f",
                )
            with col2:
                pessimistic = st.slider(
                    "Pengali Skenario Pesimis",
                    min_value=0.65,
                    max_value=1.00,
                    value=float(settings["scenario_adjustments"]["pessimistic_multiplier"]),
                    step=0.01,
                    format="%.2f",
                )

        settings["scenario_adjustments"].update(
            {
                "use_data_driven": use_data_driven,
                "optimistic_multiplier": optimistic,
                "pessimistic_multiplier": pessimistic,
            }
        )

    # TAB 5: Model Weights
    with tabs[4]:
        create_header_with_icon("Bobot Kombinasi Model Ensemble", "⚖️")
        with st.container(border=True):
            ols_weight = st.slider(
                "Bobot OLS Regression",
                min_value=0.0,
                max_value=1.0,
                value=float(settings["model_weights"]["ols_weight"]),
                step=0.05,
            )
            arima_weight = st.slider(
                "Bobot ARIMA",
                min_value=0.0,
                max_value=1.0,
                value=float(settings["model_weights"]["arima_weight"]),
                step=0.05,
            )
            exp_weight = st.slider(
                "Bobot Exponential Smoothing",
                min_value=0.0,
                max_value=1.0,
                value=float(settings["model_weights"]["exp_smoothing_weight"]),
                step=0.05,
            )

            total_weight = ols_weight + arima_weight + exp_weight
            if abs(total_weight - 1.0) > 0.01:
                st.warning(f"⚠️ Total bobot saat ini **{total_weight:.2f}**. Sesuaikan hingga tepat **1.00**.")
            else:
                st.success(f"✅ Total bobot valid (**{total_weight:.2f}**).")

        settings["model_weights"] = {
            "ols_weight": ols_weight,
            "arima_weight": arima_weight,
            "exp_smoothing_weight": exp_weight,
        }

    # TAB 6: Validation Rules
    with tabs[5]:
        create_header_with_icon("Ambang Batas Kualitas & Validasi Model", "✅")
        with st.container(border=True):
            min_r2 = st.slider(
                "Batas Minimum R²",
                min_value=0.0,
                max_value=1.0,
                value=float(settings["validation_thresholds"]["min_r2"]),
                step=0.05,
            )
            max_mape = st.slider(
                "Batas Maksimum MAPE (%)",
                min_value=1.0,
                max_value=50.0,
                value=float(settings["validation_thresholds"]["max_mape"]),
                step=1.0,
            )
            max_rmse = st.number_input(
                "Batas Maksimum RMSE (Rupiah)",
                value=float(settings["validation_thresholds"]["max_rmse"]),
                step=50_000_000_000.0,
                format="%.0f",
            )

        settings["validation_thresholds"] = {
            "min_r2": min_r2,
            "max_mape": max_mape,
            "max_rmse": max_rmse,
        }

    # TAB 7: Manage Settings (Fixed Confirmation & Direct Download)
    with tabs[6]:
        create_header_with_icon("Simpan, Ekspor, atau Kembalikan Pengaturan Default", "💾")

        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Simpan Pengaturan", type="primary", use_container_width=True):
                    save_policy_settings(settings)
                    st.session_state.policy_settings = settings
                    st.success("✅ Pengaturan kebijakan berhasil disimpan!")

            with col2:
                if st.button("🔄 Reset ke Default", use_container_width=True):
                    st.session_state.confirm_reset_policy = True

            with col3:
                settings_json = json.dumps(settings, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Unduh Konfigurasi (.json)",
                    data=settings_json.encode("utf-8"),
                    file_name=f"policy_settings_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True,
                )

            if st.session_state.confirm_reset_policy:
                st.warning("⚠️ Apakah Anda yakin ingin mengembalikan seluruh parameter kebijakan ke nilai default?")
                c_yes, c_no = st.columns(2)
                with c_yes:
                    if st.button("✅ Ya, Kembalikan Default", type="primary", use_container_width=True):
                        default_cfg = get_default_settings()
                        save_policy_settings(default_cfg)
                        st.session_state.policy_settings = default_cfg
                        st.session_state.confirm_reset_policy = False
                        st.rerun()
                with c_no:
                    if st.button("✖ Batal", use_container_width=True):
                        st.session_state.confirm_reset_policy = False
                        st.rerun()

        st.markdown("#### 📋 Ringkasan Konfigurasi Aktif")
        summary_df = pd.DataFrame(
            {
                "Parameter": [
                    "Target Simulasi PKB 2025",
                    "Target Simulasi BBNKB 2025",
                    "Target Pertumbuhan Tahunan",
                    "Tarif Dasar PKB",
                    "Tarif BBNKB Pertama",
                    "Asumsi Inflasi / PDRB",
                    "Tingkat Kepatuhan / Efisiensi",
                    "Metode Skenario Data-Driven",
                    "Bobot Model (OLS / ARIMA / Exp)",
                ],
                "Nilai Aktif": [
                    format_rupiah_compact(settings["targets"]["pkb_2025"]),
                    format_rupiah_compact(settings["targets"]["bbnkb_2025"]),
                    f"{settings['targets']['growth_target']:.1f}%",
                    f"{settings['policy_parameters']['pkb_base_rate']:.1f}%",
                    f"{settings['policy_parameters']['bbnkb_rate_first']:.1f}%",
                    f"{settings['economic_assumptions']['inflation_assumption']:.1f}% / {settings['economic_assumptions']['gdp_growth_assumption']:.1f}%",
                    f"{settings['economic_assumptions']['compliance_rate']:.0f}% / {settings['economic_assumptions']['collection_efficiency']:.0f}%",
                    "Aktif" if settings["scenario_adjustments"]["use_data_driven"] else "Manual Multiplier",
                    f"{settings['model_weights']['ols_weight']:.2f} / {settings['model_weights']['arima_weight']:.2f} / {settings['model_weights']['exp_smoothing_weight']:.2f}",
                ],
            }
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.caption(
            f"Terakhir diperbarui: `{settings.get('metadata', {}).get('last_modified', '-')}` • Versi `{settings.get('metadata', {}).get('version', '2.0')}`"
        )

        with st.expander("📤 Impor Berkas Konfigurasi JSON"):
            uploaded_file = st.file_uploader("Pilih berkas JSON Policy Settings", type=["json"])
            if uploaded_file is not None:
                try:
                    imported_settings = json.load(uploaded_file)
                    if st.button("✅ Terapkan Konfigurasi Impor", type="primary"):
                        save_policy_settings(imported_settings)
                        st.session_state.policy_settings = imported_settings
                        st.success("✅ Konfigurasi berhasil diterapkan!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Berkas JSON tidak valid: {e}")


def app() -> None:
    show_policy_settings_page()


if __name__ == "__main__":
    app()
