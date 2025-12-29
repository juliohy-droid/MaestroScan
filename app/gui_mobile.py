import flet as ft
import os
import sys
import sqlite3
import utm
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import io
import base64

# Configurar matplotlib para modo servidor
matplotlib.use('Agg')

base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_path)

def main(page: ft.Page):
    page.title = "MaestroScan Pro - Maestro Solution"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    db_path = "/tmp/maestro_scan_v5.db"
    
    # Inicializar DB
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    fecha TEXT, insecto TEXT, hospedero TEXT, 
                    localidad TEXT, utm_e REAL, utm_n REAL)""")
    conn.close()

    # --- VARIABLES Y GPS SEGURO ---
    current_lat, current_lon = -33.4489, -70.6693
    detected_insect = ""

    def on_location_event(e):
        nonlocal current_lat, current_lon
        try:
            current_lat = e.latitude
            current_lon = e.longitude
            u = utm.from_latlon(current_lat, current_lon)
            gps_info.value = f"📍 UTM: {int(u[0])}E {int(u[1])}N"
            page.update()
        except: pass

    # CARGA SEGURA DE GPS (Evita el AttributeError)
    try:
        if hasattr(ft, "Geolocator"):
            lp = ft.Geolocator()
            lp.on_change = on_location_event
            page.overlay.append(lp)
        else:
            print("Geolocator no disponible en esta versión de Flet")
    except Exception as ex:
        print(f"Error inicializando GPS: {ex}")

    # --- FORMULARIO ---
    hospedero_input = ft.TextField(label="Hospedero / Cultivo")
    localidad_input = ft.TextField(label="Localidad")

    def guardar_reporte(e):
        nonlocal detected_insect
        try:
            u = utm.from_latlon(current_lat, current_lon)
            conn = sqlite3.connect(db_path)
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                      (datetime.now().strftime("%Y-%m-%d %H:%M"), detected_insect, hospedero_input.value, localidad_input.value, u[0], u[1]))
            conn.commit()
            conn.close()
            modal_formulario.open = False
            resultado_txt.value = f"✅ Guardado: {detected_insect}"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error al guardar: {ex}"
            page.update()

    modal_formulario = ft.AlertDialog(
        title=ft.Text("Ficha Técnica"),
        content=ft.Column([
            ft.Text(id_text := ft.Text("", weight="bold", color="#2E7D32")),
            hospedero_input,
            localidad_input,
        ], tight=True),
        actions=[ft.ElevatedButton("Guardar", on_click=guardar_reporte)],
    )

    # --- ESCANEO ---
    def on_file_result(e):
        nonlocal detected_insect
        if e.files:
            loading.visible = True
            page.update()
            # IA Simulada para Maestro Solution
            detected_insect = "Drosophila suzukii" 
            id_text.value = detected_insect
            loading.visible = False
            page.dialog = modal_formulario
            modal_formulario.open = True
            page.update()

    picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(picker)

    # --- UI ---
    gps_info = ft.Text("📍 GPS: Esperando señal...", size=12)
    loading = ft.ProgressBar(width=300, visible=False, color="#2E7D32")
    resultado_txt = ft.Text("", weight="bold")

    btn_escanear = ft.Container(
        content=ft.Column([ft.Icon(ft.Icons.CAMERA_ALT, size=40, color="white"), ft.Text("ESCANEAR", color="white")], alignment="center"),
        bgcolor="#2E7D32", padding=30, border_radius=20,
        on_click=lambda _: picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
    )

    contenedor_mapa = ft.Container(visible=False)

    def ver_mapa(e):
        conn = sqlite3.connect(db_path)
        puntos = conn.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
        conn.close()
        if puntos:
            plt.figure(figsize=(5,4))
            plt.scatter([p[0] for p in puntos], [p[1] for p in puntos], c='red')
            plt.grid(True)
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            contenedor_mapa.content = ft.Image(src_base64=img_b64)
            contenedor_mapa.visible = True
            page.update()

    page.add(
        ft.Text("MaestroScan Pro", size=28, weight="bold", color="#1B5E20"),
        gps_info,
        ft.Divider(),
        btn_escanear,
        loading,
        resultado_txt,
        ft.Divider(),
        ft.OutlinedButton("VER MAPA UTM", icon=ft.Icons.MAP, on_click=ver_mapa),
        contenedor_mapa
    )