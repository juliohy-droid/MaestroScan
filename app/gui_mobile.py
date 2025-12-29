import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    db_path = "/tmp/maestro_v15.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("", weight="bold", size=16, text_align=ft.TextAlign.CENTER)
    mapa_cont = ft.Container(visible=False)
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")

    # --- LÓGICA DE RECONOCIMIENTO (IA SIMULADA) ---
    def procesar_hallazgo(e):
        if e.files:
            # Notificación visual
            resultado_txt.value = f"✅ Imagen capturada: {e.files[0].name}"
            resultado_txt.color = "blue"
            page.dialog = dlg
            dlg.open = True
            page.update()

    # --- COMPONENTE DE CÁMARA (SEGURO) ---
    # Lo declaramos de forma que no cause el error de atributo 'on_result'
    picker = ft.FilePicker()
    page.overlay.append(picker)
    picker.on_result = procesar_hallazgo # Asignación dinámica

    # --- LÓGICA DE GUARDADO ---
    def finalizar_registro(e):
        import utm
        try:
            u = utm.from_latlon(-33.45, -70.66) # Coordenada base
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Insecto Identificado", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            
            dlg.open = False
            resultado_txt.value = "✅ Registro Guardado en UTM"
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
                plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red')
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                img_b64 = base64.b64encode(buf.getvalue()).decode()
                mapa_cont.content = ft.Image(src_base64=img_b64, border_radius=10)
                mapa_cont.visible = True
                page.update()
        except: pass

    # --- DISEÑO PRINCIPAL ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION", size=12, color="grey"),
        ft.Divider(height=40),
        
        # El Botón de Cámara
        ft.ElevatedButton(
            "TOMAR FOTO / ESCANEAR",
            icon=ft.Icons.CAMERA_ALT,
            on_click=lambda _: picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE # Filtramos para que solo acepte fotos
            ),
            style=ft.ButtonStyle(bgcolor="#2E7D32", color="white", padding=30)
        ),
        
        ft.Container(height=20),
        resultado_txt,
        ft.Divider(height=40),
        
        ft.TextButton("VER MAPA DE CALOR UTM", icon=ft.Icons.MAP, on_click=generar_mapa),
        mapa_cont
    )

    page.update()