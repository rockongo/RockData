from rockongo_core import predecir_partido

# Ruta al Excel de la liga (ajústala si es necesario)
archivo = "Ligas/Primera_A_2025.xlsx"

# Equipos de prueba reales
local = "Everton"
visita = "Huachipato"

# Ejecutar predicción
resultado = predecir_partido(archivo, local, visita)

# Mostrar resultados relevantes
print("Pronóstico:", resultado["Pronóstico"])
print("Goles promedio:", resultado["Goles Totales"])
print("Probabilidad -2.5 goles:", resultado["Probabilidad -2.5 Goles"], "%")
print("Probabilidad +9.5 córners:", resultado["Probabilidad +9.5 Córners"], "%")
print("Probabilidad +4.5 tarjetas:", resultado["Probabilidad +4.5 Tarjetas"], "%")
