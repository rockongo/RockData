from rockongo_core import predecir_partido_desde_excel, generar_resumen_formateado

# Ruta y equipos para la prueba
archivo = r"C:\Users\raque\Desktop\ligas_datas\rockongo_web\Ligas\Primera_A_2025.xlsx"
equipo_local = "Colo Colo"
equipo_visita = "Universidad de Chile"

# Ejecutar predicción
resultado = predecir_partido_desde_excel(archivo, equipo_local, equipo_visita)

# Generar resumen formateado
resumen = generar_resumen_formateado(resultado["Probabilidades"])

# Mostrar resultados
print("\n=== RESUMEN ROCKDATA ===")
for clave, valor in resumen.items():
    print(f"\n{clave}:")
    if isinstance(valor, dict):
        for subclave, subvalor in valor.items():
            print(f"  {subclave}: {subvalor}")
    else:
        print(f"  {valor}")
