import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    # Configuración de página para máxima compatibilidad
    page.title = "MaestroScan Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    # Base de datos en memoria temporal del servidor Render
    db_path = "/tmp/maestro_scan_v2025.db"

    def init_db():
        conn = sqlite3.connect(db_path)
        conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo 
                     (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, 
                      hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)""")
        conn.close()

    init_db()

    # --- VARIABLES DE ESTADO ---
    current_lat, current_lon = -33.4489, -70.6693
    det_insect = "Identificando..."

    # --- ELEMENTOS DE INTERFAZ ---
    loading = ft.ProgressBar(width=300, visible=False, color="green")
    resultado_txt = ft.Text("", weight="bold", size=16, text_align=ft.TextAlign.CENTER)
    contenedor_mapa = ft.Container(visible=False)
    
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")

    # --- LÓGICA DE NEGOCIO ---
    def guardar_hallazgo(e):
        import utm
        try:
            # Conversión real a UTM para Maestro Solution
            u = utm.from_latlon(current_lat, current_lon)
            conn = sqlite3.connect(db_path)
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), det_insect, hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = f"✅ Registro Guardado en UTM\nSector: {localidad_in.value}"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error en procesamiento UTM: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Identificación"),
        content=ft.Column([
            ft.Text(f"Resultado IA: {det_insect}", weight="bold"),
            hospedero_in, 
            localidad_in
        ], tight=True),
        actions=[ft.ElevatedButton("Confirmar y Guardar", on_click=guardar_hallazgo, bgcolor="green", color="white")]
    )

    # --- CORRECCIÓN CRÍTICA DE FILEPICKER ---
    # En versiones nuevas, 'on_result' se asigna después o se maneja de forma distinta.
    picker = ft.FilePicker()
    page.overlay.append(picker)

    def procesar_seleccion(e):
        nonlocal det_insect
        if e.files:
            loading.visible = True
            page.update()
            
            # Simulamos búsqueda en red e identificación
            det_insect = "Drosophila suzukii detectada"
            
            loading.visible = False
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Asignamos el evento de forma compatible
    picker.on_result = procesar_seleccion

    def generar_mapa(e):
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg') # Necesario para Render (Headless)
        
        conn = sqlite3.connect(db_path)
        pts = conn.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
        conn.close()
        
        if pts:
            plt.figure(figsize=(4, 4))
            plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red', s=120, edgecolors='white')
            plt.title("MAPA DE CALOR - MONITOREO UTM")
            plt.grid(True, alpha=0.3)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            contenedor_mapa.content = ft.Image(src_base64=img_b64, border_radius=15)
            contenedor_mapa.visible = True
            page.update()
        else:
            resultado_txt.value = "⚠️ No hay datos UTM registrados aún."
            page.update()

    # --- DISEÑO DE LA APP ---
    page.add(
        ft.Container(height=20),
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION", size=12, italic=True, color="grey"),
        ft.Divider(height=40),
        
        # Botón Principal Estilo Industrial
        ft.GestureDetector(
            on_tap=lambda _: picker.pick_files(allow_multiple=False),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CAMERA_ALT, size=70, color="white"),
                    ft.Text("ESCANEAR INSECTO", color="white", weight="bold", size=22)
                ], alignment="center"),
                bgcolor="#2E7D32",
                padding=50,
                border_radius=40,
                shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.GREY_400)
            )
        ),
        
        ft.Container(height=20),
        loading,
        resultado_txt,
        ft.Divider(height=40),
        
        ft.ElevatedButton(
            "GENERAR MAPA DE CALOR UTM", 
            icon=ft.Icons.MAP_OUTLINED, 
            on_click=generar_mapa,
            style=ft.ButtonStyle(color="white", bgcolor="#1B5E20", padding=20)
        ),
        
        ft.Container(height=20),
        contenedor_mapa,
        ft.Text("© 2025 Maestro Solution - Agricultura de Precisión", size=10, color="grey")
    )

    page.update()