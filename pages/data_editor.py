"""
Data Editor Page
Allows users to view, edit, and manage historical data and custom datasets
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from utils.ui_components import render_gradient_header, render_info_box, create_header_with_icon
from utils.audit_utils import log_event


# Data file paths
DATA_DIR = Path("datasets")
HISTORIS_FILE = DATA_DIR / "pad_historis.csv"
CUSTOM_DATA_FILE = DATA_DIR / "pad_historis_custom.csv"


def load_data(use_custom=False):
    """Load historical data"""
    file_to_load = CUSTOM_DATA_FILE if (use_custom and CUSTOM_DATA_FILE.exists()) else HISTORIS_FILE

    if file_to_load.exists():
        df = pd.read_csv(file_to_load)
        # Ensure proper column names
        if "Rasio_Gini" in df.columns:
            df = df.rename(columns={"Rasio_Gini": "Rasio Gini"})
        if "BI7DRR" in df.columns:
            df = df.rename(columns={"BI7DRR": "Suku Bunga"})
        return df
    return None


def save_data(df, custom=True):
    """Save data to CSV"""
    # Revert column names for consistency
    df_to_save = df.copy()
    if "Rasio Gini" in df_to_save.columns:
        df_to_save = df_to_save.rename(columns={"Rasio Gini": "Rasio_Gini"})
    if "Suku Bunga" in df_to_save.columns:
        df_to_save = df_to_save.rename(columns={"Suku Bunga": "BI7DRR"})

    file_to_save = CUSTOM_DATA_FILE if custom else HISTORIS_FILE
    df_to_save.to_csv(file_to_save, index=False)

    # Log to audit
    log_event(
        event_type='data_edit',
        action=f'Data saved to {file_to_save.name}',
        details={
            'rows': len(df_to_save),
            'columns': list(df_to_save.columns),
            'file': str(file_to_save)
        }
    )


def show_data_editor_page():
    render_gradient_header(
        title="Data Editor & Manager",
        subtitle="View, edit, dan kelola data historis untuk proyeksi PAD",
        icon="📝"
    )

    render_info_box(
        "💡 <strong>Data Editor</strong> memungkinkan Anda untuk melihat, mengedit, dan menambah data historis. "
        "Perubahan data akan mempengaruhi semua perhitungan dan proyeksi dalam dashboard.",
        box_type="warning"
    )

    # Initialize session state
    if 'edited_data' not in st.session_state:
        st.session_state.edited_data = None
    if 'use_custom_data' not in st.session_state:
        st.session_state.use_custom_data = CUSTOM_DATA_FILE.exists()

    # Data source selection
    col1, col2 = st.columns([3, 1])

    with col1:
        use_custom = st.checkbox(
            "Gunakan Data Custom (jika tersedia)",
            value=st.session_state.use_custom_data,
            help="Toggle antara data original dan data yang sudah diedit"
        )
        st.session_state.use_custom_data = use_custom

    with col2:
        if st.button("🔄 Reload Data"):
            st.session_state.edited_data = None
            st.rerun()

    # Load data
    df = load_data(use_custom=use_custom)

    if df is None:
        st.error("❌ Data file tidak ditemukan!")
        return

    # Store original data
    if st.session_state.edited_data is None:
        st.session_state.edited_data = df.copy()

    # Tabs for different operations
    tabs = st.tabs([
        "📊 View & Edit Data",
        "➕ Add New Row",
        "📈 Bulk Update",
        "📁 Import/Export",
        "🔍 Data Validation"
    ])

    # TAB 1: View & Edit
    with tabs[0]:
        create_header_with_icon("Edit Data Historis", "📊")

        st.markdown("""
        <div class="info-box">
        <strong>Cara Edit:</strong> Klik dua kali pada cell yang ingin diedit, ubah nilainya, lalu tekan Enter.
        Jangan lupa klik "Save Changes" setelah selesai.
        </div>
        """, unsafe_allow_html=True)

        # Data editor
        edited_df = st.data_editor(
            st.session_state.edited_data,
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor_main",
            column_config={
                "Tahun": st.column_config.NumberColumn("Tahun", format="%d", min_value=2000, max_value=2030),
                "PKB": st.column_config.NumberColumn("PKB (Rp)", format="%.0f"),
                "BBNKB": st.column_config.NumberColumn("BBNKB (Rp)", format="%.0f"),
                "PDRB": st.column_config.NumberColumn("PDRB (%)", format="%.2f"),
                "Rasio Gini": st.column_config.NumberColumn("Rasio Gini", format="%.3f"),
                "IPM": st.column_config.NumberColumn("IPM", format="%.2f"),
                "TPT": st.column_config.NumberColumn("TPT (%)", format="%.2f"),
                "Kemiskinan": st.column_config.NumberColumn("Kemiskinan (%)", format="%.2f"),
                "Inflasi": st.column_config.NumberColumn("Inflasi (%)", format="%.2f"),
                "Suku Bunga": st.column_config.NumberColumn("Suku Bunga (%)", format="%.2f"),
            }
        )

        # Update session state
        st.session_state.edited_data = edited_df

        # Save button
        col1, col2, col3 = st.columns([2, 2, 2])

        with col1:
            if st.button("💾 Save Changes", type="primary", use_container_width=True):
                save_data(edited_df, custom=True)
                st.success("✅ Data berhasil disimpan!")
                st.balloons()

        with col2:
            if st.button("↩️ Revert to Original", use_container_width=True):
                if st.checkbox("Confirm revert?"):
                    st.session_state.edited_data = load_data(use_custom=False).copy()
                    st.success("✅ Data dikembalikan ke original!")
                    st.rerun()

        with col3:
            if st.button("🗑️ Delete Custom Data", use_container_width=True):
                if CUSTOM_DATA_FILE.exists() and st.checkbox("Confirm delete?"):
                    CUSTOM_DATA_FILE.unlink()
                    st.success("✅ Custom data deleted!")
                    st.rerun()

    # TAB 2: Add New Row
    with tabs[1]:
        create_header_with_icon("Tambah Data Tahun Baru", "➕")

        st.markdown("""
        <div class="info-box">
        Tambahkan data untuk tahun baru. Semua field harus diisi.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_new_row"):
            col1, col2 = st.columns(2)

            with col1:
                new_year = st.number_input("Tahun", min_value=2000, max_value=2030, value=2025, step=1)
                new_pkb = st.number_input("PKB (Rupiah)", value=10000000000000.0, step=100000000000.0, format="%.0f")
                new_bbnkb = st.number_input("BBNKB (Rupiah)", value=2500000000000.0, step=50000000000.0, format="%.0f")
                new_pdrb = st.number_input("PDRB (%)", value=5.5, step=0.1, format="%.2f")
                new_gini = st.number_input("Rasio Gini", value=0.40, step=0.01, format="%.3f")

            with col2:
                new_ipm = st.number_input("IPM", value=75.0, step=0.1, format="%.2f")
                new_tpt = st.number_input("TPT (%)", value=4.5, step=0.1, format="%.2f")
                new_kemiskinan = st.number_input("Kemiskinan (%)", value=10.0, step=0.1, format="%.2f")
                new_inflasi = st.number_input("Inflasi (%)", value=3.0, step=0.1, format="%.2f")
                new_suku_bunga = st.number_input("Suku Bunga (%)", value=5.0, step=0.1, format="%.2f")

            submitted = st.form_submit_button("➕ Add Row")

            if submitted:
                # Check if year already exists
                if new_year in st.session_state.edited_data['Tahun'].values:
                    st.error(f"❌ Tahun {new_year} sudah ada dalam data!")
                else:
                    new_row = pd.DataFrame({
                        'Tahun': [new_year],
                        'PKB': [new_pkb],
                        'BBNKB': [new_bbnkb],
                        'PDRB': [new_pdrb],
                        'Rasio Gini': [new_gini],
                        'IPM': [new_ipm],
                        'TPT': [new_tpt],
                        'Kemiskinan': [new_kemiskinan],
                        'Inflasi': [new_inflasi],
                        'Suku Bunga': [new_suku_bunga]
                    })

                    st.session_state.edited_data = pd.concat([st.session_state.edited_data, new_row], ignore_index=True)
                    st.session_state.edited_data = st.session_state.edited_data.sort_values('Tahun').reset_index(drop=True)

                    st.success(f"✅ Data tahun {new_year} berhasil ditambahkan!")
                    st.info("💾 Jangan lupa Save Changes di tab 'View & Edit Data'")

    # TAB 3: Bulk Update
    with tabs[2]:
        create_header_with_icon("Bulk Update Data", "📈")

        st.markdown("""
        <div class="warning-box">
        Aplikasikan perubahan massal pada kolom tertentu (misalnya: tambah 5% pada semua PKB)
        </div>
        """, unsafe_allow_html=True)

        operation_type = st.selectbox(
            "Pilih Operasi",
            ["Tambah/Kurang", "Kalikan", "Bagi", "Set Value"]
        )

        column_to_update = st.selectbox(
            "Pilih Kolom",
            ['PKB', 'BBNKB', 'PDRB', 'Rasio Gini', 'IPM', 'TPT', 'Kemiskinan', 'Inflasi', 'Suku Bunga']
        )

        # Year filter
        years_to_update = st.multiselect(
            "Tahun (kosongkan untuk semua tahun)",
            options=st.session_state.edited_data['Tahun'].unique().tolist(),
            default=[]
        )

        value = st.number_input(
            "Nilai untuk Operasi",
            value=0.0 if operation_type == "Tambah/Kurang" else 1.0,
            step=0.01,
            format="%.4f"
        )

        if st.button("🔄 Apply Bulk Update"):
            df_to_update = st.session_state.edited_data.copy()

            # Filter by year if specified
            if years_to_update:
                mask = df_to_update['Tahun'].isin(years_to_update)
            else:
                mask = pd.Series([True] * len(df_to_update))

            # Apply operation
            if operation_type == "Tambah/Kurang":
                df_to_update.loc[mask, column_to_update] += value
            elif operation_type == "Kalikan":
                df_to_update.loc[mask, column_to_update] *= value
            elif operation_type == "Bagi":
                if value != 0:
                    df_to_update.loc[mask, column_to_update] /= value
                else:
                    st.error("❌ Tidak bisa membagi dengan nol!")
                    return
            elif operation_type == "Set Value":
                df_to_update.loc[mask, column_to_update] = value

            st.session_state.edited_data = df_to_update
            st.success(f"✅ Bulk update applied to {mask.sum()} rows!")
            st.info("💾 Jangan lupa Save Changes di tab 'View & Edit Data'")

    # TAB 4: Import/Export
    with tabs[3]:
        create_header_with_icon("Import/Export Data", "📁")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📥 Import Data")

            uploaded_file = st.file_uploader("Upload CSV File", type=['csv'])

            if uploaded_file is not None:
                try:
                    imported_df = pd.read_csv(uploaded_file)
                    st.write("Preview:")
                    st.dataframe(imported_df.head(), use_container_width=True)

                    if st.button("✅ Apply Imported Data"):
                        st.session_state.edited_data = imported_df
                        st.success("✅ Data imported successfully!")
                        st.info("💾 Jangan lupa Save Changes di tab 'View & Edit Data'")
                except Exception as e:
                    st.error(f"❌ Error importing file: {e}")

        with col2:
            st.subheader("📤 Export Data")

            export_format = st.selectbox("Format", ["CSV", "Excel"])

            if export_format == "CSV":
                csv = st.session_state.edited_data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"pad_historis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                # Excel export
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    st.session_state.edited_data.to_excel(writer, index=False, sheet_name='Data')
                output.seek(0)

                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name=f"pad_historis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # TAB 5: Data Validation
    with tabs[4]:
        create_header_with_icon("Validasi Data", "🔍")

        st.markdown("""
        <div class="info-box">
        Cek kualitas dan konsistensi data yang sedang diedit.
        </div>
        """, unsafe_allow_html=True)

        df_check = st.session_state.edited_data

        # Check for missing values
        st.subheader("📋 Missing Values")
        missing = df_check.isnull().sum()
        if missing.sum() == 0:
            st.success("✅ Tidak ada missing values")
        else:
            st.warning("⚠️ Ada missing values:")
            st.write(missing[missing > 0])

        # Check for duplicates
        st.subheader("🔁 Duplicate Years")
        duplicates = df_check[df_check.duplicated(subset=['Tahun'], keep=False)]
        if len(duplicates) == 0:
            st.success("✅ Tidak ada tahun duplikat")
        else:
            st.error("❌ Ada tahun duplikat:")
            st.dataframe(duplicates)

        # Check data ranges
        st.subheader("📊 Data Range Check")

        ranges = {
            'PKB': (1e12, 20e12),  # 1T - 20T
            'BBNKB': (1e12, 5e12),  # 1T - 5T
            'PDRB': (-10, 20),  # -10% to 20%
            'Rasio Gini': (0, 1),
            'IPM': (0, 100),
            'TPT': (0, 30),
            'Kemiskinan': (0, 100),
            'Inflasi': (-10, 30),
            'Suku Bunga': (0, 30)
        }

        issues = []
        for col, (min_val, max_val) in ranges.items():
            if col in df_check.columns:
                out_of_range = df_check[(df_check[col] < min_val) | (df_check[col] > max_val)]
                if len(out_of_range) > 0:
                    issues.append(f"{col}: {len(out_of_range)} values out of expected range [{min_val}, {max_val}]")

        if len(issues) == 0:
            st.success("✅ Semua nilai dalam range yang wajar")
        else:
            st.warning("⚠️ Nilai di luar range normal:")
            for issue in issues:
                st.write(f"- {issue}")

        # Data statistics
        st.subheader("📈 Data Statistics")
        st.dataframe(df_check.describe(), use_container_width=True)


def app():
    show_data_editor_page()


if __name__ == "__main__":
    app()
