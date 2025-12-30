import streamlit as st
import sqlite3
import utm
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="MaestroScan Pro", page_icon="🌿")

st.title("MaestroScan Pro")
st.caption("MAESTRO SOLUTION - Inteligencia Agrícola")

# Inicialización de Base de Datos
DB_PATH = "maestro_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, insecto TEXT, 
                  hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)""")
    conn.close()

init_db()

# --- SECCIÓN DE ESCANEO ---
st.header("📸 Escaneo de Terreno")

# El componente de cámara "Mágico" de Streamlit
foto = st.camera_input("Toma una foto del insecto")

if foto:
    st.success("✅ Imagen capturada correctamente")
    
    with st.form("ficha_tecnica"):
        st.subheader("Ficha Técnica del Hallazgo")
        insecto = st.text_input("Insecto Detectado", value="Drosophila suzukii")
        hospedero = st.text_input("Hospedero / Cultivo", placeholder="Ej: Frutilla")
        localidad = st.text_input("Localidad", placeholder="Ej: Curicó")
        
        btn_guardar = st.form_submit_button("Guardar Registro UTM")
        
        if btn_guardar:
            # Simulación de UTM (Santiago, Chile)
            # En Streamlit es más fácil integrar GPS real después
            u = utm.from_latlon(-33.45, -70.66)
            
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%Y-%m-%d %H:%M"), insecto, hospedero, localidad, u[0], u[1]))
            conn.commit()
            conn.close()
            st.balloons()
            st.info(f"Registro guardado en {localidad}")

# --- SECCIÓN DE MAPA ---
st.divider()
st.header("📍 Mapa de Monitoreo")

if st.button("Generar Mapa de Calor UTM"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT utm_e, utm_n, insecto FROM monitoreo", conn)
    conn.close()
    
    if not df.empty:
        fig, ax = plt.subplots()
        ax.scatter(df['utm_e'], df['utm_n'], color='red', s=100, alpha=0.6)
        ax.set_title("Distribución Geográfica de Plagas")
        ax.set_xlabel("UTM Este")
        ax.set_ylabel("UTM Norte")
        ax.grid(True, linestyle='--', alpha=0.7)
        st.pyplot(fig)
    else:
        st.warning("No hay datos suficientes para generar el mapa.")

st.sidebar.info("© 2025 Maestro Solution")