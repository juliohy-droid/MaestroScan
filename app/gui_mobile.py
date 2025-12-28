import flet as ft
import os
import sys
import sqlite3
from datetime import datetime

# Forzar a Python a encontrar tus carpetas locales en el servidor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importaciones con manejo de errores para evitar que la sesión muera
try:
    from ia_engine import clasificar_plaga
    from pdf_generator import generar_pdf_profesional
except ImportError:
    # Intento alternativo para entornos de servidor
    from .ia_engine import clasificar_plaga
    from .pdf_generator import generar_pdf_profesional

def main(page: ft.Page):
    # Esto es vital para móviles: evita que la página se recargue por error
    page.title = "MaestroScan Pro"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.LIGHT