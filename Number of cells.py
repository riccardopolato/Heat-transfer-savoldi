import numpy as np
import CoolProp.CoolProp as CP
import pandas as pd

# def Nusselt_number(Re, Pr):
    


# def pressure_drop():




def overall_heat_transfer_coefficient(h_h, h_c, k_wall, t_wall):
    return 1 / (1/h_h + 1/h_c + t_wall/k_wall)



# %% Data
# Parameters of the fluid (Air)
cp = 1005 # Specific heat capacity at constant pressure (J/kg*K)
rho = 1.225 # Density of air (kg/m^3)
mu = 1.81e-5 # Dynamic viscosity of air (kg/m*s)
k_r = 0.2 # Thermal conductivity of air (W/m*K)
# Parameters of flow
m_h =  3.1e-4 # Mass flow rate (kg/s)
m_c = 6.7e-5 # Mass flow rate (kg/s)
T_hi = 50 # Inlet temperature of hot fluid (°C)
T_ci = 20 # Inlet temperature of cold fluid (°C) [= T_amb = 18/25°C]
eps =  0.15 # Effectiveness of the heat exchanger

# Parameters of the heat exchanger to be extracted
df = pd.read_csv("dati_tabella.csv")

# Creazione dizionario con i dati del CSV organizzato per tipo di TPMS.
# Convertiamo le unità di misura: s_mm (mm) in L (m), e phi (%) in phi_tot (-)
tpms_dict = {}
for _, row in df.iterrows():
    tipo = row["tipo"]
    if tipo not in tpms_dict:
        tpms_dict[tipo] = {}
        
    s_mm = int(row["s_mm"])
    tpms_dict[tipo][s_mm] = {
        "L": s_mm * 1e-3,              # Characteristic length (m)
        "phi_tot": row["phi"] / 100.0, # Porosity (fraction)
        "A_wet": row["A_wet"]          # Wet area (m^2)
    }

# Selezioniamo un TPMS e una taglia di cella (s) di default per i calcoli successivi
tpms_type = "D"
cell_size = 10

L = tpms_dict[tpms_type][cell_size]["L"]
phi_tot = tpms_dict[tpms_type][cell_size]["phi_tot"]
A_wet = tpms_dict[tpms_type][cell_size]["A_wet"]

phi_single = 0.5*phi_tot
# consideriamo zero offset tra le due superfici, quindi A_wet_hot = A_wet_cold = A_wet
# D_h_hot = 4 * phi * L**3 / A_wet_hot # Hydraulic diameter (m)
# D_h_cold = 4 * phi * L**3 / A_wet_cold # Hydraulic diameter (m)
D_h = 4 * phi_single * L**3 / A_wet # Hydraulic diameter (m)
# Reynolds number
Re_c  = (4 * m_c) / (np.pi * D_h * mu) # Reynolds number for the cold fluid
Re_h  = (4 * m_h) / (np.pi * D_h * mu) # Reynolds number for the hot fluid

# TPMS parameters
U = overall_heat_transfer_coefficient(h_hot, h_cold, k_r, thickness) # Overall heat transfer coefficient (W/m^2*K)


# Type of HX
hx_type = 'countercurrent' # Type of heat exchanger (countercurrent, cocurrent)

# %% Calculations
# Calculate the required heat transfer 
q_max = min(m_h * cp * (T_hi - T_ci), m_c * cp * (T_hi - T_ci)) # Maximum possible heat transfer rate (W)
q = eps * q_max # Actual heat transfer rate (W)
T_ho = T_hi - q / (m_h * cp) # Outlet temperature of hot fluid (°C)
T_co = T_ci + q / (m_c * cp) # Outlet temperature of cold fluid (°C)

# Calculate the log mean temperature difference
if hx_type == 'countercurrent':
    DT1 = T_hi - T_co
    DT2 = T_ho - T_ci
elif hx_type == 'cocurrent':
    DT1 = T_hi - T_co
    DT2 = T_ho - T_ci
DT_ml =  (DT1 - DT2) / np.log(DT1 / DT2) # Log mean temperature difference (°C)

# Calculate the required heat transfer area and the number of cells
A = q / (U * DT_ml) # Required heat transfer area (m^2)
N_cell = A / A_cell # Number of cells required


# %% Output results
results = [
    ("Maximum heat transfer rate", "q_max", q_max, "W"),
    ("Heat transfer rate", "q", q, "W"),
    ("Outlet temperature hot fluid", "T_ho", T_ho, "degC"),
    ("Outlet temperature cold fluid", "T_co", T_co, "degC"),
    ("Log mean temperature difference", "DT_ml", DT_ml, "degC"),
    ("Required heat transfer area", "A", A, "m^2"),
    ("Reynolds number cold fluid", "Re_c", Re_c, "-"),
    ("Reynolds number hot fluid", "Re_h", Re_h, "-"),
    ("Number of cells required", "N_cell", N_cell, "-"),
]

name_w = 34
sym_w = 8
val_w = 12
unit_w = 8

line = "+" + "-" * (name_w + 2) + "+" + "-" * (sym_w + 2) + "+" + "-" * (val_w + 2) + "+" + "-" * (unit_w + 2) + "+"
print(line)
print(f"| {'Description':<{name_w}} | {'Symbol':<{sym_w}} | {'Value':>{val_w}} | {'Unit':<{unit_w}} |")
print(line)
for desc, sym, val, unit in results:
    if sym == "A":
        value_str = f"{val:.2e}"
    elif sym in {"Re_c", "Re_h"}:
        value_str = f"{val:.0f}"
    else:
        value_str = f"{val:.2f}"
    print(f"| {desc:<{name_w}} | {sym:<{sym_w}} | {value_str:>{val_w}} | {unit:<{unit_w}} |")
print(line)