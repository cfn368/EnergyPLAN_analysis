# pyfiles/overview_fig.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import itertools

import pyfiles.fig_setup as fig_setup

from pathlib import Path


# ==================== ==================== ==================== ====================
# 1. multi-panel monthly grid plot
def plot_metrics_months_grid(
    dfs,
    plots=None,
    case_labels=None,
    tech_labels=None,
    colors=None,
    nrows=3,
    ncols=3,
    savepath=None,
    dpi=300,
    save_kwargs=None,
    show=True,
    close=False,
    bg_color=None,
    fill_alpha=0.0,
):
    """
    Multi-panel monthly plot:
    - one subplot per variable in `plots`
    - one line per case (dataframe)
    - arranged in an nrows x ncols grid (default 3x4)

    Saving: pass savepath='path/filename.png' or '.pdf'

    bg_color   : hex/name for figure + axes background (e.g. "#d8e9f4"). None = default white.
    fill_alpha : 0–1, draws a filled area from zero to each line. 0 = lines only (default).
    """
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
        print("Warning (monthly grid): missing in at least one df and will be skipped:", cols_missing)

    plots_valid = [col for col in plots if col not in cols_missing]
    if not plots_valid:
        print("No valid monthly columns to plot.")
        return None, None

    # 3. cap by number of available subplot slots
    max_plots = min(len(plots_valid), nrows * ncols)
    plots_valid = plots_valid[:max_plots]

    # 4. build case IDs from 'source' column or fallback index
    case_ids = []
    for i, d in enumerate(dfs):
        if "source" in d.columns:
            case_ids.append(str(d["source"].iloc[0]))
        else:
            case_ids.append(f"case_{i}")

    n_cases = len(case_ids)

    # 5. map month labels to numeric x-axis positions
    month_vals = list(dict.fromkeys(dfs[0]["month"].tolist()))
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

    # 6. assign colours per case (fixed across all subplots)
    if colors is None:
        color_cycle = plt.rcParams['axes.prop_cycle'].by_key().get('color', [])
        if len(color_cycle) == 0:
            color_cycle = [None] * n_cases
        color_list = [color_cycle[i % len(color_cycle)] for i in range(n_cases)]
    else:
        color_list = [colors[i % len(colors)] for i in range(n_cases)]

    linestyles = ['-', '--', '--', '-.']

    # 7. set up figure and axes grid
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(12, 11), sharex=True)
    axes = np.array(axes).reshape(-1)

    if bg_color is not None:
        fig.patch.set_facecolor(bg_color)

    handle_dict = {}

    for k, col in enumerate(plots_valid):
        ax = axes[k]

        if bg_color is not None:
            ax.set_facecolor(bg_color)
            for spine in ax.spines.values():
                spine.set_edgecolor("#9ab4c8")

        for j, (case_id, d) in enumerate(zip(case_ids, dfs)):
            if col not in d.columns:
                continue

            x_month = month_to_x(d["month"])
            label   = case_labels.get(case_id, case_id) if case_labels is not None else case_id
            c  = color_list[j]
            ls = linestyles[j % len(linestyles)]

            if fill_alpha > 0:
                y = d[col] / 1000
                ax.fill_between(x_month, 0, y, alpha=fill_alpha, color=c, linewidth=0)

            line, = ax.plot(x_month, d[col] / 1000, linewidth=2, linestyle=ls, label=label, color=c)

            if label not in handle_dict:
                handle_dict[label] = line

        pretty_name = tech_labels.get(col, col) if tech_labels is not None else col
        ax.set_title(pretty_name)

        if bg_color is not None:
            ax.grid(True, which="major", linestyle="-", color="white", alpha=0.5)
        else:
            ax.grid(True, which="both", linestyle="--", alpha=0.3)

    # 8. axis labels and month tick marks
    for idx, ax in enumerate(axes):
        if idx >= len(plots_valid):
            break

        row     = idx // ncols
        col_idx = idx % ncols

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels)

        if col_idx == 0:
            if row == 1:
                ax.set_ylabel("Månedlige gns. (GW eller GWh)")

    # 9. legend placement
    legend_ax = None
    use_legend_panel = (len(plots_valid) == 8) and (len(axes) > len(plots_valid))

    if handle_dict:
        handles = list(handle_dict.values())
        labels  = list(handle_dict.keys())

        legend_kwargs = dict(
            frameon=True,
            facecolor=bg_color if bg_color is not None else "white",
            edgecolor="#9ab4c8" if bg_color is not None else "0.8",
        )

        if use_legend_panel:
            legend_ax = axes[len(plots_valid)]
            legend_ax.axis("off")
            if bg_color is not None:
                legend_ax.set_facecolor(bg_color)
            legend_ax.legend(handles, labels, loc="center", ncol=min(len(labels), 1), **legend_kwargs)
        else:
            fig.legend(
                handles, labels,
                loc="lower center",
                ncol=min(len(labels), 4),
                bbox_to_anchor=(0.5, -0.02),
                **legend_kwargs,
            )

    # 10. hide unused axes (keep legend panel if used)
    start_delete = len(plots_valid) + (1 if legend_ax is not None else 0)
    for k in range(start_delete, len(axes)):
        fig.delaxes(axes[k])

    # 11. layout and y-tick count
    if legend_ax is not None:
        plt.tight_layout()
    else:
        plt.tight_layout(rect=(0, 0.04, 1, 1))

    for idx, ax in enumerate(axes[:len(plots_valid)]):
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4, min_n_ticks=4))
        ax.locator_params(axis="y", nbins=4)

    # 12. save if path provided
    if savepath is not None:
        savepath = Path(savepath)
        savepath.parent.mkdir(parents=True, exist_ok=True)

        skw = dict(bbox_inches="tight")
        if savepath.suffix.lower() in [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"]:
            skw["dpi"] = dpi
        if save_kwargs:
            skw.update(save_kwargs)

        fig.savefig(savepath, **skw)

    # 13. show / close
    if show:
        plt.show()
    if close:
        plt.close(fig)

    return fig, axes
