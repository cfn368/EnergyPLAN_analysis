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

def plot_metrics(
    dfs,
    plots=None,
    case_labels=None,
    tech_labels=None,
    colors=None,
):

    if dfs is None or len(dfs) == 0:
        raise ValueError("`dfs` must be a non-empty list of DataFrames.")

    # ------------------------------------------------------------------
    # 1. default variables to plot
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 2. drop variables that are missing in at least one df
    # ------------------------------------------------------------------
    cols_missing = [col for col in plots if not all(col in d.columns for d in dfs)]
    if cols_missing:
        print("Warning: missing in at least one df and will be skipped:", cols_missing)

    plots_valid = [col for col in plots if col not in cols_missing]
    if not plots_valid:
        print("No valid columns to plot.")
        return

    # ------------------------------------------------------------------
    # 3. build case IDs for legend lookup
    # ------------------------------------------------------------------
    case_ids = []
    for i, d in enumerate(dfs):
        if "source" in d.columns:
            case_ids.append(str(d["source"].iloc[0]))
        else:
            case_ids.append(f"case_{i}")

    # ------------------------------------------------------------------
    # 4. plotting
    # ------------------------------------------------------------------
    linestyles = ['-', ':', ':', ':']  # cycle if more cases

    for col in plots_valid:
        fig, ax = plt.subplots(figsize=(12, 5))

        # color iterator
        if colors is None:
            color_iter = itertools.cycle([None])  # mpl defaults
        else:
            color_iter = itertools.cycle(colors)

        for case_id, d, ls in zip(case_ids, dfs, itertools.cycle(linestyles)):

            # label for legend
            if case_labels is not None:
                label = case_labels.get(case_id, case_id)
            else:
                label = case_id

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

# def plot_metrics_months(
#     dfs,
#     plots=None,
#     case_labels=None,
#     tech_labels=None,
#     colors=None,
# ):

#     if dfs is None or len(dfs) == 0:
#         raise ValueError("`dfs` must be a non-empty list of DataFrames.")

#     # --- default variables to plot ---
#     if plots is None:
#         plots = [
#             'Storage2_Heat',
#             'Storage3_Heat',
#             'V2G_Storage',
#             'Storage_Content',
#             'Store_Storage',
#             'H2_Storage',
#         ]
#     plots = list(plots)

#     # --- drop vars missing in some dfs (like hourly version) ---
#     cols_missing = [col for col in plots if not all(col in d.columns for d in dfs)]
#     if cols_missing:
#         print("Warning (monthly): missing in at least one df and will be skipped:", cols_missing)

#     plots_valid = [col for col in plots if col not in cols_missing]
#     if not plots_valid:
#         print("No valid monthly columns to plot.")
#         return

#     # --- build case IDs from 'source' or fallback ---
#     case_ids = []
#     for i, d in enumerate(dfs):
#         if "source" in d.columns:
#             case_ids.append(str(d["source"].iloc[0]))
#         else:
#             case_ids.append(f"case_{i}")

#     linestyles = ['-', '--', ':', '-.']

#     for col in plots_valid:
#         fig, ax = plt.subplots(figsize=(12, 5))

#         if colors is None:
#             color_iter = itertools.cycle([None])   # mpl defaults
#         else:
#             color_iter = itertools.cycle(colors)   # cycle given colors

#         drew_any = False

#         # one line per case
#         for case_id, d, ls in zip(case_ids, dfs, itertools.cycle(linestyles)):
#             if col not in d.columns:
#                 continue

#             # legend label
#             if case_labels is not None:
#                 label = case_labels.get(case_id, case_id)
#             else:
#                 label = case_id

#             c = next(color_iter)

#             if c is None:
#                 ax.plot(
#                     d["month"], d[col],
#                     linewidth=1.2,
#                     linestyle=ls,
#                     label=label,
#                 )
#             else:
#                 ax.plot(
#                     d["month"], d[col],
#                     linewidth=1.2,
#                     linestyle=ls,
#                     label=label,
#                     color=c,
#                 )

#             drew_any = True

#         if not drew_any:
#             plt.close(fig)
#             print(f"Skipping '{col}': not found in any monthly dataframe.")
#             continue

#         ax.set_xlabel("Month")
#         ax.set_ylabel("MW")

