# pyfiles/ep_run_v2.py
"""
EnergyPLAN runner v2 — parquet-based output.

Replaces the ASCII → Excel round-trip with direct ASCII parsing into five
parquet files per run:

  {out_name}_scalars.parquet     1 row  × named scalar metrics (costs, emissions…)
  {out_name}_annual.parquet      1 row  × named production/flow columns (TWh/year)
  {out_name}_monthly.parquet    12 rows × named columns (monthly averages, MW)
  {out_name}_hourly.parquet   8760 rows × named columns (hourly dispatch, MW)
  {out_name}_investments.parquet  N rows × technology investment breakdown

Loading helpers (ann_T, load_scalars, load_monthly, load_hourly, load_investments)
accept either a bare stem ('ETT_base_v2') or a legacy xlsx name ('ETT_base_v2.xlsx').
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

# 1. default paths  (relative to this file: pyfiles/ → LL_project/ → EnergyPLAN/)
DEFAULT_EXE = Path(__file__).parent.parent.parent / "ZipEnergyPLAN163" / "energyPLAN.exe"
DEFAULT_OUT_DIR = Path(__file__).parent.parent / "0_EP_runs"

_MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# 2. scalar labels to extract from left-column of the ASCII summary section
_SCALAR_MAP = {
    "CO2-emission (total)":        "co2_total_Mt",
    "CO2-emission (corrected)":    "co2_corrected_Mt",
    "RES share of PES":            "res_pes_pct",
    "RES share of elec. prod.":    "res_elec_pct",
    "RES electricity prod.":       "res_elec_TWh",
    "Fuel Consumption (total)":    "fuel_total_TWh",
    "Fuel(incl.Biomass excl.RES)": "fuel_excl_res_TWh",
    "Ngas Consumption":            "ngas_TWh",
    "Biomass Consumption":         "biomass_TWh",
    "Nuclear Fuel Consumption":    "nuclear_TWh",
    "Waste Input":                 "waste_TWh",
    "Fuel ex. Ngas exchange":      "fuel_ex_ngas_MEUR",
    "Ngas Exchange costs":         "ngas_exchange_MEUR",
    "Marginal operation costs":    "var_marginal_MEUR",
    "Electricity exchange":        "elec_exchange_MEUR",
    "CO2 emission costs":          "co2_costs_MEUR",
    "Variable costs":              "var_costs_MEUR",
    "Fixed operation costs":       "fixed_costs_MEUR",
    "Annual Investment costs":     "inv_costs_MEUR",
    "TOTAL ANNUAL COSTS":          "total_costs_MEUR",
}


# =============================================================================
# NUMERIC HELPERS
# =============================================================================

_NUM_RE = re.compile(r"""
    ^\s*[-+]?
    (?:
        (?:\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d+)?
        |(?:[.,]\d+)
    )
    (?:e[-+]?\d+)?\s*$
