import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gasoducto Trans-Andino", page_icon="👷🏼", layout="wide")

# --- 1. PERSONALIZACIÓN DE INTERFAZ (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #87CEEB; 
        color: black;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #1f77b4;
    }
    
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Colores personalizados para las alertas de Streamlit */
    div[data-testid="stNotificationContentError"] {
        background-color: #FDEDEC;
        color: #943126;
        border-left: 6px solid #CB4335;
    }
    div[data-testid="stNotificationContentWarning"] {
        background-color: #FEF9E7;
        color: #7D6608;
        border-left: 6px solid #F4D03F;
    }
    div[data-testid="stNotificationContentSuccess"] {
        background-color: #EAFAF1;
        color: #186A3B;
        border-left: 6px solid #27AE60;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ENCABEZADO E IMÁGENES ---
st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="https://www.aga.org/wp-content/uploads/2023/05/Natural-Gas-Transport.jpg" 
        style="width:100%; height:150px; object-fit: cover; border-radius: 10px;">
    </div>
    <div style="display: flex; align-items: center; gap: 20px;">
        <img src="https://cdn-icons-png.flaticon.com/512/3232/3232975.png" width="50">
        <div>
            <h1 style="margin: 0; color: #2C3E50;">Sistema de Optimización Trans-Andino</h1>
            <p style="margin: 0; color: #4682B4; font-size: 1.2em;">Transporte de Gas Natural</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---") 

# --- DATOS TÉCNICOS DEL PROYECTO ---
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

# --- PANEL DE CONFIGURACIÓN (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    with st.expander("💰 Económicos", expanded=True):
        tasa = st.slider("Tasa de Interés (%)", 1, 20, 10) / 100
        e_cost = st.number_input("Costo Energía (USD/kWh)", value=0.12)
        
    with st.expander("🛠️ Materiales", expanded=True):
        d_nom = st.selectbox("Diámetro Nominal", list(TABLA_TUBERIAS.keys()), index=2)
        grado = st.selectbox("Grado de Acero", list(TABLA_ACERO.keys()))
        
    with st.expander("🚀 Operación", expanded=True):
        Q = st.number_input("Flujo (Q) [MMscfd]", value=500.0)
        # CORRECCIÓN: P_in ahora es ajustable para que varíen las alertas MAOP [cite: 16]
        P_in = st.number_input("Presión de Entrada [psia]", value=800.0, step=50.0)
        N = st.slider("N° Estaciones (N)", 1, 5, 2)

# --- VARIABLES BASE [cite: 14-20] ---
L = 400.0  # km
P_min_entrega = 500.0 # psia
T_succion = 293.15  # K (20°C)
gamma = 0.65
Z = 0.90
E_eff = 0.92
k = 1.3
R_const = 10.73
n_isentr = 0.75

# --- CÁLCULOS HIDRÁULICOS (Weymouth) [cite: 28] ---
d_ext_in = TABLA_TUBERIAS[d_nom]["D_ext"] / 25.4
t_in = TABLA_TUBERIAS[d_nom]["t"] / 25.4
D_int = d_ext_in - 2 * t_in 

L_tramo = L / N
distancias = np.linspace(0, L, 200)
presiones = []
P_actual = P_in

for d in distancias:
    dist_tramo = d % L_tramo
    # Detectar estación de compresión (reinicio de presión)
    if d > 0 and dist_tramo < (distancias[1] - distancias[0]):
        P_actual = P_in
    
    factor = 433.5 * (Q/E_eff)**2 * (gamma * T_succion * Z) / (D_int**5.33)
    P_calc = np.sqrt(max(1.0, P_in**2 - factor * dist_tramo))
    presiones.append(P_calc)

# CORRECCIÓN: P_final_real captura la presión JUSTO ANTES de la última estación 
P_final_real = presiones[-2] 

# --- CÁLCULOS DE COMPRESIÓN Y COSTOS [cite: 31-33] ---
P_suc_real = presiones[int(len(presiones)/N)-1] 
r_comp = P_in / P_suc_real

HP_estacion = (Q * 10**6 / (24*3600*n_isentr)) * \
              (Z * R_const * T_succion / (k - 1)) * \
              ((r_comp)**((k - 1) / k) - 1)
HP_total = HP_estacion * N
T_out_C = T_succion * (r_comp)**((k - 1) / k) - 273.15 

CAPEX_ducto = TABLA_TUBERIAS[d_nom]["costo"] * L * 1000
CAPEX_comp = HP_total * 1500 
OPEX = HP_total * 0.7457 * 8760 * e_cost 
TAC = (CAPEX_ducto + CAPEX_comp) * tasa + OPEX

# --- VISUALIZACIÓN PRINCIPAL ---
st.title("🏗️ Dashboard de Simulación")

# 1. Dashboard de Métricas [cite: 41]
m1, m2, m3 = st.columns(3)
m1.metric("TAC Total", f"${TAC/1e6:,.2f} M USD")
m2.metric("Potencia Total", f"{HP_total:,.0f} HP")
m3.metric("P. Entrega Final", f"{P_final_real:.1f} psia", delta=round(P_final_real - P_min_entrega, 1))

t1, t2, t3 = st.tabs(["📈 Perfil Hidráulico", "📊 Desglose de Costos", "🛡️ Seguridad"])

with t1: 
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=distancias, y=presiones, name="Presión (psia)", line=dict(color='#1f77b4', width=3)))
    fig.add_hline(y=P_min_entrega, line_dash="dash", line_color="red")
    
    fig.update_layout(
        title="<b>Perfil de Presión Weymouth</b>",
        plot_bgcolor="white",
        xaxis=dict(title="<b>Distancia (km)</b>", showgrid=True, gridcolor='lightgray', linewidth=2, linecolor='black', mirror=True),
        yaxis=dict(title="<b>Presión (psia)</b>", showgrid=True, gridcolor='lightgray', linewidth=2, linecolor='black', mirror=True)
    )
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.bar_chart({"CAPEX Anual": (CAPEX_ducto + CAPEX_comp) * tasa, "OPEX Energía": OPEX})

with t3:
    # MAOP (Límite Barlow) 
    MAOP = (2 * TABLA_ACERO[grado]["SMYS"] * t_in * TABLA_ACERO[grado]["F"]) / d_ext_in
    
    if P_in > MAOP: 
        st.error(f"❌ Riesgo MAOP: {P_in:.0f} > {MAOP:.0f} psia (Límite Barlow superado)")
    else: 
        st.success(f"✅ Presión de entrada segura (MAOP: {MAOP:.0f} psia)")
    
    if T_out_C > 65: 
        st.error(f"❌ Alerta Térmica: {T_out_C:.1f} °C > 65 °C")
    else: 
        st.success(f"✅ Temperatura de descarga segura ({T_out_C:.1f} °C)")
    
    if P_final_real < P_min_entrega: 
        st.error(f"❌ Presión de entrega insuficiente ({P_final_real:.1f} psia < 500 psia)")
    else: 
        st.success(f"✅ Entrega garantizada ({P_final_real:.1f} psia)")
