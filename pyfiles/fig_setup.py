# nice figures

import matplotlib as mpl

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": [
        "TeX Gyre Pagella",   # best Palatino-ish if installed
        "Palatino Linotype",  # Windows
        "Book Antiqua",       # Windows fallback (Palatino-ish)
        "URW Palladio L",     # Linux Palatino-ish
        "DejaVu Serif"        # always there
    ],
    "mathtext.fontset": "dejavuserif",  # matches the serif vibe better than stix/times
})

BASE = 9


mpl.rcParams.update({
    # global default
    "font.size": BASE,

    # figure-level title (suptitle)
    "figure.titlesize": BASE + 9,

    # axes
    "axes.titlesize": BASE + 7,
    "axes.labelsize": BASE + 7,

    # ticks
    "xtick.labelsize": BASE + 3,
    "ytick.labelsize": BASE + 3,

    # legend
    "legend.fontsize": BASE + 7,
    "legend.title_fontsize": BASE + 4,

    # optional: annotations
    "text.usetex": False,  # keep unless you deliberately use LaTeX
})