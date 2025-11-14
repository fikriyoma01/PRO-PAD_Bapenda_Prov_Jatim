"""
Ensemble Models for Time Series Forecasting
Provides ARIMA and Exponential Smoothing as alternatives to OLS regression
"""

import numpy as np
import pandas as pd
import warnings
from typing import Dict, Tuple, List, Optional
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import statsmodels.api as sm

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


def fit_arima_model(
    series: pd.Series,
    order: Tuple[int, int, int] = (1, 1, 1),
    forecast_steps: int = 2
) -> Dict:
    """
    Fit ARIMA model and generate forecasts

    Args:
        series: Time series data
        order: ARIMA(p,d,q) order
        forecast_steps: Number of steps to forecast

    Returns:
        dict: Model results and forecasts
    """
    try:
        # Fit ARIMA model
        model = ARIMA(series, order=order)
        fitted_model = model.fit()

        # Generate forecasts
        forecast = fitted_model.forecast(steps=forecast_steps)
        forecast_ci = fitted_model.get_forecast(steps=forecast_steps).conf_int(alpha=0.05)

        return {
            'model': 'ARIMA',
            'order': order,
            'fitted_values': fitted_model.fittedvalues,
            'forecast': forecast.values,
            'forecast_lower': forecast_ci.iloc[:, 0].values,
            'forecast_upper': forecast_ci.iloc[:, 1].values,
            'aic': fitted_model.aic,
            'bic': fitted_model.bic,
            'residuals': fitted_model.resid,
            'success': True,
            'error': None
        }
    except Exception as e:
        return {
            'model': 'ARIMA',
            'success': False,
            'error': str(e)
        }


def fit_exponential_smoothing(
    series: pd.Series,
    seasonal: bool = False,
    seasonal_periods: Optional[int] = None,
    forecast_steps: int = 2
) -> Dict:
    """
    Fit Exponential Smoothing model and generate forecasts

    Args:
        series: Time series data
        seasonal: Whether to include seasonal component
        seasonal_periods: Number of periods in season
        forecast_steps: Number of steps to forecast

    Returns:
        dict: Model results and forecasts
    """
    try:
        # Configure model
        if seasonal and seasonal_periods:
            model = ExponentialSmoothing(
                series,
                trend='add',
                seasonal='add',
                seasonal_periods=seasonal_periods
            )
        else:
            model = ExponentialSmoothing(series, trend='add')

        # Fit model
        fitted_model = model.fit()

        # Generate forecasts
        forecast = fitted_model.forecast(steps=forecast_steps)

        # For confidence intervals, use simple percentage-based bounds
        # (ExponentialSmoothing doesn't provide native CI)
        std_error = np.std(fitted_model.resid)
        forecast_lower = forecast - 1.96 * std_error
        forecast_upper = forecast + 1.96 * std_error

        return {
            'model': 'Exponential Smoothing',
            'seasonal': seasonal,
            'fitted_values': fitted_model.fittedvalues,
            'forecast': forecast.values,
            'forecast_lower': forecast_lower.values,
            'forecast_upper': forecast_upper.values,
            'aic': fitted_model.aic,
            'residuals': fitted_model.resid,
            'success': True,
            'error': None
        }
    except Exception as e:
        return {
            'model': 'Exponential Smoothing',
            'success': False,
            'error': str(e)
        }


def fit_ols_regression(
    df: pd.DataFrame,
    response: str,
    predictor: str,
    forecast_predictor_values: List[float]
) -> Dict:
    """
    Fit OLS regression model (existing approach for comparison)

    Args:
        df: Historical data
        response: Response variable
        predictor: Predictor variable
        forecast_predictor_values: Predictor values for forecasting

    Returns:
        dict: Model results and forecasts
    """
    try:
        # Fit OLS model
        X = sm.add_constant(df[[predictor]])
        y = df[response]
        model = sm.OLS(y, X).fit()

        # Generate forecasts
        forecasts = []
        forecast_lower = []
        forecast_upper = []

        for pred_val in forecast_predictor_values:
            pred_input = np.array([[1, pred_val]])
            pred = model.predict(pred_input)[0]
            pred_summary = model.get_prediction(pred_input)
            ci = pred_summary.conf_int(alpha=0.05)[0]

            forecasts.append(pred)
            forecast_lower.append(ci[0])
            forecast_upper.append(ci[1])

        return {
            'model': 'OLS Regression',
            'predictor': predictor,
            'coefficient': model.params[predictor],
            'intercept': model.params['const'],
            'r_squared': model.rsquared,
            'p_value': model.pvalues[predictor],
            'fitted_values': model.fittedvalues,
            'forecast': np.array(forecasts),
            'forecast_lower': np.array(forecast_lower),
            'forecast_upper': np.array(forecast_upper),
            'aic': model.aic,
            'bic': model.bic,
            'residuals': model.resid,
            'success': True,
            'error': None
        }
    except Exception as e:
        return {
            'model': 'OLS Regression',
            'success': False,
            'error': str(e)
        }


