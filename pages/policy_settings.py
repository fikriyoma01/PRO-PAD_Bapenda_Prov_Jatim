"""
Policy Settings & Configuration Page
Allows users to customize parameters, targets, and assumptions for policy planning
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from utils.ui_components import render_gradient_header, render_info_box, create_header_with_icon


# Configuration file path
CONFIG_FILE = Path("config/policy_settings.json")


def load_policy_settings():
    """Load policy settings from JSON file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return get_default_settings()


def save_policy_settings(settings):
    """Save policy settings to JSON file"""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    settings['last_modified'] = datetime.now().isoformat()
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


def get_default_settings():
    """Get default policy settings"""
    return {
        'targets': {
            'pkb_2025': 10500000000000,  # Rp 10.5T
            'pkb_2026': 11000000000000,  # Rp 11.0T
            'bbnkb_2025': 2500000000000,  # Rp 2.5T
            'bbnkb_2026': 2600000000000,  # Rp 2.6T
            'growth_target': 5.0,  # %
        },
        'policy_parameters': {
            'pkb_base_rate': 1.5,  # %
            'pkb_progressive_rate': 2.5,  # %
            'bbnkb_rate_first': 12.5,  # %
            'bbnkb_rate_second': 1.0,  # %
            'late_payment_penalty': 2.0,  # % per month
            'discount_early_payment': 5.0,  # %
            'discount_online_payment': 2.0,  # %
        },
        'economic_assumptions': {
            'inflation_assumption': 3.0,  # %
            'gdp_growth_assumption': 5.2,  # %
            'vehicle_growth_assumption': 4.0,  # %
            'compliance_rate': 85.0,  # %
            'collection_efficiency': 90.0,  # %
        },
        'scenario_adjustments': {
            'optimistic_multiplier': 1.10,  # 10% above
            'pessimistic_multiplier': 0.90,  # 10% below
            'use_data_driven': True,  # Use statistical bounds
        },
        'model_weights': {
            'ols_weight': 0.50,
            'arima_weight': 0.25,
            'exp_smoothing_weight': 0.25,
        },
        'validation_thresholds': {
            'min_r2': 0.5,
            'max_mape': 15.0,
            'max_rmse': 500000000000,  # Rp 500B
        },
        'metadata': {
            'created': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'version': '2.0'
        }
    }


