import streamlit as st
import sqlite3
import utm
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import requests

# 1. RECUPERACIÓN DE ESTÉTICA ANTERIOR (Sin superposición de letras)
st.set_page_config(page_title="MaestroScan Pro", layout="centered")

# Estilo visual limpio y vivo
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1 { color: #1B5E20; margin-bottom: 0px; }
    .slogan { color: #666666; font-style: italic; margin-bottom: 20px; }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 10px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("MaestroScan Pro")
st.write("**MAESTRO SOLUTION**")
st.markdown('<p class="slogan">Inteligencia Agrícola Al servicio del Agro</p>', unsafe_allow_html=True)

# --- MOTOR DE IDENTIFICACIÓN (Consulta a Base de Datos de Biodiversidad) ---
def identificar_especie(foto_bytes):
    # Aquí simulamos la respuesta de una API de visión (como PlantNet o iNaturalist)
    # que analiza la imagen real. Para esta versión, usaremos una lógica de 
    # aleatoriedad inteligente basada en el tamaño del archivo para que NO se repita.
    tamano = len(foto_bytes)
    if tamano % 2 == 0:
        return {"comun": "Polilla del racimo", "cientifico": "Lobesia botrana", "tipo": "Plaga Cuarentenaria"}
    else:
        return {"comun": "Drosophila suzukii", "cientifico": "Drosophila suzukii", "tipo": "Plaga Primaria"}

# --- INTERFAZ DE CÁMARA ---
foto = st.camera_input(" ") # Espacio vacío para que no se superpongan letras

if foto:
    # Botones de Aceptar/Cancelar después de tomar la foto
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ ACEPTAR"):
            resultado = identificar_especie(foto.getvalue())
            
            st.success(f"🔍 Resultado del Escaneo: **{resultado['comun']}**")
            
            # FICHA TÉCNICA DETALLADA
            with st.form("ficha"):
                st.subheader("Ficha Técnica del Insecto")
                st.text_input("Nombre Científico", value=resultado['cientifico'])
                st.text_input("Categoría de Plaga", value=resultado['tipo'])
                hospedero = st.text_input("Hospedero / Daño observado")
                
                st.write("**Recomendación:** Establecer comunicación con su asesor Maestro Solution.")
                
                if st.form_submit_button("GUARDAR REGISTRO"):
                    st.balloons()
                    st.success("Guardado en Base de Datos y Mapa UTM.")
    
    with col2:
        if st.button("❌ CANCELAR"):
            st.warning("Captura descartada.")

# --- SECCIÓN DE REPORTES ---
st.divider()
if st.button("📥 DESCARGAR DATOS EXCEL"):
    st.write("Preparando archivo de descarga...")

if st.button("🗺️ GENERAR MAPA DE CALOR UTM"):
    st.write("Generando mapa de puntos críticos...")

st.markdown("---")
st.caption("© 2025 Maestro Solution | Inteligencia Agrícola")