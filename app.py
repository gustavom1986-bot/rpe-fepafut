import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero después de los imports)
st.set_page_config(page_title="FEPAFUT RPE PRO", layout="wide")

# Estilos visuales (Diseño Oscuro Pro)
st.markdown("""
    <style>
    .stApp { background-color: #12141d; color: #ffffff; }
    div.stButton > button {
        background-color: #1e2129; color: #ffffff; border: 1px solid #cc0000;
        border-radius: 10px; font-weight: bold; height: 3.5em; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #cc0000; color: white; border-color: white; }
    h1 { text-align: center; border-bottom: 2px solid #cc0000; padding-bottom: 10px; color: white; }
    .status-card { background-color: #1e2129; border-radius: 10px; padding: 20px; border-top: 4px solid #cc0000; }
    </style>
    """, unsafe_allow_html=True)

# 2. VARIABLES DE ENLACE Y DATOS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSfpsb_RZQoF-5qBGjDCUuaCsvYBGG9zopQHjurVmIjIV-JkoeXp6DW3zixUTvARYfGQnnplHhjhdij/pub?output=csv"
ID_PREGUNTA = "1935706063"
URL_BASE_FORM = f"https://docs.google.com/forms/d/e/1FAIpQLSdfKHr_Ia197fDJysfVVEy1YZQfIpOCFR7iLKKArOVBdukPzw/viewform?usp=pp_url&entry.{ID_PREGUNTA}="

nombres_fijos = [
    "EDDIE ROBERTS", "OMAR CORDOBA", "LUIS ASPRILLA", "DANIEL APARICIO", 
    "ORMAN DAVIS", "RICHARD PERALTA", "JIMAR SANCHEZ", "KEVIN GALVAN", 
    "JORGE GUTIERREZ", "JUAN HALL", "JAVIER RIVERA", "GILBER MURILLO", 
    "ABDUL KNIGHT", "RICARDO PHILLIPS", "GIOVANI HERBERT", "HECTOR HURTADO", 
    "ARIEL ARROYO", "JOVANY WELCH", "GUSTAVO HERRERA", "KIDIR BARRIA", 
    "ANGEL CAICEDO", "SAED DIAZ", "KILISER LENIS"
]

if 'url_form' not in st.session_state: 
    st.session_state.url_form = None

# --- LÓGICA DE NAVEGACIÓN ---
if st.session_state.url_form:
    if st.button("⬅️ VOLVER AL PANEL PRINCIPAL"):
        st.session_state.url_form = None
        st.rerun()
    st.markdown(f'<iframe src="{st.session_state.url_form}" width="100%" height="800px" frameborder="0"></iframe>', unsafe_allow_html=True)

else:
    # --- LOGO Y TÍTULO ---
    c1, c2, c3 = st.columns([2,1,2])
    with c2:
        # Logo oficial de la selección
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/3/30/Panama_national_football_team_crest.svg/1200px-Panama_national_football_team_crest.svg.png", width=120)
    
    st.markdown("<h1>⚽ SISTEMA RPE FEPAFUT</h1>", unsafe_allow_html=True)
    
    # Grid de botones para los 23 jugadores
    st.subheader("👥 Registro de Jugadores")
    cols = st.columns(6)
    for i, nombre in enumerate(nombres_fijos):
        with cols[i % 6]:
            if st.button(nombre, key=f"btn_{i}", use_container_width=True):
                st.session_state.url_form = f"{URL_BASE_FORM}{urllib.parse.quote_plus(nombre)}"
                st.rerun()

    st.divider()

    # --- ANÁLISIS DE DATOS ---
    try:
        # Cargamos datos con un "cachebuster" para que se actualice al instante
        df = pd.read_csv(f"{URL_CSV}&t={int(time.time())}")
        df.columns = ['Fecha', 'Nombre', 'Sentimiento'] + list(df.columns[3:])
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Fecha', 'Nombre'])
        
        # Escala 1-10 (10 es el máximo esfuerzo/rojo)
        df['Nivel'] = df['Sentimiento'].astype(str).str.extract('(\d+)').astype(float)
        df['Dia_Texto'] = df['Fecha'].dt.strftime('%d/%m %a')

        st.subheader("📊 Tendencia de Esfuerzo (RPE)")
        df_semana = df[df['Fecha'].dt.date >= (datetime.now().date() - timedelta(days=7))]
        
        # Gráfico con paleta corregida: 1=Verde, 5=Amarillo, 10=Rojo
        fig = px.bar(df_semana, x='Dia_Texto', y='Nivel', color='Nivel',
                     template="plotly_dark",
                     color_continuous_scale=[[0, '#2ecc71'], [0.5, '#f1c40f'], [1, '#e74c3c']],
                     range_color=[1, 10], barmode='group', hover_name='Nombre')
        fig.update_layout(yaxis_range=[0, 10.5], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Resumen de Hoy
        st.divider()
        st.subheader("📋 Resumen de Asistencia Hoy")
        hoy = datetime.now().date()
        df_hoy = df[df['Fecha'].dt.date == hoy]
        completaron = df_hoy['Nombre'].tolist()
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="status-card">✅ <b>COMPLETADOS:</b></div>', unsafe_allow_html=True)
            if not df_hoy.empty:
                st.dataframe(df_hoy[['Nombre', 'Nivel']].sort_values('Nivel', ascending=False), use_container_width=True, hide_index=True)
            else: st.info("Esperando los primeros registros de hoy...")
            
        with col_b:
            st.markdown('<div class="status-card">❌ <b>PENDIENTES:</b></div>', unsafe_allow_html=True)
            pendientes = [n for n in nombres_fijos if n not in completaron]
            if pendientes:
                st.write(", ".join(pendientes))
            else: st.success("¡Excelente! Todo el equipo ha registrado hoy. ✅")

    except Exception as e:
        st.info("Sincronizando con la base de datos de Google...")
