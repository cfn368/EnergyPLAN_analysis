import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import itertools
import builtins
import numpy as np

# aggregator helper
def aggregate_heat_units(df):
    """
    Aggregate unit-specific heat columns into tech-level aggregates
    and drop the original unit columns.

    Returns a *copy* of df with new columns:
    - Solar_tot_Heat
    - CSHP_tot_Heat
    - CHP_tot_Heat
    - HP_tot_Heat
    """
    agg_map = {
        'Solar_tot_Heat': ['Solar_Heat', 'Solar2_Heat'],
        'CSHP_tot_Heat':  ['CSHP 2_Heat', 'CSHP 3_Heat'],
        'CHP_tot_Heat':   ['CHP 2_Heat', 'CHP 3_Heat'],
        'HP_tot_Heat':    ['HP 2_Heat', 'HP 3_Heat'],
        'Storage_Heat':   ['Storage2_Heat','Storage3_Heat']
    }

    df = df.copy()

    # create aggregates
    for new_col, old_cols in agg_map.items():
        existing = [c for c in old_cols if c in df.columns]
        if existing:
            df[new_col] = df[existing].sum(axis=1)

    # drop originals
    cols_to_drop = {c for cols_ in agg_map.values() for c in cols_ if c in df.columns}
    if cols_to_drop:
        df = df.drop(columns=list(cols_to_drop))

    return df

# -------------------------------------------------------------------------------
# 1. Core loader: ONE file -> cleaned hourly dataframe
# -------------------------------------------------------------------------------

def timeseries_hourly(excel_path, sheet_name=0):
    """
    Read EnergyPLAN-style Excel output and return hourly df.
    """
    df_ = pd.read_excel('0_EP_runs/' + excel_path, sheet_name=sheet_name)

    # 1. eliminate initial rows
    df = df_[df_.index >= 79].copy()

    # 2. merge top two header rows
    df.columns = [
        f"{str(col1).strip()}_{str(col2).strip()}" if col2 else str(col1).strip()
        for col1, col2 in zip(df.iloc[0], df.iloc[1])
    ]
    df = df.iloc[2:].reset_index(drop=True)

    # 3. select data (same rule as before: index >= 23)
    hourly = df[df.index >= 23].copy()

    # 4. ensure numeric
    hourly = hourly.apply(pd.to_numeric, errors='coerce')

    # 5a. enforce that the *first* column is called 'hour'
    first_col = hourly.columns[0]
    hourly = hourly.rename(columns={first_col: "hour"})

    # 5b. if there were any duplicate 'hour' columns, keep the first
    hourly = hourly.loc[:, ~hourly.columns.duplicated()]

    # 5c. add tag and summer dummy
    hourly["source"] = Path(excel_path).stem   # use the actual file, not hardcoded
    hourly["d_summer"] = (hourly["hour"] >= 3649) & (hourly["hour"] < 5857)

    # 6. arrange columns: hour, source, d_summer, rest...
    cols = hourly.columns.tolist()
    cols.remove("source")
    cols.remove("d_summer")
    cols.insert(1, "source")
    cols.insert(2, "d_summer")
    hourly = hourly[cols]

    # 7. aggregate heat units
    hourly = aggregate_heat_units(hourly)

    return hourly


# -------------------------------------------------------------------------------
# 2. Multi-case plotting: MANY files -> one plot per variable, one line per case
# -------------------------------------------------------------------------------

