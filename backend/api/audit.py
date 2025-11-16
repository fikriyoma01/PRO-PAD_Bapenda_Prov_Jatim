"""
Audit API endpoints
Handles activity logging and audit trail
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os
from io import BytesIO
import pandas as pd

router = APIRouter()

# Audit log file path
AUDIT_LOG_DIR = "backend/data/audit"
AUDIT_LOG_FILE = os.path.join(AUDIT_LOG_DIR, "audit_log.json")


class ActivityLog(BaseModel):
    user: str
    action: str
    module: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


def ensure_audit_log_exists():
    """Ensure audit log directory and file exist"""
    os.makedirs(AUDIT_LOG_DIR, exist_ok=True)
    if not os.path.exists(AUDIT_LOG_FILE):
        with open(AUDIT_LOG_FILE, 'w') as f:
            json.dump([], f)


def load_audit_logs() -> List[Dict]:
    """Load all audit logs from file"""
    ensure_audit_log_exists()
    try:
        with open(AUDIT_LOG_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_audit_logs(logs: List[Dict]):
    """Save audit logs to file"""
    ensure_audit_log_exists()
    with open(AUDIT_LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=2)


@router.post("/log")
async def log_activity(activity: ActivityLog):
    """Log user activity"""
    try:
        # Load existing logs
        logs = load_audit_logs()

        # Create new log entry
        log_entry = {
            "id": len(logs) + 1,
            "timestamp": datetime.now().isoformat(),
            "user": activity.user,
            "action": activity.action,
            "module": activity.module,
            "details": activity.details,
            "ip_address": activity.ip_address
        }

        # Append and save
        logs.append(log_entry)
        save_audit_logs(logs)

        return {
            "success": True,
            "message": "Activity logged successfully",
            "log_id": log_entry["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logging Error: {str(e)}")


@router.get("/trail")
async def get_audit_trail(
    user: Optional[str] = None,
    action: Optional[str] = None,
    module: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0
):
    """Get audit trail with filters"""
    try:
        # Load all logs
        logs = load_audit_logs()

        # Apply filters
        filtered_logs = logs

        if user:
            filtered_logs = [log for log in filtered_logs if log.get("user") == user]

        if action:
            filtered_logs = [log for log in filtered_logs if log.get("action") == action]

        if module:
            filtered_logs = [log for log in filtered_logs if log.get("module") == module]

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                filtered_logs = [
                    log for log in filtered_logs
                    if datetime.fromisoformat(log.get("timestamp", "")) >= start_dt
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                filtered_logs = [
                    log for log in filtered_logs
                    if datetime.fromisoformat(log.get("timestamp", "")) <= end_dt
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")

        # Sort by timestamp (newest first)
        filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Apply pagination
        total_count = len(filtered_logs)
        paginated_logs = filtered_logs[offset:offset + limit]

        return {
            "success": True,
            "data": paginated_logs,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit Trail Error: {str(e)}")


@router.get("/export")
async def export_audit_log(
    format: str = "excel",
    user: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Export audit log to Excel or CSV"""
    try:
        # Get filtered audit trail
        logs = load_audit_logs()

        # Apply filters (similar to get_audit_trail)
        filtered_logs = logs

        if user:
            filtered_logs = [log for log in filtered_logs if log.get("user") == user]

        if action:
            filtered_logs = [log for log in filtered_logs if log.get("action") == action]

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                filtered_logs = [
                    log for log in filtered_logs
                    if datetime.fromisoformat(log.get("timestamp", "")) >= start_dt
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                filtered_logs = [
                    log for log in filtered_logs
                    if datetime.fromisoformat(log.get("timestamp", "")) <= end_dt
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")

        # Sort by timestamp
        filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # Convert to DataFrame
        df = pd.DataFrame(filtered_logs)

        if df.empty:
            raise HTTPException(status_code=404, detail="No audit logs found")

        # Create BytesIO buffer
        buffer = BytesIO()

        if format.lower() == "excel":
            # Export to Excel
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Audit Log', index=False)

            buffer.seek(0)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        elif format.lower() == "csv":
            # Export to CSV
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            media_type = "text/csv"
            filename = f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Must be 'excel' or 'csv'"
            )

        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export Error: {str(e)}")


@router.get("/stats")
async def get_audit_stats():
    """Get audit log statistics"""
    try:
        logs = load_audit_logs()

        if not logs:
            return {
                "success": True,
                "stats": {
                    "total_logs": 0,
                    "unique_users": 0,
                    "unique_actions": 0,
                    "date_range": None
                }
            }

        # Calculate statistics
        users = set(log.get("user") for log in logs if log.get("user"))
        actions = set(log.get("action") for log in logs if log.get("action"))
        modules = set(log.get("module") for log in logs if log.get("module"))

        timestamps = [log.get("timestamp") for log in logs if log.get("timestamp")]
        timestamps.sort()

        # Action counts
        action_counts = {}
        for log in logs:
            action = log.get("action")
            if action:
                action_counts[action] = action_counts.get(action, 0) + 1

        # User counts
        user_counts = {}
        for log in logs:
            user = log.get("user")
            if user:
                user_counts[user] = user_counts.get(user, 0) + 1

        stats = {
            "total_logs": len(logs),
            "unique_users": len(users),
            "unique_actions": len(actions),
            "unique_modules": len(modules),
            "date_range": {
                "start": timestamps[0] if timestamps else None,
                "end": timestamps[-1] if timestamps else None
            },
            "top_actions": sorted(
                [{"action": k, "count": v} for k, v in action_counts.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:10],
            "top_users": sorted(
                [{"user": k, "count": v} for k, v in user_counts.items()],
                key=lambda x: x["count"],
                reverse=True
            )[:10]
        }

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats Error: {str(e)}")


@router.delete("/clear")
async def clear_audit_log(confirm: bool = False):
    """Clear all audit logs (requires confirmation)"""
    try:
        if not confirm:
            raise HTTPException(
                status_code=400,
                detail="Please confirm deletion by setting confirm=true"
            )

        # Backup current logs
        logs = load_audit_logs()
        backup_file = AUDIT_LOG_FILE + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        with open(backup_file, 'w') as f:
            json.dump(logs, f, indent=2)

        # Clear logs
        save_audit_logs([])

        return {
            "success": True,
            "message": "Audit log cleared",
            "logs_cleared": len(logs),
            "backup_file": backup_file
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear Error: {str(e)}")
