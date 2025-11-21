# pyfiles/var_groups.py
# Scenario lists, variable groups, and label dictionaries used across notebooks.


# ==================== ==================== ==================== ====================
# 1. scenario file lists

# 1a. active scenarios (v3)
shock = ['ETT_base_v3.xlsx', 'ETT_shock_v3.xlsx']

# 1b. legacy scenario lists (xlsx-based, kept for reference)
refs        = ['ETT_base.xlsx', 'IDA2045_Final.xlsx', 'RES.xlsx']


# ==================== ==================== ==================== ====================
# 2. display label dict for scenario stems
all_cases_dict = {
    '1GWnuc'                        : 'NOR Grundforløb',
    'IDA2045_Final'                 : 'FOA IDA2045',
    'IDA2045_nuclear_flexible_dh'   : 'FOA 1 GW nuclear (dh)',
    'R_1_nt'                        : 'ET baseline',
    'RES'                           : 'NOR baseline',
    'S_1_nt'                        : 'ET 1 GW nuclear with DH',
    'ETT_base_v3'                   : 'Grundforløb',
    'ETT_shock_v3'                  : 'Kernekraftforløb',
}


# ==================== ==================== ==================== ====================
# 3. variable groups for plotting

storages = [
    'Storage_Heat',
    'V2G_Storage',
    'Store_Storage',
    'H2_Storage',
]

# 3a. central variables for quick diagnostics
core_vars = [
    'Electr._Demand',
    'PV_Electr.',
    'Offshore_Electr.',
    'Nuclear_Electr.',
    'CSHP_tot_Heat',
    'PP2_Electr.',
    'H2_prod.',
    'H2_Storage',
    # 'Storage_Heat',
    'Store_Storage',
]


# ==================== ==================== ==================== ====================
# 4. display label dicts

tech_labels = {
    # 4a. core electricity technologies
    'Wind_Electr.':       'Landvind',
    'Offshore_Electr.':   'Havvind',
    'PV_Electr.':         'Sol',
    'HP_Electr.':         'HP',
    'CHP_Electr.':        'CHP',
    'Charge_Electr.':     'Charging',
    'Discharge_Electr.':  'Discharging',
    'H2_Electr.':         'Elektrolyse',
    'HH-HP_Electr.':      'HH HP',
    'Nuclear_Electr.':    'Kernekraft el',
    'PP2_Electr.':        'Kondensværk (spidsbelastning)',

    # 4b. demand and system flows
    'Electr._Demand':     'Elefterspørgsel',
    'Elec.dem_Cooling':   'Electricity demand for cooling',
    'Import_Electr.':     'Electricity imports',
    'Export_Electr.':     'Electricity exports',
    'Storage_Content':    'Total storage content',
    'Flexible_Electr.':   'Flexible electricity demand',
    'Cooling_Electr.':    'Electricity demand for cooling equipment',

    # 4c. aggregated heat technologies
    'Solar_tot_Heat':     'Solar thermal heat',
    'CSHP_tot_Heat':      'FJV-produktion inkl. kernekraft',
    'CHP_tot_Heat':       'CHP heat',
    'HP_tot_Heat':        'Decentral HP heat',

    # 4d. other heat-related
    'Waste 3_Heat':       'Heat from waste plant (unit 3)',
    'HH Dem._Heat':       'Household heat demand',
    'HH CHP+HP_Heat':     'Household heat from CHP + HP',
    'HH Solar_Heat':      'Household solar thermal heat',

    # 4e. power plants and storage
    'CHP2+3_':            'Total output from CHP units 2+3',
    'PP_CAES':            'PP/CAES fuel demand',
    'PP_Electr.':         'Power plant (electricity)',

    # 4f. fuels and molecules
    'Biogas_':            'Biogas (production/consumption)',
    'Export_Gas':         'Gas eksport',
    'CO2Hydro_liq.fuel':  'Synthetic liquid fuel',
    'NH3Hydro_Ammonia':   'Ammonia from hydrogen',

    # 4g. hydrogen system
    'H2_demand':          'Hydrogen demand',
    'H2_prod.':           r'$H_2$-produktion',

    # 4h. storage state variables
    'H2_Storage':         r'$H_2$-lagring',
    'V2G_Storage':        'V2G lagring',
    'Store_Storage':      'Ellagring',
    'Storage_Heat':       'Termisk lagring',

    'InMarket_Prices':    'Market electricity price (EUR/MWh)',
}


# ==================== ==================== ==================== ====================
# 5. waterfall chart display mapping
waterfall_dict_full = {
    'Nuclear':                                      'KK inv.',
    'Marginal operation costs':                     'MC',
    'Fuel ex. Ngas exchange (after CHSP corr.)':    'Brændsel',
    'Wind offshore':                                'Havvind inv.',
    'Fleks. & Stab.':                               'Fleks. & Stab.',
    'Delta_sys':                                    'Systemomk.',
}
