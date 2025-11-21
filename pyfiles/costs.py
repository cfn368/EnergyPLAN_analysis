# pyfiles/costs.py

import pandas as pd
import numpy as np
import pyfiles.ep_run_v2 as ep_run_v2


# ==================== ==================== ==================== ====================
# 1. load cost scalars for one run
def get_costs(name):
    """
    Return cost summary for one run as a single-row DataFrame.
    Reads from _scalars.parquet produced by ep_run_v2.
    """
    s = ep_run_v2.load_scalars(name)
    stem = ep_run_v2._stem(name)
    row = {
        'Variable costs':          s.get('var_costs_MEUR'),
        'Fixed operation costs':   s.get('fixed_costs_MEUR'),
        'Annual Investment costs': s.get('inv_costs_MEUR'),
        'TOTAL ANNUAL COSTS':      s.get('total_costs_MEUR'),
        'Import':                  s.get('elec_exchange_MEUR'),
    }
    return pd.DataFrame([row], index=pd.Index([stem], name='Case (M EUR)'))


# ==================== ==================== ==================== ====================
# 2. load investment cost breakdown for one run
def waterfall_inv(name):
    """
    Return investment overview for one run.
    Reads from _investments.parquet produced by ep_run_v2.
    """
    df = ep_run_v2.load_investments(name).copy()
    df['run'] = name
    df['annuity'] = df['annual_inv'] + df['O&M']
    return df


# ==================== ==================== ==================== ====================
# 3. load variable cost breakdown for one run
def waterfall_var(name):
    """
    Return variable-cost breakdown for one run.
    Reads from _scalars.parquet produced by ep_run_v2.
    """
    s = ep_run_v2.load_scalars(name)
    rows = [
        {"variable_costs": "Fuel ex. Ngas exchange",   "MEUR": s.get("fuel_ex_ngas_MEUR")},
        {"variable_costs": "Ngas Exchange costs",       "MEUR": s.get("ngas_exchange_MEUR")},
        {"variable_costs": "Marginal operation costs",  "MEUR": s.get("var_marginal_MEUR")},
        {"variable_costs": "Electricity exchange",      "MEUR": s.get("elec_exchange_MEUR")},
        {"variable_costs": "CO2 emission costs",        "MEUR": s.get("co2_costs_MEUR")},
    ]
    df = pd.DataFrame(rows)
    df["run"] = name
    return df
