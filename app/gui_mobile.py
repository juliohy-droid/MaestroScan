import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    # Configuración básica de arranque rápido
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    
    db_path = "/tmp/maestro_sol_final.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("", weight="bold", size=16, text_align=ft.TextAlign.CENTER)
    mapa_cont = ft.Container(visible=False)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo")
    localidad_in = ft.TextField(label="Localidad")

    # --- LÓGICA DE ALMACENAMIENTO ---
    def guardar_datos(e):
        # Importamos UTM solo aquí, cuando se necesita, para no saturar el inicio
        import utm
        try:
            # Simulación de posición para la base de datos
            u = utm.from_latlon(-33.45, -70.66) 
            conn = sqlite3.connect(db_path)
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%H:%M"), "Insecto Detectado", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = "✅ Reporte Guardado Exitosamente"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Confirmar", on_click=guardar_datos)]
    )

    # --- MANEJO DE ARCHIVOS ---
    def al_seleccionar(e):
        if e.files:
            resultado_txt.value = "🔍 Imagen capturada. Procesando..."
            page.dialog = dlg
            dlg.open = True
            page.update()

    # FilePicker declarado de forma segura
    picker = ft.FilePicker(on_result=al_seleccionar)
    page.overlay.append(picker)

    # --- MAPA DE CALOR ---
    def ver_mapa(e):
        # Importamos matplotlib solo aquí para evitar que la app pese al arrancar
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        
        conn = sqlite3.connect(db_path)
        pts = conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)").connection.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
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
            page.update()
        else:
            resultado_txt.value = "No hay datos para el mapa."
            page.update()

    # --- DISEÑO FINAL ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION", size=12, italic=True),
        ft.Divider(height=20),
        ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CAMERA_ALT, size=60, color="white"),
                ft.Text("ESCANEAR INSECTO", color="white", weight="bold")
            ], alignment="center"),
            bgcolor="#2E7D32",
            padding=40,
            border_radius=30,
            on_click=lambda _: picker.pick_files()
        ),
        resultado_txt,
        ft.Divider(),
        ft.OutlinedButton("VER MAPA DE CALOR UTM", icon=ft.Icons.MAP, on_click=ver_mapa),
        mapa_cont
    )