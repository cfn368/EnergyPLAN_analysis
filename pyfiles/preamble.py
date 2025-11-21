# pyfiles/preamble.py

# 1. third-party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as mticker
from matplotlib.ticker import MaxNLocator
import requests
from ET_eds_api import get_wp_h, wagg_wp, VE, columns, VE_run

# 2. stdlib imports
import itertools
import shutil
import sys
import time
from pathlib import Path
from typing import Sequence

# 3. project module imports
import pyfiles.fig_setup as fig_setup
from pyfiles.scenario_functions import load_energyplan_file, format_value, build_params
import pyfiles.ep_run_v2 as ep_run_v2
import pyfiles.var_groups as var_groups
import pyfiles.costs as costs
import pyfiles.build_frames as build_frames
import pyfiles.overview_fig as overview_fig
import pyfiles.wf as wf


# ==================== ==================== ==================== ====================
# 1. enable IPython autoreload
def enable_autoreload(mode: int = 2) -> None:
    """Enable IPython autoreload (call from a notebook)."""
    ip = get_ipython()  # noqa: F821
    ip.run_line_magic("load_ext", "autoreload")
    ip.run_line_magic("autoreload", str(mode))


__all__ = [
    "np", "pd", "plt", "mcolors", "mticker", "MaxNLocator", "requests",
    "get_wp_h", "wagg_wp", "VE", "columns", "VE_run",
    "itertools", "shutil", "sys", "time", "Path", "Sequence",
    "fig_setup",
    "load_energyplan_file", "format_value", "build_params",
    "var_groups", "costs", "build_frames", "overview_fig", "wf",
    "ep_run_v2", "enable_autoreload",
]
