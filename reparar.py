import os

# 1. Asegurar carpetas
os.makedirs('app', exist_ok=True)
os.makedirs('output/reports', exist_ok=True)

# 2. Crear config.py
with open('app/config.py', 'w', encoding='utf-8') as f:
    f.write("import os\nBASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n"
            "REPORT_DIR = os.path.join(BASE_DIR, 'output', 'reports')\n"
            "COMPANY = 'Maestro Solution'\nAPP_NAME = 'MaestroScan'")

# 3. Crear ia_engine.py
with open('app/ia_engine.py', 'w', encoding='utf-8') as f:
    f.write("def clasificar_plaga(nombre):\n"
            "    categorias = {'Drosophila suzukii': 'Primaria / Alerta SAG', 'Agrotis ipsilon': 'Primaria'}\n"
            "    return categorias.get(nombre, 'Asociado')")

# 4. Crear pdf_generator.py
with open('app/pdf_generator.py', 'w', encoding='utf-8') as f:
    f.write("from reportlab.pdfgen import canvas\nfrom reportlab.lib.pagesizes import letter\nimport os\n"
            "def generar_pdf_profesional(datos):\n"
            "    from .config import REPORT_DIR, COMPANY\n"
            "    ruta = os.path.join(REPORT_DIR, f'Reporte_{datos[\"insecto\"]}.pdf')\n"
            "    c = canvas.Canvas(ruta, pagesize=letter)\n"
            "    c.drawString(100, 750, f'{COMPANY} - MaestroScan')\n"
            "    c.drawString(100, 730, f'Plaga: {datos[\"insecto\"]}')\n"
            "    c.drawString(100, 710, f'Categoria: {datos[\"categoria\"]}')\n"
            "    c.save()\n    return ruta")

# 5. Crear main.py (IMPORTANTE: Con los puntos de importación correctos)
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write("import sys, os\nsys.path.append(os.path.dirname(os.path.abspath(__file__)))\n"
            "from config import APP_NAME\nfrom ia_engine import clasificar_plaga\n"
            "from pdf_generator import generar_pdf_profesional\n\n"
            "if __name__ == '__main__':\n"
            "    datos = {'cultivo': 'Frutilla', 'insecto': 'Drosophila suzukii', 'gps': '-33.4, -70.6'}\n"
            "    datos['categoria'] = clasificar_plaga(datos['insecto'])\n"
            "    print(f'Generando informe para {APP_NAME}...')\n"
            "    ruta = generar_pdf_profesional(datos)\n"
            "    print(f'EXITO. Archivo en: {ruta}')")

print("Sistema reparado. Ahora ejecuta: python app/main.py")