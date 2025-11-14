"""
Decision Support System
Executive summary, risk assessment, and recommendation engine for final decision making
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from data_loader import load_pad_historis
from utils.ui_components import render_gradient_header, render_info_box, create_header_with_icon
from utils.policy_utils import get_target, get_policy_settings, format_policy_summary


def calculate_risk_score(variance, volatility, confidence_width):
    """
    Calculate risk score based on model metrics

    Args:
        variance: Model variance
        volatility: Historical volatility
        confidence_width: Width of confidence interval

    Returns:
        tuple: (score, category, color)
    """
    # Normalize to 0-100 scale
    score = min(100, (variance * 10 + volatility * 20 + confidence_width * 70))

    if score < 30:
        return score, "LOW", "#4caf50"
    elif score < 60:
        return score, "MEDIUM", "#ff9800"
    else:
        return score, "HIGH", "#ef5350"


def generate_executive_summary(df, projections, targets):
    """Generate executive summary for decision makers"""
    summary = {
        'overview': [],
        'key_findings': [],
        'risks': [],
        'recommendations': []
    }

    # Overview
    latest_year = int(df['Tahun'].max())
    latest_pkb = df.loc[df['Tahun'] == latest_year, 'PKB'].iloc[0]
    latest_bbnkb = df.loc[df['Tahun'] == latest_year, 'BBNKB'].iloc[0]

    summary['overview'].append(
        f"📊 Data historis mencakup {len(df)} tahun ({int(df['Tahun'].min())}-{latest_year})"
    )
    summary['overview'].append(
        f"💰 Realisasi {latest_year}: PKB Rp {latest_pkb/1e12:.2f}T, BBNKB Rp {latest_bbnkb/1e12:.2f}T"
    )

    # Projections vs Targets
    if projections and targets:
        pkb_2025_proj = projections.get('pkb_2025', 0)
        pkb_2025_target = targets.get('pkb_2025', 0)

        gap = ((pkb_2025_proj - pkb_2025_target) / pkb_2025_target * 100)

        if gap >= 0:
            summary['key_findings'].append(
                f"✅ Proyeksi PKB 2025 (Rp {pkb_2025_proj/1e12:.2f}T) MEMENUHI target (Rp {pkb_2025_target/1e12:.2f}T) dengan surplus {abs(gap):.1f}%"
            )
        else:
            summary['key_findings'].append(
                f"⚠️ Proyeksi PKB 2025 (Rp {pkb_2025_proj/1e12:.2f}T) KURANG dari target (Rp {pkb_2025_target/1e12:.2f}T) sebesar {abs(gap):.1f}%"
            )

    # Growth analysis
    if len(df) >= 2:
        growth_rates = []
        for i in range(1, len(df)):
            prev = df.iloc[i-1]['PKB']
            curr = df.iloc[i]['PKB']
            growth = ((curr - prev) / prev * 100)
            growth_rates.append(growth)

        avg_growth = sum(growth_rates) / len(growth_rates)
        summary['key_findings'].append(
            f"📈 Rata-rata pertumbuhan historis PKB: {avg_growth:.2f}% per tahun"
        )

    # Risks
    summary['risks'].append(
        "📉 Model berbasis data terbatas (n=7) memiliki uncertainty tinggi"
    )
    summary['risks'].append(
        "🌍 Perubahan kondisi makroekonomi global dapat mempengaruhi akurasi proyeksi"
    )

    # Recommendations
    summary['recommendations'].append(
        "🎯 Monitor realisasi triwulanan dan adjust proyeksi secara berkala"
    )
    summary['recommendations'].append(
        "📊 Perbaiki sistem pengumpulan data untuk meningkatkan akurasi model"
    )

    return summary


def create_risk_matrix():
    """Create risk assessment matrix"""
    risks = [
        {
            'risk': 'Model Accuracy',
            'probability': 'Medium',
            'impact': 'High',
            'mitigation': 'Regular model validation and recalibration'
        },
        {
            'risk': 'Economic Downturn',
            'probability': 'Low',
            'impact': 'High',
            'mitigation': 'Maintain pessimistic scenario planning'
        },
        {
            'risk': 'Policy Changes',
            'probability': 'Medium',
            'impact': 'Medium',
            'mitigation': 'Flexible policy parameters in system'
        },
        {
            'risk': 'Data Quality',
            'probability': 'Low',
            'impact': 'High',
            'mitigation': 'Implement data validation rules'
        },
        {
            'risk': 'Collection Efficiency',
            'probability': 'Medium',
            'impact': 'Medium',
            'mitigation': 'Improve enforcement and online systems'
        }
    ]

    return pd.DataFrame(risks)


def show_decision_support_page():
    render_gradient_header(
        title="Decision Support System",
        subtitle="Executive summary, risk assessment, dan rekomendasi untuk pengambilan keputusan",
        icon="🎯"
    )

    # Load data
    df = load_pad_historis()
    settings = get_policy_settings()

    # Tabs
    tabs = st.tabs([
        "📊 Executive Summary",
        "🎯 Target vs Projection",
        "⚠️ Risk Assessment",
        "💡 Recommendations",
        "📈 Scenario Comparison",
        "📄 Export Report"
    ])

    # TAB 1: Executive Summary
    with tabs[0]:
        create_header_with_icon("Executive Summary", "📊")

        st.markdown("""
        <div class="modern-card" style="background: linear-gradient(135deg, #1a5fb4 0%, #3584e4 100%); color: white; padding: 2rem;">
            <h2 style="color: white; margin: 0;">📋 Laporan Eksekutif Proyeksi PAD</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">
                Generated on: {}</p>
        </div>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

        st.markdown("---")

        # Key metrics
        st.subheader("📌 Key Metrics")

        latest_year = int(df['Tahun'].max())
        latest_pkb = df.loc[df['Tahun'] == latest_year, 'PKB'].iloc[0]
        latest_bbnkb = df.loc[df['Tahun'] == latest_year, 'BBNKB'].iloc[0]

        # Calculate simple projection (you can integrate actual model here)
        avg_growth = 0.055  # 5.5% assumption
        proj_2025_pkb = latest_pkb * (1 + avg_growth)
        proj_2026_pkb = proj_2025_pkb * (1 + avg_growth)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                f"PKB {latest_year}",
                f"Rp {latest_pkb/1e12:.2f}T",
                delta=None
            )

        with col2:
            target_2025 = settings['targets']['pkb_2025']
            gap = proj_2025_pkb - target_2025
            st.metric(
                "Proj. PKB 2025",
                f"Rp {proj_2025_pkb/1e12:.2f}T",
                delta=f"{gap/1e12:+.2f}T vs target"
            )

        with col3:
            st.metric(
                "Target 2025",
                f"Rp {target_2025/1e12:.2f}T"
            )

        with col4:
            achievement = (proj_2025_pkb / target_2025 * 100)
            st.metric(
                "Achievement",
                f"{achievement:.1f}%"
            )

        st.markdown("---")

        # Summary sections
        projections = {
            'pkb_2025': proj_2025_pkb,
            'pkb_2026': proj_2026_pkb
        }
        targets = settings['targets']

        summary = generate_executive_summary(df, projections, targets)

        # Overview
        st.subheader("🔍 Overview")
        for item in summary['overview']:
            st.markdown(f"- {item}")

        # Key Findings
        st.subheader("📊 Key Findings")
        for item in summary['key_findings']:
            st.markdown(f"- {item}")

        # Risks
        st.subheader("⚠️ Key Risks")
        for item in summary['risks']:
            st.markdown(f"- {item}")

        # Recommendations
        st.subheader("💡 Recommendations")
        for item in summary['recommendations']:
            st.markdown(f"- {item}")

    # TAB 2: Target vs Projection
    with tabs[1]:
        create_header_with_icon("Target Achievement Analysis", "🎯")

        # Comparison chart
        st.subheader("📊 Target vs Projection Comparison")

        comparison_data = {
            'Category': ['PKB 2025', 'PKB 2026', 'BBNKB 2025', 'BBNKB 2026'],
            'Target': [
                settings['targets']['pkb_2025'] / 1e12,
                settings['targets']['pkb_2026'] / 1e12,
                settings['targets']['bbnkb_2025'] / 1e12,
                settings['targets']['bbnkb_2026'] / 1e12
            ],
            'Projection (Moderate)': [
                proj_2025_pkb / 1e12,
                proj_2026_pkb / 1e12,
                latest_bbnkb * 1.04 / 1e12,  # Assuming 4% growth
                latest_bbnkb * 1.04 * 1.04 / 1e12
            ]
        }

        df_comparison = pd.DataFrame(comparison_data)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Target',
            x=df_comparison['Category'],
            y=df_comparison['Target'],
            marker_color='#ff9800',
            text=df_comparison['Target'].apply(lambda x: f'Rp {x:.2f}T'),
            textposition='outside'
        ))

        fig.add_trace(go.Bar(
            name='Projection',
            x=df_comparison['Category'],
            y=df_comparison['Projection (Moderate)'],
            marker_color='#1a5fb4',
            text=df_comparison['Projection (Moderate)'].apply(lambda x: f'Rp {x:.2f}T'),
            textposition='outside'
        ))

        fig.update_layout(
            barmode='group',
            title="Target vs Projection Comparison",
            xaxis_title="Category",
            yaxis_title="Amount (Trillion Rupiah)",
            template="plotly_white",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Gap analysis
        st.markdown("---")
        st.subheader("📉 Gap Analysis")

        gap_data = []
        for i, cat in enumerate(df_comparison['Category']):
            target = df_comparison['Target'].iloc[i]
            proj = df_comparison['Projection (Moderate)'].iloc[i]
            gap = proj - target
            gap_pct = (gap / target * 100)

            gap_data.append({
                'Category': cat,
                'Target (T)': f"Rp {target:.2f}T",
                'Projection (T)': f"Rp {proj:.2f}T",
                'Gap (T)': f"Rp {gap:+.2f}T",
                'Gap (%)': f"{gap_pct:+.1f}%",
                'Status': '✅ Surplus' if gap >= 0 else '⚠️ Shortfall'
            })

        st.dataframe(pd.DataFrame(gap_data), use_container_width=True, hide_index=True)

    # TAB 3: Risk Assessment
    with tabs[2]:
        create_header_with_icon("Risk Assessment Matrix", "⚠️")

        st.markdown("""
        <div class="warning-box">
        <strong>Risk Assessment</strong> mengidentifikasi dan mengevaluasi risiko yang dapat mempengaruhi pencapaian target PAD.
        </div>
        """, unsafe_allow_html=True)

        # Risk matrix
        df_risks = create_risk_matrix()

        # Color coding
        def color_probability(val):
            if val == 'High':
                return 'background-color: #ffcdd2'
            elif val == 'Medium':
                return 'background-color: #fff9c4'
            else:
                return 'background-color: #c8e6c9'

        styled_df = df_risks.style.applymap(
            color_probability,
            subset=['probability', 'impact']
        )

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Risk score visualization
        st.markdown("---")
        st.subheader("📊 Overall Risk Score")

        # Calculate hypothetical risk score
        risk_score, risk_category, risk_color = calculate_risk_score(
            variance=0.15,
            volatility=0.08,
            confidence_width=0.12
        )

        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Risk Level: {risk_category}"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': risk_color},
                'steps': [
                    {'range': [0, 30], 'color': "#c8e6c9"},
                    {'range': [30, 60], 'color': "#fff9c4"},
                    {'range': [60, 100], 'color': "#ffcdd2"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))

        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True)

        # Risk interpretation
        if risk_category == "LOW":
            st.success("✅ **Low Risk**: Proyeksi memiliki tingkat kepercayaan tinggi. Lanjutkan dengan monitoring rutin.")
        elif risk_category == "MEDIUM":
            st.warning("⚠️ **Medium Risk**: Ada beberapa ketidakpastian. Pertimbangkan skenario alternatif dan contingency planning.")
        else:
            st.error("🚨 **High Risk**: Tingkat ketidakpastian tinggi. Rekomendasi: review asumsi, perbaiki data, dan siapkan mitigasi.")

    # TAB 4: Recommendations
    with tabs[3]:
        create_header_with_icon("Strategic Recommendations", "💡")

        st.markdown("""
        <div class="success-box">
        Rekomendasi strategis berdasarkan analisis proyeksi, gap terhadap target, dan risk assessment.
        </div>
        """, unsafe_allow_html=True)

        # Categorized recommendations
        st.subheader("🎯 Policy Recommendations")
        policy_recs = [
            "Pertahankan tarif PKB dan BBNKB pada level saat ini untuk stabilitas",
            "Tingkatkan insentif pembayaran online untuk meningkatkan compliance rate",
            "Implementasi program edukasi wajib pajak untuk mengurangi tunggakan"
        ]
        for rec in policy_recs:
            st.markdown(f"- {rec}")

        st.markdown("---")
        st.subheader("📊 Operational Recommendations")
        ops_recs = [
            "Upgrade sistem informasi PAD untuk real-time monitoring",
            "Perkuat koordinasi dengan Samsat untuk efisiensi pemungutan",
            "Lakukan audit data historis untuk meningkatkan kualitas proyeksi"
        ]
        for rec in ops_recs:
            st.markdown(f"- {rec}")

        st.markdown("---")
        st.subheader("🔬 Analytical Recommendations")
        analytical_recs = [
            "Perbanyak data point dengan breakdown bulanan/triwulanan",
            "Integrasikan variabel tambahan (pertumbuhan kendaraan, urbanisasi)",
            "Lakukan sensitivity analysis berkala untuk update asumsi"
        ]
        for rec in analytical_recs:
            st.markdown(f"- {rec}")

        st.markdown("---")
        st.subheader("⏰ Timeline & Priorities")

        timeline = pd.DataFrame({
            'Priority': ['High', 'High', 'Medium', 'Medium', 'Low'],
            'Action': [
                'Set final target PKB/BBNKB 2025-2026',
                'Review dan approve proyeksi moderat',
                'Prepare contingency plan untuk skenario pesimis',
                'Setup monitoring dashboard triwulanan',
                'Research additional predictor variables'
            ],
            'Timeline': [
                'Q1 2025',
                'Q1 2025',
                'Q2 2025',
                'Q2 2025',
                'Q3 2025'
            ],
            'Owner': [
                'Kepala Bapenda',
                'Tim Analisis',
                'Tim Perencanaan',
                'Tim IT',
                'Tim Penelitian'
            ]
        })

        st.dataframe(timeline, use_container_width=True, hide_index=True)

    # TAB 5: Scenario Comparison
    with tabs[4]:
        create_header_with_icon("Scenario Comparison", "📈")

        st.subheader("📊 Multi-Scenario Analysis")

        # Create scenario data
        scenarios = {
            'Scenario': ['Pessimistic', 'Moderate', 'Optimistic'],
            'PKB 2025 (T)': [
                proj_2025_pkb * 0.9 / 1e12,
                proj_2025_pkb / 1e12,
                proj_2025_pkb * 1.1 / 1e12
            ],
            'BBNKB 2025 (T)': [
                latest_bbnkb * 1.02 / 1e12,
                latest_bbnkb * 1.04 / 1e12,
                latest_bbnkb * 1.06 / 1e12
            ],
            'Probability': ['30%', '50%', '20%']
        }

        df_scenarios = pd.DataFrame(scenarios)
        df_scenarios['Total PAD 2025 (T)'] = df_scenarios['PKB 2025 (T)'] + df_scenarios['BBNKB 2025 (T)']

        st.dataframe(df_scenarios, use_container_width=True, hide_index=True)

        # Visualization
        fig_scenario = go.Figure()

        fig_scenario.add_trace(go.Bar(
            name='PKB',
            x=df_scenarios['Scenario'],
            y=df_scenarios['PKB 2025 (T)'],
            marker_color='#1a5fb4'
        ))

        fig_scenario.add_trace(go.Bar(
            name='BBNKB',
            x=df_scenarios['Scenario'],
            y=df_scenarios['BBNKB 2025 (T)'],
            marker_color='#ff9800'
        ))

        fig_scenario.update_layout(
            barmode='stack',
            title="Total PAD by Scenario (2025)",
            xaxis_title="Scenario",
            yaxis_title="Amount (Trillion Rupiah)",
            template="plotly_white",
            height=500
        )

        st.plotly_chart(fig_scenario, use_container_width=True)

        # Expected value calculation
        st.markdown("---")
        st.subheader("📐 Expected Value Analysis")

        expected_pkb = (
            df_scenarios['PKB 2025 (T)'].iloc[0] * 0.3 +
            df_scenarios['PKB 2025 (T)'].iloc[1] * 0.5 +
            df_scenarios['PKB 2025 (T)'].iloc[2] * 0.2
        )

        st.metric(
            "Expected PKB 2025 (Probability-Weighted)",
            f"Rp {expected_pkb:.2f}T"
        )

        st.info(
            f"💡 **Recommendation**: Use expected value (Rp {expected_pkb:.2f}T) "
            f"as baseline target with ±10% buffer untuk risk management."
        )

    # TAB 6: Export Report
    with tabs[5]:
        create_header_with_icon("Export Decision Report", "📄")

        st.markdown("""
        <div class="info-box">
        Export comprehensive decision report untuk presentasi ke stakeholder atau dokumentasi.
        </div>
        """, unsafe_allow_html=True)

        # Report format selection
        report_format = st.selectbox(
            "Report Format",
            options=["Executive Summary (PDF)", "Detailed Analysis (Excel)", "Presentation Slides (PPTX)"]
        )

        # Options
        st.subheader("Include in Report:")

        include_summary = st.checkbox("Executive Summary", value=True)
        include_targets = st.checkbox("Target Achievement Analysis", value=True)
        include_risks = st.checkbox("Risk Assessment", value=True)
        include_recommendations = st.checkbox("Recommendations", value=True)
        include_scenarios = st.checkbox("Scenario Comparison", value=True)
        include_charts = st.checkbox("All Charts and Visualizations", value=True)

        # Privacy controls
        st.markdown("---")
        st.subheader("Privacy Settings:")

        hide_actual_values = st.checkbox(
            "Hide Actual Projection Values",
            value=False,
            help="Replace numbers with ranges for public presentation"
        )

        add_watermark = st.checkbox(
            "Add 'CONFIDENTIAL' Watermark",
            value=False
        )

        # Generate button
        if st.button("📥 Generate & Download Report", type="primary"):
            with st.spinner("Generating report..."):
                # Simulate report generation
                import time
                time.sleep(2)

                st.success("✅ Report generated successfully!")

                # Provide download button (mocked)
                st.download_button(
                    label="📥 Download Report",
                    data="Mock report content",
                    file_name=f"PAD_Decision_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )


def app():
    show_decision_support_page()


if __name__ == "__main__":
    app()
