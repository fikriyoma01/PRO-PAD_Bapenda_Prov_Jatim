"""
Data API endpoints
Handles loading and managing historical data
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import pandas as pd
import sys
import os

# Add parent directory to path to import from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from data_loader import load_pad_historis

router = APIRouter()


@router.get("/historical")
async def get_historical_data():
    """Load historical PAD data"""
    try:
        df = load_pad_historis()
        return {
            "success": True,
            "data": df.to_dict('records'),
            "count": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pkb-inputs")
async def get_pkb_inputs():
    """Load PKB decomposition inputs"""
    try:
        # TODO: Implement PKB inputs loading
        return {
            "success": True,
            "data": [],
            "message": "PKB inputs endpoint - to be implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bbnkb-inputs")
async def get_bbnkb_inputs():
    """Load BBNKB decomposition inputs"""
    try:
        # TODO: Implement BBNKB inputs loading
        return {
            "success": True,
            "data": [],
            "message": "BBNKB inputs endpoint - to be implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def update_data(data: Dict[str, Any]):
    """Update historical data"""
    try:
        # TODO: Implement data update logic
        return {
            "success": True,
            "message": "Data update endpoint - to be implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_data(format: str = "excel"):
    """Export data to Excel or CSV"""
    try:
        # TODO: Implement data export
        return {
            "success": True,
            "message": f"Export to {format} - to be implemented"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
