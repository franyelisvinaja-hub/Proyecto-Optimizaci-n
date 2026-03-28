import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Gemelo Digital: Gasoducto Trans-Andino",
    page_icon="⛽",
    layout="wide"
)

# Estilo personalizado corregido (unsafe_allow_html)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PANEL DE CONFIGURACIÓN (SIDEBAR)  ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.markdown("---")

    # 1. Parámetros Económicos [cite: 37]
    with st.expander("💰 Parámetros Económicos", expanded=True):
        costo_energia = st.number_input("Costo Energía (USD/kWh)", value=0.12)
        costo_acero = st.number_input("Costo Acero ($/m)", value=350)
        tasa_interes = st.slider("Tasa de Interés (%)", 1, 20, 10)
    
    # 2. Selección de Material [cite: 38]
    with st.expander("🛠️ Selección de Material", expanded=True):
        diam_comercial = st.selectbox("Diámetro Nominal (pulg)", ["12\"", "16\"", "20\"", "24\""])
        grado_acero = st.radio("Grado del Acero", ["X52", "X60"])
    
    # 3. Variables Operativas [cite: 39]
    with st.expander("🚀 Variables Operativas", expanded=True):
        flujo_q = st.number_input("Flujo de Gas (Q) [MMscfd]", value=500.0)
        n_estaciones = st.slider("N° Estaciones (N)", 1, 5, 2)

# --- 3. VISUALIZACIÓN PRINCIPAL (MAIN PANEL)  ---
st.title("🏗️ Simulación: Gasoducto Trans-Andino")
st.markdown("---")

# 1. Dashboard de Métricas [cite: 41]
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("TAC Total", "$ --", help="Costo Total Anualizado [cite: 32]")
with col2:
    st.metric("Potencia Total", "-- HP", help="Potencia total instalada [cite: 41]")
with col3:
    st.metric("Presión Final", "-- psia", help="Presión de entrega [cite: 41]")

# Pestañas de Navegación
tab1, tab2, tab3 = st.tabs(["📈 Perfil Hidráulico", "📊 Desglose de Costos", "🛡️ Validación y Seguridad"])

with tab1:
    st.subheader("Perfil de Presión [psia] vs Distancia [km] [cite: 42]")
    st.info("Este gráfico mostrará la caída por fricción y el incremento por compresión[cite: 43].")
    # Gráfico vacío temporal
    fig_p = go.Figure()
    fig_p.update_layout(height=450, template="plotly_white", xaxis_title="Distancia (km)", yaxis_title="Presión (psia)")
    st.plotly_chart(fig_p, use_container_width=True)

with tab2:
    st.subheader("Análisis Económico (CAPEX vs OPEX) [cite: 44]")
    st.write("*(Espacio para gráfico de barras o sectores)*")

with tab3:
    st.subheader("Sistema de Validación y Alertas [cite: 45]")
    c1, c2, c3 = st.columns(3)
    # Alertas según el enunciado [cite: 46, 47, 48]
    with c1:
        st.warning("**Verificación MAOP:** Pendiente de cálculo.")
    with c2:
        st.warning("**Verificación Térmica:** Pendiente de cálculo.")
    with c3:
        st.warning("**Cumplimiento Entrega:** Pendiente de cálculo.")

# Pie de Página
st.markdown("---")
st.caption("Proyecto: Optimización y Simulación Digital de Sistemas de Transporte de Gas | 2026-02-17 [cite: 1, 4]")
