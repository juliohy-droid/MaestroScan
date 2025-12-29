import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    page.title = "MaestroScan Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    # Base de datos en carpeta temporal de Render
    db_path = "/tmp/maestro_scan_v12.db"

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

    # --- UI COMPONENTS ---
    loading = ft.ProgressBar(width=300, visible=False, color="green")
    resultado_txt = ft.Text("", weight="bold", size=16)
    contenedor_mapa = ft.Container(visible=False)
    
    hospedero_in = ft.TextField(label="Hospedero / Cultivo")
    localidad_in = ft.TextField(label="Localidad")

    # --- FUNCIONES ---
    def guardar_hallazgo(e):
        import utm
        try:
            u = utm.from_latlon(current_lat, current_lon)
            conn = sqlite3.connect(db_path)
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), det_insect, hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = f"✅ Reporte guardado con éxito"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error al procesar coordenadas: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Guardar Reporte", on_click=guardar_hallazgo)]
    )

    # CORRECCIÓN AQUÍ: Eliminamos 'ft.FilePickerResultEvent' para evitar el AttributeError
    def al_cambiar_archivo(e): 
        nonlocal det_insect
        if e.files:
            loading.visible = True
            page.update()
            
            # Aquí simulamos la identificación. 
            # Maestro, en el futuro aquí conectaremos con la búsqueda de imágenes en red.
            det_insect = "Drosophila suzukii (Identificado)" 
            
            loading.visible = False
            page.dialog = dlg
            dlg.open = True
            page.update()

    picker = ft.FilePicker(on_result=al_cambiar_archivo)
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
            plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red', s=100)
            plt.title("Puntos de Plaga (UTM)")
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            contenedor_mapa.content = ft.Image(src_base64=img_b64, border_radius=10)
            contenedor_mapa.visible = True
            page.update()
        else:
            resultado_txt.value = "Aún no hay puntos para el mapa."
            page.update()

    # --- INTERFAZ PRINCIPAL ---
    page.add(
        ft.Text("MaestroScan Pro", size=30, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION", size=10, italic=True),
        ft.Divider(),
        ft.GestureDetector(
            on_tap=lambda _: picker.pick_files(allow_multiple=False),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CAMERA_ALT, size=60, color="white"),
                    ft.Text("ESCANEAR INSECTO", color="white", weight="bold", size=20)
                ], alignment="center"),
                bgcolor="#2E7D32",
                padding=50,
                border_radius=30,
                width=300,
                height=250,
            )
        ),
        loading,
        resultado_txt,
        ft.Divider(),
        ft.OutlinedButton(
            "GENERAR MAPA DE CALOR", 
            icon=ft.Icons.MAP, 
            on_click=generar_mapa,
            style=ft.ButtonStyle(color="#2E7D32")
        ),
        contenedor_mapa
    )