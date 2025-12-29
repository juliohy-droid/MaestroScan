import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    # 1. Configuración de inicio rápido
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    db_path = "/tmp/maestro_sol_2025.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("", weight="bold", size=16, text_align=ft.TextAlign.CENTER)
    mapa_cont = ft.Container(visible=False)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")

    # --- LÓGICA DE ALMACENAMIENTO ---
    def guardar_datos(e):
        import utm # Carga diferida para evitar errores de inicio
        try:
            # Coordenadas por defecto para la base de datos (se pueden ajustar luego)
            u = utm.from_latlon(-33.45, -70.66) 
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Insecto Identificado", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = "✅ Hallazgo Guardado Exitosamente"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([
            ft.Text("Complete los datos del escaneo:"),
            hospedero_in, 
            localidad_in
        ], tight=True),
        actions=[ft.ElevatedButton("Confirmar y Guardar", on_click=guardar_datos, bgcolor="green", color="white")]
    )

    # --- CORRECCIÓN UNIVERSAL DE FILEPICKER ---
    def procesar_archivo(e):
        if e.files:
            resultado_txt.value = "🔍 Imagen capturada. Procesando..."
            page.dialog = dlg
            dlg.open = True
            page.update()

    # Se crea el objeto vacío y se asigna el evento después para evitar el error 'unexpected argument'
    picker = ft.FilePicker()
    picker.on_result = procesar_archivo
    page.overlay.append(picker)

    # --- FUNCIÓN MAPA DE CALOR ---
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
                plt.title("Puntos de Monitoreo UTM")
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_base64, border_radius=10)
                mapa_cont.visible = True
                page.update()
            else:
                resultado_txt.value = "⚠️ No hay datos registrados."
                page.update()
        except:
            resultado_txt.value = "Error al generar el mapa."
            page.update()

    # --- DISEÑO PRINCIPAL (UI) ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION - TECNOLOGÍA DE CAMPO", size=10, italic=True),
        ft.Divider(height=20),
        
        # Botón Grande de Escaneo
        ft.GestureDetector(
            on_tap=lambda _: picker.pick_files(),
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CAMERA_ALT, size=60, color="white"),
                    ft.Text("ESCANEAR EN TERRENO", color="white", weight="bold")
                ], alignment="center", spacing=10),
                bgcolor="#2E7D32",
                padding=50,
                border_radius=30,
            )
        ),
        
        resultado_txt,
        ft.Divider(height=30),
        
        ft.ElevatedButton(
            "VER MAPA DE CALOR UTM", 
            icon=ft.Icons.MAP, 
            on_click=generar_mapa,
            style=ft.ButtonStyle(color="green")
        ),
        
        ft.Container(height=10),
        mapa_cont,
        ft.Text("© 2025 Maestro Solution", size=10, color="grey")
    )