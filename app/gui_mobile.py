import flet as ft
import os
import sqlite3
import utm
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import io
import base64

# Configurar matplotlib para modo servidor
matplotlib.use('Agg')

def main(page: ft.Page):
    page.title = "MaestroScan Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    # Ruta en Render para persistencia temporal
    db_path = "/tmp/maestro_scan_v3.db"
    
    # Inicializar DB
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo 
                 (id INTEGER PRIMARY KEY, fecha TEXT, cultivo TEXT, 
                  insecto TEXT, utm_e REAL, utm_n REAL)""")
    conn.close()

    # --- FUNCIÓN: GENERAR MAPA DE CALOR ---
    def generar_mapa_calor(e):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT utm_e, utm_n FROM monitoreo")
            puntos = cursor.fetchall()
            conn.close()

            if not puntos:
                resultado.value = "⚠️ No hay datos para el mapa aún"
                page.update()
                return

            plt.figure(figsize=(5, 4))
            x = [p[0] for p in puntos]
            y = [p[1] for p in puntos]
            
            plt.scatter(x, y, c='red', alpha=0.6, s=100)
            plt.title("Mapa de Calor UTM")
            plt.grid(True)

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            
            img_base64 = base64.b64encode(buf.getvalue()).decode()
            contenedor_mapa.content = ft.Image(src_base64=img_base64, border_radius=10)
            contenedor_mapa.visible = True
            resultado.value = "🗺️ Mapa generado con éxito"
            page.update()
        except Exception as ex:
            resultado.value = f"Error mapa: {ex}"
            page.update()

    # --- LÓGICA DE REGISTRO ---
    def registrar_hallazgo(e):
        if not dropdown.value:
            resultado.value = "⚠️ Selecciona un cultivo"
            page.update()
            return
        
        # Simulación de coordenadas UTM cercanas para la prueba
        import random
        e_sim = 350000 + random.randint(-100, 100)
        n_sim = 6300000 + random.randint(-100, 100)
        
        insecto = "Drosophila suzukii" if dropdown.value == "Frutilla" else "Agrotis ipsilon"
        fecha = datetime.now().strftime("%H:%M")

        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO monitoreo (fecha, cultivo, insecto, utm_e, utm_n) VALUES (?,?,?,?,?)",
                     (fecha, dropdown.value, insecto, e_sim, n_sim))
        conn.commit()
        conn.close()

        resultado.value = f"✅ REGISTRADO UTM\n{insecto}\nE: {e_sim} | N: {n_sim}"
        page.update()

    # --- INTERFAZ (Sin atributos incompatibles) ---
    logo = ft.Text("MAESTRO SCAN PRO", size=28, weight="bold", color="#1B5E20")
    subtitulo = ft.Text("AGRICULTURA DE PRECISIÓN", size=12) # Eliminado letter_spacing
    
    dropdown = ft.Dropdown(
        label="Cultivo", 
        options=[ft.dropdown.Option("Frutilla"), ft.dropdown.Option("Espárrago")]
    )
    
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

    resultado = ft.Text("", text_align=ft.TextAlign.CENTER, weight="bold")
    contenedor_mapa = ft.Container(visible=False, border=ft.border.all(1, "grey"), border_radius=10)

    page.add(
        ft.Column([
            logo,
            subtitulo,
            ft.Divider(),
            dropdown,
            btn_scan,
            resultado,
            ft.Divider(),
            btn_mapa,
            contenedor_mapa
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )