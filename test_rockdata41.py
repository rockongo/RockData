from rockongo_core import (
    predecir_partido_desde_excel,
    generar_resumen_formateado,
    formato_rockdata_41
)

# Parámetros del partido
archivo = r"C:\Users\raque\desktop\ligas_datas\rockongo_web\Ligas\Primera_A_2025.xlsx"
equipo_local = "O'Higgins"
equipo_visita = "Colo Colo"
nombre_liga = "Primera A de Chile, Jornada X"  # Puedes poner la jornada si la conoces

# Obtener resultados con motor real
resultados = predecir_partido_desde_excel(archivo, equipo_local, equipo_visita)
resumen = generar_resumen_formateado(resultados["Probabilidades"])

# Construir el diccionario formateado para mostrar
datos_para_formato = {
    'partido': f"{equipo_local} vs {equipo_visita}",
    'liga': nombre_liga,
    'gol_1t_prob': resumen["Gol 1er Tiempo"]["Probabilidad"],
    'gol_1t_texto': resumen["Gol 1er Tiempo"]["Recomendación"],
    'ambos_marcan_prob': resumen["Ambos Marcan"]["Probabilidad"],
    'ambos_marcan_texto': resumen["Ambos Marcan"]["Recomendación"],
    'ambos_marcan_justificacion': f"{equipo_local} y {equipo_visita} presentan buen promedio de gol reciente.",
    'goles_umbral': resumen["Goles Totales"]["Umbral"],
    'goles_prob': resumen["Goles Totales"]["Probabilidad"],
    'goles_texto': resumen["Goles Totales"]["Texto"],
    'corners': resumen["Córners"],
    'corners_sugerencia': "Más de 8.5 córners" if resumen["Córners"]["+8.5"] >= 70 else "Evitar apuesta por córners altos",
    'corners_justificacion': "Promedio combinado de córners supera el umbral esperado.",
    'tarjetas': resumen["Tarjetas"],
    'tarjetas_sugerencia': "Más de 3.5 tarjetas" if resumen["Tarjetas"]["+3.5"] >= 70 else "Evitar apuestas a tarjetas altas",
    'tarjetas_justificacion': "Promedio combinado de tarjetas supera 4.0 por partido.",
    'resultado': {
        'local': resumen["Resultado"]["Local"],
        'empate': resumen["Resultado"]["Empate"],
        'visita': resumen["Resultado"]["Visita"]
    },
    'pronostico_final': resumen["Resultado"]["Sugerencia"].replace("Sugerimos apostar por: ", ""),
    'resultado_justificacion': f"{equipo_local} promedia X goles. {equipo_visita} promedia Y goles. (puedes ajustar)",
    'forma_reciente': f"{equipo_visita} viene en buena racha reciente. (puedes reemplazar con función real)"
}

# Mostrar el resultado final en consola
formato_rockdata_41(datos_para_formato)
