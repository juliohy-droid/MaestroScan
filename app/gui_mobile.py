import flet as ft
import os
import sqlite3
from datetime import datetime
import io
import base64

def main(page: ft.Page):
    # 1. Configuración de la página
    page.title = "MaestroScan Pro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    # 2. Definición del FilePicker (Debe ser lo primero)
    def al_recibir_archivo(e):
        if e.files:
            loading.visible = True
            page.update()
            # Simulación de identificación para Maestro Solution
            resultado_txt.value = "🔍 Procesando imagen..."
            loading.visible = False
            page.dialog = dlg
            dlg.open = True
            page.update()

    picker = ft.FilePicker(on_result=al_recibir_archivo)
    page.overlay.append(picker) # Esto lo saca de la vista y evita la franja roja

    # 3. Base de Datos
    db_path = "/tmp/maestrosolution_v2.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
    conn.close()

    # 4. Componentes de Interfaz
    loading = ft.ProgressBar(width=300, visible=False, color="green")
    resultado_txt = ft.Text("", weight="bold", size=16)
    mapa_cont = ft.Container(visible=False)
    
    hospedero_in = ft.TextField(label="Hospedero / Cultivo")
    localidad_in = ft.TextField(label="Localidad")

    def guardar_datos(e):
        import utm
        try:
            u = utm.from_latlon(-33.44, -70.66) # Coordenada base
            conn = sqlite3.connect(db_path)
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%H:%M"), "Drosophila suzukii", hospedero_in.value, localidad_in.value, u[0], u[1]))
            conn.commit()
            conn.close()
            dlg.open = False
            resultado_txt.value = "✅ Registro Guardado con éxito"
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error: {ex}"
            page.update()

    dlg = ft.AlertDialog(
        title=ft.Text("Ficha de Terreno"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Guardar", on_click=guardar_datos)]
    )

    def generar_mapa(e):
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
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
            page.update()

    # 5. Diseño Final
    page.add(
        ft.Text("MaestroScan Pro", size=30, weight="bold", color="green"),
        ft.Text("MAESTRO SOLUTION", size=10),
        ft.Divider(),
        ft.ElevatedButton(
            "ESCANEAR INSECTO",
            icon=ft.Icons.CAMERA_ALT,
            on_click=lambda _: picker.pick_files(),
            style=ft.ButtonStyle(bgcolor="green", color="white", padding=20)
        ),
        loading,
        resultado_txt,
        ft.Divider(),
        ft.ElevatedButton("VER MAPA DE CALOR UTM", on_click=generar_mapa),
        mapa_cont
    )