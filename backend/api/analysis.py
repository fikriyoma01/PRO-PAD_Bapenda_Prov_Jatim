"""
Analysis API endpoints
Handles various analytical functions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import statsmodels.api as sm
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_loader import load_pad_historis

router = APIRouter()


class SensitivityRequest(BaseModel):
    response_var: str
    predictor_vars: List[str]
    variation_pct: Optional[float] = 10.0  # Variation percentage (default 10%)


class DecompositionRequest(BaseModel):
    revenue_type: str  # "PKB" or "BBNKB"
    year: int


@router.post("/sensitivity")
async def get_sensitivity_analysis(request: SensitivityRequest):
    """
    Perform sensitivity analysis (Tornado chart data)
    Measures impact of ±variation% change in each predictor on response variable
    """
    try:
        # Load data
        df = load_pad_historis()

        # Prepare data
        y = df[request.response_var]
        X = df[request.predictor_vars]
        X = sm.add_constant(X)

        # Fit base model
        base_model = sm.OLS(y, X).fit()
        base_prediction = base_model.predict(X).iloc[-1]  # Latest year prediction

        sensitivity_results = []

        # Calculate sensitivity for each predictor
        for var in request.predictor_vars:
            # Get latest value for this variable
            latest_value = df[var].iloc[-1]

            # Calculate variation
            variation = latest_value * (request.variation_pct / 100)

            # Positive variation
            X_pos = X.copy()
            X_pos.loc[X_pos.index[-1], var] = latest_value + variation
            pred_pos = base_model.predict(X_pos).iloc[-1]

            # Negative variation
            X_neg = X.copy()
            X_neg.loc[X_neg.index[-1], var] = latest_value - variation
            pred_neg = base_model.predict(X_neg).iloc[-1]

            # Calculate impacts
            impact_pos = pred_pos - base_prediction
            impact_neg = pred_neg - base_prediction

            # Calculate elasticity (% change in Y / % change in X)
            elasticity = ((pred_pos - pred_neg) / base_prediction) / (2 * request.variation_pct / 100)

            sensitivity_results.append({
                "variable": var,
                "base_value": float(latest_value),
                "variation_pct": request.variation_pct,
                "impact_positive": float(impact_pos),
                "impact_negative": float(impact_neg),
                "total_impact": float(abs(impact_pos) + abs(impact_neg)),
                "elasticity": float(elasticity),
                "pred_at_positive": float(pred_pos),
                "pred_at_negative": float(pred_neg)
            })

        # Sort by total impact (for Tornado chart)
        sensitivity_results.sort(key=lambda x: x["total_impact"], reverse=True)

        return {
            "success": True,
            "response_var": request.response_var,
            "base_prediction": float(base_prediction),
            "variation_pct": request.variation_pct,
            "sensitivity": sensitivity_results,
            "interpretation": {
                "most_sensitive": sensitivity_results[0]["variable"] if sensitivity_results else None,
                "least_sensitive": sensitivity_results[-1]["variable"] if sensitivity_results else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensitivity Analysis Error: {str(e)}")


@router.post("/decomposition")
async def get_decomposition(request: DecompositionRequest):
    """
    Perform revenue decomposition analysis (Waterfall chart data)
    Breaks down PAD into components
    """
    try:
        # This is a simplified decomposition
        # In real implementation, you would load from pkb_inputs.csv or bbnkb_inputs.csv

        if request.revenue_type == "PKB":
            # Example PKB decomposition
            components = [
                {"name": "Base Year Revenue", "value": 6000000000000, "type": "base"},
                {"name": "Vehicle Growth", "value": 500000000000, "type": "increase"},
                {"name": "Rate Adjustment", "value": 300000000000, "type": "increase"},
                {"name": "Collection Efficiency", "value": 200000000000, "type": "increase"},
                {"name": "Exemptions", "value": -100000000000, "type": "decrease"},
                {"name": "Total PKB", "value": 6900000000000, "type": "total"}
            ]
        else:  # BBNKB
            components = [
                {"name": "Base Year Revenue", "value": 3500000000000, "type": "base"},
                {"name": "Vehicle Transactions", "value": 250000000000, "type": "increase"},
                {"name": "Rate Changes", "value": 150000000000, "type": "increase"},
                {"name": "Administrative Improvements", "value": 100000000000, "type": "increase"},
                {"name": "Total BBNKB", "value": 4000000000000, "type": "total"}
            ]

        # Calculate cumulative for waterfall
        cumulative = 0
        for comp in components:
            if comp["type"] == "base":
                cumulative = comp["value"]
                comp["start"] = 0
                comp["end"] = cumulative
            elif comp["type"] == "total":
                comp["start"] = 0
                comp["end"] = comp["value"]
            else:
                comp["start"] = cumulative
                cumulative += comp["value"]
                comp["end"] = cumulative

        return {
            "success": True,
            "revenue_type": request.revenue_type,
            "year": request.year,
            "components": components,
            "total": components[-1]["value"] if components else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decomposition Error: {str(e)}")


@router.post("/correlation")
async def get_correlation(data: Dict[str, Any]):
    """Calculate correlation matrix for variables"""
    try:
        # Load data
        df = load_pad_historis()

        # Get variables to correlate (default: all numeric columns)
        variables = data.get("variables", None)
        if variables is None:
            # Use all numeric columns
            variables = df.select_dtypes(include=[np.number]).columns.tolist()
            # Remove Tahun
            if 'Tahun' in variables:
                variables.remove('Tahun')

        # Calculate correlation matrix
        corr_matrix = df[variables].corr()

        # Convert to list of dictionaries for easier frontend consumption
        correlation_data = []
        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                correlation_data.append({
                    "var1": var1,
                    "var2": var2,
                    "correlation": float(corr_matrix.iloc[i, j])
                })

        # Find strongest correlations (excluding diagonal)
        strong_correlations = []
        for i, var1 in enumerate(variables):
            for j, var2 in enumerate(variables):
                if i < j:  # Avoid duplicates and diagonal
                    corr_val = float(corr_matrix.iloc[i, j])
                    if abs(corr_val) > 0.5:  # Threshold for "strong"
                        strong_correlations.append({
                            "var1": var1,
                            "var2": var2,
                            "correlation": corr_val,
                            "strength": "Very Strong" if abs(corr_val) > 0.8 else "Strong"
                        })

        strong_correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)

        return {
            "success": True,
            "variables": variables,
            "correlation_matrix": corr_matrix.to_dict(),
            "correlation_data": correlation_data,
            "strong_correlations": strong_correlations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correlation Error: {str(e)}")


@router.post("/stats-summary")
async def get_stats_summary(data: Dict[str, Any]):
    """Get comprehensive statistical summary"""
    try:
        # Load data
        df = load_pad_historis()

        # Get variables (default: all numeric)
        variables = data.get("variables", None)
        if variables is None:
            variables = df.select_dtypes(include=[np.number]).columns.tolist()
            if 'Tahun' in variables:
                variables.remove('Tahun')

        summary_results = {}

        for var in variables:
            series = df[var]

            # Calculate statistics
            summary_results[var] = {
                "count": int(series.count()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(series.std()),
                "min": float(series.min()),
                "max": float(series.max()),
                "q1": float(series.quantile(0.25)),
                "q3": float(series.quantile(0.75)),
                "range": float(series.max() - series.min()),
                "variance": float(series.var()),
                "cv": float(series.std() / series.mean() * 100) if series.mean() != 0 else 0,  # Coefficient of variation
                "skewness": float(series.skew()),
                "kurtosis": float(series.kurtosis()),
                # Growth statistics
                "growth_total": float((series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100) if series.iloc[0] != 0 else 0,
                "growth_annual_avg": float(((series.iloc[-1] / series.iloc[0]) ** (1 / (len(series) - 1)) - 1) * 100) if series.iloc[0] != 0 else 0,
                "trend": "Increasing" if series.iloc[-1] > series.iloc[0] else "Decreasing" if series.iloc[-1] < series.iloc[0] else "Stable"
            }

        return {
            "success": True,
            "variables": variables,
            "summary": summary_results,
            "years_covered": {
                "start": int(df['Tahun'].min()),
                "end": int(df['Tahun'].max()),
                "count": int(df['Tahun'].count())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats Summary Error: {str(e)}")
