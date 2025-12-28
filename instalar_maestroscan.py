import os

def crear_proyecto_maestro():
    # 1. Definición de la estructura de carpetas
    directorios = [
        'MaestroScan_Project/app',
        'MaestroScan_Project/data/db',
        'MaestroScan_Project/data/photos',
        'MaestroScan_Project/data/datasets',
        'MaestroScan_Project/output/reports',
        'MaestroScan_Project/assets/models',
    ]

    for carpeta in directorios:
        os.makedirs(carpeta, exist_ok=True)
        print(f"Directorio creado: {carpeta}")

    # 2. Creación de archivos base
    archivos = {
        'MaestroScan_Project/requirements.txt': 'reportlab\npandas\ngeopy\nopencv-python-headless',
        
        'MaestroScan_Project/app/config.py': (
            "import os\nBASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
            "REPORT_DIR = os.path.join(BASE_DIR, 'output', 'reports')\n"
            "COMPANY = 'Maestro Solution'\nAPP_NAME = 'MaestroScan'"
        ),

        'MaestroScan_Project/app/ia_engine.py': (
            "def clasificar_plaga(nombre):\n"
            "    reglas = {'Drosophila suzukii': 'Primaria', 'Agrotis ipsilon': 'Primaria', 'Thrips': 'Secundaria'}\n"
            "    return reglas.get(nombre, 'Asociado / Desconocido')"
        ),

        'MaestroScan_Project/app/main.py': (
            "from config import APP_NAME\n"
            "print(f'--- {APP_NAME} cargado correctamente ---')\n"
            "print('Sistema listo para pruebas en terreno (Frutilla/Espárrago)')"
        )
    }

    for ruta, contenido in archivos.items():
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(contenido)
        print(f"Archivo generado: {ruta}")

    print("\n¡Listo, Maestro! Tu estructura de Maestro Solution ha sido desplegada.")

if __name__ == "__main__":
    crear_proyecto_maestro()