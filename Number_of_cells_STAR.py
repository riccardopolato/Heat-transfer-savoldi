import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %% Data
# Parameters of the fluid (Air) and resin
cp = 1005 # Specific heat capacity at constant pressure (J/kg*K)
rho = 1.225 # Density of air (kg/m^3)
mu = 1.81e-5 # Dynamic viscosity of air (kg/m*s)
k_air = 0.0257 # Thermal conductivity of air (W/m*K)
Pr = 0.71 # Prandtl number for air 
k_r = 0.2 # Thermal conductivity of resin (W/m*K)

# Parameters of flow
m_h =  3.1e-4 # Mass flow rate (kg/s)
m_c = 6.7e-5 # Mass flow rate (kg/s)
T_hi = 50 # Inlet temperature of hot fluid (°C)
T_ci = 20 # Inlet temperature of cold fluid (°C) [= T_amb = 18/25°C]
eps =  np.linspace(0.05, 0.9, 10) # Effectiveness of the heat exchanger (range: 0.5 to 0.9)

# Maximum volume of the heat exchanger
Axy_max = (55 - 2) * (65 - 2) * 1e-6 # Maximum cross-sectional area of the HX (m^2)
Lz_max = (125 - 20 - 2) * 1e-3 # Maximum length of the HX(m)
V_max = Axy_max * Lz_max # Maximum volume of the HX(m^3)

# Type of heat exchanger
hx_type = 'countercurrent' # Type of heat exchanger (countercurrent or cocurrent)

# %% TPMS parameters
Type = 'G' # Type of TPMS
Lc = 10 # Characteristic length of the TPMS (mm)
Thickness = 1 # Thickness of the wall between hot and cold fluids (mm)
NxNy = 25 # Number of cells in the x and y directions

# Read csv file with TPMS data and create a dictionary with the data
TPMS_data = pd.read_csv('TPMS data.csv', sep=';')
TPMS_dict = {}
for _, row in TPMS_data.iterrows():
    key = (
        row['Type'], 
        float(row['Lc [mm]']), 
        float(row['Thickness [mm]']), 
        float(row['NxNy'])
        )
    TPMS_dict[key] = float(row['UA_cell [W/K]'])


# Trasmittance of the single cell of the TPMS
TPMS_key = (Type, Lc, Thickness, NxNy)
UA_cell = TPMS_dict[TPMS_key]

# limit values
NxNy_max = int(np.floor(Axy_max / (Lc * 1e-3)**2)) # Maximum number of cells in x and y directions based on the maximum cross-sectional area
Nz_max = int(np.floor(Lz_max / (Lc * 1e-3))) # Maximum number of cells in the z direction based on the maximum length

print(f'Maximum number of cells in x and y directions: {NxNy_max}')
print(f'Maximum number of cells in z direction: {Nz_max}')

# %% Calculation of the overall trasmittance UA
# Calculate the required heat transfer 
q_max = min(m_h * cp , m_c * cp ) * (T_hi - T_ci) # Maximum possible heat transfer rate (W)
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
DT_ml =  (DT1 - DT2) / np.log(DT1 / DT2) # Log mean temperature difference (°C)

UA = q / DT_ml # Overall Trasmittance (W/K)
N_cells = UA / UA_cell # Number of cells required to achieve the desired UA

Nz = N_cells / NxNy # Number of cells in the z direction


# %% plotting
plt.figure(figsize=(10, 6))
legend_label = f'Type {Type}, Lc={Lc} mm, Thickness={Thickness} mm, NxNy={NxNy}, NxNy_max={NxNy_max}'
plt.plot(eps, Nz, marker='o', label=legend_label)
plt.axhline(y=Nz_max, color='r', linestyle='--', label=f'Maximum Nz = {Nz_max}')
plt.title('Number of Cells along z vs Effectiveness')
plt.xlabel('ε')
plt.ylabel('Nz')
plt.grid()
plt.legend()
plt.show()