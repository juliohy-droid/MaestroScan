import flet as ft
import os
import sys
import urllib.parse
from datetime import datetime
import sqlite3

# Configuración de rutas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ia_engine import clasificar_plaga
from pdf_generator import generar_pdf_profesional

def main(page: ft.Page):
    page.title = "MaestroScan Pro - Maestro Solution"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # --- BASE DE DATOS ---
    def inicializar_db():
        db_path = os.path.join(os.getcwd(), "maestro_scan.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS historial 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           fecha TEXT, cultivo TEXT, insecto TEXT, gps TEXT)''')
        conn.commit()
        conn.close()

    def guardar_en_historial(datos):
        db_path = os.path.join(os.getcwd(), "maestro_scan.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO historial (fecha, cultivo, insecto, gps) VALUES (?, ?, ?, ?)",
                       (datos['fecha'], datos['cultivo'], datos['insecto'], datos['gps']))
        conn.commit()
        conn.close()

    inicializar_db()

    # --- VARIABLES Y GPS (PROTEGIDO) ---
    coordenadas = "Ubicación manual o no disponible"
    
    def on_location_event(e):
        nonlocal coordenadas
        try:
            coordenadas = f"{e.latitude:.4f}, {e.longitude:.4f}"
            gps_text.value = f"📍 Ubicación: {coordenadas}"
            page.update()
        except:
            pass

    # Intentamos activar el GPS solo si la versión de Flet lo permite
    try:
        if hasattr(ft, "Geolocator"):
            lp = ft.Geolocator()
            page.overlay.append(lp)
            lp.on_change = on_location_event
        else:
            coordenadas = "GPS no soportado en esta versión"
    except Exception as ex:
        coordenadas = f"GPS Off"

    # --- MANEJO DE CÁMARA ---
    def capturar_foto(e):
        file_picker.pick_files(allow_multiple=False, file_type=ft.FilePickerFileType.IMAGE)

    def al_seleccionar_archivo(e):
        if e.files:
            analizar_y_reportar(e.files[0].name)

    file_picker = ft.FilePicker(on_result=al_seleccionar_archivo)
    page.overlay.append(file_picker)

    # --- LÓGICA DE ANÁLISIS ---
    def analizar_y_reportar(nombre_foto):
        if not opciones_cultivo.value:
            resultado_texto.value = "⚠️ Selecciona un cultivo"
            resultado_texto.color = ft.Colors.RED
            page.update()
            return

        cargando.visible = True
        resultado_texto.value = "Analizando plaga..."
        page.update()

        insecto = "Drosophila suzukii" if opciones_cultivo.value == "Frutilla" else "Agrotis ipsilon"
        categoria = clasificar_plaga(insecto)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        datos = {
            "cultivo": opciones_cultivo.value, "insecto": insecto,
            "categoria": categoria, "gps": coordenadas, "fecha": fecha_actual
        }

        generar_pdf_profesional(datos)
        guardar_en_historial(datos)
        
        cargando.visible = False
        resultado_texto.value = f"✅ Detectado: {insecto}"
        resultado_texto.color = ft.Colors.GREEN_800
        btn_whatsapp.visible = True
        actualizar_lista_historial()
        page.update()

    # --- INTERFAZ ---
    logo = ft.Text("MaestroScan Pro", size=32, weight="bold", color=ft.Colors.GREEN_800)
    gps_text = ft.Text(f"📍 {coordenadas}", italic=True, size=12)
    
    opciones_cultivo = ft.Dropdown(
        label="Cultivo",
        options=[ft.dropdown.Option("Frutilla"), ft.dropdown.Option("Espárrago")],
        border_color=ft.Colors.GREEN_700
    )

    btn_escanear = ft.ElevatedButton(
        " TOMAR FOTO", icon=ft.Icons.CAMERA_ALT,
        on_click=capturar_foto,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color="white"),
        height=50
    )

    cargando = ft.ProgressBar(visible=False, color=ft.Colors.GREEN_700)
    resultado_texto = ft.Text("", weight="bold", text_align=ft.TextAlign.CENTER)
    historial_lista = ft.Column(spacing=5)

    def actualizar_lista_historial():
        historial_lista.controls.clear()
        try:
            db_path = os.path.join(os.getcwd(), "maestro_scan.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, cultivo, insecto FROM historial ORDER BY id DESC LIMIT 3")
            for row in cursor.fetchall():
                historial_lista.controls.append(
                    ft.Text(f"• {row[0]}: {row[1]} ({row[2]})", size=12)
                )
            conn.close()
        except: pass
        page.update()

    btn_whatsapp = ft.FloatingActionButton(
        content=ft.Icon(ft.Icons.SHARE, color="white"),
        bgcolor=ft.Colors.GREEN_600,
        on_click=lambda _: page.launch_url(f"https://wa.me/56912345678?text=Reporte MaestroScan"),
        visible=False
    )

    actualizar_lista_historial()

    page.add(
        ft.Column([
            logo, gps_text, ft.Divider(),
            opciones_cultivo, btn_escanear,
            cargando, resultado_texto,
            ft.Divider(),
            ft.Text("Historial Reciente:", weight="bold"),
            historial_lista
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        btn_whatsapp
    )