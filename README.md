# Nuclear Power in Denmark's Energy Mix — EnergyPLAN Analysis

Developed by Linus Lindquist for [Erhvervslivets Tænketank](https://www.e-tank.dk/) as part of Kernekraftprojektet.


---

**Omkostningerne ved kernekraft i det danske energimiks**

A quantitative assessment of the cost implications of introducing a 1 GW nuclear plant into Denmark's 2040 electricity system, using [EnergyPLAN](https://www.energyplan.eu/) v16.3 as the simulation engine.


## Background

Denmark's 2037 electricity system is modelled using **Klimafremskrivning 2026 (KF26)** as the baseline projection. The central question is:

> *What happens to the 
total system costs if Denmark replaces a portion of offshore wind with a 1 GW nuclear plant?*

Nuclear displaces offshore wind specifically — not onshore wind or solar — because binding constraints on land-based renewables are driven by local opposition rather than economics. Total electricity production is held approximately constant across scenarios.

---

## Methodology

### Scenario design

| Scenario | Nuclear capacity | Offshore wind |
|----------|-----------------|---------------|
| **Base** | 0 MW | 9,686 MW |
| **Shock** (nuclear) | 1,000 MW | 7,986 MW (− 1,690 MW) |

### Optimisation

An iterative Nelder-Mead optimisation (`2_2_optimiser.ipynb`) finds the backup power plant capacity (PP2), electrolyser capacity (ELT), and hydrogen storage (H₂St) that jointly minimise the **5_cost_decomposition metric** subject to an electricity import ceiling (≤ 0.8 TWh). The objective is:

```
TC5 = TAC − I_CSHP + Q_VRE × (145/7.45) + Q_KK × (10/7.45)
```

where TAC is EnergyPLAN's total annual cost, I_CSHP is the CSHP investment double-count, and the last two terms are external system costs at 145 DKK/MWh for VRE and 10 DKK/MWh for nuclear. (EnergyPLAN's electricity exchange cost is already part of TAC and is not added separately.) The optimisation is solved independently for each scenario.

### Cost decomposition

The total cost difference between scenarios is decomposed into six bars in the waterfall chart (`5_cost_decomposition.ipynb`):

1. **KK inv.** — annualised nuclear investment and O&M
2. **Havvind inv.** — annualised offshore wind investment and O&M (negative — cost saving from displaced capacity)
3. **MC** — change in marginal operating costs
4. **Brændsel** — fuel costs ex. gas exchange (uranium cost fully explains the difference)
5. **Fleks. & Stab.** — combined: electrolyser, electricity storage, backup power plants (PP2), gas exchange, and net import cost
6. **Systemomk.** — external grid integration costs (145 DKK/MWh for VRE, 10 DKK/MWh for nuclear), following ET working paper

---

## Repository structure

```
LL_project/
│
├── 1_get_vp.ipynb               # Fetch hourly time series from EDS API and write
│                                #   EnergyPLAN distribution files (.txt):
│                                #   demand, offshore/onshore wind, solar, spot price.
│                                #   Currently uses 2024/2025 data year.
│
├── 2_2_optimiser.ipynb          # Nelder-Mead optimisation over PP2, ELT, and H₂St;
│                                #   calls create_scenarios() then solver.py via the
│                                #   EnergyPLAN binary (no manual step required).
│
├── 3_run_all.ipynb              # Orchestration: calls create_scenarios(), runs both
│                                #   scenarios via ep_run_v2.run_many (calls EnergyPLAN
│                                #   binary, saves parquet), then executes notebooks 4 and 5.
│
├── 4_time_series_output.ipynb   # Explore model output: monthly production profiles,
│                                #   hourly dispatch.
│
├── 5_cost_decomposition.ipynb   # Full cost decomposition between scenarios;
│                                #   waterfall chart in absolute (M EUR)
│                                #   and relative (%) form.
│                                #   Saves: 0_figs/fig4.png (absolute),
│                                #          0_figs/fig5.png (relative).
│
├── pyfiles/                     # Python library 
│   ├── preamble.py              #   Shared imports; re-exports all modules
│   ├── create_scenario.py       #   Parameter dicts (BASE_PARAMS, BASE_CASE_PARAMS,
│   │                            #     SHOCK_CASE_PARAMS) and create_scenarios();
│   │                            #     patches IDA2045_Final.txt and writes scenario .txt
│   ├── ep_run_v2.py             #   EnergyPLAN runner: calls binary, parses ASCII,
│   │                            #     saves five parquet files per run
│   ├── build_frames.py          #   Load hourly/monthly parquet output;
│   │                            #     aggregate heat units; plot helpers
│   ├── costs.py                 #   Cost summary and waterfall input helpers
│   ├── scenario_functions.py    #   Read/write EnergyPLAN parameter files
│   ├── solver.py                #   Nelder-Mead minimiser of the 5_cost metric
│   │                            #     (TAC − CSHP inv + sys costs)
│   ├── var_groups.py            #   Scenario lists, variable groups, label dicts
│   ├── fig_setup.py             #   Global matplotlib style (serif, DK-safe fonts)
│   ├── overview_fig.py          #   Multi-panel monthly grid plot
│   └── wf.py                    #   Waterfall chart
│
├── 0_EP_runs/                   # EnergyPLAN parquet output — gitignored
│                                #   {name}_scalars.parquet, _annual, _monthly,
│                                #   _hourly, _investments (one set per run)
│
├── 0_intermediate/              # EDS API parquet cache — gitignored
├── 0_figs/                      # Output figures (tracked)
│   ├── fig4.png / fig5.png      #   Waterfall decomposition, absolute and relative (5_cost_decomposition)
│   ├── månedlig_oversigt.png    #   Monthly production profiles (4_time_series_output)
│   └── hourly/                  #   Hourly dispatch figures, one per variable (4_time_series_output)
│
└── .gitignore
```

