# pyfiles/solver.py
"""
solver.py
---------
Minimises the 5_cost_decomposition metric instead of EnergyPLAN's TOTAL ANNUAL COSTS.

5_cost objective:
    TC5 = TAC  −  cshp_inv  +  ve_prod × (145/7.45)  +  kk_prod × (10/7.45)

  TAC           EnergyPLAN TOTAL ANNUAL COSTS (~95% of the 5_cost metric)
  cshp_inv      annual_inv + O&M for 'Indust. CHP Heat' (CSHP double-count, subtract)
  ve_prod       Offshore + Wind + PV production, TWh
  kk_prod       Nuclear production, TWh
  rates         VRE 145 DKK/MWh, nuclear 10 DKK/MWh, at 7.45 DKK/EUR → MEUR/TWh

Note: EnergyPLAN's 'Electricity exchange' line is already part of Variable costs → TAC
(confirmed against raw ASCII output) and must NOT be added as a separate correction.

Starting from TAC is more robust than building from components — it automatically
captures all background infrastructure costs and only requires targeted corrections.

Differences vs solver.py:
  1. 'Indust. CHP Heat' subtracted from TAC (CSHP investment double-count)
  2. External system costs for VRE and nuclear added at policy rates

Constraint: electricity imports <= IMPORT_LIMIT_TWH (penalty method)
Usage: identical to solver.py — configure() then run()
"""

from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).parent.parent   # LL_project/
sys.path.insert(0, str(ROOT))

from pyfiles.scenario_functions import build_params, format_value, load_energyplan_file

# =============================================================================
# SOLVER CONFIGURATION
# =============================================================================

MAX_EVALUATIONS  = 20
IMPORT_LIMIT_TWH = 0.0
IMPORT_PENALTY   = 1e9
BOUNDS_PENALTY   = 1e9

VRE_RATE  = 155 / 7.45   # MEUR per TWh of VRE production  (DKK/MWh → MEUR/TWh)
KK_RATE   =  10 / 7.45   # MEUR per TWh of nuclear production
CSHP_EXCL = "Indust. CHP Heat"   # investment row to subtract from TAC

X0 = {
    "input_cap_pp2_el"          : 1200.0,   # MW
    "input_cap_ELTtrans_el"     : 3493.0,   # MW
    "input_H2storage_trans_cap" : 7.,       # GWh
}

BOUNDS: dict[str, tuple[float | None, float | None]] = {
}

EP_EXE   = Path(__file__).parent.parent.parent / "ZipEnergyPLAN163" / "energyPLAN.exe"
DATA_DIR = Path(__file__).parent.parent.parent / "ZipEnergyPLAN163" / "energyPlan Data" / "Data"
REF_FILE = DATA_DIR / "IDA2045_Final.txt"

# =============================================================================
# MODULE-LEVEL STATE  —  set by configure()
# =============================================================================

_case              = None
_base_params       = None
_base_case_params  = None
_shock_case_params = None
_eval_count        = 0
_best_cost         = float("inf")
_best_x            = None


# =============================================================================
# 1. configure
# =============================================================================

def configure(case: str, base_params: dict, base_case_params: dict, shock_case_params: dict) -> None:
    """Set scenario parameters before running. Call once per run."""
    global _case, _base_params, _base_case_params, _shock_case_params
    global _eval_count, _best_cost, _best_x

    if case not in ("base", "shock"):
        raise ValueError(f"case must be 'base' or 'shock', got {case!r}")

    _case              = case
    _base_params       = base_params
    _base_case_params  = base_case_params.copy()
    _shock_case_params = shock_case_params.copy()
    _eval_count        = 0
    _best_cost         = float("inf")
    _best_x            = None


# =============================================================================
# ASCII PARSING HELPERS  (copied from solver.py)
# =============================================================================

_NUM_RE = re.compile(r"""
    ^\s*[-+]?
    (?:
        (?:\d{1,3}(?:[.,]\d{3})+|\d+)(?:[.,]\d+)?
        |(?:[.,]\d+)
    )
    (?:e[-+]?\d+)?\s*$
""", re.IGNORECASE | re.VERBOSE)

_UNIT_RE = re.compile(r"\s*(MW|MWh|GWh|TWh|kW|EUR|MEUR|M\s*EUR)\s*$", re.IGNORECASE)


def _to_number(x: str):
    s = x.strip()
    if s == "":
        return ""
    s_clean = re.sub(r"[%€]", "", s)
    s_clean = _UNIT_RE.sub("", s_clean).strip()
    s0 = s_clean.replace(" ", "")
    if not _NUM_RE.match(s0):
        return s
    if "," in s0 and "." in s0:
        s1 = s0.replace(".", "").replace(",", ".") if s0.rfind(",") > s0.rfind(".") else s0.replace(",", "")
    elif "," in s0 and "." not in s0:
        s1 = s0.replace(",", ".")
    else:
        s1 = s0.replace(",", "")
    try:
        return float(s1)
    except ValueError:
        return s


def _split_line(ln: str) -> list:
    if "\t" in ln:
        return ln.split("\t")
    if ";" in ln:
        return ln.split(";")
    return re.split(r"\s{2,}", ln.rstrip())


def _parse_rows(ascii_path: Path) -> list[list]:
    try:
        text = ascii_path.read_text(encoding="cp1252")
    except UnicodeDecodeError:
        text = ascii_path.read_text(encoding="latin-1")
    rows = []
    for ln in text.splitlines():
        if ln.strip() == "":
            rows.append([""])
        else:
            parts = _split_line(ln)
            rows.append([_to_number(p) for p in parts])
    return rows


def _first_float(row: list, start_col: int = 1) -> float | None:
    for v in row[start_col:]:
        if isinstance(v, float):
            return v
    return None


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="cp1252")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


# =============================================================================
# 2. extract TAC (reused from solver.py)
# =============================================================================

def get_total_annual_cost(rows: list[list]) -> float:
    for raw_idx in [54, 55, 61, 63, 65, 67]:
        if raw_idx >= len(rows):
            continue
        row = rows[raw_idx]
        label = str(row[0]).strip() if row else ""
        if "TOTAL" in label.upper():
            val = _first_float(row)
            if val is not None:
                return val
    for row in rows:
        if not row:
            continue
        label = str(row[0]).strip()
        if "TOTAL" in label.upper() and "ANNUAL" in label.upper():
            val = _first_float(row)
            if val is not None:
                return val
    raise ValueError("Could not find TOTAL ANNUAL COSTS in ASCII output.")


# =============================================================================
# 3. extract import TWh (reused from solver.py)
# =============================================================================

def get_imports_twh(ascii_path: Path) -> float:
    try:
        text = ascii_path.read_text(encoding="cp1252")
    except UnicodeDecodeError:
        text = ascii_path.read_text(encoding="latin-1")

    lines = text.splitlines()
    if len(lines) < 85:
        print("  WARNING: ASCII output too short to find electricity imports.", flush=True)
        return 0.0

    h1     = lines[80].split("\t")
    h2     = lines[81].split("\t")
    annual = lines[84].split("\t")

    for i, (a, b) in enumerate(zip(h1, h2)):
        if f"{a.strip()}_{b.strip()}" == "Import_Electr." and i < len(annual):
            try:
                return float(annual[i].strip().replace(",", "."))
            except ValueError:
                pass

    print("  WARNING: 'Import_Electr.' column not found — constraint not enforced.", flush=True)
    return 0.0


# =============================================================================
# 6. extract CSHP investment cost to subtract
# =============================================================================

def _get_cshp_investment(text: str) -> float:
    """Return annual_inv + O&M for 'Indust. CHP Heat'; 0.0 if not found."""
    lines = text.splitlines()
    inv_start: int | None = None
    for i, ln in enumerate(lines):
        parts = ln.rstrip("\n").split("\t")
        if len(parts) > 6 and parts[6].strip() == "OVERVIEW OF INVESTMENT COSTS":
            inv_start = i
            break
    if inv_start is None:
        return 0.0
    for ln in lines[inv_start + 4:]:
        parts = ln.rstrip("\n").split("\t")
        if len(parts) < 10:
            break
        name = parts[6].strip()
        if not name:
            break
        if name == CSHP_EXCL:
            annual = _to_number(parts[8])
            om     = _to_number(parts[9])
            if isinstance(annual, float) and isinstance(om, float):
                return annual + om
    return 0.0


# =============================================================================
# 7. extract annual VRE and nuclear production
# =============================================================================

