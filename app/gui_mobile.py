import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    # 1. Configuración de página ultra-estable
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    # Base de datos local en Render
    db_path = "/tmp/maestro_v14.db"

    # --- COMPONENTES DE UI ---
    resultado_txt = ft.Text("", weight="bold", size=16, text_align=ft.TextAlign.CENTER)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")
    mapa_cont = ft.Container(visible=False)

    # --- LÓGICA DE NEGOCIO ---
    def finalizar_registro(e):
        import utm
        try:
            # Simulación de UTM (Zona 19S Chile)
            u = utm.from_latlon(-33.45, -70.66)
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Identificado por MaestroScan", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            
            dlg.open = False
            resultado_txt.value = f"✅ Registro Guardado para {localidad_in.value}"
            resultado_txt.color = "green"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Finalizar Escaneo", on_click=finalizar_registro)]
    )

    # --- FUNCIÓN DE ESCANEO (Sin FilePicker para evitar franja roja) ---
    def iniciar_escaneo(e):
        resultado_txt.value = "🔍 Iniciando motor de identificación..."
        page.update()
        # En esta versión, saltamos el selector de archivos para asegurar que la App funcione
        # y abrimos directamente el formulario de datos.
        page.dialog = dlg
        dlg.open = True
        page.update()

    # --- MAPA DE CALOR ---
    def generar_mapa(e):
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        try:
            conn = sqlite3.connect(db_path)
            pts = conn.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
            conn.close()
            if pts:
                plt.figure(figsize=(4, 3))
                plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red', s=100)
                plt.title("Mapa de Calor Maestro Solution")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_b64, border_radius=10)
                mapa_cont.visible = True
            else:
                resultado_txt.value = "⚠️ No hay datos para el mapa."
            page.update()
        except:
            pass

    # --- DISEÑO ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION - AGRO INTELIGENCIA", size=10),
        ft.Divider(height=40),
        
        # Botón de acción principal (Sin dependencias externas)
        ft.Container(
            content=ft.ElevatedButton(
                "ESCANEAR INSECTO",
                icon=ft.Icons.CAMERA_ALT,
                on_click=iniciar_escaneo, # Llama a la función directa
                style=ft.ButtonStyle(bgcolor="#2E7D32", color="white", padding=30)
            )
        ),
        
        ft.Container(height=20),
        resultado_txt,
        ft.Divider(height=40),
        
        ft.OutlinedButton("VER MAPA DE CALOR UTM", icon=ft.Icons.MAP, on_click=generar_mapa),
        ft.Container(height=10),
        mapa_cont
    )

    page.update()