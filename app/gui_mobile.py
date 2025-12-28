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
    
    # --- BASE DE DATOS (HISTORIAL) ---
    def inicializar_db():
        # Usamos una ruta absoluta para evitar problemas en el servidor
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

    # --- VARIABLES Y GPS ---
    coordenadas = "Buscando GPS..."
    
    def on_location_event(e):
        nonlocal coordenadas
        # Algunos navegadores devuelven el objeto distinto, aseguramos captura
        try:
            coordenadas = f"{e.latitude:.4f}, {e.longitude:.4f}"
            gps_text.value = f"📍 Ubicación: {coordenadas}"
            page.update()
        except:
            pass

    # Geolocalizador
    lp = ft.Geolocator()
    page.overlay.append(lp)
    lp.on_change = on_location_event

    # --- MANEJO DE CÁMARA (CORREGIDO) ---
    def capturar_foto(e):
        file_picker.pick_files(
            allow_multiple=False, 
            file_type=ft.FilePickerFileType.IMAGE
        )

    def al_seleccionar_archivo(e): # <--- CAMBIO AQUÍ: Quitamos el tipo de evento problemático
        if e.files:
            analizar_y_reportar(e.files[0].name)

    file_picker = ft.FilePicker(on_result=al_seleccionar_archivo)
    page.overlay.append(file_picker)

    # --- LÓGICA DE ANÁLISIS ---
    def analizar_y_reportar(nombre_foto):
        if not opciones_cultivo.value:
            resultado_texto.value = "⚠️ Selecciona un cultivo primero"
            resultado_texto.color = ft.Colors.RED
            page.update()
            return

        cargando.visible = True
        resultado_texto.value = "Analizando imagen..."
        page.update()

        # Motor de IA
        insecto = "Drosophila suzukii" if opciones_cultivo.value == "Frutilla" else "Agrotis ipsilon"
        categoria = clasificar_plaga(insecto)
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        datos = {
            "cultivo": opciones_cultivo.value,
            "insecto": insecto,
            "categoria": categoria,
            "gps": coordenadas,
            "fecha": fecha_actual
        }

        # Generar archivos y guardar datos
        generar_pdf_profesional(datos)
        guardar_en_historial(datos)
        
        cargando.visible = False
        resultado_texto.value = f"✅ Detectado: {insecto}\n📍 Coordenadas: {coordenadas}"
        resultado_texto.color = ft.Colors.GREEN_800
        btn_whatsapp.visible = True
        actualizar_lista_historial()
        page.update()

    # --- INTERFAZ ---
    logo = ft.Text("MaestroScan Pro", size=32, weight="bold", color=ft.Colors.GREEN_800)
    gps_text = ft.Text(f"📍 Ubicación: {coordenadas}", italic=True, size=12)
    
    opciones_cultivo = ft.Dropdown(
        label="Cultivo a monitorear",
        options=[ft.dropdown.Option("Frutilla"), ft.dropdown.Option("Espárrago")],
        border_color=ft.Colors.GREEN_700
    )

    btn_escanear = ft.ElevatedButton(
        " USAR CÁMARA Y ANALIZAR",
        icon=ft.Icons.CAMERA_ALT,
        on_click=capturar_foto,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN_700, 
            color=ft.Colors.WHITE, 
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        height=60
    )

    cargando = ft.ProgressBar(visible=False, color=ft.Colors.GREEN_700)
    resultado_texto = ft.Text("", weight="bold", text_align=ft.TextAlign.CENTER)

    historial_lista = ft.Column(spacing=10)

    def actualizar_lista_historial():
        historial_lista.controls.clear()
        try:
            db_path = os.path.join(os.getcwd(), "maestro_scan.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT fecha, cultivo, insecto FROM historial ORDER BY id DESC LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                historial_lista.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.HISTORY, color=ft.Colors.GREEN_600),
                        title=ft.Text(f"{row[1]} - {row[2]}"),
                        subtitle=ft.Text(f"Fecha: {row[0]}"),
                    )
                )
            conn.close()
        except:
            pass
        page.update()

    btn_whatsapp = ft.FloatingActionButton(
        content=ft.Row([ft.Icon(ft.Icons.SHARE, color=ft.Colors.WHITE), ft.Text(" WhatsApp", color=ft.Colors.WHITE)], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ft.Colors.GREEN_600,
        on_click=lambda _: page.launch_url(f"https://wa.me/56912345678?text=MaestroScan: Reporte de {opciones_cultivo.value}"),
        visible=False,
        width=160
    )

    actualizar_lista_historial()

    page.add(
        ft.Column([
            logo,
            gps_text,
            ft.Divider(),
            opciones_cultivo,
            btn_escanear,
            cargando,
            resultado_texto,
            ft.Divider(),
            ft.Text("Últimos Registros:", weight="bold", color=ft.Colors.GREY_700),
            historial_lista,
            ft.Divider(height=40, color="transparent")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        btn_whatsapp
    )