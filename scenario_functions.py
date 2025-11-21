from pathlib import Path

def load_energyplan_file(path):
    """Load EnergyPLAN .txt and return (lines, value_index_by_name).

    We map parameter names WITHOUT trailing '=' so that
    'Input_el_demand_Twh' matches a line 'Input_el_demand_Twh='.
    """
    # note: encoding changed to 'utf-16'
    with open(path, encoding="utf-16") as f:
        lines = f.readlines()

    value_idx = {}

    for i in range(0, len(lines) - 1, 2):
        raw_name = lines[i].strip()   # 'Input_el_demand_Twh='
        key = raw_name.rstrip("=")    # 'Input_el_demand_Twh'
        value_idx[key] = i + 1

    return lines, value_idx


def format_value(v):
    """Format new value for EnergyPLAN (comma decimal, newline)."""
    if isinstance(v, (int, float)):
        s = f"{v}"          # or f"{v:.2f}" if you want fixed decimals
    else:
        s = str(v)

    if not s.endswith("\n"):
        s = s + "\n"
    return s


def build_params(case: str, base_params, base_case_params, shock_case_params):
    """Return combined parameter dict given case."""
    params = base_params.copy()

    if case == "base":
        params.update(base_case_params)
    elif case == "shock":
        params.update(shock_case_params)
    else:
        raise ValueError(f"Unknown case: {case}")

    return params
