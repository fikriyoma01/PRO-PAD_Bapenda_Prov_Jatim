"""
Model validation utilities for PAD dashboard
Includes RMSE, MAPE, MAE, and backtesting functionality
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
import statsmodels.api as sm


def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Root Mean Squared Error

    Args:
        y_true: Actual values
        y_pred: Predicted values

    Returns:
        float: RMSE value
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Percentage Error

    Args:
        y_true: Actual values
        y_pred: Predicted values

    Returns:
        float: MAPE value as percentage
    """
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error

    Args:
        y_true: Actual values
        y_pred: Predicted values

    Returns:
        float: MAE value
    """
    return np.mean(np.abs(y_true - y_pred))


def calculate_r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate R² Score

    Args:
        y_true: Actual values
        y_pred: Predicted values

    Returns:
        float: R² score
    """
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)


def calculate_all_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Calculate all validation metrics

    Args:
        y_true: Actual values
        y_pred: Predicted values

    Returns:
        dict: Dictionary containing all metrics
    """
    return {
        'RMSE': calculate_rmse(y_true, y_pred),
        'MAE': calculate_mae(y_true, y_pred),
        'MAPE (%)': calculate_mape(y_true, y_pred),
        'R²': calculate_r2_score(y_true, y_pred)
    }


def leave_one_out_cross_validation(df: pd.DataFrame, response: str, predictor: str) -> Dict[str, any]:
    """
    Perform Leave-One-Out Cross Validation (LOOCV)

    Args:
        df: DataFrame with historical data
        response: Response variable name
        predictor: Predictor variable name

    Returns:
        dict: CV results including predictions and metrics
    """
    n = len(df)
    predictions = []
    actuals = []

    for i in range(n):
        # Split data: leave one out
        train_mask = df.index != i
        train_df = df[train_mask]
        test_df = df[~train_mask]

        # Train model
        X_train = sm.add_constant(train_df[[predictor]])
        y_train = train_df[response]
        model = sm.OLS(y_train, X_train).fit()

        # Predict
        X_test = sm.add_constant(test_df[[predictor]])
        y_pred = model.predict(X_test)[0]  # model.predict returns numpy array, not pandas Series
        y_true = test_df[response].values[0]

        predictions.append(y_pred)
        actuals.append(y_true)

    predictions = np.array(predictions)
    actuals = np.array(actuals)

    # Calculate metrics
    metrics = calculate_all_metrics(actuals, predictions)

    return {
        'predictions': predictions,
        'actuals': actuals,
        'metrics': metrics,
        'cv_type': 'Leave-One-Out'
    }


def backtest_model(df: pd.DataFrame, response: str, predictor: str, test_years: int = 2) -> Dict[str, any]:
    """
    Backtest model by training on historical data and testing on recent years

    Args:
        df: DataFrame with historical data
        response: Response variable name
        predictor: Predictor variable name
        test_years: Number of years to use for testing

    Returns:
        dict: Backtest results
    """
    # Sort by year
    df_sorted = df.sort_values('Tahun').reset_index(drop=True)

    # Split data
    train_size = len(df_sorted) - test_years
    train_df = df_sorted.iloc[:train_size]
    test_df = df_sorted.iloc[train_size:]

    # Train model
    X_train = sm.add_constant(train_df[[predictor]])
    y_train = train_df[response]
    model = sm.OLS(y_train, X_train).fit()

    # Predict on test set
    X_test = sm.add_constant(test_df[[predictor]])
    y_pred = model.predict(X_test)  # Returns numpy array
    y_true = test_df[response]

    # Calculate metrics
    metrics = calculate_all_metrics(y_true.values, y_pred)  # y_pred is already numpy array

    return {
        'train_years': train_df['Tahun'].tolist(),
        'test_years': test_df['Tahun'].tolist(),
        'y_train': y_train.values,
        'y_test': y_true.values,
        'y_pred': y_pred,  # Already a numpy array
        'metrics': metrics,
        'model_params': {
            'intercept': model.params['const'],
            'coefficient': model.params[predictor],
            'r2': model.rsquared,
            'p_value': model.pvalues[predictor]
        }
    }


def interpret_mape(mape: float) -> Tuple[str, str]:
    """
    Interpret MAPE value

    Args:
        mape: MAPE value in percentage

    Returns:
        tuple: (category, description)
    """
    if mape < 10:
        return ("Sangat Baik", "Prediksi sangat akurat")
    elif mape < 20:
        return ("Baik", "Prediksi cukup akurat")
    elif mape < 50:
        return ("Cukup", "Prediksi memiliki error moderat")
    else:
        return ("Kurang", "Prediksi memiliki error besar")


def interpret_r2(r2: float) -> Tuple[str, str]:
    """
    Interpret R² value

    Args:
        r2: R² value (0-1)

    Returns:
        tuple: (category, description)
    """
    if r2 > 0.9:
        return ("Sangat Kuat", "Model menjelaskan >90% variasi data")
    elif r2 > 0.7:
        return ("Kuat", "Model menjelaskan 70-90% variasi data")
    elif r2 > 0.5:
        return ("Sedang", "Model menjelaskan 50-70% variasi data")
    elif r2 > 0.3:
        return ("Lemah", "Model menjelaskan 30-50% variasi data")
    else:
        return ("Sangat Lemah", "Model menjelaskan <30% variasi data")
