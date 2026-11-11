"""
Data Editor & Manager Page
Menyunting, menambah tahun observasi, memvalidasi kualitas, dan mengelola dataset historis kustom.
"""

from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.audit_utils import log_event
from utils.ui_components import (
    create_header_with_icon,
    render_info_box,
    render_kpi_card,
    render_page_header,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "datasets"
HISTORIS_FILE = DATA_DIR / "pad_historis.csv"
CUSTOM_DATA_FILE = DATA_DIR / "pad_historis_custom.csv"


def load_data(use_custom: bool = False) -> pd.DataFrame | None:
    file_to_load = CUSTOM_DATA_FILE if (use_custom and CUSTOM_DATA_FILE.exists()) else HISTORIS_FILE
    if file_to_load.exists():
        df = pd.read_csv(file_to_load)
        if "Rasio_Gini" in df.columns:
            df = df.rename(columns={"Rasio_Gini": "Rasio Gini"})
        if "BI7DRR" in df.columns:
            df = df.rename(columns={"BI7DRR": "Suku Bunga"})
        return df
    return None


def save_data(df: pd.DataFrame, custom: bool = True) -> None:
    df_to_save = df.copy()
    if "Rasio Gini" in df_to_save.columns:
        df_to_save = df_to_save.rename(columns={"Rasio Gini": "Rasio_Gini"})
    if "Suku Bunga" in df_to_save.columns:
        df_to_save = df_to_save.rename(columns={"Suku Bunga": "BI7DRR"})

    file_to_save = CUSTOM_DATA_FILE if custom else HISTORIS_FILE
    file_to_save.parent.mkdir(parents=True, exist_ok=True)
    df_to_save.to_csv(file_to_save, index=False)

    log_event(
        event_type="data_edit",
        action=f"Data saved to {file_to_save.name}",
        details={
            "rows": len(df_to_save),
            "columns": list(df_to_save.columns),
            "file": str(file_to_save.name),
        },
    )


def show_data_editor_page() -> None:
    render_page_header(
        title="Editor & Manajemen Data Historis",
        subtitle="Kelola pembaruan realisasi PKB, BBNKB, dan indikator makroekonomi dengan validasi kualitas otomatis",
        icon="📝",
    )

    render_info_box(
        "<strong>Penyimpanan Aman:</strong> Setiap perubahan disimpan ke berkas terpisah "
        "<code>pad_historis_custom.csv</code> sehingga data resmi bawaan tetap terjaga utuh dan dapat dipulihkan kapan saja.",
        box_type="info",
    )

    if "edited_data" not in st.session_state:
        st.session_state.edited_data = None
    if "use_custom_data" not in st.session_state:
        st.session_state.use_custom_data = CUSTOM_DATA_FILE.exists()
    if "confirm_revert_data" not in st.session_state:
        st.session_state.confirm_revert_data = False
    if "confirm_delete_custom_data" not in st.session_state:
        st.session_state.confirm_delete_custom_data = False

    with st.container(border=True):
        c_src1, c_src2, c_src3 = st.columns([2.2, 1.2, 1])
        with c_src1:
            use_custom = st.toggle(
                "Aktifkan Dataset Kustom di Seluruh Halaman Analisis",
                value=bool(st.session_state.use_custom_data and CUSTOM_DATA_FILE.exists()),
                disabled=not CUSTOM_DATA_FILE.exists(),
                help="Apabila aktif, seluruh halaman proyeksi & pemodelan akan menggunakan dataset kustom Anda.",
            )
            st.session_state.use_custom_data = use_custom
        with c_src2:
            status_txt = "Dataset Kustom" if (use_custom and CUSTOM_DATA_FILE.exists()) else "Dataset Resmi Bawaan"
            st.caption(f"📂 Sumber Aktif:\n**{status_txt}**")
        with c_src3:
            if st.button("🔄 Muat Ulang Tabel", use_container_width=True):
                st.session_state.edited_data = None
                st.rerun()

    df = load_data(use_custom=use_custom)
    if df is None:
        st.error("❌ Berkas dataset historis tidak ditemukan!")
        return

    if st.session_state.edited_data is None:
        st.session_state.edited_data = df.copy()

    tabs = st.tabs(
        [
            "📊 Tabel & Penyuntingan",
            "➕ Tambah Tahun Baru",
            "📈 Pembaruan Massal",
            "📁 Impor / Ekspor",
            "🔍 Validasi Kualitas Data",
        ]
    )

    # TAB 1: View & Edit
    with tabs[0]:
        create_header_with_icon("Penyuntingan Langsung Tabel Historis", "📊")

        edited_df = st.data_editor(
            st.session_state.edited_data,
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor_main",
            column_config={
                "Tahun": st.column_config.NumberColumn("Tahun", format="%d", min_value=2000, max_value=2040),
                "PKB": st.column_config.NumberColumn("PKB (Rp)", format="%.0f"),
                "BBNKB": st.column_config.NumberColumn("BBNKB (Rp)", format="%.0f"),
                "PDRB": st.column_config.NumberColumn("PDRB (%)", format="%.2f"),
                "Rasio Gini": st.column_config.NumberColumn("Rasio Gini", format="%.3f"),
                "IPM": st.column_config.NumberColumn("IPM", format="%.2f"),
                "TPT": st.column_config.NumberColumn("TPT (%)", format="%.2f"),
                "Kemiskinan": st.column_config.NumberColumn("Kemiskinan (%)", format="%.2f"),
                "Inflasi": st.column_config.NumberColumn("Inflasi (%)", format="%.2f"),
                "Suku Bunga": st.column_config.NumberColumn("Suku Bunga (%)", format="%.2f"),
            },
        )
        st.session_state.edited_data = edited_df

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Simpan sebagai Dataset Kustom", type="primary", use_container_width=True):
                save_data(edited_df, custom=True)
                st.session_state.use_custom_data = True
                st.success("✅ Perubahan berhasil disimpan ke `pad_historis_custom.csv` dan langsung diaktifkan!")
        with col2:
            if st.button("↩️ Kembalikan ke Data Resmi", use_container_width=True):
                st.session_state.confirm_revert_data = True
        with col3:
            if st.button(
                "🗑️ Hapus Berkas Kustom",
                disabled=not CUSTOM_DATA_FILE.exists(),
                use_container_width=True,
            ):
                st.session_state.confirm_delete_custom_data = True

        if st.session_state.confirm_revert_data:
            st.warning("⚠️ Buang perubahan di layar dan muat ulang nilai asli dari `pad_historis.csv`?")
            r1, r2 = st.columns(2)
            with r1:
                if st.button("✅ Ya, Muat Data Resmi", type="primary", use_container_width=True):
                    orig = load_data(use_custom=False)
                    if orig is not None:
                        st.session_state.edited_data = orig.copy()
                    st.session_state.use_custom_data = False
                    st.session_state.confirm_revert_data = False
                    st.rerun()
            with r2:
                if st.button("✖ Batal", key="cancel_revert", use_container_width=True):
                    st.session_state.confirm_revert_data = False
                    st.rerun()

        if st.session_state.confirm_delete_custom_data:
            st.warning("⚠️ Hapus berkas `pad_historis_custom.csv` secara permanen?")
            d1, d2 = st.columns(2)
            with d1:
                if st.button("✅ Ya, Hapus Berkas Kustom", type="primary", use_container_width=True):
                    if CUSTOM_DATA_FILE.exists():
                        CUSTOM_DATA_FILE.unlink()
                    orig = load_data(use_custom=False)
                    if orig is not None:
                        st.session_state.edited_data = orig.copy()
                    st.session_state.use_custom_data = False
                    st.session_state.confirm_delete_custom_data = False
                    st.rerun()
            with d2:
                if st.button("✖ Batal", key="cancel_del_custom", use_container_width=True):
                    st.session_state.confirm_delete_custom_data = False
                    st.rerun()

    # TAB 2: Add New Row
    with tabs[1]:
        create_header_with_icon("Tambah Observasi Tahun Baru", "➕")
        with st.container(border=True):
            with st.form("add_new_row_form"):
                col1, col2 = st.columns(2)
                next_yr = int(st.session_state.edited_data["Tahun"].max()) + 1
                with col1:
                    new_year = st.number_input("Tahun", min_value=2000, max_value=2040, value=next_yr, step=1)
                    new_pkb = st.number_input("Realisasi PKB (Rupiah)", value=8_500_000_000_000.0, step=100_000_000_000.0, format="%.0f")
                    new_bbnkb = st.number_input("Realisasi BBNKB (Rupiah)", value=2_800_000_000_000.0, step=50_000_000_000.0, format="%.0f")
                    new_pdrb = st.number_input("Pertumbuhan PDRB (%)", value=5.10, step=0.1, format="%.2f")
                    new_gini = st.number_input("Rasio Gini", value=0.375, step=0.005, format="%.3f")
                with col2:
                    new_ipm = st.number_input("IPM", value=75.20, step=0.1, format="%.2f")
                    new_tpt = st.number_input("TPT (%)", value=4.20, step=0.1, format="%.2f")
                    new_kemiskinan = st.number_input("Kemiskinan (%)", value=9.60, step=0.1, format="%.2f")
                    new_inflasi = st.number_input("Inflasi (%)", value=2.80, step=0.1, format="%.2f")
                    new_suku_bunga = st.number_input("Suku Bunga (%)", value=5.75, step=0.25, format="%.2f")

                submitted = st.form_submit_button("➕ Tambahkan Baris Tahun", type="primary")
                if submitted:
                    if new_year in st.session_state.edited_data["Tahun"].values:
                        st.error(f"❌ Data untuk tahun **{new_year}** sudah tersedia!")
                    else:
                        new_row = pd.DataFrame(
                            [
                                {
                                    "Tahun": int(new_year),
                                    "PKB": new_pkb,
                                    "BBNKB": new_bbnkb,
                                    "PDRB": new_pdrb,
                                    "Rasio Gini": new_gini,
                                    "IPM": new_ipm,
                                    "TPT": new_tpt,
                                    "Kemiskinan": new_kemiskinan,
                                    "Inflasi": new_inflasi,
                                    "Suku Bunga": new_suku_bunga,
                                }
                            ]
                        )
                        combined = pd.concat([st.session_state.edited_data, new_row], ignore_index=True)
                        st.session_state.edited_data = combined.sort_values("Tahun").reset_index(drop=True)
                        st.success(
                            f"✅ Baris tahun **{new_year}** berhasil ditambahkan ke tabel kerja! Klik **Simpan sebagai Dataset Kustom** pada Tab 1 untuk menyimpan permanen."
                        )

    # TAB 3: Bulk Update
    with tabs[2]:
        create_header_with_icon("Penyesuaian Massal (Bulk Update)", "📈")
        with st.container(border=True):
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                operation_type = st.selectbox("Jenis Operasi", ["Tambah / Kurang (+ / -)", "Kalikan (×)", "Bagi (÷)", "Tetapkan Nilai (=)"])
                column_to_update = st.selectbox(
                    "Kolom Target",
                    ["PKB", "BBNKB", "PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"],
                )
            with c_b2:
                years_to_update = st.multiselect(
                    "Filter Tahun (kosongkan untuk seluruh tahun)",
                    options=sorted(st.session_state.edited_data["Tahun"].unique().tolist()),
                    default=[],
                )
                value = st.number_input(
                    "Nilai Operasi",
                    value=0.0 if operation_type.startswith("Tambah") else 1.0,
                    step=0.01,
                    format="%.4f",
                )

            if st.button("⚡ Terapkan Pembaruan Massal", type="primary"):
                df_upd = st.session_state.edited_data.copy()
                mask = df_upd["Tahun"].isin(years_to_update) if years_to_update else pd.Series([True] * len(df_upd))

                if operation_type.startswith("Tambah"):
                    df_upd.loc[mask, column_to_update] += value
                elif operation_type.startswith("Kalikan"):
                    df_upd.loc[mask, column_to_update] *= value
                elif operation_type.startswith("Bagi"):
                    if value == 0:
                        st.error("❌ Pembagian dengan nol tidak diizinkan!")
                        return
                    df_upd.loc[mask, column_to_update] /= value
                else:
                    df_upd.loc[mask, column_to_update] = value

                st.session_state.edited_data = df_upd
                st.success(f"✅ Berhasil memperbarui **{int(mask.sum())}** baris pada kolom `{column_to_update}`.")

    # TAB 4: Import/Export
    with tabs[3]:
        create_header_with_icon("Impor & Ekspor Dataset", "📁")
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("#### 📥 Impor CSV")
                uploaded_file = st.file_uploader("Unggah berkas CSV dataset historis", type=["csv"])
                if uploaded_file is not None:
                    try:
                        imported_df = pd.read_csv(uploaded_file)
                        st.dataframe(imported_df.head(), use_container_width=True, hide_index=True)
                        if st.button("✅ Muat ke Tabel Editor", type="primary"):
                            st.session_state.edited_data = imported_df
                            st.success("✅ Data berhasil dimuat ke editor!")
                    except Exception as e:
                        st.error(f"❌ Gagal membaca CSV: {e}")

        with col2:
            with st.container(border=True):
                st.markdown("#### 📤 Ekspor Dataset Kerja")
                export_format = st.radio("Pilih Format Berkas", ["CSV (.csv)", "Excel (.xlsx)"], horizontal=True)
                stamp = datetime.now().strftime("%Y%m%d")
                if export_format.startswith("CSV"):
                    csv_bytes = st.session_state.edited_data.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Unduh Berkas CSV",
                        data=csv_bytes,
                        file_name=f"pad_historis_{stamp}.csv",
                        mime="text/csv",
                        type="primary",
                        use_container_width=True,
                    )
                else:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        st.session_state.edited_data.to_excel(writer, index=False, sheet_name="PAD_Historis")
                    st.download_button(
                        label="📥 Unduh Berkas Excel",
                        data=output.getvalue(),
                        file_name=f"pad_historis_{stamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True,
                    )

    # TAB 5: Data Validation
    with tabs[4]:
        create_header_with_icon("Pemeriksaan Integritas & Kewajaran Nilai", "🔍")
        df_check = st.session_state.edited_data
        missing_count = int(df_check.isnull().sum().sum())
        dup_count = int(df_check.duplicated(subset=["Tahun"]).sum())

        ranges = {
            "PKB": (1e12, 25e12),
            "BBNKB": (5e11, 10e12),
            "PDRB": (-10, 20),
            "Rasio Gini": (0, 1),
            "IPM": (0, 100),
            "TPT": (0, 30),
            "Kemiskinan": (0, 100),
            "Inflasi": (-10, 30),
            "Suku Bunga": (0, 30),
        }
        issues = []
        for col, (min_val, max_val) in ranges.items():
            if col in df_check.columns:
                out = df_check[(df_check[col] < min_val) | (df_check[col] > max_val)]
                if len(out) > 0:
                    issues.append(f"`{col}`: {len(out)} baris di luar rentang wajar [{min_val:,.0f}, {max_val:,.0f}]")

        v1, v2, v3 = st.columns(3)
        with v1:
            render_kpi_card(
                label="Nilai Kosong (Missing)",
                value=str(missing_count),
                delta="Bersih" if missing_count == 0 else "Perlu Diperbaiki",
                delta_positive=missing_count == 0,
                variant="success" if missing_count == 0 else "danger",
            )
        with v2:
            render_kpi_card(
                label="Duplikasi Tahun",
                value=str(dup_count),
                delta="Unik" if dup_count == 0 else "Terdapat Duplikat",
                delta_positive=dup_count == 0,
                variant="success" if dup_count == 0 else "danger",
            )
        with v3:
            render_kpi_card(
                label="Anomali Rentang Nilai",
                value=str(len(issues)),
                delta="Wajar" if not issues else "Periksa Peringatan",
                delta_positive=not issues,
                variant="success" if not issues else "warning",
            )

        if issues:
            for item in issues:
                st.warning(f"⚠️ {item}")

        st.markdown("#### 📈 Statistik Deskriptif Dataset Kerja")
        st.dataframe(df_check.describe(), use_container_width=True)


def app() -> None:
    show_data_editor_page()


if __name__ == "__main__":
    app()
