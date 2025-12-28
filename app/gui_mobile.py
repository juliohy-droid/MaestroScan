import flet as ft
import os
import sqlite3
import utm  # Librería profesional para coordenadas
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import io
import base64

# Configurar matplotlib para que no necesite ventana (modo servidor)
matplotlib.use('Agg')

def main(page: ft.Page):
    page.title = "MaestroScan Pro - Inteligencia de Campo"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    db_path = "/tmp/maestro_scan_v3.db"
    
    # Inicializar DB con campos numéricos para el mapa
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo 
                 (id INTEGER PRIMARY KEY, fecha TEXT, cultivo TEXT, 
                  insecto TEXT, utm_e REAL, utm_n REAL)""")
    conn.close()

    # --- FUNCIÓN: GENERAR GRÁFICO DE CALOR ---
    def generar_mapa_calor(e):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT utm_e, utm_n, insecto FROM monitoreo")
        puntos = cursor.fetchall()
        conn.close()

        if not puntos:
            page.snack_bar = ft.SnackBar(ft.Text("No hay datos para el mapa"))
            page.snack_bar.open = True
            page.update()
            return

        # Crear el gráfico
        plt.figure(figsize=(5, 4))
        x = [p[0] for p in puntos]
        y = [p[1] for p in puntos]
        
        plt.scatter(x, y, c='red', alpha=0.6, s=100, edgecolors='none')
        plt.title("Mapa de Calor de Plagas (UTM)")
        plt.xlabel("Este (m)")
        plt.ylabel("Norte (m)")
        plt.grid(True, linestyle='--', alpha=0.7)

        # Guardar gráfico en memoria para mostrarlo en Flet
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        
        # Convertir a imagen de Flet
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        contenedor_mapa.content = ft.Image(src_base64=img_base64, border_radius=10)
        contenedor_mapa.visible = True
        page.update()

    # --- LÓGICA DE REGISTRO ---
    def registrar_hallazgo(e):
        if not dropdown.value: return
        
        # Coordenadas de prueba (En el futuro usaremos el GPS real del paso anterior)
        # Simulamos un punto cercano para ver el mapa
        import random
        e_sim = 350000 + random.randint(-50, 50)
        n_sim = 6300000 + random.randint(-50, 50)
        
        insecto = "Drosophila suzukii" if dropdown.value == "Frutilla" else "Agrotis ipsilon"
        fecha = datetime.now().strftime("%H:%M")

        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO monitoreo (fecha, cultivo, insecto, utm_e, utm_n) VALUES (?,?,?,?,?)",
                     (fecha, dropdown.value, insecto, e_sim, n_sim))
        conn.commit(); conn.close()

        resultado.value = f"✅ REGISTRADO UTM\nE: {e_sim} | N: {n_sim}"
        page.update()

    # --- INTERFAZ ---
    logo = ft.Text("MAESTRO SCAN PRO", size=28, weight="bold", color="#1B5E20")
    dropdown = ft.Dropdown(label="Cultivo", options=[ft.dropdown.Option("Frutilla"), ft.dropdown.Option("Espárrago")])
    
    btn_scan = ft.ElevatedButton(
        "ESCANEAR E IDENTIFICAR", 
        icon=ft.Icons.CAMERA_ALT, 
        on_click=registrar_hallazgo,
        style=ft.ButtonStyle(bgcolor="#2E7D32", color="white")
    )
    
    btn_mapa = ft.OutlinedButton(
        "VER MAPA DE CALOR", 
        icon=ft.Icons.MAP, 
        on_click=generar_mapa_calor
    )

    resultado = ft.Text("", text_align="center", weight="bold")
    contenedor_mapa = ft.Container(visible=False, border=ft.border.all(1, "grey"), border_radius=10)

    page.add(
        ft.Column([
            logo,
            ft.Text("AGRICULTURA DE PRECISIÓN", size=10, letter_spacing=2),
            ft.Divider(),
            dropdown,
            btn_scan,
            resultado,
            ft.Divider(),
            btn_mapa,
            contenedor_mapa
        ], horizontal_alignment="center")
    )