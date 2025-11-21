# pyfiles/scenario_functions.py

from pathlib import Path


# ==================== ==================== ==================== ====================
# 1. load EnergyPLAN parameter file
def load_energyplan_file(path):
    """Load EnergyPLAN .txt and return (lines, value_index_by_name).

    Parameter names are mapped WITHOUT the trailing '=' so that
    'Input_el_demand_Twh' matches a line 'Input_el_demand_Twh='.
    """
    # 1. read UTF-16 encoded file
    with open(path, encoding="utf-16") as f:
        lines = f.readlines()

    # 2. build name -> line-index map (strip trailing '=' from keys)
    value_idx = {}
    for i in range(0, len(lines) - 1, 2):
        raw_name = lines[i].strip()   # e.g. 'Input_el_demand_Twh='
        key = raw_name.rstrip("=")    # e.g. 'Input_el_demand_Twh'
        value_idx[key] = i + 1

    return lines, value_idx


# ==================== ==================== ==================== ====================
# 2. format a parameter value for writing to EnergyPLAN file
def format_value(v):
    """Format a new value for EnergyPLAN (plain number string, terminated with newline)."""
    if isinstance(v, (int, float)):
        s = f"{v}"
    else:
        s = str(v)

    if not s.endswith("\n"):
        s = s + "\n"
    return s


# ==================== ==================== ==================== ====================
# 3. build combined parameter dict for a given case
def build_params(case: str, base_params, base_case_params, shock_case_params):
    """Return merged parameter dict for the requested case ('base' or 'shock')."""
    params = base_params.copy()

    if case == "base":
        params.update(base_case_params)
    elif case == "shock":
        params.update(shock_case_params)
    else:
        raise ValueError(f"Unknown case: {case}")

    return params
