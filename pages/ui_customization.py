"""
UI Customization & Theme Manager
Allows users to customize dashboard appearance and save preferences
"""

import streamlit as st
import json
from pathlib import Path
from utils.ui_components import render_gradient_header, create_header_with_icon


THEME_FILE = Path("config/ui_theme.json")


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
            'number_format': 'T',  # T for Trillion, B for Billion, M for Million
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


def load_theme():
    """Load theme from file"""
    if THEME_FILE.exists():
        with open(THEME_FILE, 'r') as f:
            return json.load(f)
    return get_default_theme()


def save_theme(theme):
    """Save theme to file"""
    THEME_FILE.parent.mkdir(exist_ok=True)
    with open(THEME_FILE, 'w') as f:
        json.dump(theme, f, indent=2)


def get_preset_themes():
    """Get preset theme options"""
    return {
        'Professional Blue': {
            'primary': '#1a5fb4',
            'primary_light': '#3584e4',
            'accent': '#ffd700',
            'sidebar_bg_start': '#0f2027',
            'sidebar_bg_end': '#2c5364',
        },
        'Corporate Green': {
            'primary': '#2e7d32',
            'primary_light': '#4caf50',
            'accent': '#ffeb3b',
            'sidebar_bg_start': '#1b5e20',
            'sidebar_bg_end': '#388e3c',
        },
        'Modern Purple': {
            'primary': '#6a1b9a',
            'primary_light': '#8e24aa',
            'accent': '#ff4081',
            'sidebar_bg_start': '#4a148c',
            'sidebar_bg_end': '#7b1fa2',
        },
        'Elegant Dark': {
            'primary': '#424242',
            'primary_light': '#616161',
            'accent': '#ffc107',
            'sidebar_bg_start': '#212121',
            'sidebar_bg_end': '#424242',
        },
        'Ocean Blue': {
            'primary': '#0277bd',
            'primary_light': '#0288d1',
            'accent': '#00bcd4',
            'sidebar_bg_start': '#01579b',
            'sidebar_bg_end': '#0277bd',
        }
    }


