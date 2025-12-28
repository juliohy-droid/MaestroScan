import flet as ft
import os
import sys
import sqlite3
from datetime import datetime

# Configuración de rutas para Render
base_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_path)

def main(page: ft.Page):
    try:
        page.title = "MaestroScan Pro"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.scroll = ft.ScrollMode.AUTO

        # Importación diferida para evitar pantalla en blanco si fallan los módulos
        try:
            from ia_engine import clasificar_plaga
            from pdf_generator import generar_pdf_profesional
        except Exception as e:
            page.add(ft.Text(f"Error de módulos: {e}", color="red"))
            return

        # --- BASE DE DATOS LOCAL ---
        db_path = "/tmp/maestro_scan.db" # Render prefiere la carpeta /tmp para escritura
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS historial (id INTEGER PRIMARY KEY, fecha TEXT, cultivo TEXT, insecto TEXT)")
        conn.close()

        # --- UI BÁSICA ---
        logo = ft.Text("MaestroScan Pro", size=30, weight="bold", color="green")
        
        opciones = ft.Dropdown(
            label="Seleccionar Cultivo",
            options=[ft.dropdown.Option("Frutilla"), ft.dropdown.Option("Espárrago")]
        )

        resultado = ft.Text("", weight="bold")

        def analizar(e):
            if not opciones.value:
                resultado.value = "Selecciona un cultivo"
                page.update()
                return
            
            insecto = "Drosophila suzukii" if opciones.value == "Frutilla" else "Agrotis ipsilon"
            resultado.value = f"Detectado: {insecto}"
            
            # Guardar en DB
            c = sqlite3.connect(db_path)
            c.execute("INSERT INTO historial (fecha, cultivo, insecto) VALUES (?,?,?)", 
                      (datetime.now().strftime("%H:%M"), opciones.value, insecto))
            c.commit()
            c.close()
            page.update()

        btn = ft.ElevatedButton("Analizar", on_click=analizar, bgcolor="green", color="white")

        page.add(
            logo,
            ft.Text("Maestro Solution - Panel de Monitoreo", size=12, italic=True),
            ft.Divider(),
            opciones,
            btn,
            resultado
        )

    except Exception as ex:
        # Si algo falla, esto se verá en tu teléfono en lugar de la pantalla blanca
        page.add(ft.Text(f"Error crítico de inicio: {ex}", color="red"))
    
    page.update()