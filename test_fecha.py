from datetime import datetime

def obtener_fecha_hoy():
    return datetime.now().strftime("%Y-%m-%d")

print("📅 Hoy es:", obtener_fecha_hoy())
