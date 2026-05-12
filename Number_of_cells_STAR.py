import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# %% Data
# Parameters of the fluid (Air) and resin
cp = 1005 # Specific heat capacity at constant pressure (J/kg*K)
rho = 1.225 # Density of air (kg/m^3)
mu = 1.81e-5 # Dynamic viscosity of air (kg/m*s)
k_air = 0.0257 # Thermal conductivity of air (W/m*K)
Pr = 0.71 # Prandtl number for air 
k_r = 0.2 # Thermal conductivity of resin (W/m*K)

# Parameters of flow
m_h =  3.1e-4# Mass flow rate (kg/s)
m_c = 6.7e-5 # Mass flow rate (kg/s)
T_hi = 50 # Inlet temperature of hot fluid (°C)
T_ci = 20 # Inlet temperature of cold fluid (°C) [= T_amb = 18/25°C]
eps =  np.linspace(0.01, 1, 10) # Effectiveness of the heat exchanger (range: 0.5 to 0.9)

# Maximum volume of the heat exchanger
Axy_max = (55 - 2) * (65 - 2) * 1e-6 # Maximum cross-sectional area of the HX (m^2)
Lz_max = (125 - 20 - 2) * 1e-3 # Maximum length of the HX(m)
V_max = Axy_max * Lz_max # Maximum volume of the HX(m^3)

# Type of heat exchanger
hx_type = 'countercurrent' # Type of heat exchanger (countercurrent or cocurrent)

# Read csv file with TPMS data and create a dictionary with the data
SCRIPT_DIR = Path(__file__).resolve().parent
FIGURES_DIR = SCRIPT_DIR / 'Figures'
FIGURES_DIR.mkdir(exist_ok=True)
TPMS_data = pd.read_csv(SCRIPT_DIR / 'TPMS data.csv', sep=';')


def get_first_available_value(row, column_names):
    for column_name in column_names:
        if column_name in row and pd.notna(row[column_name]):
            return row[column_name]
    raise KeyError(f"Missing required columns: {column_names}")


TPMS_dict = {}
for _, row in TPMS_data.iterrows():
    try:
        key = (
            row['Type'],
            float(row['Lc [mm]']),
            float(row['Thickness [mm]']),
            float(row['NxNy'])
        )
        TPMS_dict[key] = {
            'UA_cell': float(get_first_available_value(row, ['UA_cell [W/K]', 'UA_cell'])),
            'V_cell': float(get_first_available_value(row, ['V_cell [mm3]', 'V_cell', 'V_resin_percell [mm3]'])),
        }
    except (KeyError, ValueError):
        print(f"Skipping incomplete TPMS row: {row.to_dict()}")
        continue

# %% TPMS parameters
configurations = [
    {
        'Type': row['Type'],
        'Lc': int(row['Lc [mm]']),
        'Thickness': int(row['Thickness [mm]']),
        'NxNy': int(row['NxNy']),
    }
    for _, row in TPMS_data.drop_duplicates(subset=['Type', 'Lc [mm]', 'Thickness [mm]', 'NxNy']).iterrows()
]


plt.figure(figsize=(10, 6))

# Calculate the required heat transfer
q_max = min(m_h * cp, m_c * cp) * (T_hi - T_ci) # Maximum possible heat transfer rate (W)
q = eps * q_max # Actual heat transfer rate (W)
T_ho = T_hi - q / (m_h * cp) # Outlet temperature of hot fluid (°C)
T_co = T_ci + q / (m_c * cp) # Outlet temperature of cold fluid (°C)

# Calculate the log mean temperature difference
if hx_type == 'countercurrent':
    DT1 = T_hi - T_co
    DT2 = T_ho - T_ci
elif hx_type == 'cocurrent':
    DT1 = T_hi - T_ci
    DT2 = T_ho - T_co
else:
    raise ValueError("hx_type must be 'countercurrent' or 'cocurrent'")

DT_ml = (DT1 - DT2) / np.log(DT1 / DT2) # Log mean temperature difference (°C)
UA = q / DT_ml # Overall Trasmittance (W/K)

for config in configurations:
    Type = config['Type']
    Lc = config['Lc']
    Thickness = config['Thickness']
    NxNy = config['NxNy']

    TPMS_key = (Type, Lc, Thickness, NxNy)
    if TPMS_key not in TPMS_dict:
        print(f'Skipping missing TPMS data for {TPMS_key}')
        continue

    TPMS_entry = TPMS_dict[TPMS_key]
    UA_cell = TPMS_entry['UA_cell']
    V_resin_cell = TPMS_entry['V_cell']

    # limit values
    NxNy_max = int(np.floor(Axy_max / (Lc * 1e-3)**2)) # Maximum number of cells in x and y directions based on the maximum cross-sectional area
    Nz_max = int(np.floor(Lz_max / (Lc * 1e-3))) # Maximum number of cells in the z direction based on the maximum length

    N_cells = UA / UA_cell # Number of cells required to achieve the desired UA
    Nz = N_cells / NxNy # Number of cells in the z direction
    V_resin = N_cells * V_resin_cell # Total volume of resin required

    legend_label = (f'Type {Type}, Lc={Lc} mm, Thickness={Thickness} mm, NxNy={NxNy}, \n NxNy_max={NxNy_max}, Nz_max={Nz_max}')
    line, = plt.plot(eps, Nz, marker='o', label=legend_label)
    #plt.axhline(y=Nz_max, color=line.get_color(), linestyle='--', label=f'Maximum Nz = {Nz_max}')

plt.title('Number of Cells along z vs Effectiveness')
plt.xlabel('ε')
plt.ylabel('Nz')
plt.grid()
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'Number_of_cells_STAR.png', bbox_inches='tight', dpi=300)
plt.close()

plt.figure(figsize=(10, 6))

print(f"{'Type':<8} {'Lc':>6} {'Thickness':>10} {'NxNy':>6} {'V_resin_6cells [mm^3]':>24}")

for config in configurations:
    Type = config['Type']
    Lc = config['Lc']
    Thickness = config['Thickness']
    NxNy = config['NxNy']

    TPMS_key = (Type, Lc, Thickness, NxNy)
    if TPMS_key not in TPMS_dict:
        continue

    TPMS_entry = TPMS_dict[TPMS_key]
    UA_cell = TPMS_entry['UA_cell']
    V_resin_cell = TPMS_entry['V_cell']

    N_cells = UA / UA_cell
    V_resin = N_cells * V_resin_cell # Total resin volume in mm^3
    V_resin_6cells = NxNy * 6 * V_resin_cell 

    print(f"{Type:<8} {Lc:>6} {Thickness:>10} {NxNy:>6} {V_resin_6cells:>24.3f}")

    legend_label = f'Type {Type}, Lc={Lc} mm, Thickness={Thickness} mm, NxNy={NxNy}'
    line, = plt.plot(eps, V_resin, marker='o', label=legend_label)
    #plt.axhline(y=V_max, color=line.get_color(), linestyle='--', label=f'Maximum V = {V_max:.3e} m^3')

plt.title('Total Resin Volume vs Effectiveness')
plt.xlabel('ε')
plt.ylabel('V_resin [mm^3]')
plt.grid()
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(FIGURES_DIR / 'Total_resin_volume_STAR.png', bbox_inches='tight', dpi=300)
plt.close()
# %%
