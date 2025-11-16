"""
Projection API endpoints
Handles forecasting and projections
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_loader import load_pad_historis

router = APIRouter()


class ProjectionRequest(BaseModel):
    response_var: str
    predictor_vars: Optional[List[str]] = None
    forecast_years: int = 5
    forecast_data: Optional[Dict[str, List[float]]] = None
    model_type: str = "ensemble"  # ols, arima, exp_smoothing, ensemble
    include_confidence_intervals: bool = True


class ScenarioRequest(BaseModel):
    response_var: str
    predictor_vars: List[str]
    base_forecast_data: Dict[str, List[float]]
    forecast_years: int = 5
    scenario_adjustments: Optional[Dict[str, float]] = None  # percentage adjustments


def calculate_growth_rate(series):
    """Calculate average growth rate from historical data"""
    if len(series) < 2:
        return 0.05  # Default 5% growth

    # Calculate year-over-year growth rates
    growth_rates = []
    for i in range(1, len(series)):
        if series[i-1] != 0:
            rate = (series[i] - series[i-1]) / series[i-1]
            growth_rates.append(rate)

    if not growth_rates:
        return 0.05

    # Return median growth rate (more robust than mean)
    return np.median(growth_rates)


def generate_forecast_data(df, predictor_vars, years):
    """Generate forecast data for predictors based on historical trends"""
    forecast_data = {}

    for var in predictor_vars:
        if var in df.columns:
            # Calculate growth rate
            growth_rate = calculate_growth_rate(df[var].values)

            # Generate forecast based on last value and growth rate
            last_value = df[var].iloc[-1]
            forecast_values = []

            for i in range(1, years + 1):
                forecast_value = last_value * ((1 + growth_rate) ** i)
                forecast_values.append(float(forecast_value))

            forecast_data[var] = forecast_values

    return forecast_data


@router.post("/generate")
async def generate_projection(request: ProjectionRequest):
    """Generate PAD projections using specified model"""
    try:
        # Load data
        df = load_pad_historis()

        # Validate response variable
        if request.response_var not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Response variable '{request.response_var}' not found"
            )

        # Get historical data for context
        historical = {
            "years": df['Tahun'].tolist(),
            "values": df[request.response_var].tolist()
        }

        # Generate forecast based on model type
        if request.model_type == "ols":
            if not request.predictor_vars:
                raise HTTPException(
                    status_code=400,
                    detail="OLS model requires predictor_vars"
                )

            # Generate forecast data if not provided
            if not request.forecast_data:
                request.forecast_data = generate_forecast_data(
                    df, request.predictor_vars, request.forecast_years
                )

            # Prepare data
            y = df[request.response_var]
            X = df[request.predictor_vars]
            X = sm.add_constant(X)

            # Fit model
            model = sm.OLS(y, X).fit()

            # Generate forecast
            forecast_df = pd.DataFrame(request.forecast_data)
            forecast_X = sm.add_constant(forecast_df[request.predictor_vars])
            predictions = model.predict(forecast_X)

            # Get confidence intervals
            if request.include_confidence_intervals:
                prediction_results = model.get_prediction(forecast_X)
                pred_summary = prediction_results.summary_frame(alpha=0.05)
                lower_ci = pred_summary['obs_ci_lower'].tolist()
                upper_ci = pred_summary['obs_ci_upper'].tolist()
            else:
                lower_ci = None
                upper_ci = None

            forecast = {
                "years": list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_years)),
                "predictions": predictions.tolist(),
                "lower_ci": lower_ci,
                "upper_ci": upper_ci,
                "model_params": {k: float(v) for k, v in model.params.items()},
                "r_squared": float(model.rsquared)
            }

        elif request.model_type == "arima":
            # Fit ARIMA model
            y = df[request.response_var]
            model = ARIMA(y, order=(1, 1, 1))
            fitted_model = model.fit()

            # Generate forecast
            forecast_obj = fitted_model.forecast(steps=request.forecast_years)

            if request.include_confidence_intervals:
                forecast_ci = fitted_model.get_forecast(steps=request.forecast_years).conf_int()
                lower_ci = forecast_ci.iloc[:, 0].tolist()
                upper_ci = forecast_ci.iloc[:, 1].tolist()
            else:
                lower_ci = None
                upper_ci = None

            forecast = {
                "years": list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_years)),
                "predictions": forecast_obj.tolist(),
                "lower_ci": lower_ci,
                "upper_ci": upper_ci,
                "aic": float(fitted_model.aic),
                "bic": float(fitted_model.bic)
            }

        elif request.model_type == "exp_smoothing":
            # Fit Exponential Smoothing
            y = df[request.response_var]
            model = ExponentialSmoothing(y, trend="add")
            fitted_model = model.fit()

            # Generate forecast
            forecast_obj = fitted_model.forecast(steps=request.forecast_years)

            if request.include_confidence_intervals:
                # Simulate for confidence intervals
                simulations = fitted_model.simulate(
                    nsimulations=request.forecast_years,
                    repetitions=1000,
                    random_errors='bootstrap'
                )
                lower_ci = np.percentile(simulations, 2.5, axis=1).tolist()
                upper_ci = np.percentile(simulations, 97.5, axis=1).tolist()
            else:
                lower_ci = None
                upper_ci = None

            forecast = {
                "years": list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_years)),
                "predictions": forecast_obj.tolist(),
                "lower_ci": lower_ci,
                "upper_ci": upper_ci
            }

        elif request.model_type == "ensemble":
            # Combine multiple models
            results = []

            # ARIMA
            y = df[request.response_var]
            arima_model = ARIMA(y, order=(1, 1, 1)).fit()
            arima_forecast = arima_model.forecast(steps=request.forecast_years)
            results.append(arima_forecast)

            # Exp Smoothing
            exp_model = ExponentialSmoothing(y, trend="add").fit()
            exp_forecast = exp_model.forecast(steps=request.forecast_years)
            results.append(exp_forecast)

            # OLS (if predictor vars provided)
            if request.predictor_vars:
                if not request.forecast_data:
                    request.forecast_data = generate_forecast_data(
                        df, request.predictor_vars, request.forecast_years
                    )

                X = df[request.predictor_vars]
                X = sm.add_constant(X)
                ols_model = sm.OLS(y, X).fit()
                forecast_df = pd.DataFrame(request.forecast_data)
                forecast_X = sm.add_constant(forecast_df[request.predictor_vars])
                ols_forecast = ols_model.predict(forecast_X)
                results.append(ols_forecast)
                weights = [0.3, 0.3, 0.4]  # ARIMA, Exp, OLS
            else:
                weights = [0.5, 0.5]  # ARIMA, Exp only

            # Weighted average
            ensemble_forecast = np.average(results, axis=0, weights=weights)

            # Calculate ensemble confidence intervals
            if request.include_confidence_intervals:
                # Use std of individual models as uncertainty measure
                std = np.std(results, axis=0)
                lower_ci = (ensemble_forecast - 1.96 * std).tolist()
                upper_ci = (ensemble_forecast + 1.96 * std).tolist()
            else:
                lower_ci = None
                upper_ci = None

            forecast = {
                "years": list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_years)),
                "predictions": ensemble_forecast.tolist(),
                "lower_ci": lower_ci,
                "upper_ci": upper_ci,
                "weights": {
                    "arima": weights[0],
                    "exp_smoothing": weights[1],
                    "ols": weights[2] if len(weights) > 2 else 0
                }
            }

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid model_type: {request.model_type}"
            )

        return {
            "success": True,
            "model_type": request.model_type,
            "response_var": request.response_var,
            "historical": historical,
            "forecast": forecast
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Projection Error: {str(e)}")


@router.post("/scenarios")
async def get_scenario_analysis(request: ScenarioRequest):
    """Get scenario analysis (optimistic, moderate, pessimistic)"""
    try:
        # Load data
        df = load_pad_historis()

        # Validate inputs
        if request.response_var not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Response variable '{request.response_var}' not found"
            )

        for var in request.predictor_vars:
            if var not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Predictor variable '{var}' not found"
                )

        # Fit OLS model
        y = df[request.response_var]
        X = df[request.predictor_vars]
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit()

        # Define scenario adjustments (percentage changes)
        scenarios = {
            "pessimistic": -0.10,  # -10%
            "moderate": 0.0,       # 0% (base case)
            "optimistic": 0.10     # +10%
        }

        # Override with custom adjustments if provided
        if request.scenario_adjustments:
            scenarios.update(request.scenario_adjustments)

        results = {}

        for scenario_name, adjustment in scenarios.items():
            # Adjust forecast data
            adjusted_data = {}
            for var, values in request.base_forecast_data.items():
                adjusted_values = [v * (1 + adjustment) for v in values]
                adjusted_data[var] = adjusted_values

            # Generate forecast
            forecast_df = pd.DataFrame(adjusted_data)
            forecast_X = sm.add_constant(forecast_df[request.predictor_vars])
            predictions = model.predict(forecast_X)

            # Get confidence intervals
            prediction_results = model.get_prediction(forecast_X)
            pred_summary = prediction_results.summary_frame(alpha=0.05)

            results[scenario_name] = {
                "predictions": predictions.tolist(),
                "lower_ci": pred_summary['obs_ci_lower'].tolist(),
                "upper_ci": pred_summary['obs_ci_upper'].tolist(),
                "adjustment": adjustment,
                "total": float(sum(predictions))
            }

        years = list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_years))

        return {
            "success": True,
            "response_var": request.response_var,
            "years": years,
            "scenarios": results,
            "base_forecast_data": request.base_forecast_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario Analysis Error: {str(e)}")


@router.post("/confidence-intervals")
async def get_confidence_intervals(data: Dict[str, Any]):
    """Calculate confidence intervals for projections"""
    try:
        response_var = data.get("response_var")
        predictor_vars = data.get("predictor_vars", [])
        forecast_data = data.get("forecast_data", {})
        confidence_level = data.get("confidence_level", 0.95)

        if not response_var:
            raise HTTPException(status_code=400, detail="response_var is required")

        # Load data
        df = load_pad_historis()

        # Validate
        if response_var not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Response variable '{response_var}' not found"
            )

        # Calculate alpha from confidence level
        alpha = 1 - confidence_level

        if predictor_vars and forecast_data:
            # OLS-based confidence intervals
            y = df[response_var]
            X = df[predictor_vars]
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()

            forecast_df = pd.DataFrame(forecast_data)
            forecast_X = sm.add_constant(forecast_df[predictor_vars])

            # Get prediction with intervals
            prediction_results = model.get_prediction(forecast_X)
            pred_summary = prediction_results.summary_frame(alpha=alpha)

            result = {
                "predictions": model.predict(forecast_X).tolist(),
                "lower_ci": pred_summary['obs_ci_lower'].tolist(),
                "upper_ci": pred_summary['obs_ci_upper'].tolist(),
                "confidence_level": confidence_level,
                "method": "OLS prediction intervals"
            }
        else:
            # ARIMA-based confidence intervals
            y = df[response_var]
            model = ARIMA(y, order=(1, 1, 1))
            fitted_model = model.fit()

            forecast_steps = data.get("forecast_steps", 5)
            forecast_result = fitted_model.get_forecast(steps=forecast_steps)
            pred_summary = forecast_result.summary_frame(alpha=alpha)

            result = {
                "predictions": pred_summary['mean'].tolist(),
                "lower_ci": pred_summary['mean_ci_lower'].tolist(),
                "upper_ci": pred_summary['mean_ci_upper'].tolist(),
                "confidence_level": confidence_level,
                "method": "ARIMA forecast intervals"
            }

        return {
            "success": True,
            "response_var": response_var,
            "confidence_intervals": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Confidence Interval Error: {str(e)}")
