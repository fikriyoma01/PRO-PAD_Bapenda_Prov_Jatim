"""
Model API endpoints
Handles statistical modeling (OLS, ARIMA, etc.)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_loader import load_pad_historis

router = APIRouter()


class OLSRequest(BaseModel):
    response_var: str
    predictor_vars: List[str]
    forecast_years: Optional[int] = 2
    forecast_data: Optional[Dict[str, List[float]]] = None


class ARIMARequest(BaseModel):
    response_var: str
    order: tuple = (1, 1, 1)
    forecast_steps: Optional[int] = 2


class ExpSmoothingRequest(BaseModel):
    response_var: str
    trend: Optional[str] = "add"
    seasonal: Optional[str] = None
    forecast_steps: Optional[int] = 2


class EnsembleRequest(BaseModel):
    response_var: str
    predictor_vars: List[str]
    forecast_years: int = 2
    forecast_data: Optional[Dict[str, List[float]]] = None
    weights: Optional[Dict[str, float]] = None


class ValidationRequest(BaseModel):
    actual: List[float]
    predicted: List[float]


def calculate_metrics(actual, predicted):
    """Calculate validation metrics"""
    actual = np.array(actual)
    predicted = np.array(predicted)

    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(actual, predicted)
    r2 = r2_score(actual, predicted)

    # MAPE
    mape = np.mean(np.abs((actual - predicted) / actual)) * 100

    return {
        "mse": float(mse),
        "rmse": float(rmse),
        "mae": float(mae),
        "r2": float(r2),
        "mape": float(mape)
    }


@router.post("/ols")
async def run_ols_regression(request: OLSRequest):
    """Run OLS regression model with full statistics"""
    try:
        # Load data
        df = load_pad_historis()

        # Prepare data
        y = df[request.response_var]
        X = df[request.predictor_vars]
        X = sm.add_constant(X)

        # Fit model
        model = sm.OLS(y, X).fit()

        # Get predictions
        predictions = model.predict(X)

        # Calculate metrics
        metrics = calculate_metrics(y, predictions)

        # Prepare forecast if forecast_data provided
        forecast = None
        if request.forecast_data and request.forecast_years > 0:
            forecast_df = pd.DataFrame(request.forecast_data)
            forecast_X = sm.add_constant(forecast_df[request.predictor_vars])
            forecast_pred = model.predict(forecast_X)

            # Calculate prediction intervals (95%)
            prediction_results = model.get_prediction(forecast_X)
            pred_summary = prediction_results.summary_frame(alpha=0.05)

            forecast = {
                "predictions": forecast_pred.tolist(),
                "lower_ci": pred_summary['obs_ci_lower'].tolist(),
                "upper_ci": pred_summary['obs_ci_upper'].tolist(),
                "years": list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_years))
            }

        # Return comprehensive results
        return {
            "success": True,
            "model": "OLS",
            "response_var": request.response_var,
            "predictor_vars": request.predictor_vars,
            "results": {
                "r_squared": float(model.rsquared),
                "adj_r_squared": float(model.rsquared_adj),
                "f_statistic": float(model.fvalue),
                "f_pvalue": float(model.f_pvalue),
                "aic": float(model.aic),
                "bic": float(model.bic),
                "params": {k: float(v) for k, v in model.params.items()},
                "pvalues": {k: float(v) for k, v in model.pvalues.items()},
                "std_errors": {k: float(v) for k, v in model.bse.items()},
                "conf_int": {k: [float(v[0]), float(v[1])] for k, v in model.conf_int().iterrows()},
                "predictions": predictions.tolist(),
                "residuals": model.resid.tolist(),
                "metrics": metrics
            },
            "forecast": forecast,
            "summary": str(model.summary())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OLS Error: {str(e)}")


@router.post("/arima")
async def run_arima(request: ARIMARequest):
    """Run ARIMA time series model"""
    try:
        # Load data
        df = load_pad_historis()

        # Get time series
        y = df[request.response_var]

        # Fit ARIMA model
        model = ARIMA(y, order=request.order)
        fitted_model = model.fit()

        # Get fitted values
        fitted = fitted_model.fittedvalues

        # Calculate metrics
        metrics = calculate_metrics(y[1:], fitted[1:])  # Skip first value due to differencing

        # Forecast
        forecast_obj = fitted_model.forecast(steps=request.forecast_steps)
        forecast_ci = fitted_model.get_forecast(steps=request.forecast_steps).conf_int()

        return {
            "success": True,
            "model": "ARIMA",
            "order": request.order,
            "response_var": request.response_var,
            "results": {
                "aic": float(fitted_model.aic),
                "bic": float(fitted_model.bic),
                "params": {k: float(v) for k, v in fitted_model.params.items()},
                "fitted_values": fitted.tolist(),
                "residuals": fitted_model.resid.tolist(),
                "metrics": metrics
            },
            "forecast": {
                "predictions": forecast_obj.tolist(),
                "lower_ci": forecast_ci.iloc[:, 0].tolist(),
                "upper_ci": forecast_ci.iloc[:, 1].tolist(),
                "years": list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_steps))
            },
            "summary": str(fitted_model.summary())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ARIMA Error: {str(e)}")


@router.post("/exp-smoothing")
async def run_exp_smoothing(request: ExpSmoothingRequest):
    """Run Exponential Smoothing model"""
    try:
        # Load data
        df = load_pad_historis()

        # Get time series
        y = df[request.response_var]

        # Fit Exponential Smoothing
        model = ExponentialSmoothing(
            y,
            trend=request.trend,
            seasonal=request.seasonal,
            seasonal_periods=None
        )
        fitted_model = model.fit()

        # Get fitted values
        fitted = fitted_model.fittedvalues

        # Calculate metrics
        metrics = calculate_metrics(y, fitted)

        # Forecast
        forecast = fitted_model.forecast(steps=request.forecast_steps)

        return {
            "success": True,
            "model": "Exponential Smoothing",
            "response_var": request.response_var,
            "results": {
                "aic": float(fitted_model.aic) if hasattr(fitted_model, 'aic') else None,
                "fitted_values": fitted.tolist(),
                "residuals": (y - fitted).tolist(),
                "metrics": metrics,
                "params": {
                    "smoothing_level": float(fitted_model.params['smoothing_level']) if 'smoothing_level' in fitted_model.params else None,
                    "smoothing_trend": float(fitted_model.params['smoothing_trend']) if 'smoothing_trend' in fitted_model.params else None
                }
            },
            "forecast": {
                "predictions": forecast.tolist(),
                "years": list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_steps))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exp Smoothing Error: {str(e)}")


@router.post("/ensemble")
async def run_ensemble(request: EnsembleRequest):
    """Run ensemble model combining OLS, ARIMA, and Exponential Smoothing"""
    try:
        # Load data
        df = load_pad_historis()

        # Default weights
        weights = request.weights or {"ols": 0.4, "arima": 0.3, "exp_smoothing": 0.3}

        # Run OLS
        ols_request = OLSRequest(
            response_var=request.response_var,
            predictor_vars=request.predictor_vars,
            forecast_years=request.forecast_years,
            forecast_data=request.forecast_data
        )
        ols_result = await run_ols_regression(ols_request)

        # Run ARIMA
        arima_request = ARIMARequest(
            response_var=request.response_var,
            order=(1, 1, 1),
            forecast_steps=request.forecast_years
        )
        arima_result = await run_arima(arima_request)

        # Run Exp Smoothing
        exp_request = ExpSmoothingRequest(
            response_var=request.response_var,
            trend="add",
            forecast_steps=request.forecast_years
        )
        exp_result = await run_exp_smoothing(exp_request)

        # Combine forecasts
        ols_forecast = ols_result["forecast"]["predictions"] if ols_result.get("forecast") else []
        arima_forecast = arima_result["forecast"]["predictions"]
        exp_forecast = exp_result["forecast"]["predictions"]

        # Weighted average
        ensemble_forecast = []
        for i in range(len(arima_forecast)):
            weighted = (
                weights["ols"] * (ols_forecast[i] if i < len(ols_forecast) else arima_forecast[i]) +
                weights["arima"] * arima_forecast[i] +
                weights["exp_smoothing"] * exp_forecast[i]
            )
            ensemble_forecast.append(weighted)

        return {
            "success": True,
            "model": "Ensemble",
            "response_var": request.response_var,
            "weights": weights,
            "individual_models": {
                "ols": ols_result,
                "arima": arima_result,
                "exp_smoothing": exp_result
            },
            "forecast": {
                "predictions": ensemble_forecast,
                "years": list(range(df['Tahun'].max() + 1, df['Tahun'].max() + 1 + request.forecast_years))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ensemble Error: {str(e)}")


@router.post("/validate")
async def validate_model(request: ValidationRequest):
    """Validate model with comprehensive metrics"""
    try:
        metrics = calculate_metrics(request.actual, request.predicted)

        # Interpretation
        interpretation = {
            "r2": "Excellent" if metrics["r2"] > 0.9 else "Good" if metrics["r2"] > 0.7 else "Fair" if metrics["r2"] > 0.5 else "Poor",
            "mape": "Excellent" if metrics["mape"] < 10 else "Good" if metrics["mape"] < 20 else "Fair" if metrics["mape"] < 30 else "Poor"
        }

        return {
            "success": True,
            "metrics": metrics,
            "interpretation": interpretation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation Error: {str(e)}")


@router.post("/cross-validate")
async def cross_validate(data: Dict[str, Any]):
    """Perform Leave-One-Out Cross-Validation"""
    try:
        # Load data
        df = load_pad_historis()

        response_var = data.get("response_var")
        predictor_vars = data.get("predictor_vars", [])

        y = df[response_var]
        X = df[predictor_vars]
        X = sm.add_constant(X)

        n = len(y)
        cv_predictions = []
        cv_actual = []

        # Leave-One-Out CV
        for i in range(n):
            # Create train set (exclude i)
            train_idx = [j for j in range(n) if j != i]
            X_train = X.iloc[train_idx]
            y_train = y.iloc[train_idx]

            # Test set (only i)
            X_test = X.iloc[[i]]
            y_test = y.iloc[i]

            # Fit model
            model = sm.OLS(y_train, X_train).fit()

            # Predict
            pred = model.predict(X_test)[0]

            cv_predictions.append(pred)
            cv_actual.append(y_test)

        # Calculate CV metrics
        metrics = calculate_metrics(cv_actual, cv_predictions)

        return {
            "success": True,
            "method": "Leave-One-Out Cross-Validation",
            "n_folds": n,
            "metrics": metrics,
            "predictions": cv_predictions,
            "actual": cv_actual
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-Validation Error: {str(e)}")


@router.post("/backtest")
async def backtest_model(data: Dict[str, Any]):
    """Backtest model using train-test split"""
    try:
        # Load data
        df = load_pad_historis()

        response_var = data.get("response_var")
        predictor_vars = data.get("predictor_vars", [])
        test_size = data.get("test_size", 2)  # Last 2 years as test

        # Split data
        n = len(df)
        train_size = n - test_size

        df_train = df.iloc[:train_size]
        df_test = df.iloc[train_size:]

        # Train model
        y_train = df_train[response_var]
        X_train = df_train[predictor_vars]
        X_train = sm.add_constant(X_train)

        model = sm.OLS(y_train, X_train).fit()

        # Test predictions
        X_test = df_test[predictor_vars]
        X_test = sm.add_constant(X_test)
        y_test = df_test[response_var]

        predictions = model.predict(X_test)

        # Calculate metrics
        metrics = calculate_metrics(y_test, predictions)

        return {
            "success": True,
            "method": "Train-Test Split Backtest",
            "train_size": train_size,
            "test_size": test_size,
            "test_years": df_test['Tahun'].tolist(),
            "metrics": metrics,
            "predictions": predictions.tolist(),
            "actual": y_test.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest Error: {str(e)}")
