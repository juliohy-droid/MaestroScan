import flet as ft
import os
import sqlite3
import utm
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import io
import base64
import requests # Para simular la consulta a una API de IA

# Configurar matplotlib para modo servidor
matplotlib.use('Agg')

def main(page: ft.Page):
    page.title = "MaestroScan Pro - Identificación Inteligente"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    db_path = "/tmp/maestro_scan_v4.db" # Nueva DB para guardar más datos
    fotos_path = "/tmp/scans/" # Carpeta para guardar fotos (simulado)
    if not os.path.exists(fotos_path): os.makedirs(fotos_path)

    # Inicializar DB con más campos
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS monitoreo (
                    id INTEGER PRIMARY KEY, 
                    fecha TEXT, 
                    insecto TEXT, 
                    hospedero TEXT, 
                    localidad TEXT, 
                    utm_e REAL, utm_n REAL, 
                    foto_path TEXT)""")
    conn.close()

    # --- SIMULACIÓN DE IA ---
    def identificar_insecto_ia(imagen_bytes):
        # En un entorno real, enviaríamos imagen_bytes a una API como Google Vision AI o similar.
        # Por ahora, simulamos una respuesta basada en el tamaño o algún criterio simple.
        # Esta función retornaría el nombre científico del insecto detectado.
        
        # Simulación de respuesta IA (ej. si la imagen es grande, es un insecto específico)
        if len(imagen_bytes) > 10000: # Suponiendo que una foto más grande "detecta" algo
            return "Hypothenemus hampei (Broca del café)"
        else:
            return "Spodoptera frugiperda (Gusano cogollero)"

    # --- FUNCIÓN DE CONVERSIÓN UTM (Real) ---
    def latlon_to_utm_coords(lat, lon):
        try:
            utm_coords = utm.from_latlon(lat, lon)
            return utm_coords[0], utm_coords[1], utm_coords[2], utm_coords[3] # E, N, Zone, Letter
        except Exception:
            return None, None, None, None

    # --- GEOLOCALIZACIÓN (Real) ---
    current_lat, current_lon = None, None
    def on_location_event(e):
        nonlocal current_lat, current_lon
        current_lat = e.latitude
        current_lon = e.longitude
        easting, northing, zone_num, zone_let = latlon_to_utm_coords(current_lat, current_lon)
        if easting is not None:
            gps_info.value = f"📍 UTM: E {int(easting)} N {int(northing)} Z {zone_num}{zone_let}"
        else:
            gps_info.value = "📍 GPS no disponible"
        page.update()

    lp = ft.Geolocator()
    lp.on_change = on_location_event
    page.overlay.append(lp)
    
    # --- MANEJO DE IMAGEN ---
    detected_insect_name = ""
    scanned_image_base64 = "" # Para mostrar la miniatura
    scanned_image_path = "" # Para guardar la ruta

    def on_file_result(e: ft.FilePickerResultEvent):
        nonlocal detected_insect_name, scanned_image_base64, scanned_image_path
        if e.files:
            file_info = e.files[0]
            # Leer el archivo de imagen como bytes
            with open(file_info.path, "rb") as f:
                image_bytes = f.read()

            # Guardar la imagen en el servidor
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_ext = os.path.splitext(file_info.name)[1]
            scanned_image_path = os.path.join(fotos_path, f"scan_{timestamp}{file_ext}")
            with open(scanned_image_path, "wb") as f_out:
                f_out.write(image_bytes)
            
            # Mostrar miniatura
            scanned_image_base64 = base64.b64encode(image_bytes).decode()
            img_preview.src_base64 = scanned_image_base64
            img_preview.visible = True
            
            # Identificar con IA (simulado)
            loading_bar.visible = True
            result_text.value = "🔍 Identificando insecto..."
            page.update()
            
            detected_insect_name = identificar_insecto_ia(image_bytes)
            result_text.value = f"✅ Detectado: {detected_insect_name}"
            loading_bar.visible = False
            
            # Abrir el formulario para detalles
            open_form_dialog()
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_result)
    page.overlay.append(file_picker)

    # --- FORMULARIO DE DETALLES (Después de escanear) ---
    hospedero_input = ft.TextField(label="Hospedero / Cultivo", hint_text="Ej: Frutilla, Maíz")
    localidad_input = ft.TextField(label="Localidad", hint_text="Ej: Curicó, Melipilla")

    def submit_form(e):
        hospedero = hospedero_input.value if hospedero_input.value else "N/A"
        localidad = localidad_input.value if localidad_input.value else "N/A"
        
        easting, northing, zone_num, zone_let = (None, None, None, None)
        if current_lat is not None:
            easting, northing, zone_num, zone_let = latlon_to_utm_coords(current_lat, current_lon)

        # Guardar en DB
        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n, foto_path) VALUES (?,?,?,?,?,?,?)",
                      (datetime.now().strftime("%Y-%m-%d %H:%M"), detected_insect_name, hospedero, localidad, 
                       easting, northing, scanned_image_path))
        conn.commit()
        conn.close()

        result_text.value = f"✅ Reporte guardado para {detected_insect_name}."
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Detalles del Hallazgo"),
        content=ft.Column([
            ft.Text("Insecto identificado: "),
            ft.Text(value=detected_insect_name, weight="bold"),
            hospedero_input,
            localidad_input
        ]),
        actions=[
            ft.TextButton("Guardar Reporte", on_click=submit_form)
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Formulario cerrado")
    )

    def open_form_dialog():
        dialog.content.controls[1].value = detected_insect_name # Actualizar el insecto en el dialog
        page.dialog = dialog
        dialog.open = True
        page.update()

    # --- GENERAR MAPA DE CALOR ---
    def generar_mapa_calor(e):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT utm_e, utm_n FROM monitoreo WHERE utm_e IS NOT NULL")
        puntos = cursor.fetchall()
        conn.close()

        if not puntos:
            result_text.value = "⚠️ No hay datos GPS para el mapa"
            page.update()
            return

        plt.figure(figsize=(6, 5))
        x = [p[0] for p in puntos]
        y = [p[1] for p in puntos]
        
        plt.scatter(x, y, c='red', alpha=0.7, s=100)
        plt.title("Mapa de Monitoreo UTM")
        plt.xlabel("Este (m)")
        plt.ylabel("Norte (m)")
        plt.grid(True, linestyle='--', alpha=0.6)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        map_image.src_base64 = img_base64
        map_image.visible = True
        page.update()

    # --- INTERFAZ ---
    logo = ft.Text("MaestroScan Pro", size=32, weight="bold", color="#2E7D32")
    subtitulo = ft.Text("Inteligencia de Campo para Maestro Solution", size=10)
    
    gps_info = ft.Text("📍 Buscando ubicación...", italic=True, size=12)
    
    img_preview = ft.Image(width=150, height=150, fit=ft.ImageFit.CONTAIN, visible=False)

    scan_button = ft.ElevatedButton(
        "ESCANEAR INSECTO (Cámara)", 
        icon=ft.Icons.CAMERA_ALT,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE),
        style=ft.ButtonStyle(bgcolor="#2E7D32", color="white", padding=ft.padding.all(15))
    )
    
    loading_bar = ft.ProgressBar(width=300, color="#2E7D32", visible=False)
    result_text = ft.Text("", text_align=ft.TextAlign.CENTER, weight="bold")
    
    map_image = ft.Image(visible=False, width=350, height=300, fit=ft.ImageFit.CONTAIN)

    generate_map_button = ft.OutlinedButton(
        "GENERAR MAPA DE CALOR", 
        icon=ft.Icons.MAP, 
        on_click=generar_mapa_calor
    )

    page.add(
        ft.Column([
            logo,
            subtitulo,
            ft.Divider(),
            gps_info,
            img_preview,
            scan_button,
            loading_bar,
            result_text,
            ft.Divider(),
            generate_map_button,
            map_image
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    )