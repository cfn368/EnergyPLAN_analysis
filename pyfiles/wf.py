# pyfiles/wf.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# ==================== ==================== ==================== ====================
# 1. waterfall chart
def plot_waterfall(
    values: dict,
    name_map: dict,
    *,
    figsize=(14, 5),
    base_color="#3A3A3A",
    fade_to=0.75,
    ylabel="Rise in costs (MEUR)",
    title="",
    connector_color="0.6",
    connector_lw=0.8,
    zero_color="0.25",
    zero_lw=0.9,
    grid_color="0.88",
    grid_lw=0.8,
    show_delta=True,
    delta_fmt="{:+.1f}",
    delta_color="0.15",
    delta_fontsize=None,
    delta_pad_frac=0.02,
    show_table=True,
    table_round=2,
    table_title="Table (same items as figure)",
    bg_color=None,
    pos_color=None,
    neg_color=None,
):
    """
    Waterfall chart using the order of `name_map` (no sorting).

    values   : dict key -> numeric value
    name_map : dict key -> label (also defines plotting order)
    """
    # 1. filter to keys present in both dicts, preserving name_map order
    keys = [k for k in name_map if k in values]
    if not keys:
        raise ValueError("No overlapping keys between `values` and `name_map`.")

    df = pd.DataFrame(
        [(k, name_map[k], float(values[k])) for k in keys],
        columns=["key", "label", "value"]
    )

    # 2. compute waterfall geometry (running cumulative totals)
    cum = 0.0
    starts, ends, bottoms, heights = [], [], [], []
    for v in df["value"].to_numpy():
        start = cum
        end   = cum + v
        starts.append(start)
        ends.append(end)
        bottoms.append(min(start, end))
        heights.append(abs(v))
        cum = end

    df["start"]  = starts
    df["end"]    = ends
    df["bottom"] = bottoms
    df["height"] = heights

    # 3. build bar colours
    n = len(df)

    def lighten(rgb, amt):
        return tuple((1 - amt) * c + amt * 1.0 for c in rgb)

    if pos_color is not None and neg_color is not None:
        # strong edge in sign colour; fill = edge blended onto bg at fill_alpha
        bg_rgb = mcolors.to_rgb(bg_color) if bg_color is not None else (1.0, 1.0, 1.0)
        bar_edgecolors = [pos_color if v >= 0 else neg_color for v in df["value"].to_numpy()]
        bar_facecolors = [
            tuple(0.18 * c + 0.82 * b for c, b in zip(mcolors.to_rgb(ec), bg_rgb))
            for ec in bar_edgecolors
        ]
        bar_linewidths = 1.8
    else:
        # fade progressively from base_color to white
        base_rgb = mcolors.to_rgb(base_color)
        amts = np.linspace(0.00, float(fade_to), n)
        bar_facecolors = [lighten(base_rgb, a) for a in amts]
        bar_edgecolors = "none"
        bar_linewidths = 0

    # 4. draw bars and connectors
    fig, ax = plt.subplots(figsize=figsize)

    if bg_color is not None:
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        for spine in ax.spines.values():
            spine.set_edgecolor("#9ab4c8")

    x = np.arange(n)
    ax.bar(x, df["height"], bottom=df["bottom"],
           color=bar_facecolors, edgecolor=bar_edgecolors, linewidth=bar_linewidths)

    for i in range(n - 1):
        ax.plot(
            [i + 0.5, i + 0.5],
            [df.loc[i, "end"], df.loc[i + 1, "start"]],
            color=connector_color, lw=connector_lw,
        )

    # 5. add value labels above each bar
    if show_delta:
        y_all  = np.r_[df["start"].to_numpy(), df["end"].to_numpy(), [0.0]]
        y_span = float(np.nanmax(y_all) - np.nanmin(y_all)) or 1.0
        pad    = delta_pad_frac * y_span

        fs = (plt.rcParams.get("xtick.labelsize", plt.rcParams["font.size"])
              if delta_fontsize is None else delta_fontsize)

        y_needed_top = None
        for i, v in enumerate(df["value"].to_numpy()):
            y_top = max(df.loc[i, "start"], df.loc[i, "end"])
            y_txt = y_top + pad

            txt = delta_fmt.format(v).replace("%", r"\%")
            ax.text(
                x[i], y_txt, rf"${txt}$",
                ha="center", va="bottom",
                fontsize=fs, color=delta_color, clip_on=True,
            )
            y_needed_top = y_txt if y_needed_top is None else max(y_needed_top, y_txt)

        lo, hi = ax.get_ylim()
        if y_needed_top is not None:
            ax.set_ylim(lo, max(hi, y_needed_top + 5.0 * pad))

    # 6. axis formatting
    ax.set_xticks(x)
    ticklabels = [f"{lab}\n({i})" for i, lab in enumerate(df["label"], start=1)]      
    ax.set_xticklabels(ticklabels, rotation=0, ha="center")
    ax.axhline(0, color='#FF0000', lw=zero_lw)
    ax.grid(axis="y",
            color="white" if bg_color is not None else grid_color,
            linewidth=grid_lw,
            alpha=0.5 if bg_color is not None else 1.0)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()

    # 7. print summary table
    table_df = pd.DataFrame(
        [df["value"].to_numpy()],
        columns=df["label"].to_list(),
        index=["Value"],
    )
    table_df["Bottom line"] = float(df["value"].sum())
    if table_round is not None:
        table_df = table_df.round(table_round)

    if show_table:
        try:
            from IPython.display import display
            if table_title:
                print(table_title)
            display(table_df)
        except Exception:
            if table_title:
                print(table_title)
            print(table_df.to_string())

    return fig, ax, df, table_df
