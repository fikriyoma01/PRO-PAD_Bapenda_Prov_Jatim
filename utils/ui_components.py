"""
UI Components & Plotly Design System Utilities
Komponen antarmuka terstandarisasi untuk Dashboard PRO-PAD Bapenda Provinsi Jawa Timur.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Callable, Dict, List, Optional

import plotly.graph_objects as go
import streamlit as st

from utils.ui_theme_utils import (
    apply_watermark,
    format_rupiah_compact,
    get_chart_colors,
    get_chart_height,
    get_dynamic_theme_css,
    get_ui_theme,
    get_watermark_text,
)


def load_custom_css() -> None:
    """Muat stylesheet utama, CSS preferensi dinamis, dan watermark opsional."""
    css_file = Path(__file__).resolve().parent.parent / "assets" / "custom_styles.css"
    css_blocks = []
    if css_file.exists():
        css_blocks.append(css_file.read_text(encoding="utf-8"))
    css_blocks.append(get_dynamic_theme_css())
    st.markdown(f"<style>{''.join(css_blocks)}</style>", unsafe_allow_html=True)

    if apply_watermark():
        wm_text = html.escape(get_watermark_text())
        st.markdown(
            f'<div class="propad-watermark" aria-hidden="true">{wm_text}</div>',
            unsafe_allow_html=True,
        )


def _starts_with_emoji(text: str) -> bool:
    stripped = text.lstrip()
    if not stripped:
        return False
    return ord(stripped[0]) > 0x2000


def render_page_header(
    title: str,
    subtitle: str,
    icon: str = "📊",
    badge: Optional[str] = "BAPENDA PROV. JAWA TIMUR • PRO-PAD",
) -> None:
    """Render banner header halaman standar beridentitas Bapenda Jawa Timur."""
    clean_title = title.strip()
    icon_html = f'<span class="page-hero-icon">{icon}</span>' if icon and not _starts_with_emoji(clean_title) else ""
    badge_html = f'<div class="page-hero-badge">{badge}</div>' if badge else ""

    html_block = (
        f'<div class="gradient-header fade-in">'
        f'{badge_html}'
        f'<div class="page-hero-title-row">'
        f'{icon_html}'
        f'<div><h1>{clean_title}</h1><p>{subtitle}</p></div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html_block, unsafe_allow_html=True)


def render_gradient_header(title: str, subtitle: str, icon: str = "📊") -> None:
    """Alias kompatibilitas untuk render_page_header."""
    render_page_header(title=title, subtitle=subtitle, icon=icon)


def create_header_with_icon(
    title: str,
    icon: str = "",
    color: Optional[str] = None,
    subtitle: Optional[str] = None,
) -> None:
    """
    Render subjudul seksi dengan aksen vertikal Bapenda & kontras optimal di Light/Dark mode.
    Parameter `color` dipertahankan untuk kompatibilitas tanda tangan fungsi lama, namun
    warna kini dikendalikan oleh variabel tema `--heading-accent` agar selalu terbaca di Dark Mode.
    """
    clean_title = title.strip()
    show_icon = icon and not _starts_with_emoji(clean_title)
    icon_span = f'<span class="section-heading-icon">{icon}</span>' if show_icon else ""
    sub_html = f'<p class="section-heading-sub">{subtitle}</p>' if subtitle else ""

    html_block = (
        f'<div class="section-heading-wrap">'
        f'<h2 class="section-heading">{icon_span}<span>{clean_title}</span></h2>'
        f'{sub_html}'
        f'</div>'
    )
    st.markdown(html_block, unsafe_allow_html=True)


def render_kpi_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: Optional[bool] = True,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    variant: str = "primary",
) -> None:
    """
    Render kartu KPI modern serbaguna yang seragam di seluruh halaman.
    variant: 'primary' | 'gold' | 'success' | 'warning' | 'danger' | 'indigo'
    """
    delta_html = ""
    if delta:
        if delta_positive is None:
            delta_cls = "neutral"
            symbol = "•"
        elif delta_positive:
            delta_cls = "positive"
            symbol = "▲"
        else:
            delta_cls = "negative"
            symbol = "▼"
        delta_html = f'<div class="metric-delta {delta_cls}">{symbol} {delta}</div>'

    sub_html = f'<div class="kpi-subtitle">{subtitle}</div>' if subtitle else ""
    icon_html = f'<span class="kpi-icon">{icon}</span>' if icon else ""

    html_block = (
        f'<div class="metric-card kpi-variant-{variant}">'
        f'<div class="metric-label">{icon_html}<span>{label}</span></div>'
        f'<div class="metric-value kpi-value">{value}</div>'
        f'{delta_html}{sub_html}'
        f'</div>'
    )
    st.markdown(html_block, unsafe_allow_html=True)


def render_metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    delta_positive: Optional[bool] = True,
) -> None:
    """Kompatibilitas render_metric_card menggunakan sistem KPI baru."""
    render_kpi_card(label=label, value=value, delta=delta, delta_positive=delta_positive)


def styled_metric(
    label: str,
    value: str,
    delta: Optional[str] = None,
    help_text: Optional[str] = None,
) -> None:
    """Kompatibilitas styled_metric menggunakan sistem KPI baru."""
    render_kpi_card(label=label, value=value, delta=delta, subtitle=help_text)


def render_info_box(content: str, box_type: str = "info") -> None:
    """Render kotak informasi/peringatan bertema dengan dukungan Light/Dark penuh."""
    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "success": "✅",
        "danger": "🚨",
    }
    stripped = content.lstrip()
    prefix = "" if _starts_with_emoji(stripped) else f"{icons.get(box_type, 'ℹ️')} "
    st.markdown(
        f'<div class="{box_type}-box callout-box fade-in"><div class="callout-body">{prefix}{content}</div></div>',
        unsafe_allow_html=True,
    )


def render_section_divider() -> None:
    """Render garis pemisah antar seksi."""
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


def render_badge(text: str, badge_type: str = "primary") -> str:
    """Kembalikan HTML badge status."""
    return f'<span class="badge badge-{badge_type}">{text}</span>'


def create_modern_card_container(content_func: Callable[[], None]) -> None:
    """Bungkus komponen Streamlit di dalam st.container(border=True) yang sah di DOM."""
    with st.container(border=True):
        content_func()


def render_stat_row(stats: List[Dict]) -> None:
    """Render satu baris kartu statistik."""
    cols = st.columns(len(stats))
    for col, stat in zip(cols, stats):
        with col:
            render_kpi_card(
                label=stat.get("label", ""),
                value=stat.get("value", ""),
                delta=stat.get("delta"),
                delta_positive=stat.get("delta_positive", True),
                icon=stat.get("icon"),
                variant=stat.get("variant", "primary"),
            )


def create_highlighted_text(text: str, highlight_color: str = "rgba(255, 215, 0, 0.35)") -> str:
    """Kembalikan teks tersorot yang aman untuk kedua tema."""
    return f'<mark style="background: {highlight_color}; color: inherit; padding: 0.15rem 0.45rem; border-radius: 4px;">{text}</mark>'


def render_progress_indicator(current: int, total: int, label: str = "Progress") -> None:
    """Render bilah progres bertema."""
    percentage = (current / total) * 100 if total else 0
    html_block = (
        f'<div style="margin: 1rem 0;">'
        f'<div style="display: flex; justify-content: space-between; margin-bottom: 0.45rem;">'
        f'<span style="font-weight: 600; color: var(--text-dark);">{label}</span>'
        f'<span style="font-weight: 700; color: var(--heading-accent);">{current}/{total} ({percentage:.0f}%)</span>'
        f'</div>'
        f'<div style="width: 100%; height: 10px; background: var(--gray-medium); border-radius: 999px; overflow: hidden;">'
        f'<div style="width: {percentage}%; height: 100%; background: linear-gradient(90deg, var(--primary-blue), var(--primary-blue-light)); border-radius: 999px;"></div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html_block, unsafe_allow_html=True)


def render_feature_card(icon: str, title: str, description: str) -> None:
    """Render kartu fitur unggulan yang rapi dan sejajar tinggi."""
    html_block = (
        f'<div class="feature-card">'
        f'<div class="feature-card-icon">{icon}</div>'
        f'<h3 class="feature-card-title">{title}</h3>'
        f'<p class="feature-card-desc">{description}</p>'
        f'</div>'
    )
    st.markdown(html_block, unsafe_allow_html=True)


def render_comparison_table(data: Dict[str, str], title: str = "Perbandingan") -> None:
    """Render tabel perbandingan satu baris horizontal yang valid."""
    headers = "".join(
        f'<th style="padding: 0.85rem 1rem; text-align: left; font-weight: 600;">{col}</th>'
        for col in data.keys()
    )
    cells = "".join(
        f'<td style="padding: 0.85rem 1rem;">{val}</td>'
        for val in data.values()
    )
    html_block = (
        f'<div class="modern-card">'
        f'<h3 style="color: var(--heading-accent); margin-bottom: 1rem;">{title}</h3>'
        f'<table style="width: 100%; border-collapse: collapse;">'
        f'<thead><tr style="background: var(--gray-light); border-bottom: 2px solid var(--primary-blue);">{headers}</tr></thead>'
        f'<tbody><tr style="border-bottom: 1px solid var(--gray-medium);">{cells}</tr></tbody>'
        f'</table>'
        f'</div>'
    )
    st.markdown(html_block, unsafe_allow_html=True)


def apply_plotly_theme(
    fig: go.Figure,
    title: Optional[str] = None,
    height: Optional[int] = None,
    xaxis_title: Optional[str] = None,
    yaxis_title: Optional[str] = None,
    is_currency: bool = False,
    show_legend: Optional[bool] = None,
    margin: Optional[Dict[str, int]] = None,
) -> go.Figure:
    """
    Standarisasi seluruh grafik Plotly agar rapi, proporsional, dan terbaca sempurna
    baik pada Light Mode maupun Dark Mode (tanpa background putih silau atau garis hitam hilang).
    """
    theme = get_ui_theme()
    show_grid = bool(theme["charts"].get("show_gridlines", True))
    resolved_height = height if height is not None else get_chart_height(450)
    grid_color = "rgba(148, 163, 184, 0.22)" if show_grid else "rgba(0,0,0,0)"
    zero_color = "rgba(148, 163, 184, 0.45)"

    layout_updates: Dict = dict(
        template="plotly_white",
        colorway=get_chart_colors(),
        height=resolved_height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="'Plus Jakarta Sans', 'Inter', 'Segoe UI', system-ui, sans-serif",
            size=12,
            color="#334155",
        ),
        margin=margin or dict(l=64, r=36, t=68 if title else 48, b=60),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#334155",
            font=dict(color="#f8fafc", size=12),
        ),
        legend=dict(
            bgcolor="rgba(148, 163, 184, 0.10)",
            bordercolor="rgba(148, 163, 184, 0.22)",
            borderwidth=1,
            font=dict(size=12),
        ),
    )

    if title is not None:
        layout_updates["title"] = dict(
            text=f"<b>{title}</b>" if "<b>" not in title else title,
            x=0.01,
            xanchor="left",
            font=dict(size=16, color="#1e293b"),
        )

    if show_legend is not None:
        layout_updates["showlegend"] = show_legend

    fig.update_layout(**layout_updates)

    xaxis_updates: Dict = dict(
        showgrid=show_grid,
        gridcolor=grid_color,
        zeroline=False,
        linecolor="rgba(148, 163, 184, 0.35)",
    )
    if xaxis_title is not None:
        xaxis_updates["title"] = xaxis_title

    yaxis_updates: Dict = dict(
        showgrid=show_grid,
        gridcolor=grid_color,
        zeroline=True,
        zerolinecolor=zero_color,
        zerolinewidth=1.5,
        linecolor="rgba(148, 163, 184, 0.35)",
    )
    if yaxis_title is not None:
        yaxis_updates["title"] = yaxis_title
    if is_currency:
        yaxis_updates["tickformat"] = ",.0f"

    fig.update_xaxes(**xaxis_updates)
    fig.update_yaxes(**yaxis_updates)

    return fig


def create_target_gauge(
    potensi_rp: float,
    target_rp: float,
    label: str,
    bar_color: str = "#1a5fb4",
) -> go.Figure:
    """
    Buat Gauge Chart pencapaian target dalam satuan Triliun Rupiah (1e12) yang akurat
    dan tampil harmonis baik di Light Mode maupun Dark Mode.
    """
    val_t = potensi_rp / 1e12
    target_t = target_rp / 1e12
    max_axis = max(val_t, target_t, 0.1) * 1.22

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=val_t,
            number={"prefix": "Rp ", "suffix": "T", "valueformat": ".2f", "font": {"size": 30}},
            delta={
                "reference": target_t,
                "valueformat": "+.2f",
                "suffix": "T",
                "increasing": {"color": "#10b981"},
                "decreasing": {"color": "#ef4444"},
            },
            title={
                "text": (
                    f"<b>{label}</b><br>"
                    f"<span style='font-size:0.82em;opacity:0.8'>Target: {format_rupiah_compact(target_rp)}</span>"
                ),
                "font": {"size": 16},
            },
            gauge={
                "axis": {"range": [0, max_axis], "ticksuffix": "T", "tickformat": ".1f"},
                "bar": {"color": bar_color, "thickness": 0.65},
                "bgcolor": "rgba(148, 163, 184, 0.08)",
                "borderwidth": 1,
                "bordercolor": "rgba(148, 163, 184, 0.25)",
                "steps": [
                    {"range": [0, target_t * 0.85], "color": "rgba(239, 68, 68, 0.14)"},
                    {"range": [target_t * 0.85, target_t], "color": "rgba(245, 158, 11, 0.16)"},
                    {"range": [target_t, max_axis], "color": "rgba(16, 185, 129, 0.14)"},
                ],
                "threshold": {
                    "line": {"color": "#ef4444", "width": 3},
                    "thickness": 0.8,
                    "value": target_t,
                },
            },
        )
    )

    fig.update_layout(
        height=300,
        margin=dict(l=24, r=24, t=72, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="'Plus Jakarta Sans', 'Inter', 'Segoe UI', system-ui, sans-serif",
            color="#334155",
        ),
    )
    return fig
