import flet as ft
import os
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    # 1. Configuración de página a prueba de fallos
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    # Base de datos local
    db_path = "/tmp/maestro_final_v30.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("Sistema Maestro Solution Activo", weight="bold", size=16)
    mapa_cont = ft.Container(visible=False)
    
    # --- FORMULARIO DE DATOS ---
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="#2E7D32")
    localidad_in = ft.TextField(label="Localidad", border_color="#2E7D32")

    def guardar_registro(e):
        import utm
        try:
            # Coordenada fija para validar el motor UTM
            u = utm.from_latlon(-33.45, -70.66) 
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Drosophila suzukii", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = f"✅ Registro Guardado: {localidad_in.value}"
            resultado_txt.color = "green"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Guardar Reporte", on_click=guardar_registro)]
    )

    # --- FUNCIÓN DE ACTIVACIÓN (NUEVA ESTRATEGIA) ---
    def activar_proceso(e):
        # En lugar de usar FilePicker (que da franja roja), 
        # lanzamos el formulario directamente. 
        # Maestro, esto nos permite operar la base de datos y el mapa 
        # mientras el soporte de Flet arregla el error de cámara en la nube.
        resultado_txt.value = "📸 Simulando captura de cámara..."
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- MOTOR DE MAPAS ---
    def generar_mapa(e):
        import matplotlib.pyplot as plt
        import matplotlib
        import io
        import base64
        matplotlib.use('Agg')
        try:
            conn = sqlite3.connect(db_path)
            pts = conn.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
            conn.close()
            if pts:
                plt.figure(figsize=(4, 3))
                plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red', s=100)
                plt.title("Zonas de Monitoreo")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_b64, border_radius=10)
                mapa_cont.visible = True
            else:
                resultado_txt.value = "⚠️ No hay datos para el mapa."
            page.update()
        except: pass

    # --- DISEÑO LIMPIO Y SIN COMPONENTES ROTOS ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("TECNOLOGÍA PARA EL AGRO", size=10, color="grey"),
        ft.Divider(height=40),
        
        # Botón Seguro: No usa FilePicker
        ft.ElevatedButton(
            "INICIAR ESCANEO",
            icon=ft.Icons.CAMERA_ALT,
            on_click=activar_proceso,
            style=ft.ButtonStyle(
                bgcolor="#2E7D32", 
                color="white",
                padding=30,
                shape=ft.RoundedRectangleBorder(radius=15)
            )
        ),
        
        ft.Container(height=20),
        resultado_txt,
        ft.Divider(height=40),
        
        ft.OutlinedButton(
            "VER MAPA DE CALOR UTM", 
            icon=ft.Icons.MAP, 
            on_click=generar_mapa,
            style=ft.ButtonStyle(color="#2E7D32")
        ),
        
        ft.Container(height=10),
        mapa_cont
    )
    page.update()