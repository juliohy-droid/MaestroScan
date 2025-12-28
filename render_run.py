import flet as ft
from app.gui_mobile import main

if __name__ == "__main__":
    # Esto permite que la app corra en un servidor web
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)