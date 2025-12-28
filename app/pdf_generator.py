import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def generar_pdf_profesional(datos):
    # IMPORTANTE: Quitamos el punto (.) antes de config
    import config 
    
    nombre_archivo = f"Reporte_{datos['insecto'].replace(' ', '_')}.pdf"
    ruta_completa = os.path.join(config.REPORT_DIR, nombre_archivo)

    c = canvas.Canvas(ruta_completa, pagesize=letter)
    width, height = letter

    # Diseño Maestro Solution
    c.setFillColorRGB(0.1, 0.4, 0.1)
    c.rect(0, height - 80, width, 80, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 45, f"{config.COMPANY} - MaestroScan")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 120, f"Cultivo: {datos['cultivo']}")
    c.drawString(50, height - 140, f"Plaga: {datos['insecto']}")
    c.drawString(50, height - 160, f"Categoría: {datos['categoria']}")
    c.drawString(50, height - 180, f"GPS: {datos['gps']}")
    
    c.save()
    return ruta_completa