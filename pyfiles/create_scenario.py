# pyfiles/create_scenario.py
"""
Create EnergyPLAN scenario files
==================================

Builds base and shock .txt input files by overriding parameters in IDA2045_Final.txt.
Called from 3_run_all.ipynb via create_scenarios().
"""

from pathlib import Path
from pyfiles.scenario_functions import build_params, format_value, load_energyplan_file


# ==================== ==================== ==================== ====================
# 0. paths

_ROOT    = Path(__file__).parent.parent
REF_PATH = _ROOT / ".." / "ZipEnergyPLAN163" / "energyPlan Data" / "Data" / "IDA2045_Final.txt"
DATA_DIR = _ROOT / ".." / "ZipEnergyPLAN163" / "energyPlan Data" / "Data"

# ==================== ==================== ==================== ====================
# 1. parameters

YEAR = '2024'

    # variables --------------- # value ------- # description --------------------- # source -------------------
BASE_CASE_PARAMS = {
    'input_nuclear_cap'         : 0,            # base nuclear capacity             # KF26
    'input_RES2_capacity'       : 9686,         # base off-shore wind               # KF26          
    'input_keol_reg'            : 234570000,                                        # FOA IDA

    'input_cap_pp2_el'          : 1250,         # Extra power plant cap             # (endogenous)
    'input_cap_ELTtrans_el'     : 3447,         # electrolyser: shock optimum       # ET
    'input_H2storage_trans_cap' : 73/10,        # H_2 storage cap                   # FOA
    'input_storage_pump_cap'    : 20,           # batteries                         # ET

    'input_RES1_factor'         : 800/1000,     # onshore wind                      # KF26            
    'input_RES2_factor'         : 360/1000,     # offshore wind                     # KF26            
    'input_RES3_factor'         : 500/1000,     # solar PV                          # KF26            
}

SHOCK_CASE_PARAMS = {
    'input_nuclear_cap'         : 1000,         # shock nuclear capacity            # ET
    'input_RES2_capacity'       : 9686-1690,    # shock off-shore wind              # ET            
    'input_keol_reg'            : 923457000,                                        # ET
    'input_cshp_th_gr3'         : 234/100,      # nuclear heat prod                 # endogenous, year-round, f=0.4

    'input_cap_pp2_el'          : 1193,         # Extra power plant cap             # endogenous    
    'input_cap_ELTtrans_el'     : 3496,         # electrolyses capacity             # endogenous    
    'input_H2storage_trans_cap' : 68/10,        # H_2 storage cap                   # FOA
    'input_storage_pump_cap'    : 18,           # batteries                         # endogenous FOA

    'input_RES1_factor'         : 800/1000,     # onshore wind                      # KF26            
    'input_RES2_factor'         : 360/1000,     # offshore wind                     # KF26            
    'input_RES3_factor'         : 500/1000,     # solar PV                          # KF26            
} 

BASE_PARAMS = {

    # variables --------------- # value ------- # description --------------------- # source -------------------
    # demand
    'Input_el_demand_Twh'       : 322/10,       # electricity demand                # KF26          
    'Input_add_el_TWh'          : 92/10,        # additional electricity demand     # KF26          

    # production
    'input_RES1_capacity'       : 5745,         # on-shore wind                     # KF26          
    'input_RES3_capacity'       : 21443,        # solar PV                          # KF26          

    # nuclear
    'input_nuclear_eff'         : 1,            # nuclear efficiency                # ET (to align with IEA)
    'input_Nuclear_factor'      : 9/10,         # nuclear correction factor         # FOA
    'input_fuel_price[12]'      : 259/100,      # nuclear fuel price (EUR/GJ)       # FOA
    'input_Nuclear_partload'    : 3/10,         # minimum hourly output             # ET

    # variation patterns
    'Filnavn_elbehov'           : f'q_h_2024_2025.txt',                             # ENS
    'Filnavn_wind'              : f'WS_VE_2024_2025.txt',                           # ENS
    'Filnavn_wave'              : f'WL_VE_2024_2025.txt',                           # ENS
    'Filnavn_pv'                : f'PV_VE_2024_2025.txt',                           # ENS
    'Filnavn_prices'            : f'wp_2024_2025.txt',                              # ENS
    
    'Filnavn_cshp'              : 'cshp_dh_year_f30.txt',                           # ET year-round, f=0.3
    'filnavn_nuclear'           : 'nuclear_dh_year_f30.txt',                        # ET year-round, f=0.3

    # costs
    'input_Inv_Nuclear'         : 8,            # investment cost nuclear (MEUR/MW) # ET
    'input_Period_Nuclear'      : 60,           # economic lifetime nuclear (years) # FOA
    'input_FOM_Nuclear'         : 164/100,      # fixed O&M nuclear (%)             # OECD IEA

    'input_Inv_WindOffshore'    : 25/10,        # investment cost offshore, MEUR/MW # ET
    'input_Period_WindOffshore' : 30,           # economic lifetime offshore, years # FOA
    'input_FOM_WindOffshore'    : 192/100,      # fixed O&M offshore (%)            # ET

    'input_Inv_Electrolyser'    : 1,            # investment cost electrolyser      # IEA
    'input_Period_Electrolyser' : 20,           # lifetime electrolyser (years)     # FOA
    'input_FOM_Electrolyser'    : 240/100,      # fixed O&M electrolyser (%)        # FOA

    'input_Inv_PumpStorage'     : 201,          # investment cost per GWh           # ET
    'input_Period_PumpStorage'  : 20,           # lifetime (years)                  # FOA
    'input_FOM_PumpStorage'     : 29/10,        # fixed O&M (%)                     # ET

    'input_fuel_price[3]'       : 792/100,      # Ngas price                        # KF26

    # ToT
    'input_VC_turbine'          : 0,            # import price EUR/MWh              # ET
    'input_VC_pump'             : 0,            # export price EUR/MWh              # ET
    'input_nordpool_mult_fac'   : 112/1000,     # average external market price     # KF26          
}


# ==================== ==================== ==================== ====================
# 2. write scenario files

def create_scenarios(year=YEAR, verbose=True):
    """Write base and shock .txt files to DATA_DIR."""
    for case in ('base', 'shock'):
        out_path = DATA_DIR / f'{year}_{case}_v3.txt'

        params = build_params(
            case=case,
            base_params=BASE_PARAMS,
            base_case_params=BASE_CASE_PARAMS,
            shock_case_params=SHOCK_CASE_PARAMS,
        )

        lines, value_idx = load_energyplan_file(REF_PATH)

        for name, new_val in params.items():
            if name not in value_idx:
                raise KeyError(f"Parameter name not found in file: {name!r}")
            lines[value_idx[name]] = format_value(new_val)

        with open(out_path, "w", encoding="utf-16") as f:
            f.writelines(lines)

        if verbose:
            print(f'Written: {out_path.name}')


if __name__ == '__main__':
    create_scenarios()
