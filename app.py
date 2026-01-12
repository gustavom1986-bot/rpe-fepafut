import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN DE PÁGINA (SIEMPRE DEBE IR PRIMERO)
st.set_page_config(page_title="FEPAFUT RPE PRO", layout="wide")

# Estilos visuales oscuros
st.markdown("""
    <style>
    .stApp { background-color: #12141d; color: #ffffff; }
    div.stButton > button {
        background-color: #1e2129; color: #ffffff; border: 1px solid #cc0000;
        border-radius: 10px; font-weight: bold; height: 3.5em;
    }
    div.stButton > button:hover { background-color: #cc0000; color: white; }
    h1 { text-align: center; border-bottom: 2px solid #cc0000; padding-bottom: 10px; color: white; }
    .status-card { background-color: #1e2129; border-radius: 10px; padding: 20px; border-top: 4px solid #cc0000; }
    </style>
    """, unsafe_allow_html=True)

# 2. VARIABLES DE DATOS
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
    if st.button("⬅️ VOLVER AL PANEL"):
        st.session_state.url_form = None
        st.rerun()
    st.markdown(f'<iframe src="{st.session_state.url_form}" width="100%" height="800px" frameborder="0"></iframe>', unsafe_allow_html=True)

else:
    # --- LOGO NUEVO Y TÍTULO ---
    c1, c2, c3 = st.columns([2,1,2])
    with c2:
        # Aquí está el nuevo link que pasaste
        logo_fepafut = "https://www.metrolibre.com/binrepository/550x550/0c0/0d0/none/83989904/KLFW/logo-fpf_101-6904049_20240503144045.jpg"
        st.image(logo_fepafut, width=150)
    
    st.markdown("<h1>⚽ SISTEMA RPE FEPAFUT</h1>", unsafe_allow_html=True)
    
    # Botones
    st.subheader("👥 Registro de Jugadores")
    cols = st.columns(6)
    for i, nombre in enumerate(nombres_fijos):
        with cols[i % 6]:
            if st.button(nombre, key=f"btn_{i}", use_container_width=True):
                st.session_state.url_form = f"{URL_BASE_FORM}{urllib.parse.quote_plus(nombre)}"
                st.rerun()

    st.divider()

    # --- ANÁLISIS ---
    try:
        df = pd.read_csv(f"{URL_CSV}&t={int(time.time())}")
        df.columns = ['Fecha', 'Nombre', 'Sentimiento'] + list(df.columns[3:])
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Fecha', 'Nombre'])
        df['Nivel'] = df['Sentimiento'].astype(str).str.extract('(\d+)').astype(float)
        df['Dia_Texto'] = df['Fecha'].dt.strftime('%d/%m %a')

        # Gráfico: 1=Verde, 10=Rojo
        st.subheader("📊 Tendencia Semanal")
        df_semana = df[df['Fecha'].dt.date >= (datetime.now().date() - timedelta(days=7))]
        
        fig = px.bar(df_semana, x='Dia_Texto', y='Nivel', color='Nivel',
                     template="plotly_dark",
                     color_continuous_scale=[[0, '#2ecc71'], [0.5, '#f1c40f'], [1, '#e74c3c']],
                     range_color=[1, 10], barmode='group', hover_name='Nombre')
        fig.update_layout(yaxis_range=[0, 10.5], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

        # Tablas de hoy
        st.divider()
        st.subheader("📋 Resumen de Hoy")
        hoy = datetime.now().date()
        df_hoy = df[df['Fecha'].dt.date == hoy]
        completaron = df_hoy['Nombre'].tolist()
        
        col_1, col_2 = st.columns(2)
        with col_1:
            st.markdown('<div class="status-card">✅ <b>COMPLETADOS:</b></div>', unsafe_allow_html=True)
            if not df_hoy.empty:
                st.dataframe(df_hoy[['Nombre', 'Nivel']].sort_values('Nivel', ascending=False), use_container_width=True, hide_index=True)
            else: st.write("Esperando datos...")
            
        with col_2:
            st.markdown('<div class="status-card">❌ <b>PENDIENTES:</b></div>', unsafe_allow_html=True)
            pendientes = [n for n in nombres_fijos if n not in completaron]
            st.write(", ".join(pendientes) if pendientes else "¡Todos listos! ✅")

    except Exception as e:
        st.info("Sincronizando...")