def plot_metrics(files, plots=None, sheet_name=0, case_labels=None, tech_labels=None,colors=None):
    """
    For a list of Excel filenames, produce one plot per variable in `plots`,
    with one line per case (file).
    """

    # load data for all cases
    dfs = [timeseries_hourly(f, sheet_name=sheet_name) for f in files]

    # default variables to plot if none given
    if plots is None:
        plots = [
            'Storage2_Heat',
            'Storage3_Heat',
            'V2G_Storage',
            'Storage_Content',
            'Store_Storage',
            'H2_Storage',
        ]

    plots = list(plots)

    # keep only those that exist in ALL dfs (robust to missing cols)
    cols_missing = [col for col in plots if not all(col in d.columns for d in dfs)]
    if cols_missing:
        print("Warning: missing in at least one file and will be skipped:", cols_missing)

    plots_valid = [col for col in plots if col not in cols_missing]

    linestyles = ['-', ':', ':', ':']

    for col in plots_valid:
        fig, ax = plt.subplots(figsize=(12, 5))

        # set up color iterator (very simple)
        if colors is None:
            color_iter = itertools.cycle([None])   # use mpl defaults
        else:
            color_iter = itertools.cycle(colors)   # cycle given colors

        for f, d, ls in zip(files, dfs, itertools.cycle(linestyles)):
            stem = Path(f).stem

            # pretty case labels
            if case_labels is not None:
                label = case_labels.get(stem, stem)
            else:
                label = stem

            c = next(color_iter)

            if c is None:
                ax.plot(
                    d["hour"], d[col],
                    linewidth=1.2,
                    linestyle=ls,
                    label=label,
                )
            else:
                ax.plot(
                    d["hour"], d[col],
                    linewidth=1.2,
                    linestyle=ls,
                    label=label,
                    color=c,
                )

        ax.set_xlabel("Hour")
        ax.set_ylabel("MW")

        # pretty tech name for title if available
        if tech_labels is not None:
            pretty_name = tech_labels.get(col, col)
        else:
            pretty_name = col

        ax.set_title(pretty_name)
        ax.grid(True, which="both", linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()

# -------------------------------------------------------------------------------
# 3. Same but for months
# -------------------------------------------------------------------------------

def timeseries_months(excel_path, sheet_name=0):
    """
    Replica of 'timeseries' but for months.
    """
    df_ = pd.read_excel('0_EP_runs/' + excel_path, sheet_name=sheet_name)

    df = df_[df_.index >= 79].copy()

    df.columns = [
        f"{str(col1).strip()}_{str(col2).strip()}" if col2 else str(col1).strip()
        for col1, col2 in zip(df.iloc[0], df.iloc[1])
    ]
    df = df.iloc[2:].reset_index(drop=True)

    # 3. select data (months: index 5–16)
    monthly = df[(df.index >= 5) & (df.index <= 16)].copy()

    # 4. rename first column to 'month' BEFORE numeric conversion
    first_col = monthly.columns[0]
    monthly = monthly.rename(columns={first_col: "month"})
    monthly = monthly.loc[:, ~monthly.columns.duplicated()]
    monthly["source"] = Path(excel_path).stem

    # put 'source' as second column
    cols = monthly.columns.tolist()
    cols.remove("source")
    cols.insert(1, "source")
    monthly = monthly[cols]

    # 5. ensure numeric for data columns only (not month/source)
    data_cols = [c for c in monthly.columns if c not in ["month", "source"]]
    monthly[data_cols] = monthly[data_cols].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # aggregate heat units
    monthly = aggregate_heat_units(monthly)

    return monthly

def plot_metrics_months(
    files,
    plots=None,
    sheet_name=0,
    case_labels=None,
    tech_labels=None,
    colors=None,      # NEW
):
    """
    Replica of 'plot_metrics' but for months.

    case_labels : dict or None
        Mapping file stem -> pretty scenario name for legend.
    tech_labels : dict or None
        Mapping column name -> pretty technology name for title.
    """

    # load data for all cases
    dfs = [timeseries_months(f, sheet_name=sheet_name) for f in files]

    # default variables to plot if none given
    if plots is None:
        plots = [
            'Storage2_Heat',
            'Storage3_Heat',
            'V2G_Storage',
            'Storage_Content',
            'Store_Storage',
            'H2_Storage',
        ]

    plots = list(plots)

    linestyles = ['-', '--', ':', '-.']

    for col in plots:
        fig, ax = plt.subplots(figsize=(12, 5))

        drew_any = False  # track if we actually plotted something

        # --- set up color iterator (same logic as hourly version) ---
        if colors is None:
            color_iter = itertools.cycle([None])   # use mpl defaults
        else:
            color_iter = itertools.cycle(colors)   # cycle given colors

        # one line per case
        for f, d, ls in zip(files, dfs, itertools.cycle(linestyles)):
            if col not in d.columns:
                continue  # this df simply doesn't have this variable

            stem = Path(f).stem
            if case_labels is not None:
                label = case_labels.get(stem, stem)
            else:
                label = stem

            c = next(color_iter)

            if c is None:
                ax.plot(
                    d["month"], d[col],
                    linewidth=1.2,
                    linestyle=ls,
                    label=label,
                )
            else:
                ax.plot(
                    d["month"], d[col],
                    linewidth=1.2,
                    linestyle=ls,
                    label=label,
                    color=c,
                )

            drew_any = True

        if not drew_any:
            plt.close(fig)
            print(f"Skipping '{col}': not found in any monthly dataframe.")
            continue

        ax.set_xlabel("Month")
        ax.set_ylabel('MW')

        # pretty tech label as title
        if tech_labels is not None:
            pretty_name = tech_labels.get(col, col)
        else:
            pretty_name = col
        ax.set_title(pretty_name)

        ax.grid(True, which="both", linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()
        plt.show()

# -------------------------------------------------------------------
# 4. yearly columns
# -------------------------------------------------------------------

def timeseries_yearly(excel_path, sheet_name=0):
    """
    Read EnergyPLAN-style Excel output and return a 1-row df
    with annual totals for all variables, plus a 'source' column.
    """

    df_ = pd.read_excel(
        '0_EP_runs/' + excel_path,
        sheet_name=sheet_name,
        decimal=','
    )

    # 1. drop initial junk rows
    df = df_[df_.index >= 79].copy()

    # 2. merge top two header rows
    df.columns = [
        f"{str(col1).strip()}_{str(col2).strip()}" if col2 else str(col1).strip()
        for col1, col2 in zip(df.iloc[0], df.iloc[1])
    ]
    df = df.iloc[2:].reset_index(drop=True)

    # 3. pick the annual row (index == 2)
    annual = df[df.index == 2].copy()

    # 4. rename first column and drop it
    first_col = annual.columns[0]
    annual = annual.rename(columns={first_col: "Annual (TWh/year)"})
    annual = annual.drop(columns=["Annual (TWh/year)"])

    # 5. ensure numeric
    annual = annual.apply(pd.to_numeric, errors='coerce')

    # 6. add source
    annual["source"] = Path(excel_path).stem

    # 7. put source first
    cols = annual.columns.tolist()
    cols.remove("source")
    cols.insert(0, "source")
    annual = annual[cols]

    # 8. aggregate heat units
    annual = aggregate_heat_units(annual)

    return annual

def plot_metrics_yearly(files, plots=None, sheet_name=0,
                        case_labels=None, tech_labels=None):
    """
    For a list of Excel filenames, make one bar plot per variable in `plots`,
    with one bar per case (file).

    case_labels : dict or None
        Mapping file stem or source name -> pretty scenario name (x-axis).
    tech_labels : dict or None
        Mapping column name -> pretty name for the bar-chart title.
    """

    # 1. load annual data for all cases
    dfs = [timeseries_yearly(f, sheet_name=sheet_name) for f in files]
    annual_all = pd.concat(dfs, ignore_index=True)

    # 2. figure out which variables to plot
    if plots is None:
        plots = annual_all.select_dtypes(include="number").columns.tolist()
    plots = list(plots)

    # keep only those that exist
    plots_valid = [col for col in plots if col in annual_all.columns]
    if not plots_valid:
        raise ValueError("No valid annual columns to plot.")

    # ensure numeric (robust if something slipped in as string)
    for col in plots_valid:
        if annual_all[col].dtype == 'O':
            annual_all[col] = pd.to_numeric(
                annual_all[col].astype(str)
                               .str.replace('.', '', regex=False)
                               .str.replace(',', '.', regex=False),
                errors='coerce'
            )

    # source labels
    sources = annual_all["source"].tolist()

    # map to pretty names if dict provided
    if case_labels is not None:
        display_sources = [case_labels.get(s, s) for s in sources]
    else:
        display_sources = sources

    x_pos = np.arange(len(sources))
    n_cases = len(sources)

    # width scaling with number of files
    fig_width = max(4, 0.9 * n_cases + 2)

    # 3. plot one figure per variable
    for col in plots_valid:
        fig, ax = plt.subplots(figsize=(fig_width, 4))

        ax.bar(x_pos, annual_all[col].values, width=0.6)

        # x labels
        ax.set_xticks(x_pos)
        ax.set_xticklabels(display_sources, rotation=0, ha="center")

        # labels & title
        ax.set_ylabel("TWh/year")

        if tech_labels is not None:
            pretty_name = tech_labels.get(col, col)
        else:
            pretty_name = col
        ax.set_title(pretty_name)

        # zero line
        ax.axhline(0, linewidth=0.8, color="black")

        # grid only on y, light
        ax.grid(axis="y", linestyle="-", linewidth=0.5, alpha=0.3)
        ax.set_axisbelow(True)

        # remove top/right spines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # inward ticks
        ax.tick_params(axis='x', direction='in', length=3)
        ax.tick_params(axis='y', direction='in', length=3)

        plt.tight_layout()

