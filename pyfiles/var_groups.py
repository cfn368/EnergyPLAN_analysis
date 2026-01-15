#################################################################################################
# FILES
#################################################################################################

# a. all cases
all_cases = [
    '1GWnuc.xlsx', 
    'IDA2045_Final.xlsx', 
    'IDA2045_nuclear_flexible.xlsx',
    'IDA2045_nuclear_flexible_dh.xlsx',  
    'R_1_nt.xlsx', 
    'RES.xlsx', 
    'S_1_nt.xlsx',
]

# b. reference scenarios
refs = [
    'test_new_VP.xlsx', 
    'IDA2045_Final.xlsx', 
    'RES.xlsx',
]

# c. nuclear without district heating shock set
nuc = [
    # '1GWnuc.xlsx', 
    # 'IDA2045_nuclear_flexible.xlsx',
    'IDA2045_nuclear_flexible_dh.xlsx', 
    # 'S_1_nt.xlsx',
    'S_2_nt.xlsx',
    'S_3_nt.xlsx',
]

# d. shock scenarios
shock = ['test_new_VP.xlsx','test_new_VP_shock.xlsx'] 
shock_descrip = ['test_new_VP.xlsx','test_new_VP_shock.xlsx','IDA2045_nuclear_flexible_dh.xlsx'] 

#################################################################################################
# CAPACITIES
#################################################################################################

# Installed capacities (by source)
test_new_VP_caps = {
    'Wind_Electr.':         5150,   # MW
    'Offshore_Electr.':     8287,   # MW
    'PV_Electr.':           25134,  # MW
    'Nuclear_Electr.':      0,      # MW
    'H2_Storage':           320,    # GW
    'V2G_Storage':          36.63,  # GW
    'Store_Storage':        820,    # GW
    'Storage_Heat':         156,    # GW
}

test_new_VP_shock_caps = {
    'Wind_Electr.':         5150,   # MW
    'Offshore_Electr.':     6287,   # MW
    'PV_Electr.':           25134,  # MW
    'Nuclear_Electr.':      1000,   # MW
    'H2_Storage':           320,    # GW
    'V2G_Storage':          36.63,  # GW
    'Store_Storage':        820,    # GW
    'Storage_Heat':         156,    # GW
}

RES_caps = {
    'Wind_Electr.':         5000,
    'Offshore_Electr.':     12560,
    'PV_Electr.':           10000,
    'Nuclear_Electr.':      0,
    'H2_Storage':           320,
    'V2G_Storage':          36.63,
    'Store_Storage':        820,
    'Storage_Heat':         156,
}

IDA2045_Final_caps = {
    'Wind_Electr.':         5000,
    'Offshore_Electr.':     14000,
    'PV_Electr.':           10000,
    'Nuclear_Electr.':      0,
    'H2_Storage':           320,
    'V2G_Storage':          36.63,
    'Store_Storage':        820,
    'Storage_Heat':         156,
}

IDA2045_nuclear_flexible_dh = {
    'Wind_Electr.':         5000,
    'Offshore_Electr.':     12560,
    'PV_Electr.':           10000,
    'Nuclear_Electr.':      1000,
    'H2_Storage':           320,
    'V2G_Storage':          36.63,
    'Store_Storage':        820,
    'Storage_Heat':         156,
}

GWnuc_caps = {
    'Wind_Electr.':         5000,
    'Offshore_Electr.':     12560,
    'PV_Electr.':           10000,
    'Nuclear_Electr.':      1000,
    'H2_Storage':           180.2,
    'V2G_Storage':          36.63,
    'Store_Storage':        820,
    'Storage_Heat':         156,
}

#################################################################################################
# GROUPS
#################################################################################################

storages = [
    'H2_Storage',
    'V2G_Storage',
    'Store_Storage',
    'Storage_Heat',
]

