import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    # 1. Configuración de página de alta velocidad
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    db_path = "/tmp/maestro_solution_v13.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("", weight="bold", size=16, text_align=ft.TextAlign.CENTER)
    mapa_cont = ft.Container(visible=False)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")

    # --- LÓGICA DE ALMACENAMIENTO ---
    def guardar_datos(e):
        import utm 
        try:
            # Coordenadas por defecto para Maestro Solution
            u = utm.from_latlon(-33.45, -70.66) 
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Insecto Identificado", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            
            dlg.open = False
            resultado_txt.value = "✅ Registro Guardado con Éxito"
            resultado_txt.color = "green"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([
            ft.Text("Complete los datos del hallazgo:"),
            hospedero_in, 
            localidad_in
        ], tight=True),
        actions=[ft.ElevatedButton("Finalizar Registro", on_click=guardar_datos, bgcolor="green", color="white")]
    )

    # --- LÓGICA DEL ESCÁNER (CORRECCIÓN SIN ERRORES) ---
    def al_recibir_archivo(e): # Eliminamos el tipo de evento problemático
        if e.files:
            # Notificación visual inmediata
            resultado_txt.value = f"🔍 Imagen capturada: {e.files[0].name}"
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Declaración limpia del selector
    file_picker = ft.FilePicker()
    file_picker.on_result = al_recibir_archivo 
    page.overlay.append(file_picker)

    # --- MOTOR GRÁFICO (MAPA) ---
    def generar_mapa(e):
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        try:
            conn = sqlite3.connect(db_path)
            pts = conn.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
            conn.close()
            if pts:
                plt.figure(figsize=(4, 3))
                plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red', s=100)
                plt.title("Zonas de Hallazgo")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_b64, border_radius=10)
                mapa_cont.visible = True
            else:
                resultado_txt.value = "⚠️ No hay datos para mostrar."
            page.update()
        except:
            resultado_txt.value = "Error al generar mapa."
            page.update()

    # --- DISEÑO FINAL REFORZADO ---
    page.add(
        ft.Container(height=10),
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION - AGRO INTELIGENCIA", size=10, color="grey"),
        ft.Divider(height=40),
        
        # El botón principal
        ft.ElevatedButton(
            "ESCANEAR INSECTO",
            icon=ft.Icons.CAMERA_ALT,
            on_click=lambda _: file_picker.pick_files(
                allow_multiple=False,
                file_type="image" # Parámetro simplificado
            ),
            style=ft.ButtonStyle(
                bgcolor="#2E7D32", 
                color="white",
                padding=30,
                shape=ft.RoundedRectangleBorder(radius=15)
            )
        ),
        
        ft.Container(height=20),
        resultado_txt,
        ft.Divider(height=40),
        
        ft.OutlinedButton(
            "VER MAPA DE CALOR UTM", 
            icon=ft.Icons.MAP, 
            on_click=generar_mapa,
            style=ft.ButtonStyle(color="#2E7D32")
        ),
        
        ft.Container(height=10),
        mapa_cont
    )

    page.update()