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
Pr = 0.71 # Prandtl number for air 
k_r = 0.2 # Thermal conductivity of resin (W/m*K)

# Parameters of flow
m_h =  3.1e-4 # Mass flow rate (kg/s)
m_c = 6.7e-5 # Mass flow rate (kg/s)
T_hi = 50 # Inlet temperature of hot fluid (°C)
T_ci = 20 # Inlet temperature of cold fluid (°C) [= T_amb = 18/25°C]
eps =  np.linspace(0.5, 0.9, 10) # Effectiveness of the heat exchanger (range: 0.5 to 0.9)

# Maximum volume of the heat exchanger
Axy_max = (55 - 2) * (65 - 2) * 1e-6 # Maximum cross-sectional area of the HX (m^2)
Lz_max = (125 - 20 - 2) * 1e-3 # Maximum length of the HX(m)
V_max = Axy_max * Lz_max # Maximum volume of the HX(m^3)


# %% Read csv file with TPMS data and create a dictionary with the data
TPMS_data = pd.read_csv('Dati_TPMS.csv', sep=';')
TPMS_dict = {}
for _, row in TPMS_data.iterrows():
    key = (
        row['Type'], 
        float(row['s_mm'])
        )
    TPMS_dict[key] = (float(row['A_wet_m2']), float(row['Phi']))

# %% For cicle, on different TPMS
Type_vec = ['D', 'G', 'G']
Lc_vec = [10, 10, 15] # mm
thickness_vec = [1, 1, 1] # mm
NxNy_vec = [25, 25, 12]

plt.figure(figsize=(10, 6))
for Type, Lc, thickness, NxNy in zip(Type_vec, Lc_vec, thickness_vec, NxNy_vec):

    # Trasmittance of the single cell of the TPMS
    TPMS_key = (Type, Lc)
    A_wet, phi_cell = TPMS_dict[TPMS_key]

    phi_cell = phi_cell / 100 # Convert porosity from percentage to fraction
    Lc = Lc * 1e-3 # Convert characteristic length from mm to m

    phi_single = phi_cell / 2 # Porosity of the single cell (assuming half of the cell is occupied by the hot fluid and half by the cold fluid)
    Dh_single = 4 * phi_single * Lc**3/A_wet # Hydraulic diameter of the single cell (m)

    # limit values
    NxNy_max = int(np.floor(Axy_max / (Lc)**2)) # Maximum number of cells in x and y directions based on the maximum cross-sectional area
    Nz_max = int(np.floor(Lz_max / Lc)) # Maximum number of cells in the z direction based on the maximum length
    N_max = NxNy_max * Nz_max # Maximum number of cells based on the maximum volume

    # Reynolds number
    Re_h  = (4 * m_h/NxNy * Lc) / (A_wet * mu) # Reynolds number for the hot fluid
    Re_c  = (4 * m_c/NxNy * Lc) / (A_wet * mu) # Reynolds number for the cold fluid

    # Heat transfer coefficients
    Nu_hot = Nusselt_number(Re_h, Pr, Type) # Nusselt number for the hot fluid
    Nu_cold = Nusselt_number(Re_c, Pr, Type) # Nusselt number for the cold fluid
    h_hot = Nu_hot * k_air / Dh_single # Heat transfer coefficient for the hot fluid
    h_cold = Nu_cold * k_air / Dh_single # Heat transfer coefficient for the cold fluid

    # Overall heat transfer coefficient
    U = overall_heat_transfer_coefficient(h_hot, h_cold, k_r, thickness*1e-3) # Overall heat transfer coefficient (W/m^2*K)

    # Type of HX
    hx_type = 'countercurrent' # Type of heat exchanger (countercurrent, cocurrent)

    # Calculations
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
        DT1 = T_hi - T_ci
        DT2 = T_ho - T_co
    DT_ml =  (DT1 - DT2) / np.log(DT1 / DT2) # Log mean temperature difference (°C)

    # Calculate the required heat transfer area and the number of cells
    A = q / (U * DT_ml) # Required heat transfer area (m^2)
    N_cell = A / A_wet # Number of cells required
    Nz = N_cell / NxNy # Number of cells in the z direction

    # Output results
    label = f'Type {Type}, Lc={Lc*1e3:.0f} mm, Thickness={thickness:.0f} mm, NxNy={NxNy}, NxNy_max={NxNy_max:.0f}'
    line, = plt.plot(eps, Nz, marker='o', label=label)
    label_max = f'Maximum Nz for Type {Type}, Lc={Lc*1e3:.0f} mm'
    plt.axhline(y=Nz_max, color=line.get_color(), linestyle='--', label=label_max)
    


plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.title('Number of cells required vs Effectiveness')
plt.xlabel('Effectiveness (ε)')
plt.ylabel('Nz')
plt.grid()
plt.tight_layout()
plt.show()
