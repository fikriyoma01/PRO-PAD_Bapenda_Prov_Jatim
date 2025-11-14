"""
Variable Manager
Dynamically add, remove, and manage macroeconomic variables
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from utils.ui_components import render_gradient_header, render_info_box, create_header_with_icon


VARIABLES_FILE = Path("config/custom_variables.json")


def get_default_variables():
    """Get default macro variables"""
    return {
        'PDRB': {
            'name': 'PDRB',
            'full_name': 'Pertumbuhan PDRB',
            'description': 'Pertumbuhan Produk Domestik Regional Bruto (%)',
            'unit': '%',
            'category': 'Economic Growth',
            'expected_range': [-10, 20],
            'active': True,
            'custom': False
        },
        'Rasio Gini': {
            'name': 'Rasio Gini',
            'full_name': 'Rasio Gini',
            'description': 'Indeks ketimpangan pendapatan (0-1)',
            'unit': 'index',
            'category': 'Social Indicators',
            'expected_range': [0, 1],
            'active': True,
            'custom': False
        },
        'IPM': {
            'name': 'IPM',
            'full_name': 'Indeks Pembangunan Manusia',
            'description': 'Indeks Pembangunan Manusia (0-100)',
            'unit': 'index',
            'category': 'Social Indicators',
            'expected_range': [0, 100],
            'active': True,
            'custom': False
        },
        'TPT': {
            'name': 'TPT',
            'full_name': 'Tingkat Pengangguran Terbuka',
            'description': 'Tingkat Pengangguran Terbuka (%)',
            'unit': '%',
            'category': 'Labor Market',
            'expected_range': [0, 30],
            'active': True,
            'custom': False
        },
        'Kemiskinan': {
            'name': 'Kemiskinan',
            'full_name': 'Tingkat Kemiskinan',
            'description': 'Persentase penduduk miskin (%)',
            'unit': '%',
            'category': 'Social Indicators',
            'expected_range': [0, 100],
            'active': True,
            'custom': False
        },
        'Inflasi': {
            'name': 'Inflasi',
            'full_name': 'Tingkat Inflasi',
            'description': 'Tingkat inflasi year-on-year (%)',
            'unit': '%',
            'category': 'Monetary',
            'expected_range': [-10, 30],
            'active': True,
            'custom': False
        },
        'Suku Bunga': {
            'name': 'Suku Bunga',
            'full_name': 'Suku Bunga Acuan',
            'description': 'Suku bunga acuan BI (%)',
            'unit': '%',
            'category': 'Monetary',
            'expected_range': [0, 30],
            'active': True,
            'custom': False
        }
    }


def load_variables():
    """Load variables configuration"""
    if VARIABLES_FILE.exists():
        with open(VARIABLES_FILE, 'r') as f:
            custom_vars = json.load(f)
            # Merge with defaults
            defaults = get_default_variables()
            defaults.update(custom_vars)
            return defaults
    return get_default_variables()


def save_variables(variables):
    """Save variables configuration"""
    VARIABLES_FILE.parent.mkdir(exist_ok=True)
    with open(VARIABLES_FILE, 'w') as f:
        json.dump(variables, f, indent=2)


def show_variable_manager_page():
    render_gradient_header(
        title="Variable Manager",
        subtitle="Manage macroeconomic variables and custom indicators",
        icon="📊"
    )

    render_info_box(
        "💡 <strong>Variable Manager</strong> memungkinkan Anda menambah, mengedit, atau menonaktifkan "
        "variabel makroekonomi yang digunakan dalam analisis dan proyeksi.",
        box_type="info"
    )

    # Load variables
    if 'variables_config' not in st.session_state:
        st.session_state.variables_config = load_variables()

    variables = st.session_state.variables_config

    # Tabs
    tabs = st.tabs([
        "📋 Active Variables",
        "➕ Add New Variable",
        "✏️ Edit Variables",
        "📊 Variable Statistics",
        "💾 Manage Configuration"
    ])

    # TAB 1: Active Variables
    with tabs[0]:
        create_header_with_icon("Active Variables Overview", "📋")

        # Filter active variables
        active_vars = {k: v for k, v in variables.items() if v.get('active', True)}

        if not active_vars:
            st.warning("⚠️ No active variables found!")
            return

        # Display as table
        var_data = []
        for var_name, var_info in active_vars.items():
            var_data.append({
                'Variable': var_name,
                'Full Name': var_info['full_name'],
                'Unit': var_info['unit'],
                'Category': var_info['category'],
                'Range': f"{var_info['expected_range'][0]} - {var_info['expected_range'][1]}",
                'Type': 'Custom' if var_info.get('custom', False) else 'Built-in'
            })

        df_vars = pd.DataFrame(var_data)
        st.dataframe(df_vars, use_container_width=True, hide_index=True)

        # Categories breakdown
        st.markdown("---")
        st.subheader("Variables by Category")

        categories = {}
        for var_info in active_vars.values():
            cat = var_info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(var_info['name'])

        cols = st.columns(len(categories))
        for idx, (cat, vars_list) in enumerate(categories.items()):
            with cols[idx]:
                st.markdown(f"**{cat}**")
                for var in vars_list:
                    st.markdown(f"- {var}")

    # TAB 2: Add New Variable
    with tabs[1]:
        create_header_with_icon("Add Custom Variable", "➕")

        st.markdown("""
        <div class="info-box">
        Tambahkan variabel makroekonomi custom yang relevan dengan daerah Anda.
        Contoh: Jumlah Kendaraan, Tingkat Urbanisasi, PDRB Per Kapita, dll.
        </div>
        """, unsafe_allow_html=True)

        with st.form("add_variable"):
            col1, col2 = st.columns(2)

            with col1:
                var_name = st.text_input(
                    "Variable Name (Short)",
                    placeholder="e.g., PDRB_Kapita",
                    help="Nama singkat untuk kolom data"
                )

                full_name = st.text_input(
                    "Full Name",
                    placeholder="e.g., PDRB Per Kapita",
                    help="Nama lengkap variabel"
                )

                description = st.text_area(
                    "Description",
                    placeholder="Describe what this variable measures",
                    help="Deskripsi detail variabel"
                )

            with col2:
                unit = st.text_input(
                    "Unit of Measurement",
                    placeholder="e.g., Rupiah, %, index",
                    help="Satuan pengukuran"
                )

                category = st.selectbox(
                    "Category",
                    options=[
                        'Economic Growth',
                        'Social Indicators',
                        'Labor Market',
                        'Monetary',
                        'Infrastructure',
                        'Demographics',
                        'Custom'
                    ]
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    min_range = st.number_input(
                        "Expected Min Value",
                        value=0.0,
                        step=0.1,
                        format="%.2f"
                    )
                with col_b:
                    max_range = st.number_input(
                        "Expected Max Value",
                        value=100.0,
                        step=0.1,
                        format="%.2f"
                    )

            # Data source
            st.subheader("Initial Data (Optional)")
            st.caption("You can add historical values for this variable")

            data_source = st.radio(
                "How would you like to add data?",
                options=["Manual Entry", "Upload CSV", "Skip for now"],
                horizontal=True
            )

            initial_data = None
            if data_source == "Manual Entry":
                st.text("Enter comma-separated values (one per year, 2018-2024)")
                data_input = st.text_input(
                    "Values",
                    placeholder="5.2, 5.5, 5.8, 6.0, 6.2, 6.5, 6.8"
                )
                if data_input:
                    try:
                        initial_data = [float(x.strip()) for x in data_input.split(',')]
                    except:
                        st.error("❌ Invalid format! Use comma-separated numbers.")

            elif data_source == "Upload CSV":
                uploaded_file = st.file_uploader(
                    "Upload CSV with 'Tahun' and variable column",
                    type=['csv']
                )
                if uploaded_file:
                    try:
                        df_upload = pd.read_csv(uploaded_file)
                        st.dataframe(df_upload.head())
                        # Extract data
                    except Exception as e:
                        st.error(f"❌ Error reading file: {e}")

            submitted = st.form_submit_button("➕ Add Variable", type="primary")

            if submitted:
                if not var_name or not full_name:
                    st.error("❌ Variable name and full name are required!")
                elif var_name in variables:
                    st.error(f"❌ Variable '{var_name}' already exists!")
                else:
                    # Add new variable
                    variables[var_name] = {
                        'name': var_name,
                        'full_name': full_name,
                        'description': description,
                        'unit': unit,
                        'category': category,
                        'expected_range': [min_range, max_range],
                        'active': True,
                        'custom': True
                    }

                    st.session_state.variables_config = variables
                    st.success(f"✅ Variable '{var_name}' added successfully!")
                    st.info("💾 Don't forget to save configuration in 'Manage Configuration' tab")

                    # If initial data provided, show instruction
                    if initial_data:
                        st.warning(f"⚠️ Next step: Add data values to datasets using Data Editor page")

    # TAB 3: Edit Variables
    with tabs[2]:
        create_header_with_icon("Edit Variable Configuration", "✏️")

        var_to_edit = st.selectbox(
            "Select Variable to Edit",
            options=list(variables.keys())
        )

        if var_to_edit:
            var_info = variables[var_to_edit]

            with st.form("edit_variable"):
                st.subheader(f"Editing: {var_to_edit}")

                col1, col2 = st.columns(2)

                with col1:
                    new_full_name = st.text_input(
                        "Full Name",
                        value=var_info['full_name']
                    )

                    new_description = st.text_area(
                        "Description",
                        value=var_info['description']
                    )

                    new_unit = st.text_input(
                        "Unit",
                        value=var_info['unit']
                    )

                with col2:
                    new_category = st.selectbox(
                        "Category",
                        options=[
                            'Economic Growth',
                            'Social Indicators',
                            'Labor Market',
                            'Monetary',
                            'Infrastructure',
                            'Demographics',
                            'Custom'
                        ],
                        index=0
                    )

                    col_a, col_b = st.columns(2)
                    with col_a:
                        new_min = st.number_input(
                            "Min Range",
                            value=float(var_info['expected_range'][0])
                        )
                    with col_b:
                        new_max = st.number_input(
                            "Max Range",
                            value=float(var_info['expected_range'][1])
                        )

                    new_active = st.checkbox(
                        "Active",
                        value=var_info.get('active', True),
                        help="Uncheck to deactivate this variable"
                    )

                col1, col2 = st.columns(2)

                with col1:
                    update_btn = st.form_submit_button("💾 Update Variable", type="primary")

                with col2:
                    if var_info.get('custom', False):
                        delete_btn = st.form_submit_button("🗑️ Delete Variable")
                    else:
                        delete_btn = False
                        st.caption("Built-in variables cannot be deleted")

                if update_btn:
                    variables[var_to_edit].update({
                        'full_name': new_full_name,
                        'description': new_description,
                        'unit': new_unit,
                        'category': new_category,
                        'expected_range': [new_min, new_max],
                        'active': new_active
                    })
                    st.session_state.variables_config = variables
                    st.success(f"✅ Variable '{var_to_edit}' updated!")

                if delete_btn:
                    if st.checkbox(f"Confirm delete '{var_to_edit}'?"):
                        del variables[var_to_edit]
                        st.session_state.variables_config = variables
                        st.success(f"✅ Variable '{var_to_edit}' deleted!")
                        st.rerun()

    # TAB 4: Variable Statistics
    with tabs[3]:
        create_header_with_icon("Variable Statistics", "📊")

        st.subheader("Configuration Summary")

        total_vars = len(variables)
        active_vars_count = sum(1 for v in variables.values() if v.get('active', True))
        custom_vars_count = sum(1 for v in variables.values() if v.get('custom', False))

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Variables", total_vars)

        with col2:
            st.metric("Active Variables", active_vars_count)

        with col3:
            st.metric("Custom Variables", custom_vars_count)

        # Category distribution
        st.markdown("---")
        st.subheader("Distribution by Category")

        category_counts = {}
        for var_info in variables.values():
            cat = var_info['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1

        df_cats = pd.DataFrame({
            'Category': list(category_counts.keys()),
            'Count': list(category_counts.values())
        })

        st.bar_chart(df_cats.set_index('Category'))

    # TAB 5: Manage Configuration
    with tabs[4]:
        create_header_with_icon("Save & Manage Configuration", "💾")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save Configuration", type="primary", use_container_width=True):
                save_variables(variables)
                st.success("✅ Variable configuration saved!")
                st.balloons()

        with col2:
            if st.button("🔄 Reset to Default", use_container_width=True):
                if st.checkbox("Confirm reset?"):
                    variables = get_default_variables()
                    save_variables(variables)
                    st.session_state.variables_config = variables
                    st.success("✅ Reset to default variables!")
                    st.rerun()

        with col3:
            var_json = json.dumps(variables, indent=2)
            st.download_button(
                label="📥 Export Config",
                data=var_json,
                file_name="variables_config.json",
                mime="application/json",
                use_container_width=True
            )

        st.markdown("---")
        st.subheader("Import Configuration")

        uploaded_file = st.file_uploader("Upload variables JSON", type=['json'])
        if uploaded_file is not None:
            try:
                imported_vars = json.load(uploaded_file)
                st.write("Preview:")
                st.json(imported_vars)

                if st.button("Apply Imported Configuration"):
                    save_variables(imported_vars)
                    st.session_state.variables_config = imported_vars
                    st.success("✅ Configuration imported successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error importing configuration: {e}")

        st.markdown("---")
        st.subheader("Current Configuration")
        st.json(variables)


def app():
    show_variable_manager_page()


if __name__ == "__main__":
    app()
