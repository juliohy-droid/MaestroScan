import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    page.title = "MaestroScan Pro - Maestro Solution"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    db_path = "/tmp/maestro_scan_v10.db"

    # --- INICIALIZACIÓN DE DB ---
    def init_db():
        conn = sqlite3.connect(db_path)
        conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo 
                     (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, 
                      hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)""")
        conn.close()

    init_db()

    # --- VARIABLES ---
    current_lat, current_lon = -33.4489, -70.6693
    det_insect = "Identificando..."

    # --- COMPONENTES DE UI ---
    loading = ft.ProgressBar(width=300, visible=False, color="green")
    resultado_txt = ft.Text("", weight="bold", size=16)
    contenedor_mapa = ft.Container(visible=False)
    
    hospedero_in = ft.TextField(label="Hospedero / Cultivo")
    localidad_in = ft.TextField(label="Localidad")

    # --- FUNCIONES DINÁMICAS (Carga bajo demanda) ---
    def guardar_hallazgo(e):
        import utm # Importación interna para evitar fallos de inicio
        try:
            u = utm.from_latlon(current_lat, current_lon)
            conn = sqlite3.connect(db_path)
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), det_insect, hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = f"✅ Guardado: {det_insect}"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error GPS/UTM: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Guardar Reporte", on_click=guardar_hallazgo)]
    )

    def al_escanear(e):
        nonlocal det_insect
        if e.files:
            loading.visible = True
            page.update()
            # Simulación de IA para Maestro Solution
            det_insect = "Drosophila suzukii"
            loading.visible = False
            page.dialog = dlg
            dlg.open = True
            page.update()

    picker = ft.FilePicker(on_result=al_escanear)
    page.overlay.append(picker)

    def generar_mapa(e):
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        
        conn = sqlite3.connect(db_path)
        pts = conn.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
        conn.close()
        
        if pts:
            plt.figure(figsize=(4, 3))
            plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red')
            plt.title("Mapa de Calor UTM")
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            contenedor_mapa.content = ft.Image(src_base64=img_b64)
            contenedor_mapa.visible = True
            page.update()

    # --- CONSTRUCCIÓN DE LA PÁGINA ---
    page.add(
        ft.Text("MaestroScan Pro", size=30, weight="bold", color="green"),
        ft.Text("MAESTRO SOLUTION - TECNOLOGÍA AGRÍCOLA", size=10),
        ft.Divider(),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CAMERA_ALT, size=50, color="white"),
                ft.Text("ESCANEAR INSECTO", color="white", weight="bold")
            ], alignment="center"),
            bgcolor="green",
            padding=40,
            border_radius=25,
            on_click=lambda _: picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
        ),
        loading,
        resultado_txt,
        ft.Divider(),
        ft.OutlinedButton("VER MAPA DE CALOR", icon=ft.Icons.MAP, on_click=generar_mapa),
        contenedor_mapa
    )

# Fin del archivo