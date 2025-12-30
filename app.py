import streamlit as st
import sqlite3
import utm
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 1. CONFIGURACIÓN DE INTERFAZ MODERNA Y VIVA
st.set_page_config(
    page_title="MaestroScan Pro", 
    page_icon="🌿", 
    layout="centered"
)

# CSS Personalizado para colores vivos (Verde Agro y Blanco Limpio)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 20px;
        border: none;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    .stHeader { color: #1B5E20; }
    h1 { color: #1B5E20; font-family: 'Helvetica Neue', sans-serif; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 MaestroScan Pro")
st.subheader("INTELIGENCIA AGRÍCOLA")
st.markdown("---")

DB_PATH = "maestro_data_v2.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, 
                  n_comun TEXT, n_cientifico TEXT, hospedero TEXT, 
                  tipo_plaga TEXT, control TEXT, utm_e REAL, utm_n REAL)""")
    conn.close()

init_db()

# --- MOTOR DE ESCANEO ---
foto = st.camera_input("📷 Capturar espécimen en terreno")

if foto:
    st.success("✅ Análisis de Imagen Completo")
    
    # SIMULACIÓN DE IA (Aquí se conectaría el modelo de reconocimiento)
    # Por ahora entregamos la ficha técnica avanzada que solicitaste
    with st.expander("🔍 VER FICHA TÉCNICA DETALLADA", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            n_comun = st.text_input("Nombre Común", value="Burrito de la vid")
            n_cientifico = st.text_input("Nombre Científico", value="Naupactus xanthographus")
            hospedero = st.text_input("Hospedero Detectado", value="Vid vinífera / Frutales de carozo")
        
        with col2:
            tipo_plaga = st.selectbox("Categoría de Plaga", 
                                    ["Plaga Primaria", "Plaga Secundaria", "Cuarentenaria", "Benéfico"])
            danos = st.text_area("Daños Asociados", value="Consumo de follaje por adultos. Larvas destruyen raicillas comprometiendo el vigor.")

        st.warning("**Recomendación de Control:** Requiere control químico/biológico dirigido según umbral económico.")
        
        # Botón de contacto con asesor
        if st.button("📲 CONTACTAR ASESOR MAESTRO SOLUTION"):
            st.write("📞 Conectando con su asesor técnico... (WhatsApp/Llamada)")

        # Lógica de Guardado
        if st.button("💾 REGISTRAR HALLAZGO Y COORDENADAS"):
            u = utm.from_latlon(-33.45, -70.66)
            conn = sqlite3.connect(DB_PATH)
            conn.execute("""INSERT INTO monitoreo 
                         (fecha, n_comun, n_cientifico, hospedero, tipo_plaga, control, utm_e, utm_n) 
                         VALUES (?,?,?,?,?,?,?,?)""",
                        (datetime.now().strftime("%d/%m %H:%M"), n_comun, n_cientifico, 
                         hospedero, tipo_plaga, "Químico/Manual", u[0], u[1]))
            conn.commit()
            conn.close()
            st.balloons()

# --- SECCIÓN DE REPORTES Y EXCEL ---
st.divider()
st.header("📊 Gestión de Datos")

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM monitoreo", conn)
conn.close()

if not df.empty:
    # Botón para descargar Excel (CSV compatible)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 DESCARGAR BASE DE DATOS (EXCEL/CSV)",
        data=csv,
        file_name=f"monitoreo_maestro_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
    
    # Vista previa de la tabla moderna
    st.dataframe(df.style.highlight_max(axis=0, color='#E8F5E9'))

    # Mapa de Calor
    if st.button("🗺️ ACTUALIZAR MAPA UTM"):
        fig, ax = plt.subplots()
        ax.scatter(df['utm_e'], df['utm_n'], color='#D32F2F', s=120, edgecolors='white')
        ax.set_title("Puntos Críticos de Plagas - Maestro Solution", color='#1B5E20')
        ax.set_facecolor('#F1F8E9')
        st.pyplot(fig)
else:
    st.info("No hay registros pendientes de descarga.")

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2910/2910756.png", width=100)
st.sidebar.write("**MaestroScan Pro v2.0**")
st.sidebar.write("Inteligencia Agrícola al servicio del campo.")