def ensemble_forecast(
    df: pd.DataFrame,
    response: str,
    predictor: Optional[str] = None,
    forecast_predictor_values: Optional[List[float]] = None,
    models_to_use: List[str] = ['ols', 'arima', 'exp_smoothing'],
    arima_order: Tuple[int, int, int] = (1, 1, 1),
    forecast_steps: int = 2
) -> Dict:
    """
    Run ensemble of models and combine forecasts

    Args:
        df: Historical data
        response: Response variable
        predictor: Predictor for OLS (optional)
        forecast_predictor_values: Values for OLS forecasting (optional)
        models_to_use: List of models to include
        arima_order: ARIMA order
        forecast_steps: Number of steps to forecast

    Returns:
        dict: Combined results from all models
    """
    results = {}

    # Get response series
    series = df[response]

    # OLS Regression
    if 'ols' in models_to_use and predictor and forecast_predictor_values:
        results['ols'] = fit_ols_regression(df, response, predictor, forecast_predictor_values)

    # ARIMA
    if 'arima' in models_to_use:
        results['arima'] = fit_arima_model(series, order=arima_order, forecast_steps=forecast_steps)

    # Exponential Smoothing
    if 'exp_smoothing' in models_to_use:
        results['exp_smoothing'] = fit_exponential_smoothing(
            series, seasonal=False, forecast_steps=forecast_steps
        )

    # Calculate ensemble average (only from successful models)
    successful_models = {k: v for k, v in results.items() if v.get('success', False)}

    if len(successful_models) > 0:
        # Average forecasts
        all_forecasts = np.array([m['forecast'] for m in successful_models.values()])
        ensemble_forecast = np.mean(all_forecasts, axis=0)

        # Average bounds
        all_lower = np.array([m['forecast_lower'] for m in successful_models.values()])
        all_upper = np.array([m['forecast_upper'] for m in successful_models.values()])
        ensemble_lower = np.mean(all_lower, axis=0)
        ensemble_upper = np.mean(all_upper, axis=0)

        results['ensemble'] = {
            'model': 'Ensemble (Average)',
            'forecast': ensemble_forecast,
            'forecast_lower': ensemble_lower,
            'forecast_upper': ensemble_upper,
            'num_models': len(successful_models),
            'models_used': list(successful_models.keys()),
            'success': True
        }

    return results


def compare_models(results: Dict, actual_values: Optional[pd.Series] = None) -> pd.DataFrame:
    """
    Create comparison table of model results

    Args:
        results: Results from ensemble_forecast()
        actual_values: Optional actual values for calculating errors

    Returns:
        DataFrame: Comparison table
    """
    comparison_data = []

    for model_name, model_result in results.items():
        if not model_result.get('success', False):
            continue

        row = {
            'Model': model_result.get('model', model_name),
            'Forecast 2025': f"Rp {model_result['forecast'][0]/1e9:.2f}T",
            'Forecast 2026': f"Rp {model_result['forecast'][1]/1e9:.2f}T" if len(model_result['forecast']) > 1 else 'N/A',
        }

        # Add model-specific metrics
        if 'aic' in model_result:
            row['AIC'] = f"{model_result['aic']:.1f}"
        if 'r_squared' in model_result:
            row['R²'] = f"{model_result['r_squared']:.3f}"

        comparison_data.append(row)

    return pd.DataFrame(comparison_data)


def explain_model(model_name: str) -> str:
    """Return explanation for each model type"""
    explanations = {
        'ols': """
        **OLS Regression**
        - Memodelkan hubungan linear antara PAD dan variabel makroekonomi
        - Cocok ketika ada prediktor yang kuat
        - Membutuhkan asumsi linearitas
        - Menggunakan variabel eksogen untuk prediksi
        """,
        'arima': """
        **ARIMA (AutoRegressive Integrated Moving Average)**
        - Model time series murni (tidak butuh prediktor eksternal)
        - Menangkap pola trend dan seasonality
        - ARIMA(p,d,q): p=autoregressive, d=differencing, q=moving average
        - Cocok untuk data dengan pola temporal yang jelas
        - **Keterbatasan**: Hanya 7 data point, hasil mungkin kurang reliable
        """,
        'exp_smoothing': """
        **Exponential Smoothing**
        - Memberikan bobot lebih besar pada observasi terbaru
        - Model time series sederhana dan robust
        - Cocok untuk data dengan trend tapi tanpa seasonality kompleks
        - Lebih stabil untuk dataset kecil
        """,
        'ensemble': """
        **Ensemble (Average)**
        - Rata-rata dari semua model yang berhasil
        - Mengurangi bias dari single model
        - Lebih robust terhadap outliers
        - **Recommended** untuk uncertainty reduction
        """
    }
    return explanations.get(model_name, "No explanation available")