""", re.IGNORECASE | re.VERBOSE)

_UNIT_RE = re.compile(r"\s*(MW|MWh|GWh|TWh|kW|EUR|MEUR|M\s*EUR|percent)\s*$", re.IGNORECASE)


# ==================== ==================== ==================== ====================
# 1. parse a single token to float
def _to_float(s: str) -> float | None:
    """Parse a single token to float; return None if non-numeric."""
    s = s.strip()
    if not s:
        return None
    s = re.sub(r"[%€]", "", s)
    s = _UNIT_RE.sub("", s).strip()
    s0 = s.replace(" ", "")
    if not _NUM_RE.match(s0):
        return None
    if "," in s0 and "." in s0:
        s1 = s0.replace(".", "").replace(",", ".") if s0.rfind(",") > s0.rfind(".") else s0.replace(",", "")
    elif "," in s0:
        s1 = s0.replace(",", ".")
    else:
        s1 = s0
    try:
        return float(s1)
    except ValueError:
        return None


# ==================== ==================== ==================== ====================
# 2. split one ASCII line into fields
def _split(ln: str) -> list[str]:
    if "\t" in ln:
        return ln.split("\t")
    if ";" in ln:
        return ln.split(";")
    return re.split(r"\s{2,}", ln.rstrip())


# =============================================================================
# ASCII PARSER
# =============================================================================


# ==================== ==================== ==================== ====================
# 3. parse full EnergyPLAN ASCII output into DataFrames
def _parse_ascii(text: str, run_name: str) -> dict[str, pd.DataFrame]:
    """
    Parse the full EnergyPLAN ASCII output into five DataFrames.

    Parameters
    ----------
    text     : raw ASCII content of the EnergyPLAN output file
    run_name : used as the index label in the returned DataFrames

    Returns
    -------
    dict with keys 'scalars', 'annual', 'monthly', 'hourly', 'investments'
    """
    lines = text.splitlines()

    # 1. scalars — scan every line for known labels
    scalars: dict[str, float] = {}
    for ln in lines:
        parts = _split(ln)
        label = parts[0].strip() if parts else ""
        if label not in _SCALAR_MAP:
            continue
        for p in parts[1:5]:
            v = _to_float(p)
            if v is not None:
                scalars[_SCALAR_MAP[label]] = v
                break

    scalars_df = pd.DataFrame([scalars], index=[run_name])

    # 2. locate time-series header rows (two consecutive wide tab-split lines)
    header1_idx: int | None = None
    for i, ln in enumerate(lines[:-1]):
        parts = _split(ln)
        if parts[0].strip() == "" and len(parts) > 80:
            nxt = _split(lines[i + 1])
            if nxt[0].strip() == "" and len(nxt) > 80:
                header1_idx = i
                break

    if header1_idx is None:
        raise ValueError("Could not locate time-series header rows in ASCII output.")

    h1 = [p.strip() for p in _split(lines[header1_idx])]
    h2 = [p.strip() for p in _split(lines[header1_idx + 1])]
    n_cols = max(len(h1), len(h2)) - 1
    h1 += [""] * (n_cols + 1 - len(h1))
    h2 += [""] * (n_cols + 1 - len(h2))

    col_names: list[str] = []
    for a, b in zip(h1[1:], h2[1:]):
        if a and b:
            col_names.append(f"{a}_{b}")
        elif a:
            col_names.append(a)
        elif b:
            col_names.append(b)
        else:
            col_names.append("_unknown")

    def _data_row(ln: str) -> list[float]:
        parts = _split(ln)
        vals = []
        for p in parts[1:]:
            v = _to_float(p)
            vals.append(v if v is not None else np.nan)
        vals += [np.nan] * (n_cols - len(vals))
        return vals[:n_cols]

    # 3. annual row
    annual_df: pd.DataFrame | None = None
    for ln in lines[header1_idx:]:
        first = _split(ln)[0].strip() if _split(ln) else ""
        if re.match(r"^Annual\b", first, re.IGNORECASE):
            row = _data_row(ln)
            annual_df = pd.DataFrame([row], columns=col_names, index=[run_name])
            break

    if annual_df is None:
        raise ValueError("Could not find 'Annual:' row in ASCII output.")

    # 4. monthly rows
    monthly_rows: list[pd.Series] = []
    in_monthly = False
    for ln in lines:
        if "MONTHLY AVERAGE VALUES" in ln:
            in_monthly = True
            continue
        if not in_monthly:
            continue
        first = _split(ln)[0].strip() if _split(ln) else ""
        if first in _MONTH_NAMES:
            monthly_rows.append(pd.Series(_data_row(ln), index=col_names, name=first))
        elif monthly_rows and first not in ("",) and first not in _MONTH_NAMES:
            break

    monthly_df = pd.DataFrame(monthly_rows) if monthly_rows else pd.DataFrame(columns=col_names)

    # 5. hourly rows (integers 1–8760 in the first column)
    hourly_records: list[list] = []
    for ln in lines[header1_idx + 2:]:
        if len(hourly_records) == 8760:
            break
        parts = _split(ln)
        first = parts[0].strip() if parts else ""
        v = _to_float(first)
        if v is None:
            continue
        iv = int(round(v))
        if 1 <= iv <= 8760 and abs(v - iv) < 1e-9:
            hourly_records.append([iv] + _data_row(ln))

    if hourly_records:
        hourly_df = pd.DataFrame(hourly_records, columns=["hour"] + col_names)
    else:
        hourly_df = pd.DataFrame(columns=["hour"] + col_names)

    # 6. investment overview (right-side columns of the ASCII)
    inv_start: int | None = None
    for i, ln in enumerate(lines):
        parts = ln.rstrip("\n").split("\t")
        if len(parts) > 6 and parts[6].strip() == "OVERVIEW OF INVESTMENT COSTS":
            inv_start = i
            break

    inv_records: list[dict] = []
    if inv_start is not None:
        for ln in lines[inv_start + 4:]:
            parts = ln.rstrip("\n").split("\t")
            if len(parts) < 10:
                break
            name = parts[6].strip()
            if not name:
                break
            total  = _to_float(parts[7])
            annual = _to_float(parts[8])
            om     = _to_float(parts[9])
            if total is None or annual is None or om is None:
                continue
            inv_records.append({
                "variable":   name,
                "total_inv":  total,
                "annual_inv": annual,
                "O&M":        om,
            })

    _INV_COLS = ["variable", "total_inv", "annual_inv", "O&M"]
    investments_df = (
        pd.DataFrame(inv_records)
        if inv_records
        else pd.DataFrame(columns=_INV_COLS)
    )

    return {
        "scalars":     scalars_df,
        "annual":      annual_df,
        "monthly":     monthly_df,
        "hourly":      hourly_df,
        "investments": investments_df,
    }


# =============================================================================
# RUNNER
# =============================================================================


# ==================== ==================== ==================== ====================
# 4. run EnergyPLAN for one scenario and save parquet output
def run_energyplan(
    input_file: str | Path,
    out_name: str,
    *,
    energyplan_exe: str | Path = DEFAULT_EXE,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    input_dir: str | Path | None = None,
    delete_ascii: bool = True,
) -> dict[str, Path]:
    """
    Run EnergyPLAN on *input_file* and save output as parquet files.

    Returns a dict with keys 'scalars', 'annual', 'monthly', 'hourly',
    'investments' mapping to the saved Path objects.
    """
    energyplan_exe = Path(energyplan_exe)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. resolve input file path
    inp = Path(input_file)
    if not inp.is_absolute() and input_dir is not None:
        inp = Path(input_dir) / inp
    if not inp.exists():
        raise FileNotFoundError(f"Input file not found: {inp}")

    ascii_out = out_dir / f"{out_name}.txt"

    # 2. call EnergyPLAN binary
    cmd = [str(energyplan_exe), "-i", str(inp), "-ascii", str(ascii_out)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(
            f"EnergyPLAN failed (code {res.returncode}).\n"
            f"Input:  {inp}\nOutput: {ascii_out}\n"
            f"STDOUT:\n{res.stdout}\n\nSTDERR:\n{res.stderr}"
        )
    if not ascii_out.exists() or ascii_out.stat().st_size == 0:
        raise FileNotFoundError(f"Output not created / empty: {ascii_out}")

    # 3. read ASCII output
    try:
        text = ascii_out.read_text(encoding="cp1252")
    except UnicodeDecodeError:
        text = ascii_out.read_text(encoding="latin-1")

    # 4. parse and save as parquet
    dfs = _parse_ascii(text, run_name=out_name)
    paths: dict[str, Path] = {}
    for key, df in dfs.items():
        p = out_dir / f"{out_name}_{key}.parquet"
        df.to_parquet(p)
        paths[key] = p

    if delete_ascii:
        ascii_out.unlink(missing_ok=True)

    return paths


# ==================== ==================== ==================== ====================
# 5. run EnergyPLAN for multiple scenarios
def run_many(
    inp_files: list[str | Path],
    out_names: list[str],
    *,
    energyplan_exe: str | Path = DEFAULT_EXE,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    input_dir: str | Path | None = None,
    delete_ascii: bool = True,
) -> list[dict[str, Path]]:
    """Run EnergyPLAN for each (inp_file, out_name) pair."""
    if len(inp_files) != len(out_names):
        raise ValueError("inp_files and out_names must have the same length.")
    return [
        run_energyplan(
            inp, name,
            energyplan_exe=energyplan_exe,
            out_dir=out_dir,
            input_dir=input_dir,
            delete_ascii=delete_ascii,
        )
        for inp, name in zip(inp_files, out_names)
    ]


# =============================================================================
# LOADING HELPERS
# =============================================================================


# ==================== ==================== ==================== ====================
# 6. strip extension to get run stem
def _stem(name: str | Path) -> str:
    """Accept 'ETT_base_v2' or 'ETT_base_v2.xlsx' — always return the stem."""
    return Path(name).stem


# ==================== ==================== ==================== ====================
# 7. load annual production vector, transposed
def ann_T(
    name: str | Path,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> pd.DataFrame:
    """
    Load annual production vector, transposed:
    rows = variable names, single column = run name (stem).
    """
    stem = _stem(name)
    path = Path(out_dir) / f"{stem}_annual.parquet"
    df = pd.read_parquet(path)   # shape (1, n_vars), index = run_name
    return df.T                  # shape (n_vars, 1)


# ==================== ==================== ==================== ====================
# 8. load scalar metrics for one run
def load_scalars(
    name: str | Path,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> pd.Series:
    """Return named scalar metrics for one run as a Series."""
    stem = _stem(name)
    path = Path(out_dir) / f"{stem}_scalars.parquet"
    return pd.read_parquet(path).iloc[0]


# ==================== ==================== ==================== ====================
# 9. load monthly averages for one run
def load_monthly(
    name: str | Path,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> pd.DataFrame:
    """Return monthly averages (12 rows × named columns, MW)."""
    stem = _stem(name)
    path = Path(out_dir) / f"{stem}_monthly.parquet"
    return pd.read_parquet(path)


# ==================== ==================== ==================== ====================
# 10. load hourly dispatch for one run
def load_hourly(
    name: str | Path,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> pd.DataFrame:
    """Return hourly time-series (8760 rows × named columns, first col = 'hour')."""
    stem = _stem(name)
    path = Path(out_dir) / f"{stem}_hourly.parquet"
    return pd.read_parquet(path)


# ==================== ==================== ==================== ====================
# 11. load investment overview for one run
def load_investments(
    name: str | Path,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> pd.DataFrame:
    """Return investment overview (one row per technology, columns: variable, total_inv, annual_inv, O&M)."""
    stem = _stem(name)
    path = Path(out_dir) / f"{stem}_investments.parquet"
    return pd.read_parquet(path)
