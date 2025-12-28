# Ejemplo conceptual con Flet (Interfaz moderna)
import flet as ft

def main(page: ft.Page):
    page.title = "MaestroScan"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.GREEN_50  # Fondo verde suave

    # Título con estilo Maestro Solution
    titulo = ft.Text("MaestroScan", size=30, color=ft.colors.GREEN_800, weight="bold")
    
    # Botón para simular escaneo
    btn_escanear = ft.ElevatedButton(
        "Escanear Plaga", 
        icon=ft.icons.CAMERA_ALT,
        style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE)
    )

    page.add(titulo, btn_escanear)

# ft.app(target=main) # Esto abriría la app en el móvil