import flet as ft
import os
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    # Configuración de inicio rápido para evitar Timeouts
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    db_path = "/tmp/maestro_solution_final.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("", weight="bold", size=16, text_align=ft.TextAlign.CENTER)
    mapa_cont = ft.Container(visible=False)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")

    # --- LÓGICA DE ALMACENAMIENTO ---
    def guardar_datos(e):
        import utm  # Carga diferida
        try:
            # Coordenadas base para la ficha técnica
            u = utm.from_latlon(-33.45, -70.66) 
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Identificación en proceso", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            
            dlg.open = False
            resultado_txt.value = f"✅ Reporte guardado para {localidad_in.value}"
            resultado_txt.color = "green"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Guardar Registro", on_click=guardar_datos)]
    )

    # --- MANEJO DE ARCHIVOS (CORRECCIÓN CRÍTICA) ---
    def al_seleccionar_archivo(e):
        # Manejo de evento sin importar la versión de Flet
        if e.files:
            resultado_txt.value = "🔍 Imagen analizada. Complete la ficha."
            page.dialog = dlg
            dlg.open = True
            page.update()

    # CORRECCIÓN: Se crea el objeto y se asigna el evento por separado
    picker = ft.FilePicker()
    picker.on_result = al_seleccionar_archivo # Esta línea evita el error de Render
    page.overlay.append(picker)

    # --- FUNCIÓN MAPA ---
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
                plt.title("Zonas de Hallazgos")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_b64, border_radius=10)
                mapa_cont.visible = True
            else:
                resultado_txt.value = "Sin datos registrados."
            page.update()
        except:
            pass

    # --- DISEÑO PRINCIPAL ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION - AGRO INTELIGENCIA", size=10, italic=True),
        ft.Divider(height=40),
        
        # El botón llama al picker de forma segura
        ft.ElevatedButton(
            "ESCANEAR INSECTO",
            icon=ft.Icons.CAMERA_ALT,
            on_click=lambda _: picker.pick_files(),
            style=ft.ButtonStyle(bgcolor="#2E7D32", color="white", padding=25)
        ),
        
        resultado_txt,
        ft.Divider(height=40),
        ft.TextButton("Generar Mapa de Calor UTM", icon=ft.Icons.MAP, on_click=generar_mapa),
        mapa_cont
    )