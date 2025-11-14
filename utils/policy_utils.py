"""
Policy Settings Utilities
Helper functions to access and apply policy settings across the dashboard
"""

import json
from pathlib import Path
from typing import Dict, Any


CONFIG_FILE = Path("config/policy_settings.json")


def get_policy_settings() -> Dict[str, Any]:
    """
    Get current policy settings

    Returns:
        dict: Policy settings
    """
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return get_default_settings()


def get_default_settings() -> Dict[str, Any]:
    """Get default policy settings"""
    from datetime import datetime

    return {
        'targets': {
            'pkb_2025': 10500000000000,
            'pkb_2026': 11000000000000,
            'bbnkb_2025': 2500000000000,
            'bbnkb_2026': 2600000000000,
            'growth_target': 5.0,
        },
        'policy_parameters': {
            'pkb_base_rate': 1.5,
            'pkb_progressive_rate': 2.5,
            'bbnkb_rate_first': 12.5,
            'bbnkb_rate_second': 1.0,
            'late_payment_penalty': 2.0,
            'discount_early_payment': 5.0,
            'discount_online_payment': 2.0,
        },
        'economic_assumptions': {
            'inflation_assumption': 3.0,
            'gdp_growth_assumption': 5.2,
            'vehicle_growth_assumption': 4.0,
            'compliance_rate': 85.0,
            'collection_efficiency': 90.0,
        },
        'scenario_adjustments': {
            'optimistic_multiplier': 1.10,
            'pessimistic_multiplier': 0.90,
            'use_data_driven': True,
        },
        'model_weights': {
            'ols_weight': 0.50,
            'arima_weight': 0.25,
            'exp_smoothing_weight': 0.25,
        },
        'validation_thresholds': {
            'min_r2': 0.5,
            'max_mape': 15.0,
            'max_rmse': 500000000000,
        },
        'metadata': {
            'created': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'version': '2.0'
        }
    }


def get_target(variable: str, year: int) -> float:
    """
    Get target value for a specific variable and year

    Args:
        variable: 'pkb' or 'bbnkb'
        year: Target year (2025 or 2026)

    Returns:
        float: Target value
    """
    settings = get_policy_settings()
    key = f"{variable.lower()}_{year}"
    return settings['targets'].get(key, 0)


def get_policy_parameter(param_name: str) -> float:
    """
    Get policy parameter value

    Args:
        param_name: Parameter name

    Returns:
        float: Parameter value
    """
    settings = get_policy_settings()
    return settings['policy_parameters'].get(param_name, 0)


def get_economic_assumption(assumption_name: str) -> float:
    """
    Get economic assumption value

    Args:
        assumption_name: Assumption name

    Returns:
        float: Assumption value
    """
    settings = get_policy_settings()
    return settings['economic_assumptions'].get(assumption_name, 0)


def get_scenario_multipliers() -> Dict[str, float]:
    """
    Get scenario multipliers

    Returns:
        dict: Optimistic and pessimistic multipliers
    """
    settings = get_policy_settings()
    return {
        'optimistic': settings['scenario_adjustments'].get('optimistic_multiplier', 1.10),
        'pessimistic': settings['scenario_adjustments'].get('pessimistic_multiplier', 0.90),
        'use_data_driven': settings['scenario_adjustments'].get('use_data_driven', True)
    }


def get_model_weights() -> Dict[str, float]:
    """
    Get model weights for ensemble

    Returns:
        dict: Model weights
    """
    settings = get_policy_settings()
    return settings.get('model_weights', {
        'ols_weight': 0.50,
        'arima_weight': 0.25,
        'exp_smoothing_weight': 0.25
    })


def get_validation_thresholds() -> Dict[str, float]:
    """
    Get validation thresholds

    Returns:
        dict: Validation thresholds
    """
    settings = get_policy_settings()
    return settings.get('validation_thresholds', {
        'min_r2': 0.5,
        'max_mape': 15.0,
        'max_rmse': 500000000000
    })


def apply_scenario_adjustment(base_value: float, scenario_type: str = 'moderate') -> float:
    """
    Apply scenario adjustment to a base value

    Args:
        base_value: Base projection value
        scenario_type: 'optimistic', 'moderate', or 'pessimistic'

    Returns:
        float: Adjusted value
    """
    if scenario_type == 'moderate':
        return base_value

    multipliers = get_scenario_multipliers()

    if scenario_type == 'optimistic':
        return base_value * multipliers['optimistic']
    elif scenario_type == 'pessimistic':
        return base_value * multipliers['pessimistic']

    return base_value


def calculate_policy_impact(
    base_revenue: float,
    compliance_adjustment: float = 0,
    efficiency_adjustment: float = 0
) -> Dict[str, float]:
    """
    Calculate impact of policy changes on revenue

    Args:
        base_revenue: Base revenue amount
        compliance_adjustment: Change in compliance rate (percentage points)
        efficiency_adjustment: Change in collection efficiency (percentage points)

    Returns:
        dict: Impact breakdown
    """
    settings = get_policy_settings()

    current_compliance = settings['economic_assumptions']['compliance_rate']
    current_efficiency = settings['economic_assumptions']['collection_efficiency']

    new_compliance = current_compliance + compliance_adjustment
    new_efficiency = current_efficiency + efficiency_adjustment

    # Calculate impact
    compliance_factor = new_compliance / current_compliance
    efficiency_factor = new_efficiency / current_efficiency

    adjusted_revenue = base_revenue * compliance_factor * efficiency_factor
    total_impact = adjusted_revenue - base_revenue

    return {
        'base_revenue': base_revenue,
        'adjusted_revenue': adjusted_revenue,
        'total_impact': total_impact,
        'compliance_impact': base_revenue * (compliance_factor - 1),
        'efficiency_impact': base_revenue * efficiency_factor * (1 - 1/efficiency_factor) if efficiency_factor != 0 else 0,
        'new_compliance_rate': new_compliance,
        'new_efficiency_rate': new_efficiency
    }


def validate_model_quality(r2: float, mape: float, rmse: float) -> Dict[str, Any]:
    """
    Validate model quality against thresholds

    Args:
        r2: R-squared value
        mape: Mean Absolute Percentage Error
        rmse: Root Mean Squared Error

    Returns:
        dict: Validation results
    """
    thresholds = get_validation_thresholds()

    results = {
        'r2': {
            'value': r2,
            'threshold': thresholds['min_r2'],
            'passed': r2 >= thresholds['min_r2'],
            'message': 'Good fit' if r2 >= thresholds['min_r2'] else 'Poor fit'
        },
        'mape': {
            'value': mape,
            'threshold': thresholds['max_mape'],
            'passed': mape <= thresholds['max_mape'],
            'message': 'Acceptable error' if mape <= thresholds['max_mape'] else 'High error'
        },
        'rmse': {
            'value': rmse,
            'threshold': thresholds['max_rmse'],
            'passed': rmse <= thresholds['max_rmse'],
            'message': 'Low error' if rmse <= thresholds['max_rmse'] else 'High error'
        }
    }

    results['overall_passed'] = all(r['passed'] for r in results.values() if isinstance(r, dict))

    return results


def format_policy_summary() -> str:
    """
    Format a readable summary of current policy settings

    Returns:
        str: Formatted summary (markdown)
    """
    settings = get_policy_settings()

    summary = f"""
### 📋 Current Policy Settings

**Targets:**
- PKB 2025: Rp {settings['targets']['pkb_2025']/1e12:.2f}T
- PKB 2026: Rp {settings['targets']['pkb_2026']/1e12:.2f}T
- BBNKB 2025: Rp {settings['targets']['bbnkb_2025']/1e12:.2f}T
- BBNKB 2026: Rp {settings['targets']['bbnkb_2026']/1e12:.2f}T
- Growth Target: {settings['targets']['growth_target']:.1f}%

**Policy Parameters:**
- PKB Base Rate: {settings['policy_parameters']['pkb_base_rate']:.1f}%
- BBNKB First Rate: {settings['policy_parameters']['bbnkb_rate_first']:.1f}%
- Early Payment Discount: {settings['policy_parameters']['discount_early_payment']:.1f}%

**Economic Assumptions:**
- Inflation: {settings['economic_assumptions']['inflation_assumption']:.1f}%
- PDRB Growth: {settings['economic_assumptions']['gdp_growth_assumption']:.1f}%
- Compliance Rate: {settings['economic_assumptions']['compliance_rate']:.1f}%
- Collection Efficiency: {settings['economic_assumptions']['collection_efficiency']:.1f}%

**Scenario Settings:**
- Use Data-Driven: {"Yes" if settings['scenario_adjustments']['use_data_driven'] else "No"}
- Optimistic Multiplier: {settings['scenario_adjustments']['optimistic_multiplier']:.2f}
- Pessimistic Multiplier: {settings['scenario_adjustments']['pessimistic_multiplier']:.2f}
    """

    return summary.strip()
