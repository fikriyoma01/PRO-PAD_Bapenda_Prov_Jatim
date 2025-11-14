"""
Interactive Scenario Builder - What-If Analysis Tool
Allows users to manually adjust macroeconomic variables and see real-time impact on PAD projections
"""

import streamlit as st
import pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go
from data_loader import load_pad_historis
from utils.audit_utils import log_scenario_save


def local_css():
    st.markdown(
        """
        <style>
            .scenario-header {
                background: linear-gradient(90deg, #6a1b9a, #8e24aa);
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            .scenario-header h1 {
                color: white;
                margin: 0;
                font-size: 2.2rem;
            }
            .scenario-header p {
                color: #f1f1f1;
                margin: 0;
                font-size: 1.05rem;
            }
            .scenario-card {
                background: white;
                border-left: 5px solid #8e24aa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def run_regression(df, response, predictor):
    """Run OLS regression"""
    X = sm.add_constant(df[[predictor]])
    y = df[response]
    return sm.OLS(y, X).fit()


def predict_macro_linear(df, var, year):
    """Predict macro variable using linear trend"""
    X = sm.add_constant(df[["Tahun"]])
    y = df[var]
    model = sm.OLS(y, X).fit()
    return float(model.predict([1, year])[0])


def calculate_projection(df, response, macro_vars, macro_values, year):
    """
    Calculate projection for given macro variable values

    Args:
        df: Historical data
        response: PKB or BBNKB
        macro_vars: List of macro variable names
        macro_values: Dict of macro variable values
        year: Year to project

    Returns:
        dict: Projection results
    """
    impacts = {}
    total_impact = 0

    # Get baseline (2024)
    baseline = {var: float(df.iloc[-1][var]) for var in macro_vars}

    for var in macro_vars:
        # Run regression
        model = run_regression(df, response, var)
        beta = model.params[var]

        # Calculate impact
        delta = macro_values[var] - baseline[var]
        impact = beta * delta

        impacts[var] = {
            'baseline': baseline[var],
            'scenario': macro_values[var],
            'delta': delta,
            'beta': beta,
            'impact': impact
        }
        total_impact += impact

    # Base prediction (using historical trend)
    X = sm.add_constant(df[["Tahun"]])
    y = df[response]
    base_model = sm.OLS(y, X).fit()
    base_prediction = base_model.predict([1, year])[0]

    # Final projection
    final_projection = base_prediction + total_impact

    return {
        'base_prediction': base_prediction,
        'total_impact': total_impact,
        'final_projection': final_projection,
        'impacts': impacts
    }


def show_scenario_builder():
    local_css()

    # Header
    st.markdown(
        """
        <div class="scenario-header">
            <h1>🎯 Interactive Scenario Builder</h1>
            <p>Atur variabel makroekonomi secara manual dan lihat dampaknya terhadap proyeksi PAD secara real-time</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load data
    df = load_pad_historis()

    # Macro variables
    macro_vars = ["PDRB", "Rasio Gini", "IPM", "TPT", "Kemiskinan", "Inflasi", "Suku Bunga"]

    # Instructions
    with st.expander("ℹ️ Cara Menggunakan Scenario Builder", expanded=False):
        st.markdown("""
        ### 📚 Panduan Penggunaan

        1. **Pilih Tahun**: Pilih tahun proyeksi (2025 atau 2026)
        2. **Pilih Variabel Respon**: PKB atau BBNKB
        3. **Atur Nilai Makro**: Gunakan slider untuk mengatur nilai setiap variabel makroekonomi
        4. **Lihat Hasil**: Proyeksi akan ter-update secara real-time
        5. **Bandingkan**: Bandingkan dengan baseline dan skenario lain

        ### 💡 Tips
        - Nilai default adalah proyeksi linear berdasarkan trend historis
        - Anda dapat reset ke baseline dengan klik tombol "Reset to Baseline"
        - Dampak individual setiap variabel ditampilkan di tabel
        - Skenario dapat di-save untuk perbandingan
        """)

    # Configuration
    st.markdown("---")
    st.subheader("⚙️ Konfigurasi Skenario")

    col1, col2, col3 = st.columns(3)

    with col1:
        year = st.selectbox("Tahun Proyeksi", [2025, 2026], key='scenario_year')

    with col2:
        response = st.selectbox("Variabel Respon", ["PKB", "BBNKB"], key='scenario_response')

    with col3:
        scenario_name = st.text_input("Nama Skenario", value=f"Scenario_{year}", key='scenario_name')

    # Get baseline values (linear trend predictions)
    st.markdown("---")
    st.subheader("🎛️ Atur Nilai Variabel Makroekonomi")

    st.markdown(f"""
    **Baseline**: Proyeksi linear berdasarkan trend 2018-2024
    **Skenario Anda**: Atur nilai sesuai asumsi Anda
    """)

    # Initialize macro values
    if 'macro_values' not in st.session_state:
        st.session_state.macro_values = {}

    macro_values = {}

    # Create sliders for each macro variable
    cols = st.columns(2)

    for idx, var in enumerate(macro_vars):
        col = cols[idx % 2]

        with col:
            # Get baseline prediction
            baseline_val = predict_macro_linear(df, var, year)

            # Get historical range
            hist_min = df[var].min()
            hist_max = df[var].max()
            hist_range = hist_max - hist_min

            # Set slider range (±50% from baseline)
            slider_min = max(hist_min - hist_range * 0.5, baseline_val * 0.5)
            slider_max = min(hist_max + hist_range * 0.5, baseline_val * 1.5)

            # Slider
            value = st.slider(
                f"**{var}**",
                min_value=float(slider_min),
                max_value=float(slider_max),
                value=float(baseline_val),
                step=0.01,
                key=f"slider_{var}",
                help=f"Baseline (trend): {baseline_val:.2f} | Range historis: {hist_min:.2f} - {hist_max:.2f}"
            )

            macro_values[var] = value

            # Show difference from baseline
            diff = value - baseline_val
            diff_pct = (diff / baseline_val * 100) if baseline_val != 0 else 0

            if abs(diff) < 0.01:
                st.caption(f"✅ Sama dengan baseline: {baseline_val:.2f}")
            elif diff > 0:
                st.caption(f"📈 +{diff:.2f} (+{diff_pct:.1f}%) dari baseline {baseline_val:.2f}")
            else:
                st.caption(f"📉 {diff:.2f} ({diff_pct:.1f}%) dari baseline {baseline_val:.2f}")

    # Reset button
    if st.button("🔄 Reset to Baseline"):
        st.rerun()

    # Calculate projection
    st.markdown("---")
    st.header("📊 Hasil Proyeksi")

    results = calculate_projection(df, response, macro_vars, macro_values, year)

    # Display main results
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Base Prediction (Trend)",
            value=f"Rp {results['base_prediction']/1e9:.2f}T",
            help="Proyeksi berdasarkan trend tahun tanpa adjustment makro"
        )

    with col2:
        st.metric(
            label="Total Macro Impact",
            value=f"Rp {results['total_impact']/1e9:.2f}T",
            delta=f"{results['total_impact']/results['base_prediction']*100:.1f}%",
            help="Total dampak dari perubahan variabel makroekonomi"
        )

    with col3:
        st.metric(
            label=f"Final Projection {response} {year}",
            value=f"Rp {results['final_projection']/1e9:.2f}T",
            delta=f"vs Base: {(results['final_projection']-results['base_prediction'])/results['base_prediction']*100:.1f}%",
            help="Proyeksi akhir = Base + Macro Impact"
        )

    # Detailed impact breakdown
    st.markdown("---")
    st.subheader("🔍 Detail Dampak per Variabel")

    impact_data = []
    for var in macro_vars:
        impact_info = results['impacts'][var]
        impact_data.append({
            'Variabel': var,
            'Baseline (2024)': f"{impact_info['baseline']:.2f}",
            f'Skenario ({year})': f"{impact_info['scenario']:.2f}",
            'Δ Perubahan': f"{impact_info['delta']:.2f}",
            'Koefisien (β)': f"{impact_info['beta']:,.0f}",
            'Dampak (Rp)': f"Rp {impact_info['impact']/1e9:.3f}T",
            'Kontribusi (%)': f"{impact_info['impact']/results['total_impact']*100:.1f}%" if results['total_impact'] != 0 else "0.0%"
        })

    impact_df = pd.DataFrame(impact_data)
    st.dataframe(impact_df, use_container_width=True, hide_index=True)

    # Visualization - Impact breakdown
    st.markdown("---")
    st.subheader("📈 Visualisasi Dampak")

    # Create waterfall-style chart
    fig = go.Figure()

    # Sort by impact
    sorted_impacts = sorted(
        [(var, results['impacts'][var]['impact']) for var in macro_vars],
        key=lambda x: abs(x[1]),
        reverse=True
    )

    variables = [x[0] for x in sorted_impacts]
    impacts = [x[1] for x in sorted_impacts]
    colors = ['#66bb6a' if x > 0 else '#ef5350' for x in impacts]

    fig.add_trace(go.Bar(
        x=variables,
        y=impacts,
        marker_color=colors,
        text=[f"{x/1e9:.2f}T" for x in impacts],
        textposition='outside',
        hovertemplate='%{x}<br>Dampak: Rp %{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Dampak Variabel Makro terhadap {response} {year}",
        xaxis=dict(
            title="Variabel Makroekonomi",
            tickangle=-45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title="Dampak (Rupiah)",
            tickformat=",.0f",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black'
        ),
        template="plotly_white",
        height=600,
        autosize=True,
        hovermode='x',
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Scenario comparison (if multiple scenarios saved)
    st.markdown("---")
    st.subheader("💾 Save & Compare Scenarios")

    # Initialize scenario storage
    if 'saved_scenarios' not in st.session_state:
        st.session_state.saved_scenarios = []

    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("💾 Save Current Scenario"):
            scenario_data = {
                'name': scenario_name,
                'year': year,
                'response': response,
                'macro_values': macro_values.copy(),
                'projection': results['final_projection'],
                'impact': results['total_impact']
            }
            st.session_state.saved_scenarios.append(scenario_data)

            # Log to audit trail
            log_scenario_save(
                scenario_name=scenario_name,
                details={
                    'year': year,
                    'response': response,
                    'projection': float(results['final_projection']),
                    'impact': float(results['total_impact']),
                    'num_variables': len(macro_values)
                }
            )

            st.success(f"✅ Scenario '{scenario_name}' saved!")

    with col2:
        if st.button("🗑️ Clear All"):
            st.session_state.saved_scenarios = []
            st.success("✅ All scenarios cleared!")

    # Display saved scenarios
    if st.session_state.saved_scenarios:
        st.markdown("**📋 Saved Scenarios:**")

        comparison_data = []
        for scenario in st.session_state.saved_scenarios:
            comparison_data.append({
                'Scenario': scenario['name'],
                'Year': scenario['year'],
                'Response': scenario['response'],
                'Projection': f"Rp {scenario['projection']/1e9:.2f}T",
                'Macro Impact': f"Rp {scenario['impact']/1e9:.2f}T"
            })

        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        # Comparison chart
        if len(st.session_state.saved_scenarios) > 1:
            fig_comp = go.Figure()

            for scenario in st.session_state.saved_scenarios:
                fig_comp.add_trace(go.Bar(
                    name=scenario['name'],
                    x=[scenario['response']],
                    y=[scenario['projection']],
                    text=f"Rp {scenario['projection']/1e9:.2f}T",
                    textposition='outside'
                ))

            fig_comp.update_layout(
                title="Comparison: Saved Scenarios",
                yaxis=dict(
                    title="Projection (Rupiah)",
                    tickformat=",.0f"
                ),
                xaxis=dict(
                    title="Response Variable"
                ),
                template="plotly_white",
                barmode='group',
                height=550,
                autosize=True,
                hovermode='x unified',
                showlegend=True
            )

            st.plotly_chart(fig_comp, use_container_width=True)


def app():
    show_scenario_builder()


if __name__ == "__main__":
    app()