# Trade, prices, constraints, aggregate technology blocks
vars_trade_prices = [
    'Import_Electr.',
    'Export_Electr.',
    'Export_Gas',
    'CEEP_Electr.',
    'ExMarket_Prices',
    'System_Prices',
    'InMarket_Prices',
    'Export_Payment',
    'Blt-neck_Payment',
]

# Production-related variables
production = [
    "Electr._Demand",
    "Wind_Electr.",
    "Offshore_Electr.",
    "PV_Electr.",
    "Nuclear_Electr.",
    "Import_Electr.",
    "Export_Electr.",
]

# Central variables for plots / diagnostics
core_vars = [
    # 'Electr._Demand',
    # 'DH_Demand',
    'CSHP_tot_Heat',
    'Wind_Electr.',
    'Offshore_Electr.',
    'PV_Electr.',
    'CHP_Electr.',
    'Nuclear_Electr.',
    'H2_Storage',
    'V2G_Storage',
    'Store_Storage',
    'Storage_Heat',
    # 'Import_Electr.',
    'Export_Electr.',
    'InMarket_Prices',
]

# Production decomposition (post-aggregation)
non_zero_cols = [
    # 'Electr._Demand',          # total electricity demand – excluded here
    'Elec.dem_Cooling',          # Electricity demand used for cooling
    # 'DH_Demand',               # district heating demand – excluded
    'Wind_Electr.',              # Electricity production from onshore wind
    'Offshore_Electr.',          # Electricity production from offshore wind
    'PV_Electr.',                # Electricity production from solar PV

    # aggregated heat technologies
    'Solar_tot_Heat',            # Total solar thermal heat (Solar_ + Solar2_)
    'CSHP_tot_Heat',             # Total central HP heat (CSHP 2 + CSHP 3)
    'CHP_tot_Heat',              # Total CHP heat (CHP 2 + CHP 3)
    'HP_tot_Heat',               # Total decentralised HP heat (HP 2 + HP 3)

    'Waste 3_Heat',              # Heat from waste-fired unit 3

    'Flexible_Electr.',          # Flexible electricity demand (shiftable load)
    'HP_Electr.',                # Electricity consumption by heat pumps (system)
    # 'CSHP_Electr.',              # Electricity use of central large-scale HPs
    # 'CHP_Electr.',               # Electricity production from CHP units
    'Charge_Electr.',            # Electricity used for charging storage
    'Discharge_Electr.',         # Electricity discharged from storage
    # 'V2G_Demand',
    'V2G_Charge',                # Electricity charged into EVs for V2G
    'H2_Electr.',                # Electricity consumption for hydrogen production
    'CO2Hydro_liq.fuel',         # Synthetic liquid fuel from CO₂ + hydrogen
    'NH3Hydro_Ammonia',          # Ammonia produced from hydrogen
    'HH-HP_Electr.',             # Household electricity use for heat pumps
    'HH Dem._Heat',              # Total household heat demand
    'HH CHP+HP_Heat',            # Household heat from CHP + HP
    'HH Solar_Heat',             # Household solar thermal heat
    'CHP2+3_',                   # Combined output from CHP units 2 and 3
    'PP_CAES',                   # Compressed air energy storage plant
    'Indust._Various',           # Various industrial energy uses
    # 'Demand_Sum',
    'Biogas_',                   # Biogas use/production
    # 'Storage_Content',
    'Export_Gas',                # Gas exported from the system
    # 'Cool-El_Demand',
    'Cooling_Electr.',           # Electricity demand from cooling equipment
    'H2_demand',                 # Total hydrogen demand
    'H2_prod.',                  # Total hydrogen production
]

electr = [
    'Wind_Electr.',
    'Offshore_Electr.',
    'PV_Electr.',
    'HP_Electr.',
    # 'CSHP_Electr.',
    # 'CHP_Electr.', # think this is actually combined heat and power
    'Charge_Electr.',
    'Discharge_Electr.',
    # 'V2G_Charge',
    'H2_Electr.',
    'HH-HP_Electr.',
    # 'Cooling_Electr.',
    'Nuclear_Electr.',
]

VE_electr = [
    'Wind_Electr.',
    'Offshore_Electr.',
    'PV_Electr.',
    'Nuclear_Electr.',
]

heat = [
    'Solar_tot_Heat',
    'CSHP_tot_Heat',
    'CHP_tot_Heat',
    'HP_tot_Heat',
    'Waste 3_Heat',  
    'HH Dem._Heat',
    'HH CHP+HP_Heat',
    'HH Solar_Heat',
]

#################################################################################################
# DICTIONARIES FOR VARIABLE LABELS
#################################################################################################

tech_labels = {
    # core electricity technologies
    'Wind_Electr.':       'Onshore wind',
    'Offshore_Electr.':   'Offshore wind',
    'PV_Electr.':         'Solar PV',
    'HP_Electr.':         'HP', # heat pumps
    # 'CSHP_Electr.':       'Central heat pumps', 
    # 'CHP_Electr.':        'CHP',
    'Charge_Electr.':     'Charging',
    'Discharge_Electr.':  'Discharging',
    'H2_Electr.':         'Electrolysis',
    'HH-HP_Electr.':      'HH HP', # Household heat pumps 
    'Nuclear_Electr.':    'Nuclear electricity',

    # demand / system flows
    'Electr._Demand':     'Electricity demand',
    'Elec.dem_Cooling':   'Electricity demand for cooling',
    'Import_Electr.':     'Electricity imports',
    'Export_Electr.':     'Electricity exports',
    'Storage_Content':    'Total storage content',
    'Flexible_Electr.':   'Flexible electricity demand',
    'Cooling_Electr.':    'Electricity demand for cooling equipment',

    # aggregated heat technologies
    'Solar_tot_Heat':     'Solar thermal heat',
    'CSHP_tot_Heat':      'Central HP heat',
    'CHP_tot_Heat':       'CHP heat',
    'HP_tot_Heat':        'Decentral HP heat',

    # other heat-related
    'Waste 3_Heat':       'Heat from waste plant (unit 3)',
    'HH Dem._Heat':       'Household heat demand',
    'HH CHP+HP_Heat':     'Household heat from CHP + HP',
    'HH Solar_Heat':      'Household solar thermal heat',

    # power plants / storage
    'CHP2+3_':            'Total output from CHP units 2+3',
    'PP_CAES':            'Compressed air energy storage (plant)',

    # fuels / molecules
    'Biogas_':            'Biogas (production/consumption)',
    'Export_Gas':         'Gas exports',
    'CO2Hydro_liq.fuel':  'Synthetic liquid fuel',
    'NH3Hydro_Ammonia':   'Ammonia from hydrogen',

    # hydrogen system
    'H2_demand':          'Hydrogen demand',
    'H2_prod.':           'Hydrogen production',

    # storage state variables
    'H2_Storage':         'Hydrogen storage',
    'V2G_Storage':        'V2G storage',
    'Store_Storage':      'Electric storage',
    'Storage_Heat':       'Thermal storage',

    'InMarket_Prices':    'Market electricity price (EUR/MWh)',
}

all_cases_dict = {
    '1GWnuc.xlsx'                       : 'NOR 1 GW nuclear',
    'IDA2045_Final.xlsx'                : 'FOA IDA2045',
    'IDA2045_nuclear_flexible_dh.xlsx'  : 'FOA 1 GW nuclear (dh)',
    'R_1_nt.xlsx'                       : 'ET baseline',
    'RES.xlsx'                          : 'NOR baseline',
    'S_1_nt.xlsx'                       : 'ET 1 GW nuclear with DH',
    'test_new_VP.xlsx'                  : 'ETT Reference scenario',
    'test_new_VP_shock.xlsx'            : 'ETT Nuclear shock',
}
