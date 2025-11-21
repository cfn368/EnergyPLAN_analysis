# pyfiles/build_frames.py

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import itertools
import builtins
import numpy as np
import pyfiles.ep_run_v2 as ep_run_v2


# ==================== ==================== ==================== ====================
# 1. aggregate unit-specific heat columns into tech-level totals
def aggregate_heat_units(df):
    """
    Aggregate unit-specific heat columns into tech-level aggregates
    and drop the original unit columns.

    Returns a *copy* of df with new columns:
      Solar_tot_Heat, CSHP_tot_Heat, CHP_tot_Heat, HP_tot_Heat, Storage_Heat
    """
    agg_map = {
        'Solar_tot_Heat': ['Solar_Heat',    'Solar2_Heat'],
        'CSHP_tot_Heat':  ['CSHP 2_Heat',   'CSHP 3_Heat'],
        'CHP_tot_Heat':   ['CHP 2_Heat',    'CHP 3_Heat'],
        'HP_tot_Heat':    ['HP 2_Heat',     'HP 3_Heat'],
        'Storage_Heat':   ['Storage2_Heat', 'Storage3_Heat'],
    }

    df = df.copy()

    # 1. create aggregate columns
    for new_col, old_cols in agg_map.items():
        existing = [c for c in old_cols if c in df.columns]
        if existing:
            df[new_col] = df[existing].sum(axis=1)

    # 2. drop original unit columns
    cols_to_drop = {c for cols_ in agg_map.values() for c in cols_ if c in df.columns}
    if cols_to_drop:
        df = df.drop(columns=list(cols_to_drop))

    return df


# ==================== ==================== ==================== ====================
# 2. load hourly timeseries for one run
def timeseries_hourly(name):
    """
    Return hourly DataFrame for one run (8760 rows × named columns).
    Reads from _hourly.parquet produced by ep_run_v2.
    """
    hourly = ep_run_v2.load_hourly(name)

    # 1. add metadata columns
    stem = ep_run_v2._stem(name)
    hourly["source"]   = stem
    hourly["d_summer"] = (hourly["hour"] >= 3649) & (hourly["hour"] < 5857)

    # 2. reorder: hour, source, d_summer, then all other columns
    cols = hourly.columns.tolist()
    cols.remove("source")
    cols.remove("d_summer")
    cols.insert(1, "source")
    cols.insert(2, "d_summer")
    hourly = hourly[cols]

    # 3. aggregate heat unit columns
    hourly = aggregate_heat_units(hourly)

    return hourly


# ==================== ==================== ==================== ====================
# 3. plot hourly timeseries for multiple runs
def plot_metrics(
    dfs,
    plots=None,
    case_labels=None,
    tech_labels=None,
    colors=None,
    bg_color=None,
    fill_alpha=0.0,
    save_dir=None,
    dpi=150,
):
    if dfs is None or len(dfs) == 0:
        raise ValueError("`dfs` must be a non-empty list of DataFrames.")

    # 1. default variables to plot
    if plots is None:
        plots = [
            'V2G_Storage',
            'Storage_Content',
            'Store_Storage',
            'H2_Storage',
        ]
    plots = list(plots)

    # 2. drop variables missing in at least one df
    cols_missing = [col for col in plots if not all(col in d.columns for d in dfs)]
    if cols_missing:
        print("Warning: missing in at least one df and will be skipped:", cols_missing)

    plots_valid = [col for col in plots if col not in cols_missing]
    if not plots_valid:
        print("No valid columns to plot.")
        return

    # 3. build case IDs for legend lookup
    case_ids = []
    for i, d in enumerate(dfs):
        if "source" in d.columns:
            case_ids.append(str(d["source"].iloc[0]))
        else:
            case_ids.append(f"case_{i}")

    # 4. plot one figure per variable
    linestyles = ['-', ':', ':', ':']

    for col in plots_valid:
        fig, ax = plt.subplots(figsize=(12, 5))

        if bg_color is not None:
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)
            for spine in ax.spines.values():
                spine.set_edgecolor("#9ab4c8")

        if colors is None:
            color_cycle = plt.rcParams['axes.prop_cycle'].by_key().get('color', [])
            color_iter = itertools.cycle(color_cycle) if color_cycle else itertools.cycle([None])
        else:
            color_iter = itertools.cycle(colors)

        for case_id, d, ls in zip(case_ids, dfs, itertools.cycle(linestyles)):
            label = case_labels.get(case_id, case_id) if case_labels is not None else case_id
            c = next(color_iter)

            if fill_alpha > 0:
                ax.fill_between(d["hour"], 0, d[col], alpha=fill_alpha, color=c, linewidth=0)

            ax.plot(d["hour"], d[col], linewidth=1.2, linestyle=ls, label=label, color=c)

        ax.set_xlabel("Hour")
        ax.set_ylabel("MW")

        pretty_name = tech_labels.get(col, col) if tech_labels is not None else col
        ax.set_title(pretty_name)

        if bg_color is not None:
            ax.grid(True, which="major", linestyle="-", color="white", alpha=0.5)
        else:
            ax.grid(True, which="both", linestyle="--", alpha=0.4)

        ax.legend(
            loc='upper center',
            bbox_to_anchor=(0.5, -0.18),
            ncols=2,
            facecolor=bg_color if bg_color is not None else "white",
            edgecolor="#9ab4c8" if bg_color is not None else "0.8",
            frameon=True,
        )
        plt.tight_layout()

        if save_dir is not None:
            save_dir = Path(save_dir)
            save_dir.mkdir(parents=True, exist_ok=True)
            fname = pretty_name.replace(' ', '_').replace('/', '-') + '.png'
            fig.savefig(save_dir / fname, bbox_inches='tight', dpi=dpi)


# ==================== ==================== ==================== ====================
# 4. load monthly timeseries for one run
def timeseries_months(name):
    """
    Return monthly-average DataFrame for one run (12 rows × named columns).
    Reads from _monthly.parquet produced by ep_run_v2.
    """
    monthly = ep_run_v2.load_monthly(name)

    # 1. move month-name index into a regular column
    monthly = monthly.reset_index().rename(columns={"index": "month"})

    # 2. insert source label
    stem = ep_run_v2._stem(name)
    monthly.insert(1, "source", stem)

    # 3. aggregate heat unit columns
    monthly = aggregate_heat_units(monthly)

    return monthly
