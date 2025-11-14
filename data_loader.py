from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd
import streamlit as st
from utils.audit_utils import log_data_load

DATA_DIR = Path(__file__).resolve().parent / "datasets"


def _read_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"File data '{filename}' tidak ditemukan di {DATA_DIR}")
    return pd.read_csv(path)


@st.cache_data(show_spinner=False)
def load_pad_historis() -> pd.DataFrame:
    df = _read_csv("pad_historis.csv")
    df = df.rename(columns={"Rasio_Gini": "Rasio Gini"})
    df = df.rename(columns={"BI7DRR": "Suku Bunga"})
    df["Tahun"] = df["Tahun"].astype(int)

    # Log data load (only once per cache refresh)
    log_data_load(
        source="pad_historis.csv",
        records=len(df),
        details={
            'columns': list(df.columns),
            'year_range': f"{df['Tahun'].min()}-{df['Tahun'].max()}"
        }
    )

    return df


@st.cache_data(show_spinner=False)
def load_pkb_inputs() -> pd.DataFrame:
    df = _read_csv("pkb_inputs.csv")
    df["tahun"] = df["tahun"].astype(int)
    df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce").fillna(0)
    return df


@st.cache_data(show_spinner=False)
def load_bbnkb_inputs() -> pd.DataFrame:
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