EnergyPLAN itself and all scenario `.txt` / distribution `.txt` files live outside this repo in the parent `ZipEnergyPLAN163/` directory.

---

## How to run

**One-time setup (when input data or parameters change):**

1. **`1_get_vp.ipynb`** — Fetch EDS hourly data and write EP distribution files for the chosen data year (currently 2024/2025). Results are cached in `0_intermediate/`.

2. **`2_1_input_computations.ipynb`** — Compute derived inputs (correction factors, capacity factors, CHSP capacity, gas price, O&M fractions). Outputs inform the parameter dicts in `pyfiles/create_scenario.py`.

3. **`2_2_optimiser.ipynb`** — Run Nelder-Mead to find the PP2, ELT, and H₂St capacities that jointly minimise the 5_cost_decomposition metric (TC5) for each scenario. Calls `create_scenarios()` internally — no separate scenario-creation step needed.

**Each analysis run:**

4. **`3_run_all.ipynb`** — Calls `create_scenarios()`, executes both scenarios via `ep_run_v2.run_many` (calls EnergyPLAN binary, parses ASCII output, writes parquet), then runs notebooks 4 and 5 automatically. No manual EnergyPLAN export step is needed.

---

## Data sources

- **KF26** — Danish Ministry of Climate's Klimafremskrivning 2026: capacity and demand projections for 2037
- **IDA 2045 / FOA** — IDA's long-term energy scenario (reference study year 2045 — not the modelled year), used as the reference EnergyPLAN configuration (`IDA2045_Final.txt`)
- **EDS hourly data** — 2024/2025 observed production profiles for offshore wind, onshore wind, solar, and electricity demand, fetched via EDS API (`ET_eds_api`, see `1_get_vp.ipynb`)
- **EDS spot prices** — 2024/2025 hourly Danish electricity spot prices, fetched via EDS API
- **ET working paper** — Source for the VRE and nuclear system cost add-ons (145 / 10 DKK/MWh)

**Source abbreviations**

| Abbreviation | Full name |
|---|---|
| KF26  | Klimafremskrivning 2026 (Danish government climate projection) |
| FOA   | Fakta om Atomkraft / IDA 2045 scenario (AAU) |
| ET    | Erhvervslivets Tænketank (authors) |
| IEA   | International Energy Agency |

---

## Output files

EnergyPLAN output is written as parquet to `0_EP_runs/` (gitignored). Each run produces five files:

| File | Content |
|------|---------|
| `{name}_scalars.parquet` | 1 row × named scalar metrics (costs, emissions, fuel use) |
| `{name}_annual.parquet` | 1 row × annual production/flow columns (TWh/year) |
| `{name}_monthly.parquet` | 12 rows × monthly average columns (MW) |
| `{name}_hourly.parquet` | 8760 rows × hourly dispatch columns (MW) |
| `{name}_investments.parquet` | N rows × technology investment breakdown (M EUR) |

---

## Dependencies

- **Python 3.13** with Jupyter / IPython
- `numpy`, `pandas`, `matplotlib`, `requests`, `scipy`
- **EnergyPLAN v16.3** — Windows application; path configured in `ep_run_v2.py` and `solver.py`

---

## Related documents

| File | Description |
|------|-------------|
| Publication | Full analysis, assumptions, optimisation strategy, and scenario design (Danish) |
| ET system cost working paper | Source for the 145 / 10 DKK/MWh system cost add-ons |

---

