else:
    # Logo y Título
    logo_url = "https://upload.wikimedia.org/wikipedia/en/thumb/3/30/Panama_national_football_team_crest.svg/1200px-Panama_national_football_team_crest.svg.png"
    st.image(logo_url, width=100)
    st.markdown("<h1>⚽ SISTEMA RPE FEPAFUT</h1>", unsafe_allow_html=True)
import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse
from datetime import datetime, timedelta
import time

# 1. CONFIGURACIÓN DE PÁGINA Y TEMA OSCURO
st.set_page_config(page_title="FEPAFUT - RPE PRO", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #1e2129; color: #ffffff; }
    div.stButton > button {
        background-color: #2b2e3a; color: #ffffff;
        border: 1px solid #cc0000; border-radius: 8px;
        padding: 10px; font-weight: bold; transition: all 0.3s;
    }
    div.stButton > button:hover { background-color: #cc0000; color: white; transform: scale(1.02); }
    h1 { color: #ffffff; text-align: center; font-weight: 800; border-bottom: 2px solid #cc0000; padding-bottom: 10px; }
    .status-box { background-color: #2b2e3a; padding: 15px; border-radius: 10px; border-left: 5px solid #cc0000; }
    </style>
    """, unsafe_allow_html=True)

# 2. ENLACES Y DATOS
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

if 'url_formulario' not in st.session_state:
    st.session_state.url_formulario = None

# --- NAVEGACIÓN ---
if st.session_state.url_formulario:
    if st.button("⬅️ VOLVER AL PANEL PRINCIPAL"):
        st.session_state.url_formulario = None
        st.rerun()
    st.markdown(f'<iframe src="{st.session_state.url_formulario}" width="100%" height="800px" frameborder="0"></iframe>', unsafe_allow_html=True)

else:
    st.markdown("<h1>⚽ SISTEMA RPE FEPAFUT</h1>", unsafe_allow_html=True)
    
    # 3. BOTONES DE JUGADORES
    st.subheader("👥 Registro RPE Individual")
    cols = st.columns(6)
    for i, nombre in enumerate(nombres_fijos):
        with cols[i % 6]:
            if st.button(nombre, use_container_width=True):
                st.session_state.url_formulario = f"{URL_BASE_FORM}{urllib.parse.quote_plus(nombre)}"
                st.rerun()

    st.divider()

    # 4. GRÁFICO Y RESUMEN
    try:
        # Carga fresca
        df = pd.read_csv(f"{URL_CSV}&t={int(time.time())}")
        df.columns = ['Fecha', 'Nombre', 'Respuesta_RPE'] + list(df.columns[3:])
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Fecha', 'Nombre'])
        df['Nivel'] = df['Respuesta_RPE'].astype(str).str.extract('(\d+)').astype(float)
        df['Fecha_Texto'] = df['Fecha'].dt.strftime('%d/%m %a')

        # --- SECCIÓN DE GRÁFICO ---
        st.subheader("📊 Tendencia de Esfuerzo Semanal")
        rango = st.date_input("Periodo", value=(datetime.now().date() - timedelta(days=7), datetime.now().date()))
        
        df_f = df[(df['Fecha'].dt.date >= rango[0]) & (df['Fecha'].dt.date <= rango[1])]

        if not df_f.empty:
            fig = px.bar(df_f, x='Fecha_Texto', y='Nivel', color='Nivel',
                         template="plotly_dark",
                         color_continuous_scale=[[0, '#2ecc71'], [0.5, '#f6d365'], [1, '#ff4b4b']],
                         range_color=[1, 10], barmode='group', hover_name='Nombre')
            fig.update_layout(yaxis_range=[0, 10.5], paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # --- NUEVA TABLA DE RESUMEN DE HOY ---
        st.subheader("📋 Estado de Registros de Hoy")
        hoy = datetime.now().date()
        df_hoy = df[df['Fecha'].dt.date == hoy]
        lista_completo = df_hoy['Nombre'].tolist()
        
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="status-box">✅ <b>COMPLETADOS HOY:</b></div>', unsafe_allow_html=True)
            if not df_hoy.empty:
                # Mostramos nombre y su nivel de RPE
                resumen_hoy = df_hoy[['Nombre', 'Nivel']].sort_values(by='Nivel', ascending=False)
                st.dataframe(resumen_hoy, use_container_width=True, hide_index=True)
            else:
                st.write("Nadie ha registrado todavía.")

        with c2:
            st.markdown('<div class="status-box">❌ <b>PENDIENTES:</b></div>', unsafe_allow_html=True)
            pendientes = [n for n in nombres_fijos if n not in lista_completo]
            if pendientes:
                st.write(", ".join(pendientes))
            else:
                st.success("¡Todo el equipo ha completado el registro!")

    except Exception as e:

        st.info("Sincronizando con la base de datos...")
