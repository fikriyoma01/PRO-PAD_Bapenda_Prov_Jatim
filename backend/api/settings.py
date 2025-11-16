"""
Settings API endpoints
Handles UI customization, variables, and other settings
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import os

router = APIRouter()

# Settings storage file paths
SETTINGS_DIR = "backend/data/settings"
UI_SETTINGS_FILE = f"{SETTINGS_DIR}/ui_settings.json"
VARIABLES_FILE = f"{SETTINGS_DIR}/variables.json"


class UISettings(BaseModel):
    theme: str = "light"
    primaryColor: str = "#3b82f6"
    accentColor: str = "#8b5cf6"
    fontSize: str = "medium"
    sidebarPosition: str = "left"
    compactMode: bool = False
    showAnimations: bool = True


class Variable(BaseModel):
    id: Optional[int] = None
    name: str
    type: str  # 'predictor' or 'response'
    description: str = ""
    unit: str = ""
    source_column: str


class VariablesList(BaseModel):
    variables: List[Variable]


def ensure_settings_dir():
    """Ensure settings directory exists"""
    os.makedirs(SETTINGS_DIR, exist_ok=True)


def load_json_file(filepath: str, default: Any = None):
    """Load JSON file or return default if not exists"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return default


def save_json_file(filepath: str, data: Any):
    """Save data to JSON file"""
    ensure_settings_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============= UI Settings Endpoints =============

@router.get("/ui")
async def get_ui_settings():
    """Get UI customization settings"""
    try:
        settings = load_json_file(UI_SETTINGS_FILE, {
            "theme": "light",
            "primaryColor": "#3b82f6",
            "accentColor": "#8b5cf6",
            "fontSize": "medium",
            "sidebarPosition": "left",
            "compactMode": False,
            "showAnimations": True
        })

        return {
            "success": True,
            "data": settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ui")
async def update_ui_settings(settings: UISettings):
    """Update UI customization settings"""
    try:
        save_json_file(UI_SETTINGS_FILE, settings.dict())

        return {
            "success": True,
            "message": "UI settings updated successfully",
            "data": settings.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Variables Endpoints =============

@router.get("/variables")
async def get_variables():
    """Get all model variables"""
    try:
        variables = load_json_file(VARIABLES_FILE, [
            {
                "id": 1,
                "name": "Total PAD",
                "type": "response",
                "description": "Total Pendapatan Asli Daerah",
                "unit": "Miliar Rupiah",
                "source_column": "Total_PAD"
            },
            {
                "id": 2,
                "name": "PKB",
                "type": "predictor",
                "description": "Pajak Kendaraan Bermotor",
                "unit": "Miliar Rupiah",
                "source_column": "PKB"
            },
            {
                "id": 3,
                "name": "BBNKB",
                "type": "predictor",
                "description": "Bea Balik Nama Kendaraan Bermotor",
                "unit": "Miliar Rupiah",
                "source_column": "BBNKB"
            }
        ])

        return {
            "success": True,
            "data": variables,
            "count": len(variables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/variables")
async def save_variables(data: VariablesList):
    """Save all variables"""
    try:
        variables_data = [v.dict() for v in data.variables]
        save_json_file(VARIABLES_FILE, variables_data)

        return {
            "success": True,
            "message": "Variables saved successfully",
            "data": variables_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/variables/add")
async def add_variable(variable: Variable):
    """Add a new variable"""
    try:
        variables = load_json_file(VARIABLES_FILE, [])

        # Generate new ID
        new_id = max([v.get("id", 0) for v in variables], default=0) + 1
        variable_dict = variable.dict()
        variable_dict["id"] = new_id

        variables.append(variable_dict)
        save_json_file(VARIABLES_FILE, variables)

        return {
            "success": True,
            "message": "Variable added successfully",
            "data": variable_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/variables/{variable_id}")
async def update_variable(variable_id: int, variable: Variable):
    """Update a variable"""
    try:
        variables = load_json_file(VARIABLES_FILE, [])

        # Find and update variable
        found = False
        for i, v in enumerate(variables):
            if v.get("id") == variable_id:
                variable_dict = variable.dict()
                variable_dict["id"] = variable_id
                variables[i] = variable_dict
                found = True
                break

        if not found:
            raise HTTPException(status_code=404, detail="Variable not found")

        save_json_file(VARIABLES_FILE, variables)

        return {
            "success": True,
            "message": "Variable updated successfully",
            "data": variable_dict
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/variables/{variable_id}")
async def delete_variable(variable_id: int):
    """Delete a variable"""
    try:
        variables = load_json_file(VARIABLES_FILE, [])

        # Filter out the variable
        original_count = len(variables)
        variables = [v for v in variables if v.get("id") != variable_id]

        if len(variables) == original_count:
            raise HTTPException(status_code=404, detail="Variable not found")

        save_json_file(VARIABLES_FILE, variables)

        return {
            "success": True,
            "message": "Variable deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= System Info =============

@router.get("/system/info")
async def get_system_info():
    """Get system information"""
    try:
        return {
            "success": True,
            "data": {
                "version": "1.0.0",
                "name": "PRO-PAD Dashboard",
                "description": "Prediksi dan Optimasi Pendapatan Asli Daerah",
                "settings_available": [
                    "UI Customization",
                    "Variable Manager",
                    "Policy Settings"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
