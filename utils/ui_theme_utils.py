"""
UI Theme & Formatting Utilities
Pusat pengelolaan preferensi tampilan, format angka Rupiah akurat, dan CSS dinamis PRO-PAD.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st

THEME_FILE = Path(__file__).resolve().parent.parent / "config" / "ui_theme.json"

BAPENDA_PALETTE = [
    "#1a5fb4",  # Biru Bapenda Utama
    "#f59e0b",  # Emas / Amber Jatim
    "#10b981",  # Hijau Emerald
    "#ef4444",  # Merah Karang
    "#6366f1",  # Indigo
    "#0ea5e9",  # Biru Langit
    "#8b5cf6",  # Ungu Modern
]

CHART_SCHEMES = {
    "professional": ["#1a5fb4", "#f59e0b", "#10b981", "#ef4444", "#6366f1", "#0ea5e9"],
    "vibrant": ["#2563eb", "#f97316", "#16a34a", "#dc2626", "#9333ea", "#06b6d4"],
    "pastel": ["#60a5fa", "#fbbf24", "#34d399", "#f87171", "#a78bfa", "#38bdf8"],
    "monochrome": ["#1e3a8a", "#1d4ed8", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"],
}


def get_default_theme() -> Dict[str, Any]:
    """Pengaturan tema default resmi Bapenda Provinsi Jawa Timur."""
    return {
        "theme_name": "Professional Blue",
        "colors": {
            "primary": "#1a5fb4",
            "primary_light": "#3584e4",
            "accent": "#ffd700",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "sidebar_bg_start": "#0b192c",
            "sidebar_bg_end": "#1e3a5f",
        },
        "typography": {
            "header_size": "2.1rem",
            "subheader_size": "1.35rem",
            "body_size": "0.975rem",
            "font_family": "'Plus Jakarta Sans', 'Inter', 'Segoe UI', system-ui, sans-serif",
        },
        "layout": {
            "sidebar_width": "expanded",
            "card_shadow": "medium",
            "border_radius": "14px",
            "spacing": "comfortable",
        },
        "data_display": {
            "number_format": "T",  # T = Adaptif Triliun/Miliar/Juta, B = Miliar, M = Juta, Full = Penuh
            "decimal_places": 2,
            "show_thousand_separator": True,
            "currency_symbol": "Rp",
        },
        "charts": {
            "default_height": 450,
            "color_scheme": "professional",
            "show_gridlines": True,
            "animation_enabled": True,
        },
        "privacy": {
            "blur_sensitive_numbers": False,
            "watermark_enabled": False,
            "watermark_text": "RAHASIA — INTERNAL BAPENDA JATIM",
            "show_projection_values": True,
            "redact_mode": False,
        },
    }


def _merge_defaults(loaded: Dict[str, Any]) -> Dict[str, Any]:
    """Pastikan seluruh key default selalu tersedia meskipun file JSON versi lama."""
    defaults = get_default_theme()
    for section, val in defaults.items():
        if section not in loaded:
            loaded[section] = val
        elif isinstance(val, dict) and isinstance(loaded[section], dict):
            merged = val.copy()
            merged.update(loaded[section])
            loaded[section] = merged
    return loaded


def get_ui_theme() -> Dict[str, Any]:
    """Ambil preferensi tema aktif dari session_state atau file konfigurasi."""
    try:
        if "ui_theme" in st.session_state and isinstance(st.session_state.ui_theme, dict):
            return _merge_defaults(st.session_state.ui_theme)
    except Exception:
        pass

    if THEME_FILE.exists():
        try:
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                return _merge_defaults(json.load(f))
        except Exception:
            return get_default_theme()
    return get_default_theme()


def save_ui_theme(theme: Dict[str, Any]) -> None:
    """Simpan preferensi tema ke disk."""
    THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(THEME_FILE, "w", encoding="utf-8") as f:
        json.dump(theme, f, indent=2, ensure_ascii=False)


def format_rupiah_full(value: float, signed: bool = False) -> str:
    """Format nilai Rupiah penuh dengan pemisah ribuan titik khas Indonesia."""
    if value is None:
        return "-"
    val = float(value)
    theme = get_ui_theme()
    symbol = theme["data_display"].get("currency_symbol", "Rp")
    use_sep = theme["data_display"].get("show_thousand_separator", True)

    abs_int = int(round(abs(val)))
    num_str = f"{abs_int:,}".replace(",", ".") if use_sep else str(abs_int)

    if signed:
        sign = "+" if val >= 0 else "-"
        return f"{sign}{symbol} {num_str}"
    if val < 0:
        return f"-{symbol} {num_str}"
    return f"{symbol} {num_str}"


def format_rupiah_compact(
    value: float,
    signed: bool = False,
    decimals: Optional[int] = None,
    override_format: Optional[str] = None,
    respect_privacy: bool = False,
) -> str:
    """
    Format nilai Rupiah secara akurat & adaptif:
      - >= 1e12 -> Triliun (T)   [1 Triliun = 1.000.000.000.000]
      - >= 1e9  -> Miliar (M)    [1 Miliar  = 1.000.000.000]
      - >= 1e6  -> Juta (Jt)     [1 Juta    = 1.000.000]
      - <  1e6  -> Rupiah penuh
    """
    if value is None:
        return "-"

    theme = get_ui_theme()
    privacy = theme["privacy"]

    if respect_privacy:
        if privacy.get("redact_mode", False):
            return "[REDACTED]"
        if not privacy.get("show_projection_values", True):
            return "Rp •••,•• T"

    display = theme["data_display"]
    fmt_mode = override_format or display.get("number_format", "T")
    dec = decimals if decimals is not None else int(display.get("decimal_places", 2))
    symbol = display.get("currency_symbol", "Rp")

    val = float(value)
    abs_val = abs(val)

    if fmt_mode == "Full":
        return format_rupiah_full(val, signed=signed)
    elif fmt_mode == "B":
        # Paksa satuan Miliar (Billion)
        scaled = f"{abs_val / 1e9:,.{dec}f}M"
    elif fmt_mode == "M":
        # Paksa satuan Juta (Million)
        scaled = f"{abs_val / 1e6:,.{dec}f}Jt"
    else:
        # Mode default 'T': adaptif Triliun / Miliar / Juta agar tidak pernah salah skala
        if abs_val >= 1e12:
            scaled = f"{abs_val / 1e12:.{dec}f}T"
        elif abs_val >= 1e9:
            scaled = f"{abs_val / 1e9:.{dec}f}M"
        elif abs_val >= 1e6:
            scaled = f"{abs_val / 1e6:.{dec}f}Jt"
        else:
            scaled = f"{abs_val:,.0f}".replace(",", ".")

    if signed:
        sign = "+" if val >= 0 else "-"
        return f"{sign}{symbol} {scaled}"
    if val < 0:
        return f"-{symbol} {scaled}"
    return f"{symbol} {scaled}"


def format_number_with_theme(value: float, override_format: Optional[str] = None) -> str:
    """Kompatibilitas pemformatan angka sesuai pengaturan tema."""
    return format_rupiah_compact(value, override_format=override_format)


def should_hide_value() -> bool:
    theme = get_ui_theme()
    return not theme["privacy"].get("show_projection_values", True)


def is_redact_mode() -> bool:
    theme = get_ui_theme()
    return theme["privacy"].get("redact_mode", False)


def get_chart_height(default: int = 450) -> int:
    theme = get_ui_theme()
    return int(theme["charts"].get("default_height", default))


def get_chart_colors() -> list[str]:
    theme = get_ui_theme()
    scheme = theme["charts"].get("color_scheme", "professional")
    return CHART_SCHEMES.get(scheme, BAPENDA_PALETTE)


def get_primary_color() -> str:
    theme = get_ui_theme()
    return theme["colors"].get("primary", "#1a5fb4")


def get_color_palette() -> Dict[str, str]:
    theme = get_ui_theme()
    return theme["colors"]


def format_sensitive_value(value: float, mask_type: Optional[str] = None) -> str:
    """Format nilai sensitif sesuai aturan privasi pada UI Customization."""
    theme = get_ui_theme()
    privacy = theme["privacy"]

    if privacy.get("redact_mode") or mask_type == "redact":
        return "[REDACTED]"
    if not privacy.get("show_projection_values", True) or mask_type == "hide":
        return "Rp •••,•• T"
    formatted = format_rupiah_compact(value)
    if privacy.get("blur_sensitive_numbers") or mask_type == "blur":
        return f'<span class="sensitive-blur" title="Arahkan kursor untuk melihat">{formatted}</span>'
    return formatted


def apply_watermark() -> bool:
    theme = get_ui_theme()
    return bool(theme["privacy"].get("watermark_enabled", False))


def get_watermark_text() -> str:
    theme = get_ui_theme()
    return str(theme["privacy"].get("watermark_text", "CONFIDENTIAL"))


def get_dynamic_theme_css() -> str:
    """Bangun blok CSS variabel dinamis & aturan privasi berdasarkan preferensi user."""
    theme = get_ui_theme()
    colors = theme["colors"]
    layout = theme["layout"]
    typo = theme["typography"]
    privacy = theme["privacy"]

    shadow_map = {
        "none": "none",
        "light": "0 2px 8px rgba(15, 23, 42, 0.04)",
        "medium": "0 6px 20px rgba(15, 23, 42, 0.07)",
        "strong": "0 12px 32px rgba(15, 23, 42, 0.14)",
    }
    spacing_map = {
        "compact": "1rem",
        "comfortable": "1.35rem",
        "spacious": "1.85rem",
    }

    card_shadow = shadow_map.get(layout.get("card_shadow", "medium"), shadow_map["medium"])
    card_pad = spacing_map.get(layout.get("spacing", "comfortable"), "1.35rem")
    radius = layout.get("border_radius", "14px")

    extra_rules = []
    if privacy.get("blur_sensitive_numbers", False):
        extra_rules.append(
            """
            .kpi-value, [data-testid="stMetricValue"], .sensitive-blur {
                filter: blur(6px);
                transition: filter 0.25s ease;
                cursor: pointer;
            }
            .kpi-value:hover, [data-testid="stMetricValue"]:hover, .sensitive-blur:hover {
                filter: none;
            }
            """
        )

    return f"""
    :root {{
        --primary-blue: {colors.get('primary', '#1a5fb4')};
        --primary-blue-light: {colors.get('primary_light', '#3584e4')};
        --accent-gold: {colors.get('accent', '#ffd700')};
        --success-green: {colors.get('success', '#10b981')};
        --accent-orange: {colors.get('warning', '#f59e0b')};
        --danger-red: {colors.get('danger', '#ef4444')};
        --sidebar-start: {colors.get('sidebar_bg_start', '#0b192c')};
        --sidebar-end: {colors.get('sidebar_bg_end', '#1e3a5f')};
        --radius-card: {radius};
        --shadow-card: {card_shadow};
        --pad-card: {card_pad};
        --font-sans: {typo.get('font_family', "'Plus Jakarta Sans', 'Inter', 'Segoe UI', sans-serif")};
    }}
    {"".join(extra_rules)}
    """
