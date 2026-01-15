import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools

import pyfiles.fig_setup as fig_setup

from pathlib import Path

def plot_metrics_months_grid(
    dfs,
    plots=None,
    case_labels=None,
    tech_labels=None,
    colors=None,
    nrows=3,
    ncols=4,
    savepath=None,          # <- NEW: e.g. "figs/monthly_grid.pdf" or "figs/monthly_grid.png"
    dpi=300,                # <- NEW
    save_kwargs=None,       # <- NEW: extra kwargs for fig.savefig
    show=True,              # <- NEW
    close=False,            # <- NEW: close figure after saving/showing
):
    """
    Multi-panel monthly plot:
    - one subplot per variable in `plots`
    - one line per case (dataframe)
    - arranged in an nrows x ncols grid (default 3x4).

    Saving:
    - pass savepath="path/filename.png" or ".pdf"
    """

    if dfs is None or len(dfs) == 0:
        raise ValueError("`dfs` must be a non-empty list of DataFrames.")

    # --- 1. default variables to plot ---
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

    # --- 2. drop vars missing in some dfs ---
    cols_missing = [col for col in plots if not all(col in d.columns for d in dfs)]
    if cols_missing:
        print("Warning (monthly grid): missing in at least one df and will be skipped:", cols_missing)

    plots_valid = [col for col in plots if col not in cols_missing]
    if not plots_valid:
        print("No valid monthly columns to plot.")
        return None, None

    # cap by number of subplots
    max_plots = min(len(plots_valid), nrows * ncols)
    plots_valid = plots_valid[:max_plots]

    # --- 3. case IDs from 'source' or fallback ---
    case_ids = []
    for i, d in enumerate(dfs):
        if "source" in d.columns:
            case_ids.append(str(d["source"].iloc[0]))
        else:
            case_ids.append(f"case_{i}")

    n_cases = len(case_ids)

    # --- 4. month mapping: turn month labels into numbers if needed ---
    month_vals = list(dict.fromkeys(dfs[0]["month"].tolist()))  # unique, in order
    month_vals_series = pd.Series(month_vals)
    month_vals_num = pd.to_numeric(month_vals_series, errors="coerce")

    if month_vals_num.isna().all():
        month_mapping = {val: i + 1 for i, val in enumerate(month_vals)}
        n_months = len(month_mapping)

        def month_to_x(s):
            return s.map(month_mapping)

        tick_positions = np.arange(1, n_months + 1)
        tick_labels = [str(m) for m in tick_positions]
    else:
        month_mapping = None

        def month_to_x(s):
            return pd.to_numeric(s, errors="coerce")

        ref_x = month_to_x(dfs[0]["month"])
        ref_x = np.sort(ref_x[np.isfinite(ref_x)].unique())
        tick_positions = ref_x
        tick_labels = [str(int(m)) for m in ref_x]

    # --- 5. colors per case (fixed across subplots) ---
    if colors is None:
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key().get('color', [])
        if len(color_cycle) == 0:
            color_cycle = [None] * n_cases
        color_list = [color_cycle[i % len(color_cycle)] for i in range(n_cases)]
    else:
        color_list = [colors[i % len(colors)] for i in range(n_cases)]

    linestyles = ['-', '--', ':', '-.']

    # --- 6. set up figure and axes grid ---
    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(14, 10),
        sharex=True,
    )
    axes = np.array(axes).reshape(-1)  # flatten

    handle_dict = {}  # for common legend

    for k, col in enumerate(plots_valid):
        ax = axes[k]

        for j, (case_id, d) in enumerate(zip(case_ids, dfs)):
            if col not in d.columns:
                continue

            x_month = month_to_x(d["month"])

            # legend label
            if case_labels is not None:
                label = case_labels.get(case_id, case_id)
            else:
                label = case_id

            c = color_list[j]
            ls = linestyles[j % len(linestyles)]

            line, = ax.plot(
                x_month, d[col] / 1000,
                linewidth=1.2,
                linestyle=ls,
                label=label,
                color=c,
            )

            if label not in handle_dict:
                handle_dict[label] = line

        # subplot title
        if tech_labels is not None:
            pretty_name = tech_labels.get(col, col)
        else:
            pretty_name = col
        ax.set_title(pretty_name)

        ax.grid(True, which="both", linestyle="--", alpha=0.3)

    # --- 7. axis labels & month numbers on x-axis ---
    for idx, ax in enumerate(axes):
        if idx >= len(plots_valid):
            break

        row = idx // ncols
        col_idx = idx % ncols

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels)

        if row == nrows - 1 and col_idx == 1:
            ax.set_xlabel("Month (1–12)")
        if col_idx == 0 and row ==1:
            ax.set_ylabel("Monthly Averages (GW)")

    # hide unused axes
    for k in range(len(plots_valid), len(axes)):
        fig.delaxes(axes[k])

    # --- 8. common legend at bottom ---
    if handle_dict:
        handles = list(handle_dict.values())
        labels = list(handle_dict.keys())
        fig.legend(
            handles,
            labels,
            loc="lower center",
            ncol=min(len(labels), 4),
            bbox_to_anchor=(0.5, -0.02),
            frameon=True,
        )

    # layout first
    plt.tight_layout(rect=(0, 0.04, 1, 1))

    # --- 9. SAVE (optional) ---
    if savepath is not None:
        savepath = Path(savepath)
        savepath.parent.mkdir(parents=True, exist_ok=True)

        skw = dict(bbox_inches="tight")
        if savepath.suffix.lower() in [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"]:
            skw["dpi"] = dpi
        if save_kwargs:
            skw.update(save_kwargs)

        fig.savefig(savepath, **skw)

    # --- 10. SHOW / CLOSE ---
    if show:
        plt.show()
    if close:
        plt.close(fig)

    return fig, axes