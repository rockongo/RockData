import pandas as pd
from rockongo_core import simulacion_forma_reciente

# Carga el archivo de una liga
df = pd.read_excel("Ligas/Primera_A_2025.xlsx")  # cambia por la liga que desees probar

# Equipos a comparar
equipo_local = "Colo Colo"
equipo_visita = "Universidad de Chile"

# Llamar a la función
resultado = simulacion_forma_reciente(df, equipo_local, equipo_visita)

# Mostrar el resultado
print("===== SIMULACIÓN DE FORMA RECIENTE =====")
print("LOCAL - Últimos 5 partidos:")
for k, v in resultado["Local (últimos 5)"].items():
    print(f"{k}: {v}")

print("\nVISITA - Últimos 5 partidos:")
for k, v in resultado["Visita (últimos 5)"].items():
    print(f"{k}: {v}")