#         if tech_labels is not None:
#             pretty_name = tech_labels.get(col, col)
#         else:
#             pretty_name = col
#         ax.set_title(pretty_name)

#         ax.grid(True, which="both", linestyle="--", alpha=0.4)
#         ax.legend()
#         plt.tight_layout()
#         plt.show()

# -------------------------------------------------------------------
# 4. yearly columns
# -------------------------------------------------------------------

# def timeseries_yearly(excel_path, sheet_name=0):
#     """
#     Read EnergyPLAN-style Excel output and return a 1-row df
#     with annual totals for all variables, plus a 'source' column.
#     """

#     df_ = pd.read_excel(
#         '0_EP_runs/' + excel_path,
#         sheet_name=sheet_name,
#         decimal=','
#     )

#     # 1. drop initial junk rows
#     df = df_[df_.index >= 79].copy()

#     # 2. merge top two header rows
#     df.columns = [
#         f"{str(col1).strip()}_{str(col2).strip()}" if col2 else str(col1).strip()
#         for col1, col2 in zip(df.iloc[0], df.iloc[1])
#     ]
#     df = df.iloc[2:].reset_index(drop=True)

#     # 3. pick the annual row (index == 2)
#     annual = df[df.index == 2].copy()

#     # 4. rename first column and drop it
#     first_col = annual.columns[0]
#     annual = annual.rename(columns={first_col: "Annual (TWh/year)"})
#     annual = annual.drop(columns=["Annual (TWh/year)"])

#     # 5. ensure numeric
#     annual = annual.apply(pd.to_numeric, errors='coerce')

#     # 6. add source
#     annual["source"] = Path(excel_path).stem

#     # 7. put source first
#     cols = annual.columns.tolist()
#     cols.remove("source")
#     cols.insert(0, "source")
#     annual = annual[cols]

#     # 8. aggregate heat units
#     annual = aggregate_heat_units(annual)

#     return annual

# def plot_metrics_yearly(
#     dfs,
#     plots=None,
#     case_labels=None,
#     tech_labels=None,
# ):

#     if dfs is None or len(dfs) == 0:
#         raise ValueError("`dfs` must be a non-empty list of DataFrames.")

#     # concat all annual rows
#     annual_all = pd.concat(dfs, ignore_index=True)

#     # decide which variables to plot
#     if plots is None:
#         plots = annual_all.select_dtypes(include="number").columns.tolist()
#     plots = list(plots)

#     plots_valid = [col for col in plots if col in annual_all.columns]
#     if not plots_valid:
#         raise ValueError("No valid annual columns to plot.")

#     # robust numeric conversion
#     for col in plots_valid:
#         if annual_all[col].dtype == 'O':
#             annual_all[col] = pd.to_numeric(
#                 annual_all[col].astype(str)
#                                 .str.replace('.', '', regex=False)
#                                 .str.replace(',', '.', regex=False),
#                 errors='coerce'
#             )

#     # source labels (from df["source"], created in timeseries_yearly)
#     sources = annual_all["source"].tolist()

#     # pretty names for x-axis
#     if case_labels is not None:
#         display_sources = [case_labels.get(s, s) for s in sources]
#     else:
#         display_sources = sources

#     x_pos = np.arange(len(sources))
#     n_cases = len(sources)
#     fig_width = max(4, 0.9 * n_cases + 2)

#     # one figure per variable
#     for col in plots_valid:
#         fig, ax = plt.subplots(figsize=(fig_width, 4))

#         ax.bar(x_pos, annual_all[col].values, width=0.6)

#         ax.set_xticks(x_pos)
#         ax.set_xticklabels(display_sources, rotation=0, ha="center")

#         ax.set_ylabel("TWh/year")

#         if tech_labels is not None:
#             pretty_name = tech_labels.get(col, col)
#         else:
#             pretty_name = col
#         ax.set_title(pretty_name)

#         ax.axhline(0, linewidth=0.8, color="black")
#         ax.grid(axis="y", linestyle="-", linewidth=0.5, alpha=0.3)
#         ax.set_axisbelow(True)

#         ax.spines["top"].set_visible(False)
#         ax.spines["right"].set_visible(False)

#         ax.tick_params(axis='x', direction='in', length=3)
#         ax.tick_params(axis='y', direction='in', length=3)

#         plt.tight_layout()
#         plt.show()

