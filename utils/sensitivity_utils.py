"""
Utilities for automated sensitivity analysis
Shows how projections change with variations in predictor variables
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Dict, List, Tuple
import plotly.graph_objects as go

from utils.ui_components import apply_plotly_theme
from utils.ui_theme_utils import format_rupiah_compact


def calculate_sensitivity_single_var(
    df: pd.DataFrame,
    response: str,
    predictor: str,
    base_value: float,
    variation_pct: float = 0.1
) -> Dict[str, float]:
    """
    Calculate sensitivity for a single predictor variable

    Args:
        df: Historical data
        response: Response variable (PKB/BBNKB)
        predictor: Predictor variable name
        base_value: Base value of the predictor
        variation_pct: Percentage variation (default: 0.1 for ±10%)

    Returns:
        dict: Sensitivity results
    """
    # Prepare data
    X = df[[predictor]].values
    y = df[response].values

    # Add constant manually
    X_with_const = np.column_stack([np.ones(len(X)), X])

    # Run regression with numpy arrays
    model = sm.OLS(y, X_with_const).fit()

    # Base prediction using numpy array
    base_pred = model.predict(np.array([[1, base_value]]))[0]

    # Variation values
    lower_value = base_value * (1 - variation_pct)
    upper_value = base_value * (1 + variation_pct)

    # Predictions with variations using numpy arrays
    lower_pred = model.predict(np.array([[1, lower_value]]))[0]
    upper_pred = model.predict(np.array([[1, upper_value]]))[0]

    # Calculate impacts
    lower_impact = lower_pred - base_pred
    upper_impact = upper_pred - base_pred

    # Elasticity: % change in response / % change in predictor
    elasticity = ((upper_pred - lower_pred) / base_pred) / (2 * variation_pct)

    return {
        'predictor': predictor,
        'base_value': base_value,
        'base_prediction': base_pred,
        'lower_value': lower_value,
        'lower_prediction': lower_pred,
        'lower_impact': lower_impact,
        'upper_value': upper_value,
        'upper_prediction': upper_pred,
        'upper_impact': upper_impact,
        'total_range': upper_pred - lower_pred,
        'elasticity': elasticity,
        'coefficient': model.params[1]  # Second parameter is the predictor coefficient
    }


def calculate_sensitivity_all_vars(
    df: pd.DataFrame,
    response: str,
    predictors: List[str],
    base_values: Dict[str, float],
    variation_pct: float = 0.1
) -> pd.DataFrame:
    """
    Calculate sensitivity for all predictor variables

    Args:
        df: Historical data
        response: Response variable
        predictors: List of predictor names
        base_values: Dict of base values for each predictor
        variation_pct: Percentage variation

    Returns:
        DataFrame: Sensitivity results for all variables
    """
    results = []

    for predictor in predictors:
        sensitivity = calculate_sensitivity_single_var(
            df, response, predictor, base_values[predictor], variation_pct
        )
        results.append(sensitivity)

    # Create DataFrame
    sens_df = pd.DataFrame(results)

    # Sort by absolute total range (most impactful first)
    sens_df['abs_range'] = sens_df['total_range'].abs()
    sens_df = sens_df.sort_values('abs_range', ascending=False)
    sens_df = sens_df.drop(columns=['abs_range'])

    return sens_df


def create_tornado_chart(sens_df: pd.DataFrame, response: str, variation_pct: float = 0.1) -> go.Figure:
    """
    Create a tornado chart showing sensitivity analysis results

    Args:
        sens_df: Sensitivity DataFrame from calculate_sensitivity_all_vars
        response: Response variable name
        variation_pct: Percentage variation used

    Returns:
        Plotly Figure: Tornado chart
    """
    # Sort by absolute impact
    sens_df = sens_df.copy()
    sens_df['abs_range'] = sens_df['total_range'].abs()
    sens_df = sens_df.sort_values('abs_range', ascending=True)  # Ascending for horizontal bars

    fig = go.Figure()

    # Base prediction (middle line)
    base_pred = sens_df['base_prediction'].iloc[0]

    # Add bars for each variable
    for idx, row in sens_df.iterrows():
        predictor = row['predictor']
        lower_impact = row['lower_impact']
        upper_impact = row['upper_impact']

        # Negative impact (left side)
        fig.add_trace(go.Bar(
            y=[predictor],
            x=[lower_impact],
            orientation='h',
            name=f"{predictor} (-{variation_pct*100:.0f}%)",
            marker_color='#ef4444',
            text=format_rupiah_compact(lower_impact, signed=True),
            textposition='auto',
            hovertemplate=f"<b>{predictor}</b><br>" +
                         f"Perubahan: -{variation_pct*100:.0f}%<br>" +
                         f"Dampak: Rp {lower_impact:,.0f}<br>" +
                         f"Proyeksi: Rp {row['lower_prediction']:,.0f}<extra></extra>",
            showlegend=False
        ))

        # Positive impact (right side)
        fig.add_trace(go.Bar(
            y=[predictor],
            x=[upper_impact],
            orientation='h',
            name=f"{predictor} (+{variation_pct*100:.0f}%)",
            marker_color='#10b981',
            text=format_rupiah_compact(upper_impact, signed=True),
            textposition='auto',
            hovertemplate=f"<b>{predictor}</b><br>" +
                         f"Perubahan: +{variation_pct*100:.0f}%<br>" +
                         f"Dampak: Rp {upper_impact:,.0f}<br>" +
                         f"Proyeksi: Rp {row['upper_prediction']:,.0f}<extra></extra>",
            showlegend=False
        ))

    # Add adaptive vertical line at x=0 (readable in Light & Dark modes)
    fig.add_vline(x=0, line_width=2, line_color="rgba(148, 163, 184, 0.65)")

    apply_plotly_theme(
        fig,
        title=f"<b>Tornado Chart: Sensitivitas {response}</b><br><sup>Dampak perubahan ±{variation_pct*100:.0f}% pada setiap variabel prediktor</sup>",
        height=max(440, len(sens_df) * 62),
        xaxis_title=f"Dampak terhadap {response} (Rupiah)",
        yaxis_title="Variabel Prediktor",
        show_legend=False,
        margin=dict(l=130, r=48, t=76, b=60),
    )
    fig.update_layout(
        barmode='overlay',
        hovermode='y unified',
        xaxis=dict(
            tickformat=",.0f",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(148, 163, 184, 0.65)'
        ),
        yaxis=dict(tickfont=dict(size=12))
    )

    return fig


def create_elasticity_chart(sens_df: pd.DataFrame, response: str) -> go.Figure:
    """
    Create bar chart showing elasticity coefficients
    """
    # Sort by absolute elasticity
    sens_df = sens_df.copy()
    sens_df['abs_elasticity'] = sens_df['elasticity'].abs()
    sens_df = sens_df.sort_values('abs_elasticity', ascending=False)

    # Color based on positive/negative
    colors = ['#10b981' if x > 0 else '#ef4444' for x in sens_df['elasticity']]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=sens_df['predictor'],
        y=sens_df['elasticity'],
        marker_color=colors,
        text=[f"{x:.3f}" for x in sens_df['elasticity']],
        textposition='outside',
        cliponaxis=False,
        hovertemplate='<b>%{x}</b><br>Elastisitas: %{y:.3f}<extra></extra>'
    ))

    apply_plotly_theme(
        fig,
        title=f"<b>Koefisien Elastisitas: {response} terhadap Variabel Makro</b><br><sup>|e| > 1 = elastis (sensitif), |e| < 1 = inelastis</sup>",
        height=440,
        xaxis_title="Variabel Prediktor",
        yaxis_title="Koefisien Elastisitas",
        show_legend=False,
        margin=dict(l=68, r=36, t=78, b=88),
    )
    fig.update_layout(
        yaxis=dict(
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='rgba(148, 163, 184, 0.65)',
            tickformat=".2f"
        ),
        xaxis=dict(
            tickangle=-25,
            tickfont=dict(size=12)
        ),
        hovermode='x',
    )

    return fig


def interpret_sensitivity(sens_df: pd.DataFrame) -> Dict[str, str]:
    """
    Provide interpretation of sensitivity analysis results
    """
    most_impact = sens_df.iloc[0]
    least_impact = sens_df.iloc[-1]
    high_elasticity = sens_df[sens_df['elasticity'].abs() > 1]
    low_elasticity = sens_df[sens_df['elasticity'].abs() < 0.5]

    interpretation = {
        'most_impactful': f"**{most_impact['predictor']}** memiliki dampak terbesar dengan rentang {format_rupiah_compact(most_impact['total_range'])} untuk perubahan ±10%.",
        'least_impactful': f"**{least_impact['predictor']}** memiliki dampak terkecil dengan rentang {format_rupiah_compact(least_impact['total_range'])} untuk perubahan ±10%.",
        'high_elasticity': f"Variabel elastisitas tinggi (|e| > 1): {', '.join(high_elasticity['predictor'].tolist()) if len(high_elasticity) > 0 else 'Tidak ada'}",
        'low_elasticity': f"Variabel elastisitas rendah (|e| < 0.5): {', '.join(low_elasticity['predictor'].tolist()) if len(low_elasticity) > 0 else 'Tidak ada'}"
    }

    return interpretation


def format_sensitivity_table(sens_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format sensitivity DataFrame for display
    """
    display_df = sens_df.copy()

    display_df['Variabel'] = display_df['predictor']
    display_df['Nilai Base'] = display_df['base_value'].apply(lambda x: f"{x:.2f}")
    display_df['Proyeksi Base'] = display_df['base_prediction'].apply(lambda x: format_rupiah_compact(x))
    display_df['Dampak (-10%)'] = display_df['lower_impact'].apply(lambda x: format_rupiah_compact(x, signed=True))
    display_df['Dampak (+10%)'] = display_df['upper_impact'].apply(lambda x: format_rupiah_compact(x, signed=True))
    display_df['Rentang Total'] = display_df['total_range'].apply(lambda x: format_rupiah_compact(abs(x)))
    display_df['Elastisitas'] = display_df['elasticity'].apply(lambda x: f"{x:.3f}")

    return display_df[['Variabel', 'Nilai Base', 'Proyeksi Base',
                       'Dampak (-10%)', 'Dampak (+10%)', 'Rentang Total', 'Elastisitas']]
