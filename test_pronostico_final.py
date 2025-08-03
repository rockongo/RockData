from rockongo_core import predecir_partido_desde_excel

# Ruta de prueba con archivo real y equipos reales
archivo = r"C:\Users\raque\Desktop\ligas_datas\rockongo_web\Ligas\Primera_A_2025.xlsx"

# Equipos con valores cercanos (para forzar doble oportunidad)
equipo_local = "O'Higgins"
equipo_visita = "Colo Colo"

resultado = predecir_partido_desde_excel(archivo, equipo_local, equipo_visita)

print("\n--- PRUEBA DE PRONÓSTICO FINAL ---")
print(f"🏟️ Partido: {equipo_local} vs {equipo_visita}")
print(f"🔢 Probabilidades: {resultado['Resultado Partido']}")
print(f"📌 Pronóstico Final: {resultado['Resultado Partido']['Sugerencia']}")
print(f"📋 Justificación: {resultado.get('Justificacion Resultado', 'No disponible')}")
