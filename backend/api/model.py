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

    # R2 score - handle edge cases
    try:
        r2 = r2_score(actual, predicted)
        if not np.isfinite(r2):
            r2 = 0.0
    except:
        r2 = 0.0

    # MAPE - handle division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        mape = np.mean(np.abs((actual - predicted) / np.where(actual != 0, actual, 1))) * 100
        if not np.isfinite(mape):
            mape = 0.0

    # Ensure all values are JSON-serializable
    return {
        "mse": float(mse) if np.isfinite(mse) else 0.0,
        "rmse": float(rmse) if np.isfinite(rmse) else 0.0,
        "mae": float(mae) if np.isfinite(mae) else 0.0,
        "r2": float(r2) if np.isfinite(r2) else 0.0,
        "mape": float(mape) if np.isfinite(mape) else 0.0
    }


def sanitize_float(value):
    """Convert value to JSON-safe float"""
    if value is None:
        return None
    try:
        if not np.isfinite(value):
            return None
        return float(value)
    except:
        return None


@router.post("/ols")
async def run_ols_regression(request: OLSRequest):
    """Run OLS regression model with full statistics"""
    # Load data
    df = load_pad_historis()

    # Validate response variable exists
    if request.response_var not in df.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Response variable '{request.response_var}' not found in dataset. Available columns: {', '.join(df.columns)}"
        )

    # Validate predictor variables exist
    missing_vars = [var for var in request.predictor_vars if var not in df.columns]
    if missing_vars:
        raise HTTPException(
            status_code=400,
            detail=f"Predictor variable(s) not found: {', '.join(missing_vars)}. Available columns: {', '.join(df.columns)}"
        )

    # Validate degrees of freedom
    n_obs = len(df)
    n_predictors = len(request.predictor_vars) + 1  # +1 for constant
    df_resid = n_obs - n_predictors

    if df_resid <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough observations. Need at least {n_predictors + 1} observations for {len(request.predictor_vars)} predictors, but only have {n_obs}. Please reduce the number of predictor variables."
        )

    if df_resid < 2:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient degrees of freedom ({df_resid}). Please use fewer predictor variables or add more data."
        )

    try:

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

        # Return comprehensive results with sanitized values
        return {
            "success": True,
            "model": "OLS",
            "response_var": request.response_var,
            "predictor_vars": request.predictor_vars,
            "results": {
                "r_squared": sanitize_float(model.rsquared) or 0.0,
                "adj_r_squared": sanitize_float(model.rsquared_adj) or 0.0,
                "f_statistic": sanitize_float(model.fvalue) or 0.0,
                "f_pvalue": sanitize_float(model.f_pvalue) or 1.0,
                "aic": sanitize_float(model.aic) or 0.0,
                "bic": sanitize_float(model.bic) or 0.0,
                "params": {k: sanitize_float(v) or 0.0 for k, v in model.params.items()},
                "pvalues": {k: sanitize_float(v) or 1.0 for k, v in model.pvalues.items()},
                "std_errors": {k: sanitize_float(v) or 0.0 for k, v in model.bse.items()},
                "conf_int": {k: [sanitize_float(v[0]) or 0.0, sanitize_float(v[1]) or 0.0] for k, v in model.conf_int().iterrows()},
                "predictions": [sanitize_float(p) or 0.0 for p in predictions],
                "residuals": [sanitize_float(r) or 0.0 for r in model.resid],
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

        # Validate response variable exists
        if request.response_var not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Response variable '{request.response_var}' not found in dataset"
            )

        # Get time series
        y = df[request.response_var]

        # Convert order to tuple if it's a list
        order = tuple(request.order) if isinstance(request.order, list) else request.order

        # Fit ARIMA model
        model = ARIMA(y, order=order)
        fitted_model = model.fit()

        # Get fitted values
        fitted = fitted_model.fittedvalues

        # Calculate metrics on all available fitted values
        # Align y and fitted values (handle any NaN values from differencing)
        valid_idx = ~(fitted.isna() | y.isna())
        metrics = calculate_metrics(y[valid_idx], fitted[valid_idx])

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

        # Validate response variable exists
        if request.response_var not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Response variable '{request.response_var}' not found in dataset"
            )

        # Get time series
        y = df[request.response_var]

        # Validate seasonal configuration
        seasonal_periods = None
        if request.seasonal is not None and request.seasonal != 'None':
            # Default to 4 for quarterly data, can be made configurable
            seasonal_periods = 4

        # Fit Exponential Smoothing
        model = ExponentialSmoothing(
            y,
            trend=request.trend,
            seasonal=request.seasonal if request.seasonal != 'None' else None,
            seasonal_periods=seasonal_periods
        )
        fitted_model = model.fit()

        # Get fitted values
        fitted = fitted_model.fittedvalues

        # Calculate metrics
        metrics = calculate_metrics(y, fitted)

        # Forecast with simulation for confidence intervals
        forecast_result = fitted_model.forecast(steps=request.forecast_steps)

        # Simulate forecasts for confidence intervals
        simulations = fitted_model.simulate(
            nsimulations=request.forecast_steps,
            repetitions=1000,
            random_errors='bootstrap'
        )

        # Calculate confidence intervals from simulations
        lower_ci = np.percentile(simulations, 2.5, axis=1)
        upper_ci = np.percentile(simulations, 97.5, axis=1)

        return {
            "success": True,
            "model": "Exponential Smoothing",
            "response_var": request.response_var,
            "results": {
                "aic": float(fitted_model.aic) if hasattr(fitted_model, 'aic') else None,
                "bic": float(fitted_model.bic) if hasattr(fitted_model, 'bic') else None,
                "fitted_values": fitted.tolist(),
                "residuals": (y - fitted).tolist(),
                "metrics": metrics,
                "params": {
                    "smoothing_level": float(fitted_model.params['smoothing_level']) if 'smoothing_level' in fitted_model.params else None,
                    "smoothing_trend": float(fitted_model.params['smoothing_trend']) if 'smoothing_trend' in fitted_model.params else None,
                    "smoothing_seasonal": float(fitted_model.params.get('smoothing_seasonal', 0.0)) if 'smoothing_seasonal' in fitted_model.params else None
                }
            },
            "forecast": {
                "predictions": forecast_result.tolist(),
                "lower_ci": lower_ci.tolist(),
                "upper_ci": upper_ci.tolist(),
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

        # Validate response variable exists
        if request.response_var not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Response variable '{request.response_var}' not found in dataset"
            )

        # Validate predictor variables exist
        for pred_var in request.predictor_vars:
            if pred_var not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"Predictor variable '{pred_var}' not found in dataset"
                )

        # Default weights
        weights = request.weights or {"ols": 0.4, "arima": 0.3, "exp_smoothing": 0.3}

        # Validate weights
        if not all(k in weights for k in ["ols", "arima", "exp_smoothing"]):
            raise HTTPException(
                status_code=400,
                detail="Weights must include 'ols', 'arima', and 'exp_smoothing' keys"
            )

        weights_sum = sum(weights.values())
        if not (0.99 <= weights_sum <= 1.01):  # Allow small floating point errors
            raise HTTPException(
                status_code=400,
                detail=f"Weights must sum to 1.0, but sum to {weights_sum:.4f}"
            )

        # Normalize weights to ensure they sum exactly to 1.0
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}

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
            try:
                # Create train set (exclude i)
                train_idx = [j for j in range(n) if j != i]
                X_train = X.iloc[train_idx]
                y_train = y.iloc[train_idx]

                # Test set (only i)
                X_test = X.iloc[[i]]
                y_test = y.iloc[i]

                # Fit model - suppress warnings
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    model = sm.OLS(y_train, X_train).fit()

                # Predict
                pred = model.predict(X_test)
                if hasattr(pred, 'iloc'):
                    pred = pred.iloc[0]
                elif hasattr(pred, '__len__'):
                    pred = pred[0]

                cv_predictions.append(float(pred))
                cv_actual.append(float(y_test))
            except Exception as inner_e:
                # Skip this fold if there's an error
                print(f"Error in fold {i}: {type(inner_e).__name__}: {str(inner_e)}")
                import traceback
                traceback.print_exc()
                continue

        if len(cv_predictions) == 0:
            raise ValueError("No successful cross-validation folds completed")

        # Calculate CV metrics
        metrics = calculate_metrics(cv_actual, cv_predictions)

        return {
            "success": True,
            "method": "Leave-One-Out Cross-Validation",
            "n_folds": n,
            "completed_folds": len(cv_predictions),
            "metrics": metrics,
            "predictions": cv_predictions,
            "actual": cv_actual
        }
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Cross-Validation Error: {str(e)}\n{traceback.format_exc()}")


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
