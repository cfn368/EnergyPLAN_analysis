import matplotlib.pyplot as plt
import itertools
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
from pathlib import Path

# aggregate composition
# def plot_stacked_by_source(
#     demand_df,
#     colors,
#     title="Production decomposition",
#     ylabel="TWh/year",
#     min_val=1.0,
#     legend_ncol=3,
#     figsize=(12, 7),
#     tech_labels=None,
#     source_labels=None,
# ):
#     """
#     demand_df : DataFrame with a 'source' column + numeric columns
#     colors    : list of colors (will be cycled if shorter than #cols)
#     tech_labels : dict or None
#         Mapping from raw column names -> pretty labels in legend.
#     source_labels : dict or None
#         Mapping from raw source names (e.g. file stems) -> pretty labels on x-axis.
#     """ 

#     df = demand_df.copy()

#     # 0. pretty scenario names on x-axis
#     if source_labels is not None:
#         df["source"] = df["source"].replace(source_labels)

#     # 1. numeric filtering (protect 'source')
#     fixed_part = df['source']
#     num_part   = df.drop(columns='source')
#     num_part   = num_part.apply(pd.to_numeric, errors='coerce')

#     # keep only columns where all values > min_val and no NaNs
#     col_mask = (num_part > min_val).any(axis=0) & num_part.notna().all(axis=0)
#     num_part_filtered = num_part.loc[:, col_mask]

#     # 1b. apply pretty tech labels (after filtering)
#     if tech_labels is not None:
#         rename_map = {col: tech_labels.get(col, col) for col in num_part_filtered.columns}
#         num_part_filtered = num_part_filtered.rename(columns=rename_map)

#     # combine back
#     df_plot = pd.concat([fixed_part, num_part_filtered], axis=1)

#     # 2. stacked column plot: one bar per source, all other cols stacked
#     plot_df = df_plot.set_index('source')

#     # make sure we have enough colors
#     n_cols = plot_df.shape[1]
#     if n_cols > len(colors):
#         colors = list(itertools.islice(itertools.cycle(colors), n_cols))

#     fig, ax = plt.subplots(figsize=figsize)
#     plot_df.plot(kind='bar', stacked=True, ax=ax, width=0.7, color=colors)

#     ax.set_ylabel(ylabel)
#     ax.set_title(title)
#     ax.grid(axis="y", linestyle="--", alpha=0.4)
#     ax.set_axisbelow(True)

#     ax.set_xticklabels(ax.get_xticklabels(), rotation=0, ha="center")

#     # move legend below the plot
#     handles, labels = ax.get_legend_handles_labels()
#     ax.legend(
#         handles,
#         labels,
#         loc="upper center",
#         bbox_to_anchor=(0.5, -0.10),
#         ncol=legend_ncol,
#         frameon=False,
#     )

#     fig.subplots_adjust(bottom=0.25)

#     return fig, ax

# for capture rates 1 (yearly)
def plot_capture_full(
    capture_full,
    plot_two=True,
    axline=True,
    source_labels=None,
    colors=None,
    title='Indsæt titel',
    savepath=None,        # NEW: e.g. "figs/capture_full.pdf" or "figs/capture_full.png"
    dpi=300,              # NEW
    save_kwargs=None,     # NEW
    show=True,            # NEW
    close=False,          # NEW
    rotate=True,
):
    """
    Two barplots of capture_full:
    1) Full scale
    2) Zoomed: y in [0, 1.5]

    Index: source
    Columns: technologies
    """

    # work on a copy so we don't mutate original
    df = capture_full.copy() 

    # pretty names for sources (legend / axis)
    if source_labels is not None:
        df = df.rename(index=source_labels)

    sources = df.index
    n_sources = len(sources)

    def _save_fig(fig, outpath):
        outpath = Path(outpath)
        outpath.parent.mkdir(parents=True, exist_ok=True)

        skw = dict(bbox_inches="tight")
        if outpath.suffix.lower() in [".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"]:
            skw["dpi"] = dpi
        if save_kwargs:
            skw.update(save_kwargs)

        fig.savefig(outpath, **skw)

    # resolve output paths (auto add _full / _zoom)
    base = None
    ext = None
    stem = None
    if savepath is not None:
        base = Path(savepath)
        ext = base.suffix if base.suffix else ".png"
        stem = base.with_suffix("").as_posix()

        full_path = f"{stem}{ext}"
        zoom_path = f"{stem}{ext}"
    else:
        full_path = zoom_path = None

    # --- 1) Full scale ---
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    df.T.plot(kind='bar', ax=ax1, color=colors)

    if axline:
        ax1.axhline(1.0, linestyle="--", linewidth=1)

    ax1.set_title(title)

    ax1.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, -0.10),
        ncol=min(n_sources, 4),
    )

    ax1.grid(axis='y', linestyle=':', linewidth=0.7)

    if rotate:
        ax1.tick_params(axis='x', rotation=25)
        for label in ax1.get_xticklabels():
            label.set_ha('center')
    else:
        ax1.tick_params(axis='x', rotation=0)
        for label in ax1.get_xticklabels():
            label.set_ha('center')

    plt.tight_layout()

    if full_path is not None:
        _save_fig(fig1, full_path)

    if show:
        plt.show()
    if close:
        plt.close(fig1)

    # --- 2) Zoomed y-axis (0–1.5) ---
    # fig2 = ax2 = None
    # if plot_two:
    #     fig2, ax2 = plt.subplots(figsize=(12, 6))
    #     df.T.plot(kind='bar', ax=ax2, color=colors)

    #     if axline:
    #         ax2.axhline(1.0, linestyle="--", linewidth=1)
    #         ax2.set_ylim(0, 1.5)

    #     ax2.set_title(title)

    #     ax2.legend(
    #         loc='upper center',
    #         bbox_to_anchor=(0.5, -0.2),
    #         ncol=min(n_sources, 4),
    #     )

    #     ax2.grid(axis='y', linestyle=':', linewidth=0.7)

    #     ax2.tick_params(axis='x', rotation=25)
    #     for label in ax2.get_xticklabels():
    #         label.set_ha('right')

    #     plt.tight_layout()

    #     if zoom_path is not None:
    #         _save_fig(fig2, zoom_path)

    #     if show:
    #         plt.show()
    #     if close:
    #         plt.close(fig2)

    return (fig1, ax1) #, (fig2, ax2)
    
