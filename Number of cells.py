import numpy as np
import CoolProp.CoolProp as CP
import pandas as pd
import matplotlib.pyplot as plt

def Nusselt_number(Re, Pr, geometria):
   
    """
    Parametri:
    Re (float): Numero di Reynolds
    Pr (float): Numero di Prandtl
    geometria (str): Tipo di TPMS ('G' per Gyroid, 'D' per Diamond, o 'P' per Primitive)
    
    Ritorna:
    float: Il numero di Nusselt calcolato
    """
    geometria = geometria.upper()

    if geometria == "G":
        if Re < 40:
            # Basato su Dixit et al. [Simulazione] (Range: 10 < Re < 40)
            return 0.188 * (Re ** 0.127) * (Pr ** 0.33)
        elif 40 <= Re <= 2500:
            # Basato su Reynolds et al. (Range: 40 < Re < 2500)
            return 0.172 * (Re ** 0.763) * (Pr ** 0.4)
        else:
            # Basato su Li et al. [Gyroid Cold] (Range: 3000 < Re < 70000)
            return 0.045 * (Re ** 0.883) * (Pr ** 0.33)

    elif geometria == "D":
        if Re < 40:
            # Basato su Iyer et al. (Range: 0 < Re < 300)
            return 1.18 * (Re ** 0.55) * (Pr ** 0.33)
        elif 40 <= Re <= 2500:
            # Basato su Reynolds et al. (Range: 40 < Re < 2500)
            return 0.17 * (Re ** 0.753) * (Pr ** 0.4)
        elif 2500 < Re <= 8900:
            # Basato su Liang et al. (Range: 2300 < Re < 8900)
            return 0.074 * (Re ** 0.449) * (Pr ** 0.3)
        else:
            # Basato su Li et al. [Diamond Cold] (Range: 2700 < Re < 70000)
            return 0.362 * (Re ** 0.668) * (Pr ** 0.33)

    elif geometria == "P":
        if Re < 40:
            # Basato su Iyer et al. (Range: 0 < Re < 300)
            return 0.732 * (Re ** 0.45) * (Pr ** 0.33)
        elif 40 <= Re <= 2700:
            # Basato su Reynolds et al. (Range: 40 < Re < 2700)
            return 0.056 * (Re ** 0.901) * (Pr ** 0.4)
        else:
            # Basato su Liang et al. (Range: 2300 < Re < 8900)
            return 0.128 * (Re ** 0.416) * (Pr ** 0.33)
            
    else:
        raise ValueError("Geometria non supportata. Scegli tra 'G', 'D', o 'P'.")

    


# def pressure_drop():




def overall_heat_transfer_coefficient(h_h, h_c, k_wall, t_wall):
    return 1 / (1/h_h + 1/h_c + t_wall/k_wall)



# %% Data
# Parameters of the fluid (Air) and resin
cp = 1005 # Specific heat capacity at constant pressure (J/kg*K)
rho = 1.225 # Density of air (kg/m^3)
mu = 1.81e-5 # Dynamic viscosity of air (kg/m*s)
k_air = 0.0257 # Thermal conductivity of air (W/m*K)
Pr = 1 # Prandtl number for air 
k_r = 0.2 # Thermal conductivity of resin (W/m*K)

# Parameters of flow
m_h =  3.1e-4 # Mass flow rate (kg/s)
m_c = 6.7e-5 # Mass flow rate (kg/s)
T_hi = 50 # Inlet temperature of hot fluid (°C)
T_ci = 20 # Inlet temperature of cold fluid (°C) [= T_amb = 18/25°C]
eps =  np.linspace(0.5, 0.9, 10) # Effectiveness of the heat exchanger (range: 0.5 to 0.9)

# Maximum volume of the heat exchanger
V_max = (125 - 20 - 2) * (55 - 2) * (65 - 2) * 1e-9 # Maximum volume (m^3)

# Parameters of the heat exchanger to be extracted
df = pd.read_csv("Heat-transfer-savoldi/dati_tabella.csv")

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
        "Dh": row["Dh_mm"] * 1e-3      # Hydraulic diameter (m)
    }

# Selezioniamo un TPMS e una taglia di cella (s) di default per i calcoli successivi
tpms_type = "G" # Tipo di TPMS (G, D, o P)
cell_size = 10
thickness = 1e-3 # Thickness of the wall between hot and cold fluids (m)

Lc = tpms_dict[tpms_type][cell_size]["L"]
phi_tot = tpms_dict[tpms_type][cell_size]["phi_tot"]
#A_wet = tpms_dict[tpms_type][cell_size]["A_wet"]
D_h_single = tpms_dict[tpms_type][cell_size]["Dh"]/2


phi_single = 0.5*phi_tot
A_wet = 4 * phi_single * Lc**3 / D_h_single # Wetted area per cell (m^2)

N_cell_max = V_max / Lc**3 # Maximum number of cells that can fit in the given volume

# consideriamo zero offset tra le due superfici, quindi A_wet_hot = A_wet_cold = A_wet
# D_h_hot = 4 * phi * L**3 / A_wet_hot # Hydraulic diameter (m)
# D_h_cold = 4 * phi * L**3 / A_wet_cold # Hydraulic diameter (m)
# D_h = 4 * phi_single * L**3 / A_wet # Hydraulic diameter (m)

# Reynolds number
Re_h  = (4 * m_h * Lc) / (A_wet * mu) # Reynolds number for the hot fluid
Re_c  = (4 * m_c * Lc) / (A_wet * mu) # Reynolds number for the cold fluid

# Heat transfer coefficients
Nu_hot = Nusselt_number(Re_h, Pr, tpms_type) # Nusselt number for the hot fluid
Nu_cold = Nusselt_number(Re_c, Pr, tpms_type) # Nusselt number for the cold fluid
h_hot = Nu_hot * k_air / D_h_single # Heat transfer coefficient for the hot fluid
h_cold = Nu_cold * k_air / D_h_single # Heat transfer coefficient for the cold fluid

# Overall heat transfer coefficient
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
N_cell = A / A_wet # Number of cells required


# %% Output results
plt.figure(figsize=(10, 6))
plt.subplot(1, 2, 1)
plt.plot(eps, A, marker='o')
plt.title('Area required vs Effectiveness')
plt.xlabel('Effectiveness (ε)')
plt.ylabel('Required Area (m^2)')
plt.grid()
plt.subplot(1, 2, 2)
plt.plot(eps, N_cell, marker='o', color='orange')
plt.axhline(y=N_cell_max, color='red', linestyle='--', label='Max cells (volume constraint)')
plt.legend()
plt.title('Number of cells required vs Effectiveness')
plt.xlabel('Effectiveness (ε)')
plt.ylabel('Number of cells required')
plt.grid()
plt.show()
