"""
Data API endpoints
Handles loading and managing historical data
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import sys
import os
from io import BytesIO

# Add parent directory to path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_loader import (
    load_pad_historis,
    load_pkb_inputs,
    load_bbnkb_inputs,
    get_pkb_inputs,
    get_bbnkb_inputs
)

router = APIRouter()


class DataUpdateRequest(BaseModel):
    data_type: str  # 'historical', 'pkb', 'bbnkb'
    records: List[Dict[str, Any]]


@router.get("/historical")
async def get_historical_data():
    """Load historical PAD data"""
    try:
        df = load_pad_historis()
        return {
            "success": True,
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "count": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pkb-inputs")
async def get_all_pkb_inputs(year: Optional[int] = None):
    """Load PKB decomposition inputs"""
    try:
        if year:
            # Get inputs for specific year
            df = get_pkb_inputs(year)
        else:
            # Get all PKB inputs
            df = load_pkb_inputs()

        return {
            "success": True,
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "count": len(df),
            "year": year
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bbnkb-inputs")
async def get_all_bbnkb_inputs(year: Optional[int] = None):
    """Load BBNKB decomposition inputs"""
    try:
        if year:
            # Get inputs for specific year
            df = get_bbnkb_inputs(year)
        else:
            # Get all BBNKB inputs
            df = load_bbnkb_inputs()

        return {
            "success": True,
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "count": len(df),
            "year": year
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def update_data(request: DataUpdateRequest):
    """Update historical data"""
    try:
        # Determine which file to update
        data_files = {
            'historical': 'datasets/pad_historis.csv',
            'pkb': 'datasets/pkb_inputs.csv',
            'bbnkb': 'datasets/bbnkb_inputs.csv'
        }

        if request.data_type not in data_files:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data_type. Must be one of: {', '.join(data_files.keys())}"
            )

        # Convert records to DataFrame
        df_new = pd.DataFrame(request.records)

        # Get file path
        file_path = data_files[request.data_type]

        # Validate data structure before saving
        if request.data_type == 'historical':
            required_cols = ['Tahun']
            if not all(col in df_new.columns for col in required_cols):
                raise HTTPException(
                    status_code=400,
                    detail=f"Historical data must include column: Tahun"
                )
        elif request.data_type in ['pkb', 'bbnkb']:
            required_cols = ['tahun', 'komponen', 'nilai']
            if not all(col in df_new.columns for col in required_cols):
                raise HTTPException(
                    status_code=400,
                    detail=f"{request.data_type.upper()} data must include columns: {', '.join(required_cols)}"
                )

        # Save to CSV (backup original first)
        original_file = file_path
        backup_file = file_path + '.backup'

        # Create backup if original exists
        if os.path.exists(original_file):
            import shutil
            shutil.copy2(original_file, backup_file)

        # Save new data
        df_new.to_csv(file_path, index=False)

        return {
            "success": True,
            "message": f"Successfully updated {request.data_type} data",
            "records_updated": len(df_new),
            "backup_created": backup_file
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update Error: {str(e)}")


@router.get("/export")
async def export_data(
    data_type: str = "historical",
    format: str = "excel",
    year: Optional[int] = None
):
    """Export data to Excel or CSV"""
    try:
        # Load appropriate data
        if data_type == "historical":
            df = load_pad_historis()
            filename = "pad_historis"
        elif data_type == "pkb":
            if year:
                df = get_pkb_inputs(year)
                filename = f"pkb_inputs_{year}"
            else:
                df = load_pkb_inputs()
                filename = "pkb_inputs"
        elif data_type == "bbnkb":
            if year:
                df = get_bbnkb_inputs(year)
                filename = f"bbnkb_inputs_{year}"
            else:
                df = load_bbnkb_inputs()
                filename = "bbnkb_inputs"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data_type. Must be one of: historical, pkb, bbnkb"
            )

        # Create BytesIO buffer
        buffer = BytesIO()

        if format.lower() == "excel":
            # Export to Excel
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)

            buffer.seek(0)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename_ext = f"{filename}.xlsx"

        elif format.lower() == "csv":
            # Export to CSV
            df.to_csv(buffer, index=False)
            buffer.seek(0)
            media_type = "text/csv"
            filename_ext = f"{filename}.csv"

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Must be 'excel' or 'csv'"
            )

        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename_ext}"
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export Error: {str(e)}")


@router.get("/columns")
async def get_data_columns(data_type: str = "historical"):
    """Get column names and info for a specific dataset"""
    try:
        if data_type == "historical":
            df = load_pad_historis()
        elif data_type == "pkb":
            df = load_pkb_inputs()
        elif data_type == "bbnkb":
            df = load_bbnkb_inputs()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data_type. Must be one of: historical, pkb, bbnkb"
            )

        # Get column info
        column_info = []
        for col in df.columns:
            column_info.append({
                "name": col,
                "dtype": str(df[col].dtype),
                "non_null_count": int(df[col].count()),
                "null_count": int(df[col].isnull().sum()),
                "unique_count": int(df[col].nunique())
            })

        return {
            "success": True,
            "data_type": data_type,
            "columns": column_info,
            "total_rows": len(df)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_data_summary():
    """Get summary of all available datasets"""
    try:
        summary = {}

        # Historical data
        df_hist = load_pad_historis()
        summary['historical'] = {
            "rows": len(df_hist),
            "columns": len(df_hist.columns),
            "column_names": df_hist.columns.tolist(),
            "year_range": [int(df_hist['Tahun'].min()), int(df_hist['Tahun'].max())]
        }

        # PKB data
        df_pkb = load_pkb_inputs()
        summary['pkb'] = {
            "rows": len(df_pkb),
            "columns": len(df_pkb.columns),
            "column_names": df_pkb.columns.tolist(),
            "year_range": [int(df_pkb['tahun'].min()), int(df_pkb['tahun'].max())],
            "components": df_pkb['komponen'].unique().tolist() if 'komponen' in df_pkb.columns else []
        }

        # BBNKB data
        df_bbnkb = load_bbnkb_inputs()
        summary['bbnkb'] = {
            "rows": len(df_bbnkb),
            "columns": len(df_bbnkb.columns),
            "column_names": df_bbnkb.columns.tolist(),
            "year_range": [int(df_bbnkb['tahun'].min()), int(df_bbnkb['tahun'].max())],
            "components": df_bbnkb['komponen'].unique().tolist() if 'komponen' in df_bbnkb.columns else []
        }

        return {
            "success": True,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
