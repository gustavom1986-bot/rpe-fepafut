import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import urllib.parse
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN (Debe ser lo primero)
st.set_page_config(page_title="FEPAFUT RPE PRO", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #12141d; color: #ffffff; }
    div.stButton > button {
        background-color: #1e2129; color: #ffffff; border: 1px solid #cc0000;
        border-radius: 10px; font-weight: bold; height: 3.5em;
    }
    div.stButton > button:hover { background-color: #cc0000; color: white; }
    h1 { text-align: center; border-bottom: 2px solid #cc0000; padding-bottom: 10px; }
    .status-card { background-color: #1e2129; border-radius: 10px; padding: 20px; border-top: 4px solid #cc0000; }
    .stTextInput > div > div > input { background-color: #1e2129; color: white; border: 1px solid #cc0000; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATOS Y VARIABLES
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSfpsb_RZQoF-5qBGjDCUuaCsvYBGG9zopQHjurVmIjIV-JkoeXp6DW3zixUTvARYfGQnnplHhjhdij/pub?output=csv"
ID_PREGUNTA = "1935706063"
URL_BASE_FORM = f"https://docs.google.com/forms/d/e/1FAIpQLSdfKHr_Ia197fDJysfVVEy1YZQfIpOCFR7iLKKArOVBdukPzw/viewform?usp=pp_url&entry.{ID_PREGUNTA}="

nombres_fijos = [
    "EDDIE ROBERTS", "OMAR CORDOBA", "LUIS ASPRILLA", "DANIEL APARICIO", 
    "ORMAN DAVIS", "RICHARD PERALTA", "AIMAR SANCHEZ", "KEVIN GALVAN", 
    "JORGE GUTIERREZ", "JUAN HALL", "JAVIER RIVERA", "GILBER MURILLO", 
    "ABDUL KNIGHT", "RICARDO PHILLIPS", "GIOVANI HERBERT", "HECTOR HURTADO", 
    "ARIEL ARROYO", "JOVANY WELCH", "GUSTAVO HERRERA", "KIDIR BARRIA", 
    "ANGEL CAICEDO", "SAED DIAZ", "KILISER LENIS"
]

if 'url_form' not in st.session_state: st.session_state.url_form = None

# --- NAVEGACIÓN FORMULARIO ---
if st.session_state.url_form:
    if st.button("⬅️ VOLVER AL PANEL"):
        st.session_state.url_form = None
        st.rerun()
    st.markdown(f'<iframe src="{st.session_state.url_form}" width="100%" height="800px" frameborder="0"></iframe>', unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
else:
    c1, c2, c3 = st.columns([2,1,2])
    with c2:
        logo = "https://www.metrolibre.com/binrepository/550x550/0c0/0d0/none/83989904/KLFW/logo-fpf_101-6904049_20240503144045.jpg"
        st.image(logo, width=150)
    st.markdown("<h1>⚽ SISTEMA RPE FEPAFUT</h1>", unsafe_allow_html=True)

    # BUSCADOR Y BOTONES
    st.subheader("👥 Registro de Jugadores")
    busqueda = st.text_input("🔍 Buscar jugador por nombre...", "").upper()
    
    nombres_filtrados = [n for n in nombres_fijos if busqueda in n]
    
    cols = st.columns(6)
    for i, nombre in enumerate(nombres_filtrados):
        with cols[i % 6]:
            if st.button(nombre, key=f"btn_{nombre}", use_container_width=True):
                st.session_state.url_form = f"{URL_BASE_FORM}{urllib.parse.quote_plus(nombre)}"
                st.rerun()

    st.divider()

    # ANÁLISIS Y COMPARATIVA
    try:
        df = pd.read_csv(f"{URL_CSV}&t={int(time.time())}")
        df.columns = ['Fecha', 'Nombre', 'Sentimiento'] + list(df.columns[3:])
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Fecha', 'Nombre'])
        df['Nivel'] = df['Sentimiento'].astype(str).str.extract('(\d+)').astype(float)
        df['Dia'] = df['Fecha'].dt.strftime('%d/%m')

        st.subheader("📊 Comparativa: Jugador vs. Promedio Equipo")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            # Lista de jugadores únicos para el buscador de gráfico
            opciones = sorted(df['Nombre'].unique())
            seleccionados = st.multiselect("Seleccionar Jugadores para comparar", options=opciones, default=opciones[:1] if opciones else [])
        with f_col2:
            dias_atras = st.slider("Días a mostrar en historial", 1, 14, 7)

        fecha_limite = datetime.now() - timedelta(days=dias_atras)
        df_f = df[df['Fecha'] >= fecha_limite]

        if not df_f.empty:
            promedio_grupal = df_f.groupby('Dia')['Nivel'].mean().reset_index()
            fig = go.Figure()

            # Barras para jugadores (USA 'in' EN LUGAR DE 'en')
            for j in seleccionados:
                df_j = df_f[df_f['Nombre'] == j]
                fig.add_trace(go.Bar(x=df_j['Dia'], y=df_j['Nivel'], name=j))

            # Línea de promedio del equipo
            fig.add_trace(go.Scatter(x=promedio_grupal['Dia'], y=promedio_grupal['Nivel'], 
                                     name="PROMEDIO EQUIPO", line=dict(color='white', width=4, dash='dot')))

            fig.update_layout(template="plotly_dark", yaxis_range=[0, 11], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        # RESUMEN DE HOY
        st.divider()
        st.subheader("📋 Estado de Carga Hoy")
        hoy = datetime.now().date()
        df_hoy = df[df['Fecha'].dt.date == hoy]
        
        c_list, c_pend = st.columns(2)
        with c_list:
            st.markdown('<div class="status-card">✅ <b>COMPLETADOS:</b></div>', unsafe_allow_html=True)
            if not df_hoy.empty:
                st.dataframe(df_hoy[['Nombre', 'Nivel']].sort_values('Nivel', ascending=False), use_container_width=True, hide_index=True)
            else: st.write("Aún no hay registros hoy.")
        with c_pend:
            st.markdown('<div class="status-card">❌ <b>PENDIENTES:</b></div>', unsafe_allow_html=True)
            listos = df_hoy['Nombre'].tolist()
            pendientes = [n for n in nombres_fijos if n not in listos]
            st.write(", ".join(pendientes) if pendientes else "¡Todo el equipo completado! ✅")

    except Exception as e:
        st.info("Esperando que se carguen datos en la base...")