_ANNUAL_COLS = frozenset({
    "Offshore_Electr.", "Wind_Electr.", "PV_Electr.", "Nuclear_Electr.",
})


def _get_annual(text: str) -> dict[str, float]:
    """Extract annual production (TWh) for VRE and nuclear from the Annual: row."""
    lines = text.splitlines()

    h1_idx: int | None = None
    for i in range(len(lines) - 1):
        parts = lines[i].split("\t")
        if parts[0].strip() == "" and len(parts) > 80:
            nxt = lines[i + 1].split("\t")
            if nxt[0].strip() == "" and len(nxt) > 80:
                h1_idx = i
                break
    if h1_idx is None:
        return {c: 0.0 for c in _ANNUAL_COLS}

    h1 = [p.strip() for p in lines[h1_idx].split("\t")]
    h2 = [p.strip() for p in lines[h1_idx + 1].split("\t")]
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

    col_idx = {c: i for i, c in enumerate(col_names) if c in _ANNUAL_COLS}

    for ln in lines[h1_idx + 2:]:
        parts = ln.split("\t")
        if re.match(r"^Annual\b", parts[0].strip(), re.IGNORECASE):
            result: dict[str, float] = {}
            for col, idx in col_idx.items():
                if idx + 1 < len(parts):
                    v = _to_number(parts[idx + 1])
                    result[col] = v if isinstance(v, float) else 0.0
                else:
                    result[col] = 0.0
            return result

    return {c: 0.0 for c in _ANNUAL_COLS}


# =============================================================================
# 8. objective function
# =============================================================================

def objective(x: np.ndarray) -> float:
    global _eval_count, _best_cost, _best_x

    if _case is None:
        raise RuntimeError("Call solver.configure(...) before running.")

    _eval_count += 1

    if any(v <= 0 for v in x):
        return 1e12

    # bounds penalty
    bounds_penalty = 0.0
    bounds_tags: list[str] = []
    for name, val in zip(X0.keys(), x):
        lo, hi = BOUNDS.get(name, (None, None))
        if lo is not None and val < lo:
            bounds_penalty += BOUNDS_PENALTY * (lo - val)
            bounds_tags.append(f"{name.split('_cap_')[-1][:8]}<{lo:.0f}")
        if hi is not None and val > hi:
            bounds_penalty += BOUNDS_PENALTY * (val - hi)
            bounds_tags.append(f"{name.split('_cap_')[-1][:8]}>{hi:.0f}")
    if bounds_penalty > 0:
        var_str = "  ".join(f"{k.split('_cap_')[-1].split('_el')[0][:6]}={v:7.1f}" for k, v in zip(X0.keys(), x))
        print(f"  [{_eval_count:3d}] {var_str}  → bounds violated: {', '.join(bounds_tags)}", flush=True)
        return bounds_penalty

    # build scenario and run EnergyPLAN
    params = build_params(_case, _base_params, _base_case_params, _shock_case_params)
    for name, val in zip(X0.keys(), x):
        params[name] = val

    tmp_input = DATA_DIR / f"_solver_{_case}.txt"
    tmp_ascii = ROOT / "0_EP_runs" / f"_solver_{_case}_ascii.txt"

    lines_ep, value_idx = load_energyplan_file(REF_FILE)
    for name, val in params.items():
        if name not in value_idx:
            raise KeyError(f"Parameter not in EnergyPLAN file: {name!r}")
        lines_ep[value_idx[name]] = format_value(val)

    with open(tmp_input, "w", encoding="utf-16") as fh:
        fh.writelines(lines_ep)

    tmp_ascii.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    res = subprocess.run(
        [str(EP_EXE), "-i", str(tmp_input), "-ascii", str(tmp_ascii)],
        capture_output=True, text=True,
    )
    elapsed = time.perf_counter() - t0

    if res.returncode != 0 or not tmp_ascii.exists():
        print(f"  [{_eval_count:3d}] EnergyPLAN failed — penalty returned", flush=True)
        return 1e12

    # 1. TAC from EnergyPLAN
    rows = _parse_rows(tmp_ascii)
    try:
        tac = get_total_annual_cost(rows)
    except ValueError as e:
        print(f"  [{_eval_count:3d}] Parse error: {e}", flush=True)
        return 1e12

    # 2. corrections (all from the same text read)
    text     = _read_text(tmp_ascii)
    cshp_inv = _get_cshp_investment(text)

    # 3. add external system costs
    annual  = _get_annual(text)
    ve_prod = (annual.get("Offshore_Electr.", 0.0)
               + annual.get("Wind_Electr.",   0.0)
               + annual.get("PV_Electr.",     0.0))
    kk_prod =  annual.get("Nuclear_Electr.", 0.0)
    sys_ve  = ve_prod * VRE_RATE
    sys_kk  = kk_prod * KK_RATE

    cost = tac - cshp_inv + sys_ve + sys_kk 

    # import constraint
    imports_twh = get_imports_twh(tmp_ascii)
    violation   = max(0.0, imports_twh - IMPORT_LIMIT_TWH)
    penalised   = cost + IMPORT_PENALTY * violation

    marker  = " *" if penalised < _best_cost else "  "
    imp_tag = f"  [IMPORT {imports_twh:.2f} > {IMPORT_LIMIT_TWH}!]" if violation > 0 else ""
    var_str = "  ".join(f"{k.split('_cap_')[-1].split('_el')[0][:6]}={v:7.1f}" for k, v in zip(X0.keys(), x))
    print(
        f"{marker}[{_eval_count:3d}] {var_str}  "
        f"→ 5cost={cost:8.2f} MEUR  "
        f"[TAC={tac:.0f}  -cshp={cshp_inv:.1f}  +sys={sys_ve + sys_kk:.1f}]  "
        f"imports={imports_twh:.3f} TWh  ({elapsed:.1f}s){imp_tag}",
        flush=True,
    )

    if penalised < _best_cost:
        _best_cost = penalised
        _best_x    = x.copy()

    return penalised


