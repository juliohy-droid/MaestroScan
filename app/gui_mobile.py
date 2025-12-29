import flet as ft
import os
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    # 1. Configuración de página minimalista
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    # Ruta de base de datos
    db_path = "/tmp/maestro_final_safe.db"

    # --- COMPONENTES ---
    resultado_txt = ft.Text("", weight="bold", size=16)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")

    # --- LÓGICA DE GUARDADO ---
    def guardar_reporte(e):
        import utm
        try:
            # Posición base para Maestro Solution
            u = utm.from_latlon(-33.45, -70.66)
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Insecto Identificado", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = "✅ Registro Guardado en UTM"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Finalizar", on_click=guardar_reporte)]
    )

    # --- ELIMINAMOS EL FILEPICKER QUE DA ERROR ---
    # Usaremos una simulación de escaneo directa para verificar que la franja roja desaparece.
    def simular_escaneo(e):
        resultado_txt.value = "🔍 Iniciando escaneo de imagen..."
        page.update()
        # Aquí es donde el sistema "analiza"
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- MAPA (Carga diferida) ---
    def generar_mapa_calor(e):
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
                plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red')
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_b64)
                mapa_cont.visible = True
            else:
                resultado_txt.value = "No hay datos."
            page.update()
        except:
            pass

    mapa_cont = ft.Container(visible=False)

    # --- DISEÑO LIMPIO (PAGE ADD DIRECTO) ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MONITOREO PROFESIONAL", size=10),
        ft.Divider(height=40),
        
        # Botón de acción principal
        ft.ElevatedButton(
            "TOMAR FOTO / ESCANEAR",
            icon=ft.Icons.CAMERA_ALT,
            on_click=simular_escaneo,
            style=ft.ButtonStyle(bgcolor="#2E7D32", color="white", padding=30)
        ),
        
        resultado_txt,
        ft.Divider(height=40),
        
        ft.TextButton("GENERAR MAPA UTM", icon=ft.Icons.MAP, on_click=generar_mapa_calor),
        mapa_cont
    )

    page.update()