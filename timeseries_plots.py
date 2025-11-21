import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import itertools
import builtins

# -------------------------------------------------------------------------------
# 1. Core loader: ONE file -> cleaned monthly dataframe
# -------------------------------------------------------------------------------

def timeseries(excel_path, sheet_name=0):
    """
    Read EnergyPLAN-style Excel output and return monthly df.
    """

    # read raw file
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
    monthly = df[df.index >= 23].copy()

    # 4a. enforce that the *first* column is called 'hour'
    first_col = monthly.columns[0]
    monthly = monthly.rename(columns={first_col: "hour"})

    # 4b. if there were any duplicate 'hour' columns, keep the first
    monthly = monthly.loc[:, ~monthly.columns.duplicated()]

    # 4c. add tag and summer dummy
    monthly["source"] = Path(excel_path).stem
    monthly["d_summer"] = (monthly["hour"] >= 3649) & (monthly["hour"] < 5857)  # June 1–Sept 1

    # 5. arrange columns: hour, source, d_summer, rest...
    cols = monthly.columns.tolist()
    cols.remove("source")
    cols.remove("d_summer")
    cols.insert(1, "source")
    cols.insert(2, "d_summer")
    monthly = monthly[cols]

    return monthly


# -------------------------------------------------------------------------------
# 2. Multi-case plotting: MANY files -> one plot per variable, one line per case
# -------------------------------------------------------------------------------

def plot_metrics(files, plots=None, sheet_name=0):
    """
    For a list of Excel filenames, produce one plot per variable in `plots`,
    with one line per case (file).

    Parameters
    ----------
    files : list of str
        Filenames, e.g. ['test.xlsx', 'test - Kopi.xlsx'].
    plots : list of str or None
        Column names to plot. If None, use a default list.
    sheet_name : int or str
        Sheet to read from each file.
    """

    # load data for all cases
    dfs = [timeseries(f, sheet_name=sheet_name) for f in files]

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

    # make sure it's a list (in case user gives a tuple or generator)
    plots = list(plots)

    # keep only those that exist in ALL dfs (robust to missing cols)
    cols_missing = [col for col in plots if not all(col in d.columns for d in dfs)]
    if cols_missing:
        print("Warning: missing in at least one file and will be skipped:", cols_missing)

    plots_valid = [col for col in plots if col not in cols_missing]

    linestyles = ['-', '--', ':', '-.']
    ls_cycler = itertools.cycle(linestyles)

    for col in plots_valid:
        fig, ax = plt.subplots(figsize=(12, 5))

        # zip så vi både har filnavn og df
        for f, d, ls in zip(files, dfs, itertools.cycle(linestyles)):
            label = Path(f).stem
            ax.plot(d["hour"], d[col], linewidth=1.2, linestyle=ls, label=label)

        ax.set_xlabel("hour")
        ax.set_ylabel('MW')
        ax.set_title(col)
        ax.grid(True, which="both", linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()

# -------------------------------------------------------------------------------
# 3. Same but for months
# -------------------------------------------------------------------------------

def timeseries_months(excel_path, sheet_name=0):
    """
    replica of 'timeseries' but for monthd
    """
    df_ = pd.read_excel('0_EP_runs/' + excel_path, sheet_name=0)

    df = df_[df_.index >= 79].copy()

    df.columns = [
        f"{str(col1).strip()}_{str(col2).strip()}" if col2 else str(col1).strip()
        for col1, col2 in zip(df.iloc[0], df.iloc[1])
    ]
    df = df.iloc[2:].reset_index(drop=True)

    # 3. select data (same rule as before: index >= 23)
    monthly = df[(df.index >= 5) & (df.index <= 16)].copy()


    first_col = monthly.columns[0]
    monthly = monthly.rename(columns={first_col: "month"})
    monthly = monthly.loc[:, ~monthly.columns.duplicated()]
    monthly["source"] = Path(excel_path).stem

    cols = monthly.columns.tolist()
    cols.remove("source")
    cols.insert(1, "source")
    monthly = monthly[cols]

    return monthly

def plot_metrics_months(files, plots=None, sheet_name=0):
    """
    replica of 'plot_timeseries_cases' but for months
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

    # make sure it's a list (in case user gives a tuple or generator)
    plots = list(plots)

    # keep only those that exist in ALL dfs (robust to missing cols)
    cols_missing = [
        col for col in plots
        if not builtins.all(col in d.columns for d in dfs)
    ]
    if cols_missing:
        print("Warning: missing in at least one file and will be skipped:", cols_missing)

    plots_valid = [col for col in plots if col not in cols_missing]

    linestyles = ['-', '--', ':', '-.']
    ls_cycler = itertools.cycle(linestyles)

    for col in plots_valid:
        fig, ax = plt.subplots(figsize=(12, 5))

        # zip så vi både har filnavn og df
        for f, d, ls in zip(files, dfs, itertools.cycle(linestyles)):
            label = Path(f).stem
            ax.plot(d["month"], d[col], linewidth=1.2, linestyle=ls, label=label)

        ax.set_xlabel("hour")
        ax.set_ylabel('MW')
        ax.set_title(col)
        ax.grid(True, which="both", linestyle="--", alpha=0.4)
        ax.legend()
        plt.tight_layout()