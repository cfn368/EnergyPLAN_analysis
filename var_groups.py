# a. all
all_cases = [
    '1GWnuc.xlsx', 
    'IDA2045_Final.xlsx', 
    'IDA2045_nuclear_flexible.xlsx', 
    'R_1_nt.xlsx', 
    'RES.xlsx', 
    'S_1_nt.xlsx',
]
all_cases_dict = {
    '1GWnuc.xlsx'                       : 'NOR 1GW kernekraft', 
    'IDA2045_Final.xlsx'                : 'FOA IDA2045',
    'IDA2045_nuclear_flexible.xlsx'     : 'FOA 1GW kernekraft',
    'R_1_nt.xlsx'                       : 'ET Basisforløb',
    'RES.xlsx'                          : 'NOR Basisforløb',
    'S_1_nt.xlsx'                       : 'ET 1GW kernekraft'
}

# b. references
refs = [
    'R_1_nt.xlsx', 
    'IDA2045_Final.xlsx', 
    'RES.xlsx',
]

# c. nuclear without dh
nuc = [
    '1GWnuc.xlsx', 
    'IDA2045_nuclear_flexible.xlsx', 
    'S_1_nt.xlsx',
]

# d. shock
shock = ['R_1_nt.xlsx', 'S_1_nt.xlsx']

# e. pick
files = refs

# link to caps
R_1_nt_caps = {
    'Wind_Electr.':         5150,   # MW
    'Offshore_Electr.':     8287,   # MW
    'PV_Electr.':           25134,  # MW
    'Nuclear_Electr.':      0,      # MW
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
    'H2_Storage':           180.2,
    'V2G_Storage':          36.63,
    'Store_Storage':        820,
    'Storage_Heat':         156,
}

storages = [
    'H2_Storage',
    'V2G_Storage',
    'Store_Storage',
    'Storage_Heat'
]


# Trade, prices, constraints, aggregate tech blocks
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

# production
production = [
    "Electr._Demand",
    "Wind_Electr.",
    "Offshore_Electr.",
    "PV_Electr.",
    "Nuclear_Electr.",
    "Import_Electr.",
    "Export_Electr.",
]

# central variables
core_vars = [
    'Electr._Demand',
    'Wind_Electr.',
    'Offshore_Electr.',
    'PV_Electr.',
    'CHP_Electr.',
    'PP_Electr.',
    'Nuclear_Electr.',
    'Storage_Content',
    'Import_Electr.',
    'Export_Electr.',
]


# production decomposition (post-aggregation)
non_zero_cols = [
    # 'Electr._Demand',          # (total electricity demand – excluded here)
    'Elec.dem_Cooling',          # Electricity demand used for cooling
    # 'DH_Demand',               # (district heating demand – excluded)
    'Wind_Electr.',              # Electricity production from onshore wind
    'Offshore_Electr.',          # Electricity production from offshore wind
    'PV_Electr.',                # Electricity production from solar PV

    # aggregated heat technologies
    'Solar_tot_Heat',            # Total solar thermal heat (Solar_ + Solar2_)
    'CSHP_tot_Heat',             # Total central HP heat (CSHP 2 + CSHP 3)
    'CHP_tot_Heat',              # Total CHP heat (CHP 2 + CHP 3)
    'HP_tot_Heat',               # Total decentral HP heat (HP 2 + HP 3)

    'Waste 3_Heat',              # Heat from waste-fired unit 3

    'Flexible_Electr.',          # Flexible electricity demand (shiftable load)
    'HP_Electr.',                # Electricity consumption by heat pumps (system)
    'CSHP_Electr.',              # Electricity use of central large-scale HPs
    'CHP_Electr.',               # Electricity production from CHP units
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
    'CSHP_Electr.',
    'CHP_Electr.',
    'Charge_Electr.',
    'Discharge_Electr.',
    # 'V2G_Charge',
    'H2_Electr.',
    'HH-HP_Electr.',
    # 'Cooling_Electr.',
]
tech_labels = {
    # core electricity techs
    'Wind_Electr.':       'Onshore wind',
    'Offshore_Electr.':   'Offshore wind ',
    'PV_Electr.':         'Solar PV',
    'HP_Electr.':         'El til varmepumper',
    'CSHP_Electr.':       'El til centrale varmepumper',
    'CHP_Electr.':        'Elproduktion fra kraftvarme',
    'Charge_Electr.':     'El til opladning',
    'Discharge_Electr.':  'El fra afladning',
    'H2_Electr.':         'El til elektrolyse',
    'HH-HP_Electr.':      'El til husholdningsvarmepumper',

    # demand / system flows
    'Electr._Demand':     'El-efterspørgsel',
    'Elec.dem_Cooling':   'El-efterspørgsel til køling',
    'Import_Electr.':     'Import af el',
    'Export_Electr.':     'Eksport af el',
    'Storage_Content':    'Samlet lagerindhold',
    'Flexible_Electr.':   'Fleksibelt elforbrug',
    'Cooling_Electr.':    'El-efterspørgsel til køleudstyr',

    # aggregated heat technologies
    'Solar_tot_Heat':     'Solvarme',
    'CSHP_tot_Heat':      'Central HP-varme ',
    'CHP_tot_Heat':       'Kraftvarme-varme ',
    'HP_tot_Heat':        'Decentral HP-varme ',

    # other heat-related
    'Waste 3_Heat':       'Varme fra affaldsanlæg ',
    'HH Dem._Heat':       'Husholdningers varmebehov',
    'HH CHP+HP_Heat':     'Husholdningsvarme fra CHP + HP',
    'HH Solar_Heat':      'Husholdnings solvarme',

    # power plants / storage
    'CHP2+3_':            'Samlet output fra CHP-enheder 2+3',
    'PP_CAES':            'Trykluftlager ',

    # fuels / molecules
    'Biogas_':            'Biogas (produktion/forbrug)',
    'Export_Gas':         'Eksport af gas',
    'CO2Hydro_liq.fuel':  'Syntetisk flydende brændsel',
    'NH3Hydro_Ammonia':   'Ammoniak produceret fra H₂',

    # hydrogen system
    'H2_demand':          'Efterspørgsel efter brint',
    'H2_prod.':           'Produktion af brint',

    # storage state variables
    'H2_Storage':         'Stored hydrogen',
    'V2G_Storage':        'V2G',
    'Store_Storage':      'Electirc storage',
    'Storage_Heat':       'Thermal storage'
}


VE_electr = [
    'Wind_Electr.',
    'Offshore_Electr.',
    'PV_Electr.',
    # 'Nuclear_Electr.'
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

other = [
    # 'V2G_Demand',
    'V2G_Charge',
    'CO2Hydro_liq.fuel',
    'NH3Hydro_Ammonia',
    'CHP2+3_',
    'PP_CAES',
    'Indust._Various',
    # 'Demand_Sum',
    'Biogas_',
    # 'Storage_Content',
    'Export_Gas',
    # 'Cool-El_Demand',
    'H2_demand',
    'H2_prod.',
]
