import os
import flet as ft
from app.gui_mobile import main

if __name__ == "__main__":
    # Render usa el puerto 10000 por defecto
    port = int(os.getenv("PORT", 10000))
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=port,
        host="0.0.0.0"
    )