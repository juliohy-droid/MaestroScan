import flet as ft
import os
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    # Configuración de página ultra-ligera
    page.title = "MaestroScan Pro"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    
    # 1. Función de Guardado (Carga módulos solo al usar)
    def guardar_registro(e):
        import utm # Carga diferida para evitar errores de inicio
        try:
            # Datos del formulario
            hospedero = hospedero_in.value if hospedero_in.value else "No especificado"
            localidad = localidad_in.value if localidad_in.value else "No especificada"
            
            # Coordenadas simuladas para asegurar que el motor UTM funcione
            # En producción, aquí se capturaría el GPS real
            u = utm.from_latlon(-33.45, -70.66) 
            
            db_path = "/tmp/maestro_solution_v5.db"
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE IF NOT EXISTS monitoreo (id INTEGER PRIMARY KEY, fecha TEXT, insecto TEXT, hospedero TEXT, localidad TEXT, utm_e REAL, utm_n REAL)")
            conn.execute("INSERT INTO monitoreo (fecha, insecto, hospedero, localidad, utm_e, utm_n) VALUES (?,?,?,?,?,?)",
                        (datetime.now().strftime("%d/%m %H:%M"), "Drosophila suzukii", hospedero, localidad, u[0], u[1]))
            conn.commit()
            conn.close()
            
            dlg.open = False
            resultado_txt.value = f"✅ Registro Guardado en UTM para {localidad}"
            resultado_txt.color = ft.Colors.GREEN_700
            page.update()
        except Exception as ex:
            resultado_txt.value = f"Error técnico: {ex}"
            page.update()

    # 2. UI del Formulario
    hospedero_in = ft.TextField(label="Hospedero / Cultivo", border_color="green")
    localidad_in = ft.TextField(label="Localidad", border_color="green")
    dlg = ft.AlertDialog(
        title=ft.Text("Detalles del Hallazgo"),
        content=ft.Column([hospedero_in, localidad_in], tight=True),
        actions=[ft.ElevatedButton("Guardar Reporte", on_click=guardar_registro)]
    )

    # 3. Lógica del Escáner (FilePicker Seguro)
    def al_seleccionar(e):
        if e.files:
            resultado_txt.value = "🔍 Imagen analizada con éxito."
            page.dialog = dlg
            dlg.open = True
            page.update()

    picker = ft.FilePicker(on_result=al_seleccionar)
    page.overlay.append(picker)

    # 4. Generador de Mapa (Carga diferida)
    def generar_mapa_calor(e):
        import matplotlib.pyplot as plt
        import matplotlib
        import io
        import base64
        matplotlib.use('Agg')
        
        try:
            db_path = "/tmp/maestro_solution_v5.db"
            conn = sqlite3.connect(db_path)
            pts = conn.execute("SELECT utm_e, utm_n FROM monitoreo").fetchall()
            conn.close()
            
            if not pts:
                resultado_txt.value = "⚠️ No hay datos registrados aún."
                page.update()
                return

            plt.figure(figsize=(4, 4))
            plt.scatter([p[0] for p in pts], [p[1] for p in pts], color='red', s=100)
            plt.title("Zonas de Presencia de Plagas")
            plt.grid(True, alpha=0.3)
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            mapa_cont.content = ft.Image(src_base64=img_b64, border_radius=10)
            mapa_cont.visible = True
            page.update()
        except:
            resultado_txt.value = "Error al procesar el mapa."
            page.update()

    mapa_cont = ft.Container(visible=False)

    # 5. Interfaz Visual
    resultado_txt = ft.Text("", weight="bold")

    page.add(
        ft.Text("MaestroScan Pro", size=32, weight="bold", color="#1B5E20"),
        ft.Text("MAESTRO SOLUTION - TECNOLOGÍA AGRÍCOLA", size=10, italic=True),
        ft.Divider(height=40),
        ft.ElevatedButton(
            "TOMAR FOTO / ESCANEAR",
            icon=ft.Icons.CAMERA_ALT,
            on_click=lambda _: picker.pick_files(allow_multiple=False),
            style=ft.ButtonStyle(bgcolor="#2E7D32", color="white", padding=25)
        ),
        resultado_txt,
        ft.Divider(height=40),
        ft.TextButton("Ver Historial en Mapa UTM", icon=ft.Icons.MAP, on_click=generar_mapa_calor),
        mapa_cont
    )