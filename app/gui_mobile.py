import flet as ft
import os
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    db_path = "/tmp/maestro_v25.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("Listo para escanear", weight="bold", size=16)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")
    mapa_cont = ft.Container(visible=False)

    # --- LÓGICA DE DATOS ---
    def guardar_registro(e):
        import utm
        try:
            u = utm.from_latlon(-33.45, -70.66) # Coordenada de prueba
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%H:%M"), "Drosophila suzukii", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = f"✅ Guardado en {localidad_in.value}"
            resultado_txt.color = "green"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error al guardar: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Datos del Monitoreo"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Guardar Reporte", on_click=guardar_registro)]
    )

    # --- MOTOR DE CÁMARA (NUEVO INTENTO) ---
    def resultado_camara(e):
        if e.files:
            resultado_txt.value = "📸 Imagen cargada con éxito"
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Declaración ultra-básica para evitar la franja roja
    archivo_picker = ft.FilePicker(on_result=resultado_camara)
    page.overlay.append(archivo_picker)

    # --- MAPA DE CALOR ---
    def mostrar_mapa(e):
        import matplotlib.pyplot as plt
        import matplotlib
        import io
        import base64
        matplotlib.use('Agg')
        try:
            conn = sqlite3.connect(db_path)
            # Aseguramos que la tabla existe antes de leer
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            pts = conn.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
            conn.close()
            
            if pts:
                plt.figure(figsize=(4, 3))
                plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red', s=100)
                plt.title("Zonas de Monitoreo Maestro Solution")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_b64, border_radius=10)
                mapa_cont.visible = True
            else:
                resultado_txt.value = "⚠️ No hay datos guardados todavía"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error Mapa: {ex}"
            page.update()

    # --- DISEÑO ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION", size=10, color="grey"),
        ft.Divider(height=30),
        
        # El botón de Escaneo
        ft.Container(
            padding=20,
            content=ft.ElevatedButton(
                "ABRIR CÁMARA",
                icon=ft.Icons.CAMERA_ALT,
                # Esta instrucción obliga al navegador a abrir el selector de archivos/cámara
                on_click=lambda _: archivo_picker.pick_files(allow_multiple=False),
                style=ft.ButtonStyle(
                    bgcolor="#2E7D32", 
                    color="white",
                    padding=25,
                )
            )
        ),
        
        resultado_txt,
        ft.Divider(height=30),
        
        ft.ElevatedButton(
            "VER MAPA DE CALOR UTM", 
            icon=ft.Icons.MAP, 
            on_click=mostrar_mapa,
            style=ft.ButtonStyle(color="#2E7D32")
        ),
        
        ft.Container(height=10),
        mapa_cont
    )
    page.update()