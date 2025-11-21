# pyfiles/fig_setup.py
# Global matplotlib style — Danish æ/ø/å-safe serif font with custom colour cycle.

import matplotlib as mpl
from cycler import cycler

BASE = 9

# 1. font family and rendering settings
mpl.rcParams.update({
    "font.family":   "serif",
    "font.serif": [
        "DejaVu Serif",        # robust unicode, handles æ/ø/å
        "TeX Gyre Pagella",
        "Palatino Linotype",
        "Book Antiqua",
        "URW Palladio L",
    ],
    "font.sans-serif":    ["DejaVu Sans"],
    "mathtext.fontset":   "dejavuserif",
    "mathtext.default":   "regular",
    "text.usetex":        False,   # must be False to use unicode characters directly
    "axes.unicode_minus": False,
    "pdf.fonttype":       42,      # embed TrueType fonts in PDF (preserves æ/ø/å)
    "ps.fonttype":        42,
    "svg.fonttype":       "none",  # keep text as text in SVG, not paths

    # 2. colour cycle
    "axes.prop_cycle": cycler(color=["#FF0000", "#374151", "#003A8C"]),
})

# 3. font sizes relative to BASE
mpl.rcParams.update({
    "font.size":            BASE,
    "figure.titlesize":     BASE + 9,
    "axes.titlesize":       BASE + 7,
    "axes.labelsize":       BASE + 7,
    "xtick.labelsize":      BASE + 6,
    "ytick.labelsize":      BASE + 3,
    "legend.fontsize":      BASE + 7,
    "legend.title_fontsize": BASE + 7,
})
