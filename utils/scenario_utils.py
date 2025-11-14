"""
Utilities for calculating data-driven scenario bounds
Based on historical volatility and statistical distributions
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Tuple, Dict


def calculate_historical_volatility(series: pd.Series, method: str = 'returns') -> float:
    """
    Calculate historical volatility of a time series

    Args:
        series: Time series data
        method: 'returns' for % change volatility, 'absolute' for absolute values

    Returns:
        float: Volatility (standard deviation)
    """
    if method == 'returns':
        # Calculate percentage returns
        returns = series.pct_change().dropna()
        return returns.std()
    else:
        # Absolute volatility
        return series.std()


def calculate_scenario_bounds_volatility(
    df: pd.DataFrame,
    response: str,
    prediction: float,
    num_std: float = 1.0
) -> Tuple[float, float, float]:
    """
    Calculate scenario bounds based on historical volatility

    Args:
        df: Historical data
        response: Response variable (PKB/BBNKB)
        prediction: Base prediction value
        num_std: Number of standard deviations for bounds (default: 1.0)

    Returns:
        tuple: (optimistic, moderate, pessimistic)
    """
    # Calculate historical volatility
    volatility = calculate_historical_volatility(df[response], method='returns')

    # Bounds based on volatility
    optimistic = prediction * (1 + num_std * volatility)  # Upper bound
    moderate = prediction
    pessimistic = prediction * (1 - num_std * volatility)  # Lower bound

    return optimistic, moderate, pessimistic


def calculate_scenario_bounds_ci(
    model,
    X_pred: np.ndarray,
    alpha: float = 0.32  # 68% CI (1 std dev equivalent)
) -> Tuple[float, float, float]:
    """
    Calculate scenario bounds based on confidence intervals

    Args:
        model: Fitted OLS model
        X_pred: Prediction input
        alpha: Significance level (0.32 for 68% CI, 0.05 for 95% CI)

    Returns:
        tuple: (optimistic, moderate, pessimistic)
    """
    # Get prediction with CI
    pred_summary = model.get_prediction(X_pred)
    pred_mean = pred_summary.predicted_mean[0]
    ci = pred_summary.conf_int(alpha=alpha)[0]

    return ci[1], pred_mean, ci[0]  # upper, mean, lower


def calculate_scenario_bounds_percentile(
    df: pd.DataFrame,
    response: str,
    prediction: float,
    percentiles: Tuple[float, float] = (16, 84)  # ~1 std dev for normal dist
) -> Tuple[float, float, float]:
    """
    Calculate scenario bounds based on historical percentiles

    Args:
        df: Historical data
        response: Response variable
        prediction: Base prediction
        percentiles: (lower_percentile, upper_percentile)

    Returns:
        tuple: (optimistic, moderate, pessimistic)
    """
    # Calculate historical growth rates
    growth_rates = df[response].pct_change().dropna()

    # Get percentiles
    lower_pct = np.percentile(growth_rates, percentiles[0])
    upper_pct = np.percentile(growth_rates, percentiles[1])

    # Apply to prediction
    pessimistic = prediction * (1 + lower_pct)
    moderate = prediction
    optimistic = prediction * (1 + upper_pct)

    return optimistic, moderate, pessimistic


def calculate_ensemble_scenario_bounds(
    df: pd.DataFrame,
    model,
    response: str,
    X_pred: np.ndarray,
    prediction: float,
    method: str = 'average'
) -> Dict[str, Tuple[float, float, float]]:
    """
    Calculate scenario bounds using multiple methods and combine

    Args:
        df: Historical data
        model: Fitted OLS model
        response: Response variable
        X_pred: Prediction input
        prediction: Base prediction
        method: 'average', 'conservative', or 'aggressive'

    Returns:
        dict: Scenarios with bounds from different methods
    """
    # Method 1: Volatility-based
    vol_opt, vol_mod, vol_pes = calculate_scenario_bounds_volatility(df, response, prediction, num_std=1.0)

    # Method 2: CI-based
    ci_opt, ci_mod, ci_pes = calculate_scenario_bounds_ci(model, X_pred, alpha=0.32)

    # Method 3: Percentile-based
    pct_opt, pct_mod, pct_pes = calculate_scenario_bounds_percentile(df, response, prediction)

    results = {
        'volatility': (vol_opt, vol_mod, vol_pes),
        'confidence_interval': (ci_opt, ci_mod, ci_pes),
        'percentile': (pct_opt, pct_mod, pct_pes)
    }

    # Ensemble (average)
    if method == 'average':
        ensemble_opt = np.mean([vol_opt, ci_opt, pct_opt])
        ensemble_mod = prediction
        ensemble_pes = np.mean([vol_pes, ci_pes, pct_pes])
        results['ensemble'] = (ensemble_opt, ensemble_mod, ensemble_pes)
    elif method == 'conservative':
        # Use widest bounds
        ensemble_opt = max(vol_opt, ci_opt, pct_opt)
        ensemble_mod = prediction
        ensemble_pes = min(vol_pes, ci_pes, pct_pes)
        results['ensemble'] = (ensemble_opt, ensemble_mod, ensemble_pes)
    elif method == 'aggressive':
        # Use narrowest bounds
        ensemble_opt = min(vol_opt, ci_opt, pct_opt)
        ensemble_mod = prediction
        ensemble_pes = max(vol_pes, ci_pes, pct_pes)
        results['ensemble'] = (ensemble_opt, ensemble_mod, ensemble_pes)

    return results


def format_scenario_comparison(scenarios: Dict[str, Tuple[float, float, float]]) -> pd.DataFrame:
    """
    Format scenario results for display

    Args:
        scenarios: Dict of scenario bounds from different methods

    Returns:
        DataFrame: Formatted comparison table
    """
    data = []
    for method, (opt, mod, pes) in scenarios.items():
        data.append({
            'Method': method.replace('_', ' ').title(),
            'Optimistic': f"Rp {opt/1e9:.2f}T",
            'Moderate': f"Rp {mod/1e9:.2f}T",
            'Pessimistic': f"Rp {pes/1e9:.2f}T",
            'Range (%)': f"±{((opt-pes)/(2*mod)*100):.1f}%"
        })

    return pd.DataFrame(data)


def explain_scenario_method(method: str) -> str:
    """Return explanation for each scenario calculation method"""
    explanations = {
        'volatility': """
        **Volatility-Based Scenarios**
        - Menggunakan standar deviasi dari historical returns (% perubahan tahun-ke-tahun)
        - Optimistic = Prediction × (1 + 1σ)
        - Pessimistic = Prediction × (1 - 1σ)
        - Cocok untuk: Data dengan pola volatilitas konsisten
        """,
        'confidence_interval': """
        **Confidence Interval-Based Scenarios**
        - Menggunakan 68% CI dari model regresi (≈1 standar error)
        - Bounds dihitung dari prediction interval model statistik
        - Memperhitungkan uncertainty dalam parameter model
        - Cocok untuk: Memahami ketidakpastian model
        """,
        'percentile': """
        **Percentile-Based Scenarios**
        - Menggunakan historical percentiles (16th & 84th) dari growth rates
        - Equivalent dengan ±1σ untuk distribusi normal
        - Berdasarkan distribusi empiris, bukan asumsi normalitas
        - Cocok untuk: Data dengan distribusi non-normal
        """,
        'ensemble': """
        **Ensemble (Average) Scenarios**
        - Rata-rata dari 3 metode di atas
        - Mengurangi bias dari single method
        - Lebih robust terhadap outliers
        - **Recommended**: Metode paling balanced
        """
    }
    return explanations.get(method, "No explanation available")
