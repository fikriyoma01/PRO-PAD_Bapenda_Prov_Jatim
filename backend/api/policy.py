"""
Policy API endpoints
Handles policy settings and targets
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import os

router = APIRouter()

# Policy storage file paths
POLICY_DIR = "backend/data/policy"
POLICY_SETTINGS_FILE = f"{POLICY_DIR}/policy_settings.json"
TARGETS_FILE = f"{POLICY_DIR}/targets.json"
INTERVENTIONS_FILE = f"{POLICY_DIR}/interventions.json"


class PolicySettings(BaseModel):
    targetGrowthRate: float = 10.0
    minimumGrowthRate: float = 5.0
    baselineYear: int = 2023
    targetYear: int = 2025
    conservativeScenario: float = 5.0
    moderateScenario: float = 10.0
    optimisticScenario: float = 15.0


class Target(BaseModel):
    id: Optional[int] = None
    category: str
    year: int
    target: float
    description: str = ""


class PolicyIntervention(BaseModel):
    id: Optional[int] = None
    name: str
    type: str  # 'revenue', 'efficiency', 'compliance', 'incentive'
    impact: float
    description: str = ""


def ensure_policy_dir():
    """Ensure policy directory exists"""
    os.makedirs(POLICY_DIR, exist_ok=True)


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
    ensure_policy_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ============= Policy Settings Endpoints =============

@router.get("/settings")
async def get_policy_settings():
    """Get policy settings"""
    try:
        settings = load_json_file(POLICY_SETTINGS_FILE, {
            "targetGrowthRate": 10.0,
            "minimumGrowthRate": 5.0,
            "baselineYear": 2023,
            "targetYear": 2025,
            "conservativeScenario": 5.0,
            "moderateScenario": 10.0,
            "optimisticScenario": 15.0
        })

        return {
            "success": True,
            "data": settings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings")
async def update_policy_settings(settings: PolicySettings):
    """Update policy settings"""
    try:
        save_json_file(POLICY_SETTINGS_FILE, settings.dict())

        return {
            "success": True,
            "message": "Policy settings updated successfully",
            "data": settings.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Targets Endpoints =============

@router.get("/targets")
async def get_targets():
    """Get PAD targets"""
    try:
        targets = load_json_file(TARGETS_FILE, [
            {"id": 1, "category": "PKB", "year": 2025, "target": 15000, "description": "Target Pajak Kendaraan Bermotor"},
            {"id": 2, "category": "BBNKB", "year": 2025, "target": 4500, "description": "Target BBNKB"},
            {"id": 3, "category": "Total PAD", "year": 2025, "target": 30000, "description": "Target Total PAD"}
        ])

        return {
            "success": True,
            "data": targets,
            "count": len(targets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/targets")
async def save_targets(targets: List[Target]):
    """Save all targets"""
    try:
        targets_data = [t.dict() for t in targets]
        save_json_file(TARGETS_FILE, targets_data)

        return {
            "success": True,
            "message": "Targets saved successfully",
            "data": targets_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/targets/add")
async def add_target(target: Target):
    """Add a new target"""
    try:
        targets = load_json_file(TARGETS_FILE, [])

        # Generate new ID
        new_id = max([t.get("id", 0) for t in targets], default=0) + 1
        target_dict = target.dict()
        target_dict["id"] = new_id

        targets.append(target_dict)
        save_json_file(TARGETS_FILE, targets)

        return {
            "success": True,
            "message": "Target added successfully",
            "data": target_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/targets/{target_id}")
async def delete_target(target_id: int):
    """Delete a target"""
    try:
        targets = load_json_file(TARGETS_FILE, [])

        # Filter out the target
        original_count = len(targets)
        targets = [t for t in targets if t.get("id") != target_id]

        if len(targets) == original_count:
            raise HTTPException(status_code=404, detail="Target not found")

        save_json_file(TARGETS_FILE, targets)

        return {
            "success": True,
            "message": "Target deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============= Policy Interventions Endpoints =============

@router.get("/interventions")
async def get_interventions():
    """Get policy interventions"""
    try:
        interventions = load_json_file(INTERVENTIONS_FILE, [
            {"id": 1, "name": "Digitalisasi Pembayaran", "type": "efficiency", "impact": 8, "description": "Meningkatkan efisiensi pengumpulan pajak"},
            {"id": 2, "name": "Pemutihan Pajak", "type": "revenue", "impact": 12, "description": "Program pemutihan pajak kendaraan"}
        ])

        return {
            "success": True,
            "data": interventions,
            "count": len(interventions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interventions")
async def save_interventions(interventions: List[PolicyIntervention]):
    """Save all policy interventions"""
    try:
        interventions_data = [i.dict() for i in interventions]
        save_json_file(INTERVENTIONS_FILE, interventions_data)

        return {
            "success": True,
            "message": "Policy interventions saved successfully",
            "data": interventions_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interventions/add")
async def add_intervention(intervention: PolicyIntervention):
    """Add a new policy intervention"""
    try:
        interventions = load_json_file(INTERVENTIONS_FILE, [])

        # Generate new ID
        new_id = max([i.get("id", 0) for i in interventions], default=0) + 1
        intervention_dict = intervention.dict()
        intervention_dict["id"] = new_id

        interventions.append(intervention_dict)
        save_json_file(INTERVENTIONS_FILE, interventions)

        return {
            "success": True,
            "message": "Policy intervention added successfully",
            "data": intervention_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/interventions/{intervention_id}")
async def delete_intervention(intervention_id: int):
    """Delete a policy intervention"""
    try:
        interventions = load_json_file(INTERVENTIONS_FILE, [])

        # Filter out the intervention
        original_count = len(interventions)
        interventions = [i for i in interventions if i.get("id") != intervention_id]

        if len(interventions) == original_count:
            raise HTTPException(status_code=404, detail="Intervention not found")

        save_json_file(INTERVENTIONS_FILE, interventions)

        return {
            "success": True,
            "message": "Policy intervention deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
