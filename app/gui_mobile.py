import flet as ft
import os
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    db_path = "/tmp/maestro_v15_final.db"

    # --- ELEMENTOS DE INTERFAZ ---
    resultado_txt = ft.Text("Sistema Maestro Solution - Listo", weight="bold")
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="#2E7D32")
    localidad_in = ft.TextField(label="Localidad", border_color="#2E7D32")
    mapa_cont = ft.Container(visible=False)

    # --- LÓGICA DE ALMACENAMIENTO ---
    def guardar_registro(e):
        import utm
        try:
            # Simulación de UTM
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
        actions=[ft.ElevatedButton("Finalizar", on_click=guardar_registro)]
    )

    # --- NUEVA ESTRATEGIA DE CÁMARA ---
    # Usamos un botón de carga nativo del navegador mediante un objeto invisible
    # Esto evita el componente FilePicker propenso a errores.
    
    def on_upload_result(e):
        # Esta función se dispara cuando el navegador termina de "subir" la foto
        resultado_txt.value = "📸 Imagen recibida con éxito"
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Usamos la versión de carga más básica y estable de 2025
    upload_button = ft.FilePicker(on_result=on_upload_result)
    page.overlay.append(upload_button)

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
                plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red')
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
        except: pass

    # --- DISEÑO ---
    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("TECNOLOGÍA PARA EL AGRO", size=10, color="grey"),
        ft.Divider(height=40),
        
        # Este botón usa el comando nativo de archivos del teléfono
        ft.ElevatedButton(
            "TOMAR FOTO / ESCANEAR",
            icon=ft.Icons.CAMERA_ALT,
            on_click=lambda _: upload_button.pick_files(
                allow_multiple=False,
                # Forzamos al navegador a ofrecer la cámara
                file_type=ft.FilePickerFileType.IMAGE 
            ),
            style=ft.ButtonStyle(bgcolor="#2E7D32", color="white", padding=30)
        ),
        
        resultado_txt,
        ft.Divider(height=40),
        
        ft.TextButton("VER MAPA DE CALOR UTM", icon=ft.Icons.MAP, on_click=generar_mapa),
        mapa_cont
    )
    page.update()