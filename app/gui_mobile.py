import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    # Configuración de página ultra-compatible
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Base de datos en memoria temporal
    db_path = "/tmp/maestro_solution_v3.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("", weight="bold", size=16, text_align=ft.TextAlign.CENTER)
    mapa_cont = ft.Container(visible=False)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")

    # --- LÓGICA DE ALMACENAMIENTO ---
    def guardar_datos(e):
        import utm 
        try:
            # Coordenadas por defecto para Santiago/Chile
            u = utm.from_latlon(-33.45, -70.66) 
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Insecto Identificado", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = "✅ Hallazgo Guardado Exitosamente"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([
            ft.Text("Complete la información del hallazgo:"),
            hospedero_in, 
            localidad_in
        ], tight=True, spacing=10),
        actions=[ft.ElevatedButton("Confirmar y Guardar", on_click=guardar_datos, bgcolor="green", color="white")]
    )

    # --- MANEJO DE ARCHIVOS (MODO COMPATIBLE) ---
    def al_seleccionar_archivo(e: ft.FilePickerResultEvent):
        if e.files:
            resultado_txt.value = f"🔍 Imagen: {e.files[0].name} capturada."
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Declaración del componente fuera del flujo visual
    picker = ft.FilePicker(on_result=al_seleccionar_archivo)
    page.overlay.append(picker)

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
                plt.title("MAPA DE MONITOREO")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_b64, border_radius=10)
                mapa_cont.visible = True
                page.update()
            else:
                resultado_txt.value = "⚠️ No hay datos para el mapa."
                page.update()
        except:
            resultado_txt.value = "Error al generar mapa."
            page.update()

    # --- DISEÑO FINAL REFORZADO ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION", size=12, color="grey"),
        ft.Divider(height=30),
        
        # El Botón ahora llama directamente al Picker de forma limpia
        ft.ElevatedButton(
            "ESCANEAR INSECTO",
            icon=ft.Icons.CAMERA_ALT,
            on_click=lambda _: picker.pick_files(allow_multiple=False),
            style=ft.ButtonStyle(
                bgcolor="#2E7D32", 
                color="white",
                padding=30,
                shape=ft.RoundedRectangleBorder(radius=15)
            )
        ),
        
        ft.Container(height=10),
        resultado_txt,
        ft.Divider(height=40),
        
        ft.OutlinedButton(
            "GENERAR MAPA DE CALOR UTM", 
            icon=ft.Icons.MAP, 
            on_click=generar_mapa,
            style=ft.ButtonStyle(color="#2E7D32")
        ),
        
        ft.Container(height=10),
        mapa_cont
    )