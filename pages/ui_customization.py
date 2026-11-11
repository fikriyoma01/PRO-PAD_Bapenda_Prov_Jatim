"""
UI Customization & Theme Manager Page
Personalisasi palet warna, tipografi, format angka Rupiah, preferensi grafik, dan kontrol privasi/watermark.
"""

import json

import streamlit as st

from utils.ui_components import (
    create_header_with_icon,
    render_info_box,
    render_kpi_card,
    render_page_header,
)
from utils.ui_theme_utils import (
    format_rupiah_compact,
    format_sensitive_value,
    get_default_theme,
    get_ui_theme,
    save_ui_theme,
)

FONT_OPTIONS = [
    "'Plus Jakarta Sans', 'Inter', 'Segoe UI', system-ui, sans-serif",
    "'Segoe UI', system-ui, sans-serif",
    "'Inter', Arial, sans-serif",
    "Georgia, serif",
    "'Courier New', monospace",
]


def get_preset_themes() -> dict:
    return {
        "Professional Blue (Bapenda Jatim)": {
            "primary": "#1a5fb4",
            "primary_light": "#3584e4",
            "accent": "#ffd700",
            "sidebar_bg_start": "#0b192c",
            "sidebar_bg_end": "#1e3a5f",
        },
        "Corporate Emerald": {
            "primary": "#047857",
            "primary_light": "#10b981",
            "accent": "#fbbf24",
            "sidebar_bg_start": "#064e3b",
            "sidebar_bg_end": "#065f46",
        },
        "Ocean Sapphire": {
            "primary": "#0369a1",
            "primary_light": "#0ea5e9",
            "accent": "#38bdf8",
            "sidebar_bg_start": "#082f49",
            "sidebar_bg_end": "#0c4a6e",
        },
        "Executive Slate": {
            "primary": "#334155",
            "primary_light": "#475569",
            "accent": "#f59e0b",
            "sidebar_bg_start": "#0f172a",
            "sidebar_bg_end": "#1e293b",
        },
    }


def show_ui_customization_page() -> None:
    render_page_header(
        title="Kustomisasi Antarmuka & Preferensi",
        subtitle="Sesuaikan palet warna institusi, tata letak kartu, pemformatan angka Rupiah, tinggi grafik, hingga mode sensor privasi",
        icon="🎨",
    )

    if "ui_theme" not in st.session_state:
        st.session_state.ui_theme = get_ui_theme()
    if "confirm_reset_theme" not in st.session_state:
        st.session_state.confirm_reset_theme = False

    theme = st.session_state.ui_theme

    tabs = st.tabs(
        [
            "🎨 Tema & Warna",
            "📐 Tata Letak & Tipografi",
            "🔢 Format Angka Rupiah",
            "📊 Preferensi Grafik",
            "🔒 Privasi & Watermark",
            "💾 Simpan & Ekspor",
        ]
    )

    # TAB 1: Theme & Colors
    with tabs[0]:
        create_header_with_icon("Skema Warna & Preset Institusional", "🎨")
        with st.container(border=True):
            presets = get_preset_themes()
            c_p1, c_p2 = st.columns([2.5, 1])
            with c_p1:
                selected_preset = st.selectbox("Pilih Preset Warna Cepat", options=list(presets.keys()))
            with c_p2:
                st.markdown("<div style='height: 1.65rem;'></div>", unsafe_allow_html=True)
                if st.button("✨ Terapkan Preset", type="primary", use_container_width=True):
                    theme["colors"].update(presets[selected_preset])
                    theme["theme_name"] = selected_preset
                    st.session_state.ui_theme = theme
                    save_ui_theme(theme)
                    st.rerun()

            st.markdown("##### 🎯 Warna Kustom Utama")
            col1, col2, col3 = st.columns(3)
            with col1:
                primary = st.color_picker("Warna Utama (Primary)", value=theme["colors"]["primary"])
                primary_light = st.color_picker("Warna Utama Terang", value=theme["colors"]["primary_light"])
            with col2:
                accent = st.color_picker("Warna Aksen Emas/Sorotan", value=theme["colors"]["accent"])
                success = st.color_picker("Indikator Positif (Success)", value=theme["colors"]["success"])
            with col3:
                warning = st.color_picker("Indikator Peringatan (Warning)", value=theme["colors"]["warning"])
                danger = st.color_picker("Indikator Risiko (Danger)", value=theme["colors"]["danger"])

            st.markdown("##### 🧭 Gradien Sidebar")
            s1, s2 = st.columns(2)
            with s1:
                sidebar_start = st.color_picker("Sidebar Atas", value=theme["colors"]["sidebar_bg_start"])
            with s2:
                sidebar_end = st.color_picker("Sidebar Bawah", value=theme["colors"]["sidebar_bg_end"])

            theme["colors"].update(
                {
                    "primary": primary,
                    "primary_light": primary_light,
                    "accent": accent,
                    "success": success,
                    "warning": warning,
                    "danger": danger,
                    "sidebar_bg_start": sidebar_start,
                    "sidebar_bg_end": sidebar_end,
                }
            )

            st.markdown("##### 👁️ Pratinjau Banner Header")
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #0c2d57 0%, {primary} 58%, {primary_light} 100%);
                    padding: 1.4rem 1.8rem;
                    border-radius: 16px;
                    border-bottom: 4px solid {accent};
                    color: #ffffff;
                ">
                    <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;color:#fde68a;">PRATINJAU TEMA AKTIF</div>
                    <h3 style="color:#ffffff;margin:0.25rem 0 0 0;">Dashboard Proyeksi PAD Jawa Timur</h3>
                    <p style="color:rgba(241,245,249,0.9);margin:0.25rem 0 0 0;font-size:0.9rem;">Perpaduan identitas warna pilihan Anda</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # TAB 2: Layout & Spacing
    with tabs[1]:
        create_header_with_icon("Tata Letak Kartu & Tipografi", "📐")
        with st.container(border=True):
            c_l1, c_l2 = st.columns(2)
            with c_l1:
                sidebar_width = st.radio(
                    "Kondisi Awal Sidebar",
                    options=["expanded", "collapsed"],
                    index=0 if theme["layout"].get("sidebar_width", "expanded") == "expanded" else 1,
                    horizontal=True,
                )
                spacing_opts = ["compact", "comfortable", "spacious"]
                curr_spacing = theme["layout"].get("spacing", "comfortable")
                spacing = st.radio(
                    "Kerapatan Ruang Konten",
                    options=spacing_opts,
                    index=spacing_opts.index(curr_spacing) if curr_spacing in spacing_opts else 1,
                    horizontal=True,
                )
            with c_l2:
                shadow_opts = ["none", "light", "medium", "strong"]
                curr_shadow = theme["layout"].get("card_shadow", "medium")
                card_shadow = st.select_slider(
                    "Intensitas Bayangan Kartu",
                    options=shadow_opts,
                    value=curr_shadow if curr_shadow in shadow_opts else "medium",
                )
                raw_radius = str(theme["layout"].get("border_radius", "14px")).replace("px", "").strip()
                border_radius = st.slider(
                    "Kelengkungan Sudut Kartu (px)",
                    min_value=4,
                    max_value=24,
                    value=int(float(raw_radius)) if raw_radius else 14,
                )

            theme["layout"].update(
                {
                    "sidebar_width": sidebar_width,
                    "card_shadow": card_shadow,
                    "border_radius": f"{border_radius}px",
                    "spacing": spacing,
                }
            )

            curr_font = theme["typography"].get("font_family", FONT_OPTIONS[0])
            font_options_list = FONT_OPTIONS if curr_font in FONT_OPTIONS else [curr_font] + FONT_OPTIONS
            font_family = st.selectbox(
                "Keluarga Huruf (Font Family)",
                options=font_options_list,
                index=font_options_list.index(curr_font),
            )
            theme["typography"]["font_family"] = font_family

    # TAB 3: Number Format
    with tabs[2]:
        create_header_with_icon("Pemformatan Satuan Angka & Mata Uang", "🔢")
        render_info_box(
            "Mode <strong>T (Adaptif)</strong> secara otomatis menampilkan nilai ≥ 10¹² sebagai <strong>Triliun (T)</strong>, "
            "≥ 10⁹ sebagai <strong>Miliar (M)</strong>, dan ≥ 10⁶ sebagai <strong>Juta (Jt)</strong>.",
            box_type="info",
        )
        with st.container(border=True):
            fmt_opts = ["T", "B", "M", "Full"]
            curr_fmt = theme["data_display"].get("number_format", "T")
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                number_format = st.selectbox(
                    "Mode Satuan Angka Besar",
                    options=fmt_opts,
                    index=fmt_opts.index(curr_fmt) if curr_fmt in fmt_opts else 0,
                    format_func=lambda x: {
                        "T": "T — Adaptif Triliun / Miliar / Juta (Direkomendasikan)",
                        "B": "B — Paksa Satuan Miliar (M)",
                        "M": "M — Paksa Satuan Juta (Jt)",
                        "Full": "Full — Angka Rupiah Penuh",
                    }[x],
                )
                currency_symbol = st.text_input(
                    "Simbol Mata Uang",
                    value=theme["data_display"].get("currency_symbol", "Rp"),
                    max_chars=6,
                )
            with c_n2:
                decimal_places = st.slider(
                    "Jumlah Angka Desimal",
                    min_value=0,
                    max_value=4,
                    value=int(theme["data_display"].get("decimal_places", 2)),
                )
                show_separator = st.checkbox(
                    "Gunakan Pemisah Ribuan Titik (Rp 8.262.107.764.153)",
                    value=bool(theme["data_display"].get("show_thousand_separator", True)),
                )

            theme["data_display"].update(
                {
                    "number_format": number_format,
                    "decimal_places": decimal_places,
                    "show_thousand_separator": show_separator,
                    "currency_symbol": currency_symbol,
                }
            )
            st.session_state.ui_theme = theme

            p1, p2 = st.columns(2)
            with p1:
                render_kpi_card(
                    label="Pratinjau Skala Triliun (PKB)",
                    value=format_rupiah_compact(8_262_107_764_153),
                    subtitle="Nilai uji: 8.262.107.764.153",
                    variant="primary",
                )
            with p2:
                render_kpi_card(
                    label="Pratinjau Skala Miliar (Dampak Makro)",
                    value=format_rupiah_compact(425_500_000_000),
                    subtitle="Nilai uji: 425.500.000.000",
                    variant="success",
                )

    # TAB 4: Chart Settings
    with tabs[3]:
        create_header_with_icon("Preferensi Visualisasi Grafik Plotly", "📊")
        with st.container(border=True):
            c_ch1, c_ch2 = st.columns(2)
            with c_ch1:
                default_height = st.slider(
                    "Tinggi Standar Grafik (px)",
                    min_value=320,
                    max_value=700,
                    value=int(theme["charts"].get("default_height", 450)),
                    step=20,
                )
                scheme_opts = ["professional", "vibrant", "pastel", "monochrome"]
                curr_scheme = theme["charts"].get("color_scheme", "professional")
                color_scheme = st.selectbox(
                    "Palet Warna Grafik",
                    options=scheme_opts,
                    index=scheme_opts.index(curr_scheme) if curr_scheme in scheme_opts else 0,
                )
            with c_ch2:
                show_gridlines = st.checkbox(
                    "Tampilkan Garis Bantu Grid (Gridlines)",
                    value=bool(theme["charts"].get("show_gridlines", True)),
                )
                animation_enabled = st.checkbox(
                    "Aktifkan Transisi Halus",
                    value=bool(theme["charts"].get("animation_enabled", True)),
                )

            theme["charts"].update(
                {
                    "default_height": default_height,
                    "color_scheme": color_scheme,
                    "show_gridlines": show_gridlines,
                    "animation_enabled": animation_enabled,
                }
            )

    # TAB 5: Privacy & Security
    with tabs[4]:
        create_header_with_icon("Kontrol Kerahasiaan Presentasi & Watermark", "🔒")
        with st.container(border=True):
            show_values = st.checkbox(
                "Tampilkan Nominal Angka Proyeksi",
                value=bool(theme["privacy"].get("show_projection_values", True)),
            )
            blur_sensitive = st.checkbox(
                "Efek Blur pada Kartu KPI (Terbaca Saat Kursor Diarahkan)",
                value=bool(theme["privacy"].get("blur_sensitive_numbers", False)),
            )
            redact_mode = st.checkbox(
                "Mode Redaksi Penuh (Ganti dengan [REDACTED])",
                value=bool(theme["privacy"].get("redact_mode", False)),
            )
            watermark_enabled = st.checkbox(
                "Tampilkan Watermark Latar Belakang di Seluruh Halaman",
                value=bool(theme["privacy"].get("watermark_enabled", False)),
            )
            watermark_text = st.text_input(
                "Teks Watermark",
                value=theme["privacy"].get("watermark_text", "RAHASIA — INTERNAL BAPENDA JATIM"),
                max_chars=60,
                disabled=not watermark_enabled,
            )

            theme["privacy"].update(
                {
                    "blur_sensitive_numbers": blur_sensitive,
                    "watermark_enabled": watermark_enabled,
                    "watermark_text": watermark_text,
                    "show_projection_values": show_values,
                    "redact_mode": redact_mode,
                }
            )
            st.session_state.ui_theme = theme

            st.markdown("##### 👁️ Pratinjau Tampilan Nilai Sensitif")
            st.markdown(
                f"""
                <div class="modern-card">
                    <strong>Contoh Proyeksi PKB 2025:</strong> {format_sensitive_value(8_450_000_000_000)}
                </div>
                """,
                unsafe_allow_html=True,
            )

    # TAB 6: Manage Preferences (Fixed Confirmation)
    with tabs[5]:
        create_header_with_icon("Simpan, Ekspor, atau Reset Preferensi Tampilan", "💾")
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Simpan & Terapkan Tema", type="primary", use_container_width=True):
                    save_ui_theme(theme)
                    st.session_state.ui_theme = theme
                    st.success("✅ Preferensi tampilan berhasil disimpan dan diterapkan!")
                    st.rerun()
            with col2:
                if st.button("🔄 Reset ke Tema Bapenda Default", use_container_width=True):
                    st.session_state.confirm_reset_theme = True
            with col3:
                theme_json = json.dumps(theme, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Ekspor Tema (.json)",
                    data=theme_json.encode("utf-8"),
                    file_name="ui_theme.json",
                    mime="application/json",
                    use_container_width=True,
                )

            if st.session_state.confirm_reset_theme:
                st.warning("⚠️ Kembalikan seluruh warna, ukuran grafik, dan pengaturan privasi ke standar Bapenda Jawa Timur?")
                r1, r2 = st.columns(2)
                with r1:
                    if st.button("✅ Ya, Reset Sekarang", type="primary", use_container_width=True):
                        default_t = get_default_theme()
                        save_ui_theme(default_t)
                        st.session_state.ui_theme = default_t
                        st.session_state.confirm_reset_theme = False
                        st.rerun()
                with r2:
                    if st.button("✖ Batal", use_container_width=True):
                        st.session_state.confirm_reset_theme = False
                        st.rerun()

        with st.expander("📤 Impor Berkas Tema JSON"):
            uploaded_file = st.file_uploader("Unggah berkas ui_theme.json", type=["json"])
            if uploaded_file is not None:
                try:
                    imported_theme = json.load(uploaded_file)
                    if st.button("✅ Terapkan Tema Impor", type="primary"):
                        save_ui_theme(imported_theme)
                        st.session_state.ui_theme = imported_theme
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal memuat berkas tema: {e}")


def app() -> None:
    show_ui_customization_page()


if __name__ == "__main__":
    app()
