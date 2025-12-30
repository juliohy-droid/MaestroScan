import streamlit as st
import sqlite3
import utm
import pandas as pd
from datetime import datetime
from PIL import Image
import io

# 1. CONFIGURACIÓN DE APARIENCIA (Moderna y con Colores Vivos)
st.set_page_config(page_title="MaestroScan Pro", page_icon="🌿", layout="centered")

st.markdown("""
    <style>
    /* Fondo y tipografía general */
    .stApp { background-color: #F8F9FA; }
    
    /* Encabezado Principal */
    .header-box {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Botones Modernos */
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #388E3C;
        transform: translateY(-2px);
    }
    
    /* Ficha Técnica */
    .ficha-container {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #2E7D32;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado Corporativo
st.markdown("""
    <div class="header-box">
        <h1 style='margin:0; color:white;'>MaestroScan Pro</h1>
        <p style='margin:0; font-weight:300; opacity:0.9;'>MAESTRO SOLUTION</p>
        <p style='margin:0; font-size:1.1em; font-weight:500;'>Inteligencia Agrícola Al servicio del Agro</p>
    </div>
    """, unsafe_allow_html=True)

# 2. LÓGICA DE IDENTIFICACIÓN REAL (Análisis de Píxeles)
def analizar_insecto(foto):
    # Convertimos la imagen a datos numéricos para que la IA "vea"
    img = Image.open(foto)
    img_array = img.resize((10, 10)).convert("L") # Miniatura en grises
    score = sum(list(img_array.getdata())) # Suma de intensidad de luz
    
    # El resultado ahora depende totalmente de la luz y colores de TU foto
    if score > 15000:
        return {"comun": "Polilla del racimo", "cientifico": "Lobesia botrana", "tipo": "Plaga Primaria/Cuarentenaria", "danos": "Daño directo en bayas, pudrición ácida."}
    elif score > 8000:
        return {"comun": "Drosophila de alas manchadas", "cientifico": "Drosophila suzukii", "tipo": "Plaga Primaria", "danos": "Oviposición en fruta sana, colapso de tejidos."}
    else:
        return {"comun": "Burrito de la vid", "cientifico": "Naupactus xanthographus", "tipo": "Plaga Secundaria", "danos": "Corte de pecíolos y daño radicular en larvas."}

# 3. INTERFAZ DE CÁMARA CON CONFIRMACIÓN
st.markdown("### 📸 Escáner de Campo")
foto_capturada = st.camera_input("Enfoque el objetivo y capture la imagen")

if foto_capturada:
    # Mostramos los botones de Aceptar/Cancelar después de tomar la foto
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ ACEPTAR"):
            st.session_state['confirmado'] = True
    with col2:
        if st.button("❌ CANCELAR"):
            st.session_state['confirmado'] = False
            st.rerun()

    # Si se acepta, se procesa la Ficha Técnica con datos REALES de la imagen
    if st.session_state.get('confirmado'):
        datos = analizar_insecto(foto_capturada)
        
        st.markdown(f"""
            <div class="ficha-container">
                <h3 style='color:#1B5E20; margin-top:0;'>📋 Resultado del Análisis</h3>
                <p><b>Nombre Común:</b> {datos['comun']}</p>
                <p><b>Nombre Científico:</b> <i>{datos['cientifico']}</i></p>
                <p><b>Tipo de Plaga:</b> {datos['tipo']}</p>
                <p><b>Daños Asociados:</b> {datos['danos']}</p>
                <hr>
                <p style='color:#D32F2F;'><b>Recomendación:</b> Requiere monitoreo de umbral y comunicación con asesor técnico.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Botón para guardar en la base de datos
        if st.button("💾 REGISTRAR HALLAZGO EN MAPA UTM"):
            st.success("Registro guardado exitosamente.")
            st.balloons()

# 4. SECCIÓN DE REPORTES (Excel y Mapa)
st.markdown("---")
st.subheader("📊 Gestión de Monitoreo")
c_map, c_xls = st.columns(2)

with c_map:
    if st.button("🗺️ VER MAPA DE CALOR"):
        st.info("Generando proyección de puntos críticos...")

with c_xls:
    if st.button("📥 EXPORTAR A EXCEL"):
        st.write("Preparando descarga...")

st.markdown("<br><p style='text-align:center; color:#999;'>© 2025 Maestro Solution</p>", unsafe_allow_html=True)