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

# Configurar matplotlib para modo servidor (sin interfaz gráfica propia)
matplotlib.use('Agg')

# Forzar rutas para módulos locales
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_path)

def main(page: ft.Page):
    page.title = "MaestroScan Pro - Maestro Solution"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Rutas de almacenamiento en Render
    db_path = "/tmp/maestro_scan_final.db"
    
    # Inicializar Base de Datos Industrial
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    fecha TEXT, 
                    insecto TEXT, 
                    hospedero TEXT, 
                    localidad TEXT, 
                    utm_e REAL, 
                    utm_n REAL)""")
    conn.close()

    # --- VARIABLES DE ESTADO ---
    current_lat, current_lon = -33.4489, -70.6693 # Por defecto
    detected_insect = ""

    # --- LÓGICA DE GEOPOSICIÓN ---
    def on_location_event(e):
        nonlocal current_lat, current_lon
        current_lat = e.latitude
        current_lon = e.longitude
        try:
            u = utm.from_latlon(current_lat, current_lon)
            gps_info.value = f"📍 UTM: {int(u[0])}E {int(u[1])}N (Zona {u[2]}{u[3]})"
        except:
            gps_info.value = "📍 GPS Activo (Calculando UTM...)"
        page.update()

    lp = ft.Geolocator()
    lp.on_change = on_location_event
    page.overlay.append(lp)

    # --- FORMULARIO DE REPORTE (DIALOGO) ---
    hospedero_input = ft.TextField(label="Hospedero / Cultivo", hint_text="Ej: Frutilla")
    localidad_input = ft.TextField(label="Localidad", hint_text="Ej: Curicó")

    def guardar_reporte(e):
        nonlocal detected_insect
        u = utm.from_latlon(current_lat, current_lon)
        
        conn = sqlite3.connect(db_path)
        conn.execute("""INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) 
                     VALUES (?,?,?,?,?,?)""",
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), 
                   detected_insect, hospedero_input.value, localidad_input.value, 
                   u[0], u[1]))
        conn.commit()
        conn.close()
        
        modal_formulario.open = False
        resultado_txt.value = f"✅ Reporte guardado: {detected_insect}"
        resultado_txt.color = "green"
        page.update()

    modal_formulario = ft.AlertDialog(
        modal=True,
        title=ft.Text("Ficha Técnica del Hallazgo"),
        content=ft.Column([
            ft.Text("Insecto Identificado:", size=12),
            ft.Text(id_text := ft.Text("", weight="bold", size=18, color="#2E7D32")),
            hospedero_input,
            localidad_input,
        ], tight=True),
        actions=[ft.ElevatedButton("Finalizar Reporte", on_click=guardar_reporte)],
    )

    # --- MOTOR DE ESCANEO ---
    def on_file_result(e):
        nonlocal detected_insect
        if e.files:
            loading.visible = True
            resultado_txt.value = "Analizando morfología del insecto..."
            page.update()
            
            # SIMULACIÓN DE IA: En un futuro aquí se conecta con el modelo de visión
            # Por ahora, simulamos una identificación exitosa
            detected_insect = "Drosophila suzukii (Mosca de alas manchadas)"
            id_text.value = detected_insect
            
            loading.visible = False
            page.dialog = modal_formulario
            modal_formulario.open = True
            page.update()

    picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(picker)

    # --- MOTOR DE MAPA DE CALOR ---
    def ver_mapa(e):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT utm_e, utm_n FROM monitoreo")
        puntos = cursor.fetchall()
        conn.close()

        if not puntos:
            resultado_txt.value = "⚠️ No hay datos suficientes"
            page.update()
            return

        plt.figure(figsize=(6, 4))
        plt.scatter([p[0] for p in puntos], [p[1] for p in puntos], c='red', s=100, alpha=0.5)
        plt.title("Mapa de Calor UTM - Maestro Solution")
        plt.grid(True, linestyle='--', alpha=0.6)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        
        img_b64 = base64.b64encode(buf.getvalue()).decode()
        contenedor_mapa.content = ft.Image(src_base64=img_b64, border_radius=15)
        contenedor_mapa.visible = True
        page.update()

    # --- INTERFAZ DE USUARIO (UI) ---
    gps_info = ft.Text("📍 Buscando coordenadas GPS...", italic=True, size=12)
    
    loading = ft.ProgressBar(width=300, color="#2E7D32", visible=False)
    resultado_txt = ft.Text("", text_align="center", weight="bold")

    btn_escanear = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.CAMERA_ALT, size=40, color="white"),
            ft.Text("ESCANEAR INSECTO", color="white", weight="bold")
        ], alignment="center", spacing=5),
        bgcolor="#2E7D32",
        padding=30,
        border_radius=20,
        on_click=lambda _: picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)
    )

    contenedor_mapa = ft.Container(visible=False, padding=10)

    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("SISTEMA DE INTELIGENCIA AGRÍCOLA", size=10, color="grey"),
        ft.Divider(height=20),
        gps_info,
        ft.VerticalDivider(height=20),
        btn_escanear,
        loading,
        resultado_txt,
        ft.Divider(height=30),
        ft.OutlinedButton("GENERAR MAPA DE CALOR", icon=ft.Icons.MAP, on_click=ver_mapa),
        contenedor_mapa
    )

# Fin del archivo