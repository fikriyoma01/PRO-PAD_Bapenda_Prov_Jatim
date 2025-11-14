"""
UI Theme Utilities
Helper functions to access and apply UI theme settings across the dashboard
"""

import json
from pathlib import Path


THEME_FILE = Path("config/ui_theme.json")


def get_ui_theme():
    """Get current UI theme settings"""
    if THEME_FILE.exists():
        with open(THEME_FILE, 'r') as f:
            return json.load(f)
    return get_default_theme()


def get_default_theme():
    """Get default theme settings"""
    return {
        'theme_name': 'Professional Blue',
        'colors': {
            'primary': '#1a5fb4',
            'primary_light': '#3584e4',
            'accent': '#ffd700',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#ef5350',
            'sidebar_bg_start': '#0f2027',
            'sidebar_bg_end': '#2c5364',
        },
        'typography': {
            'header_size': '2.5rem',
            'subheader_size': '1.8rem',
            'body_size': '1rem',
            'font_family': 'Segoe UI, sans-serif',
        },
        'layout': {
            'sidebar_width': 'expanded',
            'card_shadow': 'medium',
            'border_radius': '12px',
            'spacing': 'comfortable',
        },
        'data_display': {
            'number_format': 'T',
            'decimal_places': 2,
            'show_thousand_separator': True,
            'currency_symbol': 'Rp',
        },
        'charts': {
            'default_height': 500,
            'color_scheme': 'professional',
            'show_gridlines': True,
            'animation_enabled': True,
        },
        'privacy': {
            'blur_sensitive_numbers': False,
            'watermark_enabled': False,
            'watermark_text': 'CONFIDENTIAL',
            'show_projection_values': True,
            'redact_mode': False,
        }
    }


def format_number_with_theme(value, override_format=None):
    """
    Format number according to theme settings

    Args:
        value: Number to format
        override_format: Optional format override ('T', 'B', 'M', 'Full')

    Returns:
        str: Formatted number
    """
    theme = get_ui_theme()
    display_settings = theme['data_display']

    format_type = override_format or display_settings['number_format']
    decimal_places = display_settings['decimal_places']

    if format_type == 'T':
        formatted = f"{value/1e12:.{decimal_places}f}T"
    elif format_type == 'B':
        formatted = f"{value/1e9:.{decimal_places}f}B"
    elif format_type == 'M':
        formatted = f"{value/1e6:.{decimal_places}f}M"
    else:
        if display_settings['show_thousand_separator']:
            formatted = f"{value:,.{decimal_places}f}"
        else:
            formatted = f"{value:.{decimal_places}f}"

    return f"{display_settings['currency_symbol']} {formatted}"


def should_hide_value():
    """Check if values should be hidden based on privacy settings"""
    theme = get_ui_theme()
    return not theme['privacy']['show_projection_values']


def is_redact_mode():
    """Check if redaction mode is enabled"""
    theme = get_ui_theme()
    return theme['privacy']['redact_mode']


def get_chart_height():
    """Get default chart height from theme"""
    theme = get_ui_theme()
    return theme['charts']['default_height']


def get_primary_color():
    """Get primary color from theme"""
    theme = get_ui_theme()
    return theme['colors']['primary']


def get_color_palette():
    """Get full color palette from theme"""
    theme = get_ui_theme()
    return theme['colors']


def format_sensitive_value(value, mask_type='blur'):
    """
    Format value according to privacy settings

    Args:
        value: Value to format
        mask_type: 'blur', 'redact', or 'hide'

    Returns:
        str: Formatted/masked value
    """
    theme = get_ui_theme()
    privacy = theme['privacy']

    if privacy['redact_mode'] or mask_type == 'redact':
        return "[REDACTED]"
    elif not privacy['show_projection_values'] or mask_type == 'hide':
        return "***.**T"
    elif privacy['blur_sensitive_numbers'] or mask_type == 'blur':
        formatted = format_number_with_theme(value)
        return f'<span style="filter: blur(4px);">{formatted}</span>'
    else:
        return format_number_with_theme(value)


def apply_watermark():
    """Check if watermark should be applied"""
    theme = get_ui_theme()
    return theme['privacy']['watermark_enabled']


def get_watermark_text():
    """Get watermark text"""
    theme = get_ui_theme()
    return theme['privacy']['watermark_text']
