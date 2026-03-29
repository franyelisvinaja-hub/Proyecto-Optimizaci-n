import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gasoducto Trans-Andino", page_icon="👷🏼", layout="wide")

# PERSONALIZACIÓN DE INTERFAZ (CSS)
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
    /* Sombra en widgets del sidebar al pasar el mouse */
    [data-testid="stSidebar"] div[data-testid="stWidgetLabel"] + div:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: 0.3s;
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

    /* ESTILO DE TABLA UNIFICADO: Blanco con líneas negras resaltantes */
    .stTable table {
        background-color: white !important;
        color: black !important;
        border: 2px solid black !important;
        border-collapse: collapse !important;
    }
    /* Encabezados y columna de índice (th) */
    .stTable thead tr th, .stTable tbody tr th {
        background-color: white !important;
        color: black !important;
        border: 2px solid black !important;
        font-weight: bold !important;
    }
    /* Celdas de datos (td) */
    .stTable tbody tr td {
        background-color: white !important;
        border: 2px solid black !important;
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ENCABEZADO
st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="https://www.aga.org/wp-content/uploads/2023/05/Natural-Gas-Transport.jpg" 
        style="width:100%; height:150px; object-fit: cover; border-radius: 10px;">
    </div>
    <div style="display: flex; align-items: center; gap: 20px;">
        <img src="https://cdn-icons-png.flaticon.com/512/3232/3232975.png" width="50">
        <div>
            <h1 style="margin: 0; color: #2C3E50;">Sistema de Optimización Trans-Andino</h1>
            <p style="margin: 0; color: #4682B4; font-size: 1.2em;">Gemelo Digital de Transporte de Gas</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---") 

# DATOS TÉCNICOS
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

# SIDEBAR
with st.sidebar:
    st.header("⚙️ Configuración")
    with st.expander("💰 Económicos", expanded=True):
        tasa = st.slider("Tasa de Interés (%)", 1, 20, 10) / 100
        e_cost = st.number_input("Costo de Energía (USD/kWh)", value=0.12)
    with st.expander("🛠️ Materiales", expanded=True):
        d_nom = st.selectbox("Diámetro Nominal", list(TABLA_TUBERIAS.keys()), index=2)
        grado = st.selectbox("Grado de Acero", list(TABLA_ACERO.keys()))
    with st.expander("🚀 Operación", expanded=True):
        Q = st.number_input("Flujo (Q) [MMscfd]", value=500.0)
        P_in = st.number_input("Presión de Entrada [psia]", value=800.0, step=50.0)
        N = st.slider("N° Estaciones (N)", 1, 5, 2)



# VARIABLES BASE 
L = 400.0                # Longitud (km)
P_min_entrega = 500.0    # Presión de entrega mínima (psia)
T_succion = 293.15       # Temperatura de succión (K)
gamma = 0.65             # Gravedad específica (adim)
Z = 0.90                 # Factor de compresibilidad (adim)
E_eff = 0.92             # Factor de Weymouth: valor estándar para tuberías de acero nuevas o bien mantenidas
k = 1.3                  # Constante adiabática: suele estar entre 1.26 y 1.33
R_const = 10.73          # Constante de los gases en psia
n_isentr = 0.75          # Eficiencia de compresión

# CÁLCULOS HIDRÁULICOS
d_ext_in = TABLA_TUBERIAS[d_nom]["D_ext"] / 25.4
t_in = TABLA_TUBERIAS[d_nom]["t"] / 25.4
D_int = d_ext_in - 2 * t_in 
L_tramo = L / N
distancias = np.linspace(0, L, 200)
presiones = []
for d in distancias:
    dist_tramo = d % L_tramo
    factor = 433.5 * (Q/E_eff)**2 * (gamma * T_succion * Z) / (D_int**5.33)
    P_calc = np.sqrt(max(1.0, P_in**2 - factor * dist_tramo))
    presiones.append(P_calc)
P_final_real = presiones[-2] 

# COMPRESIÓN Y COSTOS
P_suc_real = presiones[int(len(presiones)/N)-1] 
r_comp = P_in / P_suc_real
HP_estacion = (Q * 10**6 / (24*3600*n_isentr)) * (Z * R_const * T_succion / (k - 1)) * ((r_comp)**((k - 1) / k) - 1)
HP_total = HP_estacion * N
T_out_C = T_succion * (r_comp)**((k - 1) / k) - 273.15 

CAPEX_ducto_anual = (TABLA_TUBERIAS[d_nom]["costo"] * L * 1000) * tasa
CAPEX_comp_anual = (HP_total * 1500) * tasa 
OPEX = HP_total * 0.7457 * 8760 * e_cost 
TAC = CAPEX_ducto_anual + CAPEX_comp_anual + OPEX

# VISUALIZACIÓN DE RESULTADOS
st.title("🏗️ Dashboard de Simulación")
m1, m2, m3 = st.columns(3)
m1.metric("TAC Total", f"${TAC/1e6:,.0f} M USD")
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
        xaxis=dict(title="<b>Distancia (km)</b>", linewidth=2, linecolor='black', mirror='all', showline=True),
        yaxis=dict(title="<b>Presión (psia)</b>", linewidth=2, linecolor='black', mirror='all', showline=True)
    )
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("Análisis Económico Detallado")
    df_costos = pd.DataFrame({
        "Categoría": ["CAPEX Ducto", "CAPEX Compresión", "OPEX Energía"],
        "Costo Anual [USD]": [CAPEX_ducto_anual, CAPEX_comp_anual, OPEX]
    })
    col_bar, col_pie = st.columns(2)
    with col_bar:
        fig_bar = px.bar(df_costos, x="Categoría", y="Costo Anual [USD]", color="Categoría",
                         color_discrete_sequence=["#1f77b4", "#7fb3d5", "#ff7f0e"],
                         title="<b>Distribución de Costos</b>", text_auto='.2s')
        fig_bar.update_layout(
            plot_bgcolor="white", showlegend=False,
            # Marco rectángular cerrado completo
            xaxis=dict(linewidth=2, linecolor='black', mirror='all', showline=True),
            yaxis=dict(linewidth=2, linecolor='black', mirror='all', showline=True)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_pie:
        fig_pie = px.pie(df_costos, values="Costo Anual [USD]", names="Categoría", hole=0.4,
                         color_discrete_sequence=["#1f77b4", "#7fb3d5", "#ff7f0e"],
                         title="<b>Peso del CAPEX vs OPEX</b>")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("### 📋 Tabla de Resumen Económico")
    df_tabla = df_costos.copy()
    df_tabla.index = df_tabla.index + 1
    df_tabla["Costo Anual [USD]"] = df_tabla["Costo Anual [USD]"].map("${:,.0f}".format)
    df_tabla["Porcentaje (%)"] = (df_costos["Costo Anual [USD]"] / TAC * 100).map("{:.1f}%".format)
    # Mostramos la tabla con el estilo unificado
    st.table(df_tabla)

with t3:
    MAOP = (2 * TABLA_ACERO[grado]["SMYS"] * t_in * TABLA_ACERO[grado]["F"]) / d_ext_in
    if P_in > MAOP: st.error(f"❌ Riesgo MAOP: {P_in:.0f} > {MAOP:.0f} psia")
    else: st.success(f"✅ Presión Segura (MAOP: {MAOP:.0f} psia)")
    if T_out_C > 65: st.error(f"❌ Alerta Térmica: {T_out_C:.f} °C > 65 °C")
    else: st.success(f"✅ Temperatura Segura ({T_out_C:.1f} °C)")
    if P_final_real < P_min_entrega: st.error(f"❌ Presión insuficiente ({P_final_real:.f} < 500 psia)")
    else: st.success(f"✅ Entrega garantizada ({P_final_real:.1f} psia)")
