import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gasoducto Trans-Andino", page_icon= "👷🏼",layout="wide")

# --- 1. PERSONALIZACIÓN DE INTERFAZ (CSS) ---
st.markdown("""
    <style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Color de fondo de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #87CEEB; /*Azul cielo*/
        color: black;
    }

    /* Estilo para las tarjetas de métricas */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #1f77b4;
    }
    
    /* Personalización de los contenedores de alertas */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
      /* Color personalizado para st.error (Fallo de MAOP o Temperatura > 65°C) */
        div[data-testid="stNotificationContentError"] {
        background-color: #FDEDEC; /* Rojo muy suave */
        color: #943126;           /* Texto granate */
        border-left: 6px solid #CB4335; /* Barra lateral roja intensa */
    }
     /* Color personalizado para st.warning (Presión < 500 psia) */
    div[data-testid="stNotificationContentWarning"] {
        background-color: #FEF9E7; /* Amarillo muy suave */
        color: #7D6608;           /* Texto ocre */
        border-left: 6px solid #F4D03F; /* Barra lateral amarilla */
    }

    /* Color personalizado para st.success (Diseño óptimo) */
    div[data-testid="stNotificationContentSuccess"] {
        background-color: #EAFAF1; /* Verde muy suave */
        color: #186A3B;           /* Texto verde oscuro */
        border-left: 6px solid #27AE60; /* Barra lateral verde */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENCABEZADO E IMÁGENES ---

st.markdown(
    """
    <div style="display: flex; justify-content: center;">
        <img src="https://www.aga.org/wp-content/uploads/2023/05/Natural-Gas-Transport.jpg" 
        style="width:1280px; height:150px; object-fit: cover; border-radius: 10px;">
    </div>
      <h1 style="margin: 0; color: #2C3E50; font-family: sans-serif;">
            Sistema de Optimización Trans-Andino
        </h1>
    </div>
     <div style="display: flex; align-items: center;">
        <img src="https://cdn-icons-png.flaticon.com/512/3232/3232975.png" width="50" style="margin-right: 20px;">
    <p style="color: #4682B4; font-size: 2.1em;">Transporte de Gas Natural</p>
    """, unsafe_allow_html=True)
st.markdown("---") 
  
# --- DATOS TÉCNICOS DEL PROYECTO  ---
TABLA_TUBERIAS = {
    "12\"": {"D_ext": 323.8, "t": 10.31, "costo": 185},
    "16\"": {"D_ext": 406.4, "t": 12.70, "costo": 260},
    "20\"": {"D_ext": 508.0, "t": 15.09, "costo": 350},
    "24\"": {"D_ext": 609.6, "t": 17.48, "costo": 440}
}
TABLA_ACERO = {
    "X52": {"SMYS": 52000, "F": 0.72},
    "X60": {"SMYS": 60000, "F": 0.72}
}

# --- PANEL DE CONFIGURACIÓN (SIDEBAR)  ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    with st.expander("💰 Económicos [cite: 37]", expanded=True):
        tasa = st.slider("Tasa de Interés (%)", 1, 20, 10) / 100
        e_cost = st.number_input("Costo Energía (USD/kWh)", value=0.12)
        
    with st.expander("🛠️ Materiales [cite: 38]", expanded=True):
        d_nom = st.selectbox("Diámetro Nominal", list(TABLA_TUBERIAS.keys()), index=2)
        grado = st.selectbox("Grado de Acero", list(TABLA_ACERO.keys()))
        
    with st.expander("🚀 Operación [cite: 39]", expanded=True):
        Q = st.number_input("Flujo (Q) [MMscfd]", value=500.0)
        N = st.slider("N° Estaciones (N)", 1, 5, 2)

# --- VARIABLES BASE ---
L_total = 400.0  # km
P_in = 800.0     # psia
P_min_entrega = 500.0 # psia
T1 = 293.15      # K (20°C)
gamma = 0.65
Z = 0.90
E = 0.92         # Eficiencia de línea
k = 1.3          # Constante adiabática
R = 10.73
n_isentr = 0.75  # Eficiencia compresión

# --- CÁLCULOS HIDRÁULICOS (Weymouth)  ---
d_ext_in = TABLA_TUBERIAS[d_nom]["D_ext"] / 25.4
t_in = TABLA_TUBERIAS[d_nom]["t"] / 25.4
D = d_ext_in - 2 * t_in # Diámetro interno en pulgadas

L_tramo = L_total / N
distancias = np.linspace(0, L_total, 200)
presiones = []
P_actual = P_in

# Simulación del perfil
for d in distancias:
    dist_tramo = d % L_tramo
    if d > 0 and dist_tramo < (distancias[1] - distancias[0]):
        P_actual = P_in # Re-compresión en cada estación
    
    # Ecuación de Weymouth: P1^2 - P2^2 = factor * L
    factor = 433.5 * (Q/E)**2 * (gamma * T1 * Z) / (D**5.33)
    P_calc = np.sqrt(max(1.0, P_in**2 - factor * dist_tramo))
    presiones.append(P_calc)

P_final = presiones[-1]

# --- CÁLCULOS DE COMPRESIÓN Y COSTOS  ---
P_suc = presiones[int(len(presiones)/N)-1] # Presión al final del primer tramo
HP_estacion = (Q * 10**6 / (24*3600*n_isentr)) * (Z*R*T1/(k-1)) * ((P_in/P_suc)**((k-1)/k) - 1)
HP_total = HP_estacion * N
T2 = T1 * (P_in/P_suc)**((k-1)/k) - 273.15 # en Celsius

# Costos (Simplificados para el ejemplo) 
CAPEX_ducto = TABLA_TUBERIAS[d_nom]["costo"] * L_total * 1000
CAPEX_comp = HP_total * 1500 # 1500 USD/HP
OPEX = HP_total * 0.7457 * 8760 * e_cost # kW * horas_año * costo
TAC = (CAPEX_ducto + CAPEX_comp) * tasa + OPEX

# --- VISUALIZACIÓN PRINCIPAL  ---
st.title("🏗️ Gemelo Digital: Gasoducto Trans-Andino")

# 1. Dashboard de Métricas 
m1, m2, m3 = st.columns(3)
m1.metric("TAC Total", f"${TAC/1e6:.2f} M USD")
m2.metric("Potencia Total", f"{HP_total:,.0f} HP")
m3.metric("P. Entrega", f"{P_final:.1f} psia", delta=round(P_final-P_min_entrega,1))

t1, t2, t3 = st.tabs(["📈 Perfil Hidráulico", "📊 Desglose de Costos", "🛡️ Seguridad"])

with t1: # 
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=distancias, y=presiones, name="Presión (psia)"))
    fig.add_hline(y=P_min_entrega, line_dash="dash", line_color="red")
    fig.update_layout(title="Perfil de Presión Weymouth", xaxis_title="Distancia (km)", yaxis_title="Presión (psia)")
    st.plotly_chart(fig, use_container_width=True)

with t2: # 
    st.bar_chart({"CAPEX Ducto": CAPEX_ducto*tasa, "CAPEX Comp": CAPEX_comp*tasa, "OPEX Energía": OPEX})

with t3: # 
    # MAOP (Límite Barlow) 
    MAOP = (2 * TABLA_ACERO[grado]["SMYS"] * t_in * TABLA_ACERO[grado]["F"]) / d_ext_in
    
    if P_in > MAOP: st.error(f"❌ Riesgo MAOP: {P_in} > {MAOP:.0f} psia")
    else: st.success(f"✅ Presión Segura (MAOP: {MAOP:.0f} psia)")
    
    if T2 > 65: st.error(f"❌ Alerta Térmica: {T2:.1f} °C > 65 °C [cite: 47]")
    else: st.success(f"✅ Temperatura Segura ({T2:.1f} °C)")
    
    if P_final < P_min_entrega: st.error(f"❌ Presión insuficiente en entrega [cite: 48]")
    else: st.success("✅ Entrega garantizada (>500 psia)")
