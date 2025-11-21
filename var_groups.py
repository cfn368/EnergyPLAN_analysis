# 1) General electricity / demand
vars_elec_demand = [
    'Electr._Demand',
    'Elec.dem_Cooling',
    'Cool-El_Demand',
    'Cooling_Electr.',
    'Flexible_Electr.',
    'V2G_Demand',
    'H2_demand',
    'Demand_Sum',
]

# 2) DH / heat demand + HH heat
vars_heat_demand = [
    'DH_Demand',
    'HH Dem._Heat',
    'HH CHP+HP_Heat',
    'HH Solar_Heat',
    'HH Store_Heat',
    'HH Balan_Heat',
]

# 3) RES electricity (wind/solar/wave etc.)
vars_res_elec = [
    'Wind_Electr.',
    'Offshore_Electr.',
    'PV_Electr.',
    'Wave_Electr.',
    'Solar_Heat',
    'Solar2_Heat',
    'Solar2 Str_Heat',
    'Solar3_Heat',
]

# 4) DH area 2 heat production / balance
vars_dh2_heat = [
    'CSHP 2_Heat',
    'CHP 2_Heat',
    'HP 2_Heat',
    'Boiler 2_Heat',
    'EH 2_Heat',
    'Storage2_Heat',
    'Balance2_Heat',
]

# 5) DH area 3 heat production / balance
vars_dh3_heat = [
    'CSHP 3_Heat',
    'CHP 3_Heat',
    'HP 3_Heat',
    'Boiler 3_Heat',
    'EH 3_Heat',
    'Storage3_Heat',
    'Balance3_Heat',
]

# 6) Conventional / thermal power + nuclear + CO2Hydro
vars_thermal_elec = [
    'CHP_Electr.',
    'PP_Electr.',
    'PP2_Electr.',
    'Nuclear_Electr.',
    'CO2Hydro_Electr.',
    'CO2Hydro_lig.fuel',
]

# 7) Utility-scale storage (electric)
vars_storage = [
    'Charge_Electr.',
    'Discarge_Electr.',
    'Store_Storage',
    'Storage_Content',
    'Storage_',
]

# 8) V2G system
vars_v2g = [
    'V2G_Charge',
    'V2G_Discha.',
    'V2G_Storage',
]

# 9) Hydrogen system
vars_h2 = [
    'H2_Electr.',
    'H2_Storage',
    'H2_prod.',
    'H2_demand',
]

# 10) Household-side electricity (HP/EB)
vars_hh_elec = [
    'HH-HP_Electr.',
    'HH-HP/EB_Electr.',
]

# 11) Trade, prices, constraints, aggregate tech blocks
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

# 12) storage
storages = [
    'Storage2_Heat',
    'Storage3_Heat',
    'V2G_Storage',
    'Storage_Content',
    'Store_Storage',
    'H2_Storage',
]

# 13) production
production = ["Electr._Demand","Wind_Electr.","Offshore_Electr.","PV_Electr.",
              "Nuclear_Electr.","Import_Electr.","Export_Electr."]

# 14) central variables
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

vars_aggregates = [
    'Boilers_',
    'CHP2+3_',
    'PP_CAES',
]

all_output = ['Electr._Demand',
              'Elec.dem_Cooling',       # no diff
              'DH_Demand',              # no diff
              'Wind_Electr.',
              'Offshore_Electr.',
              'PV_Electr.',     
              'Wave_Electr.',           # no diff
              'Solar_Heat',             # no diff
              'CSHP 2_Heat',            # no diff
              'CHP 2_Heat',  
              'HP 2_Heat', 
              'Boiler 2_Heat',
              'EH 2_Heat',
              'Solar2_Heat',            # no diff
              'Solar2 Str_Heat',        # no diff
              'Storage2_Heat', 
              'Balance2_Heat',
              'CSHP 3_Heat',
              'CHP 3_Heat',
              'HP 3_Heat',
              'Boiler 3_Heat',
              'EH 3_Heat',
              'Solar3_Heat',            # no diff
              'Storage3_Heat',
              'Balance3_Heat',
              'Flexible_Electr.',
              'HP_Electr.',
              'CHP_Electr.',
              'PP_Electr.',
              'PP2_Electr.',
              'Nuclear_Electr.',
              'Charge_Electr.',
              'Discarge_Electr.',
              'Store_Storage',
              'V2G_Demand',
              'V2G_Charge',
              'V2G_Discha.',
              'V2G_Storage',
              'H2_Electr.',
              'H2_Storage',
              'CO2Hydro_Electr.',
              'CO2Hydro_lig.fuel',
              'HH-HP_Electr.',
              'HH-HP/EB_Electr.',
              'HH Dem._Heat',
              'HH CHP+HP_Heat',
              'HH Solar_Heat',
              'HH Store_Heat',
              'HH Balan_Heat',
              'Import_Electr.',
              'Export_Electr.',
              'CEEP_Electr.',
              'ExMarket_Prices',
              'System_Prices',
              'InMarket_Prices',
              'Export_Payment',
              'Blt-neck_Payment',
              'Boilers_',
              'CHP2+3_',
              'PP_CAES',
              'Demand_Sum',
              'Storage_',
              'Storage_Content',
              'Export_Gas',
              'Cool-El_Demand',         # no diff
              'Cooling_Electr.',        # no diff
              'H2_demand',              # no diff
              'H2_prod.',    
]