"""
Variable Manager Page
Pengelolaan metadata variabel makroekonomi bawaan maupun indikator daerah kustom.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.ui_components import (
    apply_plotly_theme,
    create_header_with_icon,
    render_info_box,
    render_kpi_card,
    render_page_header,
)

VARIABLES_FILE = Path(__file__).resolve().parent.parent / "config" / "custom_variables.json"

CATEGORY_OPTIONS = [
    "Economic Growth",
    "Social Indicators",
    "Labor Market",
    "Monetary",
    "Infrastructure",
    "Demographics",
    "Custom",
]


def get_default_variables() -> dict:
    return {
        "PDRB": {
            "name": "PDRB",
            "full_name": "Pertumbuhan PDRB",
            "description": "Pertumbuhan Produk Domestik Regional Bruto (%)",
            "unit": "%",
            "category": "Economic Growth",
            "expected_range": [-10, 20],
            "active": True,
            "custom": False,
        },
        "Rasio Gini": {
            "name": "Rasio Gini",
            "full_name": "Rasio Gini",
            "description": "Indeks ketimpangan distribusi pendapatan (0–1)",
            "unit": "index",
            "category": "Social Indicators",
            "expected_range": [0, 1],
            "active": True,
            "custom": False,
        },
        "IPM": {
            "name": "IPM",
            "full_name": "Indeks Pembangunan Manusia",
            "description": "Capaian pembangunan kualitas manusia (0–100)",
            "unit": "index",
            "category": "Social Indicators",
            "expected_range": [0, 100],
            "active": True,
            "custom": False,
        },
        "TPT": {
            "name": "TPT",
            "full_name": "Tingkat Pengangguran Terbuka",
            "description": "Persentase angkatan kerja yang belum bekerja (%)",
            "unit": "%",
            "category": "Labor Market",
            "expected_range": [0, 30],
            "active": True,
            "custom": False,
        },
        "Kemiskinan": {
            "name": "Kemiskinan",
            "full_name": "Tingkat Kemiskinan",
            "description": "Persentase penduduk di bawah garis kemiskinan (%)",
            "unit": "%",
            "category": "Social Indicators",
            "expected_range": [0, 100],
            "active": True,
            "custom": False,
        },
        "Inflasi": {
            "name": "Inflasi",
            "full_name": "Tingkat Inflasi",
            "description": "Laju inflasi tahunan year-on-year (%)",
            "unit": "%",
            "category": "Monetary",
            "expected_range": [-10, 30],
            "active": True,
            "custom": False,
        },
        "Suku Bunga": {
            "name": "Suku Bunga",
            "full_name": "Suku Bunga Acuan BI",
            "description": "Suku bunga acuan Bank Indonesia / BI-Rate (%)",
            "unit": "%",
            "category": "Monetary",
            "expected_range": [0, 30],
            "active": True,
            "custom": False,
        },
    }


def load_variables() -> dict:
    defaults = get_default_variables()
    if VARIABLES_FILE.exists():
        try:
            with open(VARIABLES_FILE, "r", encoding="utf-8") as f:
                custom_vars = json.load(f)
            defaults.update(custom_vars)
        except Exception:
            pass
    return defaults


def save_variables(variables: dict) -> None:
    VARIABLES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(VARIABLES_FILE, "w", encoding="utf-8") as f:
        json.dump(variables, f, indent=2, ensure_ascii=False)


def show_variable_manager_page() -> None:
    render_page_header(
        title="Manajemen Variabel Makroekonomi",
        subtitle="Kelola katalog indikator makroekonomi bawaan maupun penambahan indikator spesifik daerah",
        icon="🗂️",
    )

    render_info_box(
        "<strong>Variable Manager</strong> memudahkan pencatatan metadata satuan, rentang wajar validasi, dan "
        "pengelompokan indikator ekonomi yang digunakan pada analisis proyeksi PAD.",
        box_type="info",
    )

    if "variables_config" not in st.session_state:
        st.session_state.variables_config = load_variables()
    if "confirm_reset_vars" not in st.session_state:
        st.session_state.confirm_reset_vars = False
    if "confirm_delete_var" not in st.session_state:
        st.session_state.confirm_delete_var = None

    variables = st.session_state.variables_config

    tabs = st.tabs(
        [
            "📋 Variabel Aktif",
            "➕ Tambah Variabel",
            "✏️ Edit Variabel",
            "📊 Statistik Katalog",
            "💾 Simpan & Ekspor",
        ]
    )

    # TAB 1: Active Variables
    with tabs[0]:
        create_header_with_icon("Daftar Variabel Aktif", "📋")
        active_vars = {k: v for k, v in variables.items() if v.get("active", True)}

        if not active_vars:
            st.warning("⚠️ Tidak ada variabel aktif saat ini. Aktifkan kembali melalui tab **Edit Variabel**.")
        else:
            var_rows = [
                {
                    "Kode Variabel": name,
                    "Nama Lengkap": info["full_name"],
                    "Satuan": info["unit"],
                    "Kategori": info["category"],
                    "Rentang Wajar": f"{info['expected_range'][0]} s.d. {info['expected_range'][1]}",
                    "Tipe": "Kustom" if info.get("custom", False) else "Bawaan",
                }
                for name, info in active_vars.items()
            ]
            st.dataframe(pd.DataFrame(var_rows), use_container_width=True, hide_index=True)

            create_header_with_icon("Pengelompokan Berdasarkan Kategori", "🗂️")
            categories: dict[str, list[str]] = {}
            for info in active_vars.values():
                categories.setdefault(info["category"], []).append(info["name"])

            cols = st.columns(min(4, max(1, len(categories))))
            for idx, (cat, vars_list) in enumerate(categories.items()):
                with cols[idx % len(cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{cat}**")
                        for v in vars_list:
                            st.markdown(f"- `{v}`")

    # TAB 2: Add New Variable
    with tabs[1]:
        create_header_with_icon("Tambah Indikator Makroekonomi Kustom", "➕")
        with st.container(border=True):
            with st.form("add_variable_form"):
                col1, col2 = st.columns(2)
                with col1:
                    var_name = st.text_input("Kode Singkat Variabel", placeholder="Contoh: Jumlah_Kendaraan")
                    full_name = st.text_input("Nama Lengkap Indikator", placeholder="Contoh: Jumlah Kendaraan Terdaftar")
                    description = st.text_area("Deskripsi Metodologis", placeholder="Jelaskan definisi dan sumber data...")
                with col2:
                    unit = st.text_input("Satuan Pengukuran", placeholder="Contoh: Unit, %, Indeks")
                    category = st.selectbox("Kategori Ekonomi", options=CATEGORY_OPTIONS)
                    c_a, c_b = st.columns(2)
                    with c_a:
                        min_range = st.number_input("Batas Minimum Wajar", value=0.0, step=0.1, format="%.2f")
                    with c_b:
                        max_range = st.number_input("Batas Maksimum Wajar", value=100.0, step=0.1, format="%.2f")

                submitted = st.form_submit_button("➕ Tambahkan Variabel", type="primary")
                if submitted:
                    clean_code = var_name.strip()
                    clean_full = full_name.strip()
                    if not clean_code or not clean_full:
                        st.error("❌ Kode variabel dan nama lengkap wajib diisi!")
                    elif clean_code in variables:
                        st.error(f"❌ Variabel `{clean_code}` sudah terdaftar!")
                    else:
                        variables[clean_code] = {
                            "name": clean_code,
                            "full_name": clean_full,
                            "description": description.strip(),
                            "unit": unit.strip() or "-",
                            "category": category,
                            "expected_range": [min_range, max_range],
                            "active": True,
                            "custom": True,
                        }
                        st.session_state.variables_config = variables
                        st.success(
                            f"✅ Variabel **{clean_code}** berhasil ditambahkan! Klik **Simpan Konfigurasi** pada tab terakhir untuk menyimpan permanen."
                        )

    # TAB 3: Edit Variables (Fixed Category Index & Delete Confirmation)
    with tabs[2]:
        create_header_with_icon("Ubah Konfigurasi Variabel", "✏️")
        var_to_edit = st.selectbox("Pilih variabel yang akan disunting:", options=list(variables.keys()))

        if var_to_edit:
            var_info = variables[var_to_edit]
            cat_idx = CATEGORY_OPTIONS.index(var_info["category"]) if var_info["category"] in CATEGORY_OPTIONS else 0

            with st.container(border=True):
                with st.form("edit_variable_form"):
                    st.markdown(f"#### Menyunting: `{var_to_edit}`")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_full_name = st.text_input("Nama Lengkap", value=var_info["full_name"])
                        new_description = st.text_area("Deskripsi", value=var_info["description"])
                        new_unit = st.text_input("Satuan", value=var_info["unit"])
                    with col2:
                        new_category = st.selectbox("Kategori", options=CATEGORY_OPTIONS, index=cat_idx)
                        c_a, c_b = st.columns(2)
                        with c_a:
                            new_min = st.number_input("Batas Minimum", value=float(var_info["expected_range"][0]))
                        with c_b:
                            new_max = st.number_input("Batas Maksimum", value=float(var_info["expected_range"][1]))
                        new_active = st.checkbox("Status Aktif", value=bool(var_info.get("active", True)))

                    update_btn = st.form_submit_button("💾 Perbarui Variabel", type="primary")
                    if update_btn:
                        variables[var_to_edit].update(
                            {
                                "full_name": new_full_name,
                                "description": new_description,
                                "unit": new_unit,
                                "category": new_category,
                                "expected_range": [new_min, new_max],
                                "active": new_active,
                            }
                        )
                        st.session_state.variables_config = variables
                        st.success(f"✅ Konfigurasi `{var_to_edit}` berhasil diperbarui!")

                if var_info.get("custom", False):
                    if st.button(f"🗑️ Hapus Variabel Kustom '{var_to_edit}'"):
                        st.session_state.confirm_delete_var = var_to_edit

                    if st.session_state.confirm_delete_var == var_to_edit:
                        st.warning(f"⚠️ Hapus permanen variabel kustom **{var_to_edit}**?")
                        d1, d2 = st.columns(2)
                        with d1:
                            if st.button("✅ Ya, Hapus Variabel", type="primary", use_container_width=True):
                                del variables[var_to_edit]
                                st.session_state.variables_config = variables
                                st.session_state.confirm_delete_var = None
                                st.rerun()
                        with d2:
                            if st.button("✖ Batal Hapus", use_container_width=True):
                                st.session_state.confirm_delete_var = None
                                st.rerun()
                else:
                    st.caption("🔒 Variabel bawaan sistem tidak dapat dihapus, namun dapat dinonaktifkan.")

    # TAB 4: Variable Statistics (Themed Plotly Bar Chart)
    with tabs[3]:
        create_header_with_icon("Statistik Katalog Variabel", "📊")

        total_vars = len(variables)
        active_vars_count = sum(1 for v in variables.values() if v.get("active", True))
        custom_vars_count = sum(1 for v in variables.values() if v.get("custom", False))

        k1, k2, k3 = st.columns(3)
        with k1:
            render_kpi_card("Total Variabel Terdaftar", str(total_vars), icon="📚", variant="primary")
        with k2:
            render_kpi_card("Variabel Berstatus Aktif", str(active_vars_count), icon="✅", variant="success")
        with k3:
            render_kpi_card("Variabel Kustom Daerah", str(custom_vars_count), icon="🛠️", variant="indigo")

        category_counts: dict[str, int] = {}
        for info in variables.values():
            cat = info["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        with st.container(border=True):
            fig_cat = go.Figure(
                go.Bar(
                    x=list(category_counts.keys()),
                    y=list(category_counts.values()),
                    marker_color="#1a5fb4",
                    text=list(category_counts.values()),
                    textposition="outside",
                    cliponaxis=False,
                )
            )
            apply_plotly_theme(
                fig_cat,
                title="Distribusi Variabel Berdasarkan Kategori Ekonomi",
                height=380,
                xaxis_title="Kategori",
                yaxis_title="Jumlah Variabel",
                show_legend=False,
            )
            fig_cat.update_yaxes(dtick=1)
            st.plotly_chart(fig_cat, use_container_width=True)

    # TAB 5: Manage Configuration
    with tabs[4]:
        create_header_with_icon("Simpan, Ekspor & Pulihkan Konfigurasi Variabel", "💾")
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Simpan Konfigurasi", type="primary", use_container_width=True):
                    save_variables(variables)
                    st.success("✅ Konfigurasi variabel berhasil disimpan!")
            with col2:
                if st.button("🔄 Reset ke Default", use_container_width=True):
                    st.session_state.confirm_reset_vars = True
            with col3:
                var_json = json.dumps(variables, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Ekspor JSON",
                    data=var_json.encode("utf-8"),
                    file_name="variables_config.json",
                    mime="application/json",
                    use_container_width=True,
                )

            if st.session_state.confirm_reset_vars:
                st.warning("⚠️ Seluruh variabel kustom akan dihapus dan dikembalikan ke 7 variabel makro bawaan. Lanjutkan?")
                r1, r2 = st.columns(2)
                with r1:
                    if st.button("✅ Ya, Reset Sekarang", type="primary", use_container_width=True):
                        defaults = get_default_variables()
                        save_variables(defaults)
                        st.session_state.variables_config = defaults
                        st.session_state.confirm_reset_vars = False
                        st.rerun()
                with r2:
                    if st.button("✖ Batal", use_container_width=True):
                        st.session_state.confirm_reset_vars = False
                        st.rerun()

        with st.expander("📤 Impor Konfigurasi Variabel (JSON)"):
            uploaded_file = st.file_uploader("Pilih berkas JSON variabel", type=["json"])
            if uploaded_file is not None:
                try:
                    imported_vars = json.load(uploaded_file)
                    if st.button("✅ Terapkan Konfigurasi Variabel", type="primary"):
                        save_variables(imported_vars)
                        st.session_state.variables_config = imported_vars
                        st.success("✅ Konfigurasi variabel berhasil diimpor!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal membaca berkas JSON: {e}")

        with st.expander("🔍 Lihat Struktur JSON Saat Ini"):
            st.json(variables)


def app() -> None:
    show_variable_manager_page()


if __name__ == "__main__":
    app()