def show_ui_customization_page():
    render_gradient_header(
        title="UI Customization & Preferences",
        subtitle="Personalize dashboard appearance and behavior",
        icon="🎨"
    )

    # Load current theme
    if 'ui_theme' not in st.session_state:
        st.session_state.ui_theme = load_theme()

    theme = st.session_state.ui_theme

    # Tabs
    tabs = st.tabs([
        "🎨 Theme & Colors",
        "📐 Layout & Spacing",
        "🔢 Number Format",
        "📊 Chart Settings",
        "🔒 Privacy & Security",
        "💾 Manage Preferences"
    ])

    # TAB 1: Theme & Colors
    with tabs[0]:
        create_header_with_icon("Color Scheme", "🎨")

        # Preset themes
        st.subheader("Quick Presets")
        presets = get_preset_themes()
        selected_preset = st.selectbox(
            "Choose a preset theme",
            options=list(presets.keys()),
            index=0
        )

        if st.button("Apply Preset"):
            theme['colors'].update(presets[selected_preset])
            theme['theme_name'] = selected_preset
            st.success(f"✅ Applied {selected_preset} theme!")
            st.rerun()

        st.markdown("---")
        st.subheader("Custom Colors")

        col1, col2 = st.columns(2)

        with col1:
            primary = st.color_picker(
                "Primary Color",
                value=theme['colors']['primary'],
                help="Main brand color"
            )

            accent = st.color_picker(
                "Accent Color",
                value=theme['colors']['accent'],
                help="Highlight and CTA color"
            )

            success = st.color_picker(
                "Success Color",
                value=theme['colors']['success'],
                help="Positive indicators"
            )

        with col2:
            primary_light = st.color_picker(
                "Primary Light",
                value=theme['colors']['primary_light'],
                help="Lighter shade of primary"
            )

            warning = st.color_picker(
                "Warning Color",
                value=theme['colors']['warning'],
                help="Warning indicators"
            )

            danger = st.color_picker(
                "Danger Color",
                value=theme['colors']['danger'],
                help="Error and critical alerts"
            )

        st.subheader("Sidebar Colors")
        col1, col2 = st.columns(2)

        with col1:
            sidebar_start = st.color_picker(
                "Sidebar Gradient Start",
                value=theme['colors']['sidebar_bg_start']
            )

        with col2:
            sidebar_end = st.color_picker(
                "Sidebar Gradient End",
                value=theme['colors']['sidebar_bg_end']
            )

        # Update theme
        theme['colors'].update({
            'primary': primary,
            'primary_light': primary_light,
            'accent': accent,
            'success': success,
            'warning': warning,
            'danger': danger,
            'sidebar_bg_start': sidebar_start,
            'sidebar_bg_end': sidebar_end,
        })

        # Preview
        st.markdown("---")
        st.subheader("Preview")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {primary}, {primary_light});
            padding: 2rem;
            border-radius: 12px;
            color: white;
            text-align: center;
        ">
            <h2>Sample Header with Gradient</h2>
            <p>This is how your headers will look</p>
        </div>
        """, unsafe_allow_html=True)

    # TAB 2: Layout & Spacing
    with tabs[1]:
        create_header_with_icon("Layout Preferences", "📐")

        sidebar_width = st.radio(
            "Sidebar Width",
            options=['collapsed', 'expanded'],
            index=0 if theme['layout']['sidebar_width'] == 'collapsed' else 1,
            horizontal=True
        )

        card_shadow = st.select_slider(
            "Card Shadow Intensity",
            options=['none', 'light', 'medium', 'strong'],
            value=theme['layout']['card_shadow']
        )

        border_radius = st.slider(
            "Border Radius (px)",
            min_value=0,
            max_value=30,
            value=int(theme['layout']['border_radius'].replace('px', '')),
            help="Roundness of cards and buttons"
        )

        spacing = st.radio(
            "Content Spacing",
            options=['compact', 'comfortable', 'spacious'],
            index=['compact', 'comfortable', 'spacious'].index(theme['layout']['spacing']),
            horizontal=True
        )

        theme['layout'].update({
            'sidebar_width': sidebar_width,
            'card_shadow': card_shadow,
            'border_radius': f'{border_radius}px',
            'spacing': spacing,
        })

        # Typography
        st.markdown("---")
        st.subheader("Typography")

        font_family = st.selectbox(
            "Font Family",
            options=[
                'Segoe UI, sans-serif',
                'Arial, sans-serif',
                'Helvetica, sans-serif',
                'Georgia, serif',
                'Times New Roman, serif',
                'Courier New, monospace'
            ],
            index=0
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            header_size = st.number_input(
                "Header Size (rem)",
                min_value=1.5,
                max_value=4.0,
                value=float(theme['typography']['header_size'].replace('rem', '')),
                step=0.1
            )

        with col2:
            subheader_size = st.number_input(
                "Subheader Size (rem)",
                min_value=1.0,
                max_value=3.0,
                value=float(theme['typography']['subheader_size'].replace('rem', '')),
                step=0.1
            )

        with col3:
            body_size = st.number_input(
                "Body Size (rem)",
                min_value=0.8,
                max_value=1.5,
                value=float(theme['typography']['body_size'].replace('rem', '')),
                step=0.05
            )

        theme['typography'].update({
            'header_size': f'{header_size}rem',
            'subheader_size': f'{subheader_size}rem',
            'body_size': f'{body_size}rem',
            'font_family': font_family,
        })

    # TAB 3: Number Format
    with tabs[2]:
        create_header_with_icon("Number Formatting", "🔢")

        st.markdown("""
        <div class="info-box">
        Customize how numbers are displayed throughout the dashboard.
        </div>
        """, unsafe_allow_html=True)

        number_format = st.selectbox(
            "Large Number Format",
            options=['T', 'B', 'M', 'Full'],
            index=['T', 'B', 'M', 'Full'].index(theme['data_display']['number_format']),
            help="T=Trillion (1.5T), B=Billion (1500B), M=Million (1500000M), Full=1500000000000"
        )

        decimal_places = st.slider(
            "Decimal Places",
            min_value=0,
            max_value=4,
            value=theme['data_display']['decimal_places']
        )

        show_separator = st.checkbox(
            "Show Thousand Separator (1,000,000)",
            value=theme['data_display']['show_thousand_separator']
        )

        currency_symbol = st.text_input(
            "Currency Symbol",
            value=theme['data_display']['currency_symbol'],
            max_chars=10
        )

        theme['data_display'].update({
            'number_format': number_format,
            'decimal_places': decimal_places,
            'show_thousand_separator': show_separator,
            'currency_symbol': currency_symbol,
        })

        # Preview
        st.markdown("---")
        st.subheader("Preview")
        sample_number = 10500000000000  # 10.5 trillion

        formatted = format_number(sample_number, theme['data_display'])
        st.metric("Sample Number", formatted)

    # TAB 4: Chart Settings
    with tabs[3]:
        create_header_with_icon("Chart Preferences", "📊")

        default_height = st.slider(
            "Default Chart Height (px)",
            min_value=300,
            max_value=800,
            value=theme['charts']['default_height'],
            step=50
        )

        color_scheme = st.selectbox(
            "Chart Color Scheme",
            options=['professional', 'vibrant', 'pastel', 'monochrome'],
            index=['professional', 'vibrant', 'pastel', 'monochrome'].index(theme['charts']['color_scheme'])
        )

        show_gridlines = st.checkbox(
            "Show Gridlines",
            value=theme['charts']['show_gridlines']
        )

        animation_enabled = st.checkbox(
            "Enable Animations",
            value=theme['charts']['animation_enabled']
        )

        theme['charts'].update({
            'default_height': default_height,
            'color_scheme': color_scheme,
            'show_gridlines': show_gridlines,
            'animation_enabled': animation_enabled,
        })

    # TAB 5: Privacy & Security
    with tabs[4]:
        create_header_with_icon("Privacy & Visibility Controls", "🔒")

        st.markdown("""
        <div class="warning-box">
        ⚠️ <strong>Privacy Controls:</strong> Hide sensitive projection values for presentations or public sharing.
        </div>
        """, unsafe_allow_html=True)

        show_values = st.checkbox(
            "Show Projection Values",
            value=theme['privacy']['show_projection_values'],
            help="Uncheck to hide actual numbers in projections"
        )

        blur_sensitive = st.checkbox(
            "Blur Sensitive Numbers",
            value=theme['privacy']['blur_sensitive_numbers'],
            help="Apply blur effect to projection values"
        )

        redact_mode = st.checkbox(
            "Redaction Mode (Replace with [REDACTED])",
            value=theme['privacy']['redact_mode'],
            help="Replace sensitive values with [REDACTED] placeholder"
        )

        st.markdown("---")
        st.subheader("Watermark Settings")

        watermark_enabled = st.checkbox(
            "Enable Watermark",
            value=theme['privacy']['watermark_enabled'],
            help="Add watermark to all pages"
        )

        if watermark_enabled:
            watermark_text = st.text_input(
                "Watermark Text",
                value=theme['privacy']['watermark_text'],
                max_chars=50
            )
        else:
            watermark_text = theme['privacy']['watermark_text']

        theme['privacy'].update({
            'blur_sensitive_numbers': blur_sensitive,
            'watermark_enabled': watermark_enabled,
            'watermark_text': watermark_text,
            'show_projection_values': show_values,
            'redact_mode': redact_mode,
        })

        # Preview
        if redact_mode or blur_sensitive or not show_values:
            st.markdown("---")
            st.subheader("Preview")
            st.markdown(f"""
            <div class="modern-card">
                <h3>Sample Projection Display</h3>
                <p>Proyeksi PKB 2025: {format_sensitive_value(10500000000000, theme['privacy'])}</p>
                <p>Proyeksi BBNKB 2025: {format_sensitive_value(2500000000000, theme['privacy'])}</p>
            </div>
            """, unsafe_allow_html=True)

    # TAB 6: Manage Preferences
    with tabs[5]:
        create_header_with_icon("Save & Manage Preferences", "💾")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save Theme", type="primary", use_container_width=True):
                save_theme(theme)
                st.session_state.ui_theme = theme
                st.success("✅ Theme saved successfully!")
                st.balloons()

        with col2:
            if st.button("🔄 Reset to Default", use_container_width=True):
                if st.checkbox("Confirm reset?"):
                    theme = get_default_theme()
                    save_theme(theme)
                    st.session_state.ui_theme = theme
                    st.success("✅ Reset to default theme!")
                    st.rerun()

        with col3:
            theme_json = json.dumps(theme, indent=2)
            st.download_button(
                label="📥 Export Theme",
                data=theme_json,
                file_name="ui_theme.json",
                mime="application/json",
                use_container_width=True
            )

        st.markdown("---")
        st.subheader("Import Theme")

        uploaded_file = st.file_uploader("Upload theme JSON", type=['json'])
        if uploaded_file is not None:
            try:
                imported_theme = json.load(uploaded_file)
                if st.button("Apply Imported Theme"):
                    save_theme(imported_theme)
                    st.session_state.ui_theme = imported_theme
                    st.success("✅ Theme imported successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error importing theme: {e}")


def format_number(value, display_settings):
    """Format number according to display settings"""
    if display_settings['number_format'] == 'T':
        formatted = f"{value/1e12:.{display_settings['decimal_places']}f}T"
    elif display_settings['number_format'] == 'B':
        formatted = f"{value/1e9:.{display_settings['decimal_places']}f}B"
    elif display_settings['number_format'] == 'M':
        formatted = f"{value/1e6:.{display_settings['decimal_places']}f}M"
    else:
        formatted = f"{value:,.{display_settings['decimal_places']}f}"

    if display_settings['show_thousand_separator'] and display_settings['number_format'] == 'Full':
        formatted = f"{value:,}"

    return f"{display_settings['currency_symbol']} {formatted}"


def format_sensitive_value(value, privacy_settings):
    """Format value according to privacy settings"""
    if privacy_settings['redact_mode']:
        return "[REDACTED]"
    elif not privacy_settings['show_projection_values']:
        return "***.**T"
    elif privacy_settings['blur_sensitive_numbers']:
        return f'<span style="filter: blur(4px);">Rp {value/1e12:.2f}T</span>'
    else:
        return f"Rp {value/1e12:.2f}T"


def app():
    show_ui_customization_page()


if __name__ == "__main__":
    app()
