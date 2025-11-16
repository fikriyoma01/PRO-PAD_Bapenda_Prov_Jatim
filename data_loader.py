from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "datasets"


def _read_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"File data '{filename}' tidak ditemukan di {DATA_DIR}")
    return pd.read_csv(path)


def load_pad_historis() -> pd.DataFrame:
    """Load historical PAD data from CSV"""
    df = _read_csv("pad_historis.csv")
    df = df.rename(columns={"Rasio_Gini": "Rasio Gini"})
    df = df.rename(columns={"BI7DRR": "Suku Bunga"})
    df["Tahun"] = df["Tahun"].astype(int)
    return df


def load_pkb_inputs() -> pd.DataFrame:
    """Load PKB inputs from CSV"""
    df = _read_csv("pkb_inputs.csv")
    df["tahun"] = df["tahun"].astype(int)
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce").fillna(0)
    return df


def load_bbnkb_inputs() -> pd.DataFrame:
    """Load BBNKB inputs from CSV"""
    df = _read_csv("bbnkb_inputs.csv")
    df["tahun"] = df["tahun"].astype(int)
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce").fillna(0)
    return df


def get_pkb_inputs(year: int) -> pd.DataFrame:
    df = load_pkb_inputs()
    subset = df[df["tahun"] == year]
    if subset.empty:
        raise ValueError(f"Data PKB untuk tahun {year} tidak ditemukan")
    return subset.copy()


def get_bbnkb_inputs(year: int) -> pd.DataFrame:
    df = load_bbnkb_inputs()
    subset = df[df["tahun"] == year]
    if subset.empty:
        raise ValueError(f"Data BBNKB untuk tahun {year} tidak ditemukan")
    return subset.copy()


def map_inputs(df: pd.DataFrame) -> Dict[str, float]:
    return df.set_index("komponen")["nilai"].to_dict()