# =============================================================================
# 7. run
# =============================================================================

def run(x0: dict | None = None, max_evaluations: int | None = None) -> dict:
    """
    Run Nelder-Mead on the 5_cost objective. Same API as solver.run().

    Returns dict with keys: 'best_cost', 'best_x', 'result'.
    """
    if _case is None:
        raise RuntimeError("Call solver.configure(...) before solver.run().")

    _x0    = np.array(list((x0 or X0).values()), dtype=float)
    maxfev = max_evaluations or MAX_EVALUATIONS

    print("=" * 70, flush=True)
    print(f"EnergyPLAN 5_cost minimiser  (case='{_case}', {maxfev} max evals)", flush=True)
    print(f"  Choice vars ({len(_x0)}): " + ",  ".join(f"{k}={v:.0f}" for k, v in zip(X0.keys(), _x0)), flush=True)
    print(f"  Import limit : {IMPORT_LIMIT_TWH} TWh", flush=True)
    print(f"  Objective    : TAC - cshp_inv + ve_prod*(145/7.45) + kk_prod*(10/7.45)", flush=True)
    active_bounds = [(k, lo, hi) for k, (lo, hi) in BOUNDS.items() if lo is not None or hi is not None]
    if active_bounds:
        for k, lo, hi in active_bounds:
            lo_s = f">= {lo}" if lo is not None else ""
            hi_s = f"<= {hi}" if hi is not None else ""
            print(f"  Bound: {k}  {lo_s}{' ' if lo_s and hi_s else ''}{hi_s}", flush=True)
    print("=" * 70, flush=True)

    result = minimize(
        objective,
        _x0,
        method="Nelder-Mead",
        options={
            "maxfev"  : maxfev,
            "maxiter" : maxfev * 1000,
            "xatol"   : 1e-6,
            "fatol"   : 1e-6,
            "adaptive": True,
            "disp"    : False,
        },
    )

    best_x = _best_x if _best_x is not None else result.x

    print("\n" + "=" * 70, flush=True)
    print(f"Finished after {_eval_count} evaluations  (converged: {result.success})", flush=True)
    print(f"  Best 5_cost : {_best_cost:.2f} MEUR", flush=True)
    print("  Best parameters:", flush=True)
    for name, val in zip(X0.keys(), best_x):
        print(f"    {name:<35s} = {val:.3f}", flush=True)
    print("=" * 70, flush=True)

    return {"best_cost": _best_cost, "best_x": best_x, "result": result}


if __name__ == "__main__":
    raise SystemExit(
        "solver.py is designed to be called from a notebook via configure() + run().\n"
        "See the docstring at the top of this file for usage."
    )