# for capture rates 2 (d_summer)
# def _shade_color(rgba, factor):
#     """Multiply RGB by factor, keep alpha, clamp to [0,1]."""
#     rgba = np.array(rgba, dtype=float)
#     rgba[:3] = np.clip(rgba[:3] * factor, 0, 1)
#     return tuple(rgba)

# def plot_capture_seasonal(
#     capture_seasonal,
#     plot_two=True,
#     axline=True,
#     source_labels=None,
#     colors_input=None, 
#     title='Indsæt titel',
# ):
#     """
#     Two barplots of capture_seasonal:
#     1) Full scale
#     2) Zoomed: y in [0, 1.5]

#     Index: MultiIndex (source, d_summer)
#     Columns: technologies
#     """

#     # sort for consistent ordering
#     df = capture_seasonal.sort_index().copy()

#     # original index for color mapping
#     sources = df.index.get_level_values(0)
#     seasons = df.index.get_level_values(1)

#     # pretty names for legend (but keep original sources for colors)
#     if source_labels is not None:
#         display_sources = sources.to_series().replace(source_labels).to_numpy()
#     else:
#         display_sources = sources.to_numpy()

#     # legend labels: "Nice name – summer" / "Nice name – non-summer"
#     legend_labels = [
#         f"{src_disp} – {'summer' if is_summer else 'non-summer'}"
#         for src_disp, is_summer in zip(display_sources, seasons)
#     ]
#     df.index = legend_labels  # used in plot legend

#     # ---- colors: base per original source, shade per season ----
#     unique_sources = sources.unique()

#     if colors_input is None:
#         # default: tab10
#         cmap = plt.get_cmap("tab10")
#         base_colors = {
#             src: cmap(i % cmap.N)
#             for i, src in enumerate(unique_sources)
#         }
#     else:
#         # user-specified colors (hex or any mpl color), cycled if needed
#         colors_input = list(colors_input)
#         base_colors = {
#             src: mcolors.to_rgba(colors_input[i % len(colors_input)])
#             for i, src in enumerate(unique_sources)
#         }

#     colors = []
#     for src, is_summer in zip(sources, seasons):
#         base = base_colors[src]
#         if is_summer:      # summer
#             c = _shade_color(base, 0.7)   # darker
#         else:              # non-summer
#             c = _shade_color(base, 1.3)   # lighter
#         colors.append(c)

#     n_legend = len(df.index)

#     # ---------- 1) Full scale ----------
#     fig, ax = plt.subplots(figsize=(12, 6))
#     df.T.plot(kind="bar", ax=ax, color=colors)

#     if axline:
#         ax.axhline(1.0, linestyle="--", linewidth=1)
#     # ax.set_ylabel("Capacity factor")
#     ax.set_title(title)
#     ax.grid(axis="y", linestyle=":", linewidth=0.7)

#     ax.tick_params(axis="x", rotation=25)
#     for label in ax.get_xticklabels():
#         label.set_ha("right")

#     handles, labels = ax.get_legend_handles_labels()
#     ax.legend_.remove()

#     fig.legend(
#         handles, labels,
#         # title="Source / season",
#         loc="lower center",
#         ncol=min(n_legend, 4),
#         bbox_to_anchor=(0.5, 0.1),
#     )

#     fig.subplots_adjust(bottom=0.30)
#     plt.show()

#     # ---------- 2) Zoomed 0–1.5 ----------
#     if plot_two:
#         fig, ax = plt.subplots(figsize=(12, 6))
#         df.T.plot(kind="bar", ax=ax, color=colors)

#         if axline:
#             ax.axhline(1.0, linestyle="--", linewidth=1)
#             ax.set_ylim(0, 1.5)

#         # ax.set_ylabel("Capacity factor")
#         ax.set_title("Samme men for restrikteret interval fra 0-1.5")
#         ax.grid(axis="y", linestyle=":", linewidth=0.7)

#         ax.tick_params(axis="x", rotation=25)
#         for label in ax.get_xticklabels():
#             label.set_ha("right")

#         handles, labels = ax.get_legend_handles_labels()
#         ax.legend_.remove()

#         fig.legend(
#             handles, labels,
#             title="Source / season",
#             loc="lower center",
#             ncol=min(n_legend, 4),
#             bbox_to_anchor=(0.5, 0.02),
#         )

#         fig.subplots_adjust(bottom=0.30)
#         plt.show()