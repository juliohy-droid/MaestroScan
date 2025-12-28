import os
import flet as ft
from app.gui_mobile import main

if __name__ == "__main__":
    # Render asigna el puerto mediante la variable PORT
    # Si no existe, usamos 8080 por defecto
    port = int(os.getenv("PORT", 8080))
    
    # Configuramos para que Flet corra como servidor web puro
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=port,
        host="0.0.0.0"  # Esto es lo que abre la app al mundo
    )