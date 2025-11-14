"""
Audit Trail System for PAD Dashboard
Tracks user actions, model runs, and data changes for transparency and accountability
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import streamlit as st


# Audit log file path
AUDIT_LOG_FILE = "audit_log.json"


def log_event(
    event_type: str,
    action: str,
    details: Optional[Dict] = None,
    user: Optional[str] = None
) -> None:
    """
    Log an event to the audit trail

    Args:
        event_type: Type of event (e.g., 'model_run', 'data_load', 'projection')
        action: Description of the action
        details: Additional details about the event
        user: User identifier (if available)
    """
    # Create event record
    event = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'action': action,
        'details': details or {},
        'user': user or 'anonymous',
        'session_id': st.session_state.get('session_id', 'unknown')
    }

    # Load existing log
    if os.path.exists(AUDIT_LOG_FILE):
        try:
            with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            log_data = []
    else:
        log_data = []

    # Append new event
    log_data.append(event)

    # Keep only last 1000 events to prevent file bloat
    if len(log_data) > 1000:
        log_data = log_data[-1000:]

    # Save log
    try:
        with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        # Silently fail - don't break app if logging fails
        print(f"Warning: Failed to write audit log: {e}")


def get_audit_log(
    event_type: Optional[str] = None,
    limit: Optional[int] = 100
) -> List[Dict]:
    """
    Retrieve audit log entries

    Args:
        event_type: Filter by event type (None = all)
        limit: Maximum number of entries to return

    Returns:
        List of event dictionaries
    """
    if not os.path.exists(AUDIT_LOG_FILE):
        return []

    try:
        with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    # Filter by event type if specified
    if event_type:
        log_data = [e for e in log_data if e.get('event_type') == event_type]

    # Sort by timestamp (newest first)
    log_data = sorted(log_data, key=lambda x: x.get('timestamp', ''), reverse=True)

    # Apply limit
    if limit:
        log_data = log_data[:limit]

    return log_data


def format_audit_log_df(log_data: List[Dict]) -> pd.DataFrame:
    """
    Format audit log data as DataFrame for display

    Args:
        log_data: List of event dictionaries

    Returns:
        Formatted DataFrame
    """
    if not log_data:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(log_data)

    # Format timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['Waktu'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Format columns
    display_df = pd.DataFrame({
        'Waktu': df['Waktu'],
        'Tipe Event': df['event_type'],
        'Aksi': df['action'],
        'User': df['user'],
        'Session ID': df['session_id'].str[:8] + '...'  # Truncate session ID
    })

    return display_df


def get_audit_statistics() -> Dict:
    """
    Get summary statistics from audit log

    Returns:
        Dictionary with statistics
    """
    log_data = get_audit_log(limit=None)  # Get all

    if not log_data:
        return {
            'total_events': 0,
            'event_types': {},
            'unique_users': 0,
            'unique_sessions': 0,
            'first_event': None,
            'last_event': None
        }

    df = pd.DataFrame(log_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Count by event type
    event_counts = df['event_type'].value_counts().to_dict()

    return {
        'total_events': len(df),
        'event_types': event_counts,
        'unique_users': df['user'].nunique(),
        'unique_sessions': df['session_id'].nunique(),
        'first_event': df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S'),
        'last_event': df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
    }


def clear_audit_log() -> bool:
    """
    Clear the audit log file

    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(AUDIT_LOG_FILE):
            os.remove(AUDIT_LOG_FILE)
        return True
    except Exception as e:
        print(f"Failed to clear audit log: {e}")
        return False


# Common event loggers for convenience
def log_model_run(response: str, predictor: str, r2: float, details: Optional[Dict] = None):
    """Log a model execution"""
    log_event(
        event_type='model_run',
        action=f'Ran regression: {response} ~ {predictor}',
        details={
            'response': response,
            'predictor': predictor,
            'r2': r2,
            **(details or {})
        }
    )


def log_projection(response: str, year: int, value: float, scenario: str, details: Optional[Dict] = None):
    """Log a projection calculation"""
    log_event(
        event_type='projection',
        action=f'Calculated projection for {response} in {year}',
        details={
            'response': response,
            'year': year,
            'value': value,
            'scenario': scenario,
            **(details or {})
        }
    )


def log_data_load(source: str, records: int, details: Optional[Dict] = None):
    """Log data loading"""
    log_event(
        event_type='data_load',
        action=f'Loaded data from {source}',
        details={
            'source': source,
            'records': records,
            **(details or {})
        }
    )


def log_scenario_save(scenario_name: str, details: Optional[Dict] = None):
    """Log scenario save"""
    log_event(
        event_type='scenario_save',
        action=f'Saved scenario: {scenario_name}',
        details={
            'scenario_name': scenario_name,
            **(details or {})
        }
    )


def log_export(export_type: str, filename: str, details: Optional[Dict] = None):
    """Log data export"""
    log_event(
        event_type='export',
        action=f'Exported {export_type} to {filename}',
        details={
            'export_type': export_type,
            'filename': filename,
            **(details or {})
        }
    )


def initialize_session():
    """Initialize audit session tracking"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
        log_event(
            event_type='session_start',
            action='User session started',
            details={'session_id': st.session_state.session_id}
        )