def show_policy_settings_page():
    render_gradient_header(
        title="Policy Settings & Configuration",
        subtitle="Customize parameters, targets, and assumptions untuk perencanaan kebijakan",
        icon="⚙️"
    )

    # Load current settings
    if 'policy_settings' not in st.session_state:
        st.session_state.policy_settings = load_policy_settings()

    settings = st.session_state.policy_settings

    render_info_box(
        "💡 <strong>Policy Settings</strong> memungkinkan Anda menyesuaikan target, parameter kebijakan, "
        "dan asumsi ekonomi untuk mendukung perencanaan strategis dan simulasi kebijakan.",
        box_type="info"
    )

    # Tabs for different settings categories
    tabs = st.tabs([
        "🎯 Target PAD",
        "📋 Parameter Kebijakan",
        "📊 Asumsi Ekonomi",
        "🔬 Scenario Settings",
        "⚖️ Model Weights",
        "✅ Validation Rules",
        "💾 Manage Settings"
    ])

    # TAB 1: Target PAD
    with tabs[0]:
        create_header_with_icon("Target Penerimaan PAD", "🎯")

        st.markdown("""
        <div class="info-box">
        Tetapkan target penerimaan PKB dan BBNKB untuk tahun proyeksi.
        Target ini akan digunakan sebagai benchmark dalam analisis dekomposisi dan gauge charts.
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📅 Target 2025")
            pkb_2025 = st.number_input(
                "Target PKB 2025 (Rupiah)",
                value=float(settings['targets']['pkb_2025']),
                step=100000000000.0,
                format="%.0f",
                help="Target penerimaan PKB untuk tahun 2025"
            )

            bbnkb_2025 = st.number_input(
                "Target BBNKB 2025 (Rupiah)",
                value=float(settings['targets']['bbnkb_2025']),
                step=50000000000.0,
                format="%.0f",
                help="Target penerimaan BBNKB untuk tahun 2025"
            )

            total_2025 = pkb_2025 + bbnkb_2025
            st.metric("Total Target PAD 2025", f"Rp {total_2025/1e12:.2f}T")

        with col2:
            st.subheader("📅 Target 2026")
            pkb_2026 = st.number_input(
                "Target PKB 2026 (Rupiah)",
                value=float(settings['targets']['pkb_2026']),
                step=100000000000.0,
                format="%.0f",
                help="Target penerimaan PKB untuk tahun 2026"
            )

            bbnkb_2026 = st.number_input(
                "Target BBNKB 2026 (Rupiah)",
                value=float(settings['targets']['bbnkb_2026']),
                step=50000000000.0,
                format="%.0f",
                help="Target penerimaan BBNKB untuk tahun 2026"
            )

            total_2026 = pkb_2026 + bbnkb_2026
            st.metric("Total Target PAD 2026", f"Rp {total_2026/1e12:.2f}T")

        # Growth target
        st.markdown("---")
        growth_target = st.slider(
            "Target Pertumbuhan Tahunan (%)",
            min_value=0.0,
            max_value=15.0,
            value=float(settings['targets']['growth_target']),
            step=0.1,
            help="Target pertumbuhan PAD year-over-year"
        )

        # Update settings
        settings['targets']['pkb_2025'] = pkb_2025
        settings['targets']['pkb_2026'] = pkb_2026
        settings['targets']['bbnkb_2025'] = bbnkb_2025
        settings['targets']['bbnkb_2026'] = bbnkb_2026
        settings['targets']['growth_target'] = growth_target

    # TAB 2: Parameter Kebijakan
    with tabs[1]:
        create_header_with_icon("Parameter Tarif & Kebijakan", "📋")

        st.markdown("""
        <div class="warning-box">
        ⚠️ <strong>Perhatian:</strong> Perubahan parameter tarif akan mempengaruhi perhitungan proyeksi.
        Pastikan nilai yang dimasukkan sesuai dengan regulasi yang berlaku.
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🚗 Tarif PKB")
            pkb_base = st.number_input(
                "Tarif PKB Dasar (%)",
                value=float(settings['policy_parameters']['pkb_base_rate']),
                min_value=0.0,
                max_value=10.0,
                step=0.1
            )

            pkb_progressive = st.number_input(
                "Tarif PKB Progresif (%)",
                value=float(settings['policy_parameters']['pkb_progressive_rate']),
                min_value=0.0,
                max_value=10.0,
                step=0.1
            )

        with col2:
            st.subheader("📝 Tarif BBNKB")
            bbnkb_first = st.number_input(
                "Tarif BBNKB Pertama (%)",
                value=float(settings['policy_parameters']['bbnkb_rate_first']),
                min_value=0.0,
                max_value=20.0,
                step=0.5
            )

            bbnkb_second = st.number_input(
                "Tarif BBNKB Kedua & Seterusnya (%)",
                value=float(settings['policy_parameters']['bbnkb_rate_second']),
                min_value=0.0,
                max_value=5.0,
                step=0.1
            )

        st.markdown("---")
        st.subheader("💰 Insentif & Penalti")

        col1, col2, col3 = st.columns(3)

        with col1:
            late_penalty = st.number_input(
                "Denda Keterlambatan (% per bulan)",
                value=float(settings['policy_parameters']['late_payment_penalty']),
                min_value=0.0,
                max_value=5.0,
                step=0.1
            )

        with col2:
            early_discount = st.number_input(
                "Diskon Bayar Awal (%)",
                value=float(settings['policy_parameters']['discount_early_payment']),
                min_value=0.0,
                max_value=20.0,
                step=0.5
            )

        with col3:
            online_discount = st.number_input(
                "Diskon Bayar Online (%)",
                value=float(settings['policy_parameters']['discount_online_payment']),
                min_value=0.0,
                max_value=10.0,
                step=0.5
            )

        # Update settings
        settings['policy_parameters'] = {
            'pkb_base_rate': pkb_base,
            'pkb_progressive_rate': pkb_progressive,
            'bbnkb_rate_first': bbnkb_first,
            'bbnkb_rate_second': bbnkb_second,
            'late_payment_penalty': late_penalty,
            'discount_early_payment': early_discount,
            'discount_online_payment': online_discount,
        }

    # TAB 3: Asumsi Ekonomi
    with tabs[2]:
        create_header_with_icon("Asumsi Variabel Ekonomi", "📊")

        st.markdown("""
        <div class="info-box">
        Tentukan asumsi untuk variabel ekonomi yang akan digunakan dalam proyeksi baseline.
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            inflation = st.slider(
                "Asumsi Inflasi (%)",
                min_value=0.0,
                max_value=10.0,
                value=float(settings['economic_assumptions']['inflation_assumption']),
                step=0.1
            )

            gdp_growth = st.slider(
                "Asumsi Pertumbuhan PDRB (%)",
                min_value=-5.0,
                max_value=15.0,
                value=float(settings['economic_assumptions']['gdp_growth_assumption']),
                step=0.1
            )

            vehicle_growth = st.slider(
                "Asumsi Pertumbuhan Kendaraan (%)",
                min_value=0.0,
                max_value=10.0,
                value=float(settings['economic_assumptions']['vehicle_growth_assumption']),
                step=0.1
            )

        with col2:
            compliance = st.slider(
                "Tingkat Kepatuhan Wajib Pajak (%)",
                min_value=50.0,
                max_value=100.0,
                value=float(settings['economic_assumptions']['compliance_rate']),
                step=1.0,
                help="Persentase wajib pajak yang membayar tepat waktu"
            )

            efficiency = st.slider(
                "Efisiensi Pemungutan (%)",
                min_value=50.0,
                max_value=100.0,
                value=float(settings['economic_assumptions']['collection_efficiency']),
                step=1.0,
                help="Persentase potensi yang berhasil terkumpul"
            )

        # Update settings
        settings['economic_assumptions'] = {
            'inflation_assumption': inflation,
            'gdp_growth_assumption': gdp_growth,
            'vehicle_growth_assumption': vehicle_growth,
            'compliance_rate': compliance,
            'collection_efficiency': efficiency,
        }

    # TAB 4: Scenario Settings
    with tabs[3]:
        create_header_with_icon("Pengaturan Skenario", "🔬")

        use_data_driven = st.checkbox(
            "Gunakan Data-Driven Scenario Bounds",
            value=settings['scenario_adjustments']['use_data_driven'],
            help="Gunakan metode statistik untuk menghitung bounds, bukan fixed percentage"
        )

        if not use_data_driven:
            st.subheader("Traditional Scenario Multipliers")

            col1, col2 = st.columns(2)

            with col1:
                optimistic = st.slider(
                    "Multiplier Skenario Optimis",
                    min_value=1.0,
                    max_value=1.5,
                    value=float(settings['scenario_adjustments']['optimistic_multiplier']),
                    step=0.01,
                    format="%.2f"
                )

            with col2:
                pessimistic = st.slider(
                    "Multiplier Skenario Pesimis",
                    min_value=0.5,
                    max_value=1.0,
                    value=float(settings['scenario_adjustments']['pessimistic_multiplier']),
                    step=0.01,
                    format="%.2f"
                )

            settings['scenario_adjustments']['optimistic_multiplier'] = optimistic
            settings['scenario_adjustments']['pessimistic_multiplier'] = pessimistic

        settings['scenario_adjustments']['use_data_driven'] = use_data_driven

    # TAB 5: Model Weights
    with tabs[4]:
        create_header_with_icon("Bobot Model Ensemble", "⚖️")

        st.markdown("""
        <div class="info-box">
        Sesuaikan bobot untuk setiap model dalam ensemble forecasting.
        Total bobot harus sama dengan 1.0 (100%).
        </div>
        """, unsafe_allow_html=True)

        ols_weight = st.slider(
            "OLS Regression Weight",
            min_value=0.0,
            max_value=1.0,
            value=float(settings['model_weights']['ols_weight']),
            step=0.05
        )

        arima_weight = st.slider(
            "ARIMA Weight",
            min_value=0.0,
            max_value=1.0,
            value=float(settings['model_weights']['arima_weight']),
            step=0.05
        )

        exp_weight = st.slider(
            "Exponential Smoothing Weight",
            min_value=0.0,
            max_value=1.0,
            value=float(settings['model_weights']['exp_smoothing_weight']),
            step=0.05
        )

        total_weight = ols_weight + arima_weight + exp_weight

        if abs(total_weight - 1.0) > 0.01:
            st.warning(f"⚠️ Total bobot = {total_weight:.2f}. Harus sama dengan 1.0!")
        else:
            st.success(f"✅ Total bobot = {total_weight:.2f} (Valid)")

        settings['model_weights'] = {
            'ols_weight': ols_weight,
            'arima_weight': arima_weight,
            'exp_smoothing_weight': exp_weight,
        }

    # TAB 6: Validation Rules
    with tabs[5]:
        create_header_with_icon("Aturan Validasi Model", "✅")

        st.markdown("""
        <div class="warning-box">
        Tetapkan threshold untuk validasi kualitas model. Model yang tidak memenuhi kriteria akan diberi warning.
        </div>
        """, unsafe_allow_html=True)

        min_r2 = st.slider(
            "Minimum R² (Coefficient of Determination)",
            min_value=0.0,
            max_value=1.0,
            value=float(settings['validation_thresholds']['min_r2']),
            step=0.05,
            help="Model dengan R² di bawah threshold ini dianggap lemah"
        )

        max_mape = st.slider(
            "Maximum MAPE - Mean Absolute Percentage Error (%)",
            min_value=0.0,
            max_value=50.0,
            value=float(settings['validation_thresholds']['max_mape']),
            step=1.0,
            help="Model dengan MAPE di atas threshold ini dianggap tidak akurat"
        )

        max_rmse = st.number_input(
            "Maximum RMSE - Root Mean Squared Error (Rupiah)",
            value=float(settings['validation_thresholds']['max_rmse']),
            step=50000000000.0,
            format="%.0f",
            help="Model dengan RMSE di atas threshold ini memiliki error besar"
        )

        settings['validation_thresholds'] = {
            'min_r2': min_r2,
            'max_mape': max_mape,
            'max_rmse': max_rmse,
        }

    # TAB 7: Manage Settings
    with tabs[6]:
        create_header_with_icon("Kelola Pengaturan", "💾")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save Settings", type="primary", use_container_width=True):
                save_policy_settings(settings)
                st.session_state.policy_settings = settings
                st.success("✅ Settings berhasil disimpan!")
                st.balloons()

        with col2:
            if st.button("🔄 Reset to Default", use_container_width=True):
                if st.checkbox("Konfirmasi reset ke default"):
                    settings = get_default_settings()
                    save_policy_settings(settings)
                    st.session_state.policy_settings = settings
                    st.success("✅ Settings direset ke default!")
                    st.rerun()

        with col3:
            if st.button("📥 Export Settings", use_container_width=True):
                settings_json = json.dumps(settings, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=settings_json,
                    file_name=f"policy_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        st.markdown("---")
        st.subheader("📊 Current Settings Summary")

        # Display summary
        summary_data = {
            'Category': [
                'Target PKB 2025',
                'Target BBNKB 2025',
                'Target Growth',
                'PKB Base Rate',
                'BBNKB First Rate',
                'Inflation Assumption',
                'Compliance Rate',
                'Use Data-Driven Scenarios',
                'OLS Model Weight'
            ],
            'Value': [
                f"Rp {settings['targets']['pkb_2025']/1e12:.2f}T",
                f"Rp {settings['targets']['bbnkb_2025']/1e12:.2f}T",
                f"{settings['targets']['growth_target']:.1f}%",
                f"{settings['policy_parameters']['pkb_base_rate']:.1f}%",
                f"{settings['policy_parameters']['bbnkb_rate_first']:.1f}%",
                f"{settings['economic_assumptions']['inflation_assumption']:.1f}%",
                f"{settings['economic_assumptions']['compliance_rate']:.1f}%",
                "Yes" if settings['scenario_adjustments']['use_data_driven'] else "No",
                f"{settings['model_weights']['ols_weight']:.2f}"
            ]
        }

        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)

        # Metadata
        st.caption(f"Last modified: {settings['metadata'].get('last_modified', 'Never')}")
        st.caption(f"Version: {settings['metadata'].get('version', 'Unknown')}")

        # Import settings
        st.markdown("---")
        st.subheader("📤 Import Settings")
        uploaded_file = st.file_uploader("Upload policy settings JSON", type=['json'])
        if uploaded_file is not None:
            try:
                imported_settings = json.load(uploaded_file)
                if st.button("Apply Imported Settings"):
                    save_policy_settings(imported_settings)
                    st.session_state.policy_settings = imported_settings
                    st.success("✅ Settings imported successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error importing settings: {e}")


def app():
    show_policy_settings_page()


if __name__ == "__main__":
    app()
