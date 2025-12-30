import streamlit as st
import sqlite3
import utm
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests

# 1. CONFIGURACIÓN VISUAL (Colores Vivos y Modernos)
st.set_page_config(page_title="MaestroScan Pro", page_icon="🌿")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .main-header { 
        background-color: #74B46E; 
        padding: 10px; 
        border-radius: 10px; 
        color: white; 
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #5BA054;
        color: white;
        border-radius: 10px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        font-size: 18px;
    }
    .title-text { color: #1B5E20; font-size: 35px; font-weight: bold; margin-bottom: 0px; }
    .slogan-text { color: #888888; font-size: 14px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# Encabezado Superior (Barra Verde de éxito)
st.markdown('<div class="main-header">✅ Interfaz cargada sin errores</div>', unsafe_allow_html=True)

# Títulos Principales
st.markdown('<p class="title-text">MaestroScan Pro</p>', unsafe_allow_html=True)
st.markdown('<p style="color:#A0A0A0; margin-top:-20px;">MAESTRO SOLUTION</p>', unsafe_allow_html=True)
st.markdown('<p class="slogan-text">Inteligencia Agrícola Al servicio del Agro</p>', unsafe_allow_html=True)

# Barra de progreso decorativa
st.progress(0.6)

DB_PATH = "maestro_ai_v5.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, n_comun TEXT, 
                  n_cientifico TEXT, hospedero TEXT, categoria TEXT, utm_e REAL, utm_n REAL)""")
    conn.close()

init_db()

# --- FUNCIÓN DE IDENTIFICACIÓN (BASES DE DATOS LIBRES) ---
def buscar_datos_insecto(nombre_busqueda):
    # Simulación de consulta a GBIF/Wikipedia
    # En producción, aquí se enviaría la imagen a un modelo como TensorFlow Lite
    datos_libres = {
        "Drosophila": {"cientifico": "Drosophila suzukii", "categoria": "Plaga Primaria", "control": "Trampeo masivo y control químico."},
        "Polilla": {"cientifico": "Lobesia botrana", "categoria": "Plaga Cuarentenaria", "control": "Confusión sexual."},
        "Burrito": {"cientifico": "Naupactus xanthographus", "categoria": "Plaga Secundaria", "control": "Barreras físicas y químicos."}
    }
    return datos_libres.get(nombre_busqueda, {"cientifico": "Especie en estudio", "categoria": "Desconocida", "control": "Consultar Asesor"})

# --- SECCIÓN DE ESCANEO ---
foto = st.camera_input("ESCANEAR INSECTO")

if foto:
    st.markdown("### 🔍 Analizando imagen capturada...")
    
    # Simulamos la aceptación de la fotografía
    col_acc, col_can = st.columns(2)
    with col_acc:
        confirmar = st.button("✅ ACEPTAR")
    with col_can:
        cancelar = st.button("❌ CANCELAR")

    if confirmar:
        # Aquí la IA identifica (Simulamos que identificó un Burrito)
        info = buscar_datos_insecto("Burrito")
        
        st.success(f"Identificación Exitosa: **{info['cientifico']}**")
        
        with st.form("ficha_ai"):
            st.subheader("📋 Ficha Técnica Generada")
            n_comun = st.text_input("Nombre Común", value="Burrito de la vid")
            n_cientifico = st.text_input("Nombre Científico", value=info['cientifico'])
            hospedero = st.text_input("Hospedero / Daños", value="Frutales y Vides. Daño en raíces y follaje.")
            categoria = st.selectbox("Clasificación", ["Plaga Primaria", "Plaga Secundaria", "Benéfico"], index=1)
            
            st.warning(f"**Recomendación:** {info['control']}")
            
            if st.form_submit_button("💾 GUARDAR EN REGISTRO UTM"):
                u = utm.from_latlon(-33.45, -70.66)
                conn = sqlite3.connect(DB_PATH)
                conn.execute("INSERT INTO monitoreo (fecha, n_comun, n_cientifico, hospedero, categoria, utm_e, utm_n) VALUES (?,?,?,?,?,?,?)",
                            (datetime.now().strftime("%d/%m %H:%M"), n_comun, n_cientifico, hospedero, categoria, u[0], u[1]))
                conn.commit()
                conn.close()
                st.balloons()

# --- SECCIÓN DE MAPA Y EXCEL ---
st.markdown("---")
if st.button("🗺️ VER MAPA DE CALOR UTM"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM monitoreo", conn)
    conn.close()

    if not df.empty:
        fig, ax = plt.subplots()
        ax.scatter(df['utm_e'], df['utm_n'], color='red', s=100)
        ax.set_title("Puntos Críticos Maestro Solution")
        st.pyplot(fig)
        
        # Botón Excel
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 DESCARGAR REPORTE EXCEL", csv, "monitoreo.csv", "text/csv")
    else:
        st.info("No hay datos para graficar.")

st.markdown('<p style="text-align:center; color:grey; font-size:10px;">© 2025 Maestro Solution</p>', unsafe_allow_html=True)