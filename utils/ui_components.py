"""
UI Components Utilities
Reusable UI components for consistent design across the dashboard
"""

import streamlit as st
from pathlib import Path


def load_custom_css():
    """Load custom CSS styling"""
    css_file = Path(__file__).parent.parent / "assets" / "custom_styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def render_gradient_header(title: str, subtitle: str, icon: str = "📊"):
    """
    Render a beautiful gradient header

    Args:
        title: Main title
        subtitle: Subtitle text
        icon: Emoji icon
    """
    st.markdown(f"""
    <div class="gradient-header fade-in">
        <h1>{icon} {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, delta: str = None, delta_positive: bool = True):
    """
    Render an enhanced metric card

    Args:
        label: Metric label
        value: Metric value
        delta: Change value (optional)
        delta_positive: Whether delta is positive
    """
    delta_html = ""
    if delta:
        delta_class = "positive" if delta_positive else "negative"
        delta_symbol = "▲" if delta_positive else "▼"
        delta_html = f'<div class="metric-delta {delta_class}">{delta_symbol} {delta}</div>'

    st.markdown(f"""
    <div class="metric-card slide-in-right">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_info_box(content: str, box_type: str = "info"):
    """
    Render styled info box

    Args:
        content: Box content (supports markdown)
        box_type: Type of box (info, warning, success, danger)
    """
    icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "success": "✅",
        "danger": "❌"
    }

    st.markdown(f"""
    <div class="{box_type}-box fade-in">
        <strong>{icons.get(box_type, "ℹ️")} {content}</strong>
    </div>
    """, unsafe_allow_html=True)


def render_section_divider():
    """Render a styled section divider"""
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


def render_badge(text: str, badge_type: str = "primary"):
    """
    Render a badge

    Args:
        text: Badge text
        badge_type: Type of badge (primary, success, warning, danger)
    """
    return f'<span class="badge badge-{badge_type}">{text}</span>'


def create_modern_card_container(content_func):
    """
    Wrapper to create a modern card container

    Args:
        content_func: Function that generates content
    """
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    content_func()
    st.markdown('</div>', unsafe_allow_html=True)


def render_stat_row(stats: list):
    """
    Render a row of statistics

    Args:
        stats: List of dicts with keys: label, value, icon
    """
    cols = st.columns(len(stats))

    for col, stat in zip(cols, stats):
        with col:
            icon = stat.get('icon', '📊')
            label = stat.get('label', '')
            value = stat.get('value', '')
            delta = stat.get('delta', None)
            delta_positive = stat.get('delta_positive', True)

            render_metric_card(label, value, delta, delta_positive)


def styled_metric(label: str, value: str, delta: str = None, help_text: str = None):
    """
    Enhanced version of st.metric with custom styling

    Args:
        label: Metric label
        value: Metric value
        delta: Delta value
        help_text: Help tooltip text
    """
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {f'<div class="metric-delta positive">▲ {delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


def create_header_with_icon(title: str, icon: str, color: str = "#1a5fb4"):
    """
    Create a header with icon and custom color

    Args:
        title: Header title
        icon: Emoji icon
        color: Header color
    """
    st.markdown(f"""
    <h2 style="
        color: {color};
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        font-size: 1.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    ">
        <span style="font-size: 2rem;">{icon}</span>
        {title}
    </h2>
    """, unsafe_allow_html=True)


def create_highlighted_text(text: str, highlight_color: str = "#ffd700"):
    """
    Create highlighted text

    Args:
        text: Text to highlight
        highlight_color: Highlight color
    """
    return f'<mark style="background: {highlight_color}; padding: 0.2rem 0.5rem; border-radius: 4px;">{text}</mark>'


def render_progress_indicator(current: int, total: int, label: str = "Progress"):
    """
    Render a custom progress indicator

    Args:
        current: Current progress
        total: Total steps
        label: Progress label
    """
    percentage = (current / total) * 100

    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="font-weight: 600; color: #2c3e50;">{label}</span>
            <span style="font-weight: 600; color: #1a5fb4;">{current}/{total} ({percentage:.0f}%)</span>
        </div>
        <div style="
            width: 100%;
            height: 12px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        ">
            <div style="
                width: {percentage}%;
                height: 100%;
                background: linear-gradient(90deg, #1a5fb4, #3584e4);
                border-radius: 10px;
                transition: width 0.3s ease;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_feature_card(icon: str, title: str, description: str):
    """
    Render a feature card

    Args:
        icon: Feature icon
        title: Feature title
        description: Feature description
    """
    st.markdown(f"""
    <div class="modern-card" style="text-align: center;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <h3 style="color: #1a5fb4; margin-bottom: 0.5rem;">{title}</h3>
        <p style="color: #6c757d;">{description}</p>
    </div>
    """, unsafe_allow_html=True)


def render_comparison_table(data: dict, title: str = "Comparison"):
    """
    Render a styled comparison table

    Args:
        data: Dictionary with comparison data
        title: Table title
    """
    st.markdown(f"""
    <div class="modern-card">
        <h3 style="color: #1a5fb4; margin-bottom: 1.5rem;">{title}</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #1a5fb4;">
                    {''.join([f'<th style="padding: 1rem; text-align: left; font-weight: 600;">{col}</th>' for col in data.keys()])}
                </tr>
            </thead>
            <tbody>
                {''.join([f'<tr style="border-bottom: 1px solid #e9ecef;"><td style="padding: 1rem;">{val}</td></tr>' for val in data.values()])}
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)


def add_fade_in_animation():
    """Add fade-in animation to page elements"""
    st.markdown("""
    <script>
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });

    document.querySelectorAll('.modern-card').forEach((el) => observer.observe(el));
    </script>
    """, unsafe_allow_html=True)
