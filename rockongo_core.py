import pandas as pd
import os

from probabilidades import (
    calcular_probabilidad_goles,
    calcular_probabilidad_corners,
    calcular_probabilidad_tarjetas
)


# Ruta donde están guardados todos los Excel de ligas
RUTA_LIGAS = r"C:\Users\raque\desktop\ligas_datas\Ligas"

LIGAS = {
    "Chile": {
        "Primera A": "Primera_A_2025.xlsx",
        "Primera B": "Primera_B_2025.xlsx"
    },
    "Bolivia": {
        "Primera A": "Liga_bolivia_2025.xlsx"
    },
    "Perú": {
        "Primera A": "Liga_peruana_2025.xlsx"
    },
    "USA": {
        "MLS": "Liga_MLS_2025.xlsx"
    },
    "Noruega": {
        "Eliteserien": "Liga_Noruega_2025.xlsx"
    },
    "Ecuador": {
        "Liga Pro": "Liga_ecuador_2025.xlsx"
    },
    "Colombia": {
        "Primera A": "Liga_colombia_2025.xlsx"
    }
}

def rockongo1_prediccion(df, equipo_local, equipo_visita):
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.sort_values('Fecha')
    local_partidos = df[df['Local'] == equipo_local].tail(10)
    visita_partidos = df[df['Visita'] == equipo_visita].tail(10)

    def calcular_promedios(partidos, tipo):
        if partidos.empty:
            return {"goles": 0, "goles_1T": 0, "goles_2T": 0, "corners": 0, "amarillas": 0, "rojas": 0}
        return {
            "goles": partidos[f"Goles {tipo}"].mean(),
            "goles_1T": partidos[f"Goles 1T {tipo}"].mean(),
            "goles_2T": partidos[f"Goles 2T {tipo}"].mean(),
            "corners": partidos[f"Corners {tipo}"].mean(),
            "amarillas": partidos[f"Amarillas {tipo}"].mean(),
            "rojas": partidos[f"Rojas {tipo}"].mean(),
        }

    stats_local = calcular_promedios(local_partidos, "Local")
    stats_visita = calcular_promedios(visita_partidos, "Visita")

    def calcular_localia_real(df, equipo_local, equipo_visita):
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df.sort_values('Fecha')
        local_partidos = df[df['Local'] == equipo_local].tail(10)
        visita_partidos = df[df['Visita'] == equipo_visita].tail(10)
        victorias_local = (local_partidos['Goles Local'] > local_partidos['Goles Visita']).sum()
        victorias_visita = (visita_partidos['Goles Visita'] > visita_partidos['Goles Local']).sum()
        porcentaje_local = (victorias_local / len(local_partidos)) * 100 if len(local_partidos) > 0 else 0
        porcentaje_visita = (victorias_visita / len(visita_partidos)) * 100 if len(visita_partidos) > 0 else 0
        influencia = 0
        if porcentaje_local - porcentaje_visita > 20:
            influencia = 0.5
        elif porcentaje_visita - porcentaje_local > 20:
            influencia = -0.5
        return influencia, porcentaje_local, porcentaje_visita

    localia_bonus, fort_local, fort_visita = calcular_localia_real(df, equipo_local, equipo_visita)

    puntaje_local = stats_local["goles"] - (stats_local["amarillas"] * 0.1 + stats_local["rojas"] * 0.3)
    puntaje_visita = stats_visita["goles"] - (stats_visita["amarillas"] * 0.1 + stats_visita["rojas"] * 0.3)
    puntaje_local += localia_bonus

    if abs(puntaje_local - puntaje_visita) < 0.4:
        resultado = "Empate"
    elif puntaje_local > puntaje_visita:
        resultado = "Local"
    else:
        resultado = "Visita"

    
        # Local
    corners_local_lista = local_partidos["Corners Local"].dropna().tolist()
    corners_visita_lista = visita_partidos["Corners Visita"].dropna().tolist()

        # ------------------------
    # CÁLCULO DE PROBABILIDADES REALES (solo con partidos recientes)
    # ------------------------

    try:
        df_local = df[df['Local'] == equipo_local].tail(10)
        df_visita = df[df['Visita'] == equipo_visita].tail(10)
        df_partido = pd.concat([df_local, df_visita])

        prob_goles_menos_25 = calcular_probabilidad_goles(df_partido, "menos", 2.5)
        prob_corners_mas_9_5 = calcular_probabilidad_corners(df_partido, "mas", 9.5)
        prob_tarjetas_mas_4_5 = calcular_probabilidad_tarjetas(df_partido, "mas", 4.5)

    except Exception as e:
        prob_goles_menos_25 = prob_corners_mas_9_5 = prob_tarjetas_mas_4_5 = None
        print("Error al calcular probabilidades:", e)
    # --------------------------
    # NUEVO BLOQUE PROBABILÍSTICO
    # --------------------------

    stats_local_data = {
        "goles": stats_local["goles"],
        "goles_1T": stats_local["goles_1T"],
        "corners": stats_local["corners"],
        "amarillas": stats_local["amarillas"],
        "rojas": stats_local["rojas"]
    }

    stats_visita_data = {
        "goles": stats_visita["goles"],
        "goles_1T": stats_visita["goles_1T"],
        "corners": stats_visita["corners"],
        "amarillas": stats_visita["amarillas"],
        "rojas": stats_visita["rojas"]
    }


    resultado_probabilistico = predecir_partido(stats_local_data, stats_visita_data)
    if not resultado_probabilistico or "Gol 1er Tiempo" not in resultado_probabilistico:
        print("⚠️ Error: resultado_probabilistico es None o no contiene 'Gol 1er Tiempo'")
        return None


# === Análisis textual de Gol en Primer Tiempo ===
    gol_1t_prob = resultado_probabilistico["Gol 1er Tiempo"]["1 gol"]

    if gol_1t_prob >= 60:
        gol_1t_texto = "Alta probabilidad de que se abra el marcador antes del descanso."
    elif 45 <= gol_1t_prob < 60:
        gol_1t_texto = "Hay chances razonables de gol antes del descanso, aunque no está garantizado."
    else:
        gol_1t_texto = "No se anticipa un primer tiempo muy activo."

    return {
        "Equipo Local": equipo_local,
        "Equipo Visita": equipo_visita,
        "Promedios Local": {
            "Goles": stats_local["goles"],
            "Goles 1T": stats_local["goles_1T"],
            "Corners": stats_local["corners"],
            "Tarjetas": stats_local["amarillas"] + stats_local["rojas"]
        },
        "Promedios Visita": {
            "Goles": stats_visita["goles"],
            "Goles 1T": stats_visita["goles_1T"],
            "Corners": stats_visita["corners"],
            "Tarjetas": stats_visita["amarillas"] + stats_visita["rojas"]
        },
        "Estadísticas Totales": {
            "Goles Totales": round(stats_local["goles"] + stats_visita["goles"], 2),
            "Corners Totales": round(stats_local["corners"] + stats_visita["corners"], 2),
            "Tarjetas Totales": round(
                stats_local["amarillas"] + stats_local["rojas"] +
                stats_visita["amarillas"] + stats_visita["rojas"], 2
            )
        },
        "Probabilidades": resultado_probabilistico,
        "Gol 1T": {
            "Probabilidad": gol_1t_prob,
            "Texto": gol_1t_texto
        }

    }



def predecir_partido_desde_excel(archivo_excel, equipo_local, equipo_visita):
    df = pd.read_excel(archivo_excel)
    return rockongo1_prediccion(df, equipo_local, equipo_visita)

def simulacion_forma_reciente(df, equipo_local, equipo_visita):
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.sort_values('Fecha')

    ultimos_5_local = df[(df['Local'] == equipo_local) | (df['Visita'] == equipo_local)].tail(5)
    ultimos_5_visita = df[(df['Local'] == equipo_visita) | (df['Visita'] == equipo_visita)].tail(5)

    def calcular_estadisticas(partidos, equipo):
        goles = []
        goles_1T = []
        goles_2T = []
        corners = []
        amarillas = []
        rojas = []

        for _, row in partidos.iterrows():
            if row['Local'] == equipo:
                goles.append(row['Goles Local'])
                goles_1T.append(row['Goles 1T Local'])
                goles_2T.append(row['Goles 2T Local'])
                corners.append(row['Corners Local'])
                amarillas.append(row['Amarillas Local'])
                rojas.append(row['Rojas Local'])
            elif row['Visita'] == equipo:
                goles.append(row['Goles Visita'])
                goles_1T.append(row['Goles 1T Visita'])
                goles_2T.append(row['Goles 2T Visita'])
                corners.append(row['Corners Visita'])
                amarillas.append(row['Amarillas Visita'])
                rojas.append(row['Rojas Visita'])

        return {
            "Goles": round(sum(goles) / len(goles), 2) if goles else 0,
            "Goles 1T": round(sum(goles_1T) / len(goles_1T), 2) if goles_1T else 0,
            "Goles 2T": round(sum(goles_2T) / len(goles_2T), 2) if goles_2T else 0,
            "Corners": round(sum(corners) / len(corners), 2) if corners else 0,
            "Amarillas": round(sum(amarillas) / len(amarillas), 2) if amarillas else 0,
            "Rojas": round(sum(rojas) / len(rojas), 2) if rojas else 0,
        }

    stats_local = calcular_estadisticas(ultimos_5_local, equipo_local)
    stats_visita = calcular_estadisticas(ultimos_5_visita, equipo_visita)

    return {
        "Local (últimos 5)": stats_local,
        "Visita (últimos 5)": stats_visita
    }

# ---------------------------------------
# NUEVAS FUNCIONES PROBABILÍSTICAS (POISSON)
# ---------------------------------------
import math

def calcular_distribucion_poisson(media_goles, max_goles=5):
    distribucion = {}
    acumulado = 0
    for k in range(0, max_goles):
        prob = (math.exp(-media_goles) * media_goles**k) / math.factorial(k)
        distribucion[f"{k} goles"] = round(prob * 100, 2)
        acumulado += prob
    distribucion[f"{max_goles}+ goles"] = round((1 - acumulado) * 100, 2)
    return distribucion

def calcular_probabilidades_escenarios(distribucion):
    probabilidades = {
        "+1.5 goles": round(sum([v for k, v in distribucion.items()
                                 if k.split()[0].isdigit() and int(k.split()[0]) >= 2]), 2),
        "+2.5 goles": round(sum([v for k, v in distribucion.items()
                                 if k.split()[0].isdigit() and int(k.split()[0]) >= 3]), 2),
        "+3.5 goles": round(sum([v for k, v in distribucion.items()
                                 if k.split()[0].isdigit() and int(k.split()[0]) >= 4]), 2),
        "-2.5 goles": round(sum([v for k, v in distribucion.items()
                                 if k.split()[0].isdigit() and int(k.split()[0]) <= 2]), 2),
        "exactamente 2 goles": distribucion.get("2 goles", 0.0),
    }
    return probabilidades

def calcular_poisson_equipo(media):
    return [((math.exp(-media) * media**k) / math.factorial(k)) for k in range(20)]

def calcular_probabilidad_btts_poisson(media_local, media_visita, max_goles=10):
    poisson_local = calcular_poisson_equipo(media_local)
    poisson_visita = calcular_poisson_equipo(media_visita)
    
    p_btts = 0
    for i in range(1, max_goles + 1):
        for j in range(1, max_goles + 1):
            p_btts += poisson_local[i] * poisson_visita[j]
    
    return round(p_btts * 100, 2)


def calcular_resultado_probable(goles_local, goles_visita):
    poisson_local = calcular_poisson_equipo(goles_local)
    poisson_visita = calcular_poisson_equipo(goles_visita)
    p_local = 0
    p_empate = 0
    p_visita = 0
    for i in range(20):
        for j in range(20):
            prob = poisson_local[i] * poisson_visita[j]
            if i > j:
                p_local += prob
            elif i == j:
                p_empate += prob
            else:
                p_visita += prob
    total = p_local + p_empate + p_visita
    return {
        "Local": round(p_local / total * 100, 2),
        "Empate": round(p_empate / total * 100, 2),
        "Visita": round(p_visita / total * 100, 2),
    }

def predecir_partido(stats_local, stats_visita):
    media_total_goles = stats_local["goles"] + stats_visita["goles"]
    distribucion_goles = calcular_distribucion_poisson(media_total_goles)
    escenarios = calcular_probabilidades_escenarios(distribucion_goles)

    media_goles_1t = stats_local["goles_1T"] + stats_visita["goles_1T"]
    distribucion_goles_1t = calcular_distribucion_poisson(media_goles_1t)
    p_1g_1t = distribucion_goles_1t.get("1 goles", 0.0)

    p_btts = calcular_probabilidad_btts_poisson(stats_local["goles"], stats_visita["goles"])

    media_corners = stats_local["corners"] + stats_visita["corners"]
    corners_poisson = calcular_poisson_equipo(media_corners)
    p_7_5 = round(sum(corners_poisson[8:]) * 100, 2)
    p_8_5 = round(sum(corners_poisson[9:]) * 100, 2)
    p_9_5 = round(sum(corners_poisson[10:]) * 100, 2)

    resultado = calcular_resultado_probable(stats_local["goles"], stats_visita["goles"])
    ganador = max(resultado, key=resultado.get)
    
    # === PROBABILIDADES DE TARJETAS (usando Poisson) ===
    media_tarjetas = stats_local["amarillas"] + stats_local["rojas"] + stats_visita["amarillas"] + stats_visita["rojas"]
    tarjetas_poisson = calcular_poisson_equipo(media_tarjetas)

    prob_tarjetas = {
        "+3.5": round(sum(tarjetas_poisson[4:]) * 100, 2),
        "+4.5": round(sum(tarjetas_poisson[5:]) * 100, 2),
        "-4.5": round(sum(tarjetas_poisson[:5]) * 100, 2),
    }
    datos = {}

    mayor_prob = max(prob_tarjetas, key=prob_tarjetas.get)
    datos["tarjetas_sugerencia"] = f"Más de {mayor_prob}" if "+" in mayor_prob else "Menos de 4.5 tarjetas"

    if prob_tarjetas[mayor_prob] >= 70:
        datos["tarjetas_justificacion"] = f"Alta probabilidad de que se superen las {mayor_prob} tarjetas."
    elif prob_tarjetas[mayor_prob] >= 50:
        datos["tarjetas_justificacion"] = f"Escenario probable para {mayor_prob} tarjetas."
    else:
        datos["tarjetas_justificacion"] = f"Partido parejo en tarjetas, cuidado con {mayor_prob}."
    
    resultados = {
        "Distribución Goles Totales": distribucion_goles,
        "Escenarios Goles": escenarios,
        "Gol 1er Tiempo": {"1 gol": p_1g_1t},
        "Ambos Marcan": {"Probabilidad": p_btts},
        "Probabilidad Córners": {
            "+7.5": p_7_5,
            "+8.5": p_8_5,
            "+9.5": p_9_5
        },
        "Resultado": resultado,
        "Sugerencia Resultado": ganador,
        "Tarjetas": prob_tarjetas,
        "Sugerencia Tarjetas": datos["tarjetas_sugerencia"],
        "Justificacion Tarjetas": datos["tarjetas_justificacion"]
        }
    
    datos["Probabilidades"] = resultados

def generar_resumen_formateado(probabilidades: dict) -> dict:
    resumen = {}

    # Gol primer tiempo
    gol_1t = probabilidades.get("Gol 1er Tiempo", {}).get("1 gol", 0)
    recomendacion_1t = "Sí" if gol_1t >= 48 else "No"
    resumen["Gol 1er Tiempo"] = {
        "Probabilidad": round(gol_1t, 2),
        "Texto": f"Hay un {gol_1t:.1f}% de probabilidad de que se marque 1 gol en el primer tiempo.",
        "Recomendación": f"Recomendamos APOSTAR a 1 gol en el primer tiempo." if recomendacion_1t == "Sí" else "NO se recomienda apostar a 1 gol en el primer tiempo."
    }


    # Ambos marcan
    ambos = probabilidades.get("Ambos Marcan", {})
    prob_ambos = ambos.get("Probabilidad", 0)
    recomendacion = "Sí" if prob_ambos >= 55 else "No"
    resumen["Ambos Marcan"] = {
        "Probabilidad": round(prob_ambos, 2),
        "Texto": f"Hay un {prob_ambos:.1f}% de probabilidad de que ambos equipos anoten.",
        "Recomendación": f"Recomendamos APOSTAR a que {'ambos anotan' if recomendacion == 'Sí' else 'no anotan'}."
    }

    # Goles totales (mejor umbral según mayor probabilidad)
    escenarios = probabilidades.get("Escenarios Goles", {})
    if escenarios:
        mejor_umbral = max(escenarios, key=escenarios.get)
        mejor_valor = escenarios[mejor_umbral]
        resumen["Goles Totales"] = {
            "Umbral": mejor_umbral,
            "Probabilidad": round(mejor_valor, 2),
            "Texto": f"Hay un {mejor_valor:.1f}% de probabilidad de que se marquen {mejor_umbral} goles en el partido. Esta es la opción más probable."
        }

    # Córners
    corners = probabilidades.get("Probabilidad Córners", {})
    resumen["Córners"] = {
        "+7.5": round(corners.get("+7.5", 0), 2),
        "+8.5": round(corners.get("+8.5", 0), 2),
        "+9.5": round(corners.get("+9.5", 0), 2),
    }

    # Tarjetas
    tarjetas = probabilidades.get("Probabilidad Tarjetas", {})
    resumen["Tarjetas"] = {
        "+3.5": round(tarjetas.get("+3.5", 0), 2),
        "+4.5": round(tarjetas.get("+4.5", 0), 2),
        "-4.5": round(tarjetas.get("-4.5", 0), 2),
    }


    # Resultado
    resultado = probabilidades.get("Resultado", {})
    local = resultado.get("Local", 0)
    empate = resultado.get("Empate", 0)
    visita = resultado.get("Visita", 0)

    sugerencia = max([("Local", local), ("Empate", empate), ("Visita", visita)], key=lambda x: x[1])[0]
    resumen["Resultado"] = {
        "Local": round(local, 2),
        "Empate": round(empate, 2),
        "Visita": round(visita, 2),
        "Texto": f"Local: {local:.1f}%, Empate: {empate:.1f}%, Visita: {visita:.1f}%",
        "Sugerencia": f"Sugerimos apostar por: {sugerencia}"
    }

    return resumen

def sugerencia_resultado_segura(resultado: dict) -> str:
    local = resultado.get("Local", 0)
    visita = resultado.get("Visita", 0)

    if max(local, visita) >= 50:
        return "Local" if local > visita else "Visita"
    else:
        return "1X" if local > visita else "2X"


def formato_rockdata_41(datos):
    print("\nAnálisis probabilístico generado por RockData\n")
    print(f"⚽ Partido: {datos['partido']}")
    print(f"({datos['liga']})\n")

    print("⏱️ Probabilidad de Gol en el Primer Tiempo:")
    print(f"  Probabilidad: {datos['gol_1t_prob']}%")
    print(f"  Recomendación: {datos['gol_1t_texto']}\n")

    print("Ambos Equipos Marcan:")
    print(f"  Probabilidad: {datos['ambos_marcan_prob']}%")
    print(f"  Recomendación: {datos['ambos_marcan_texto']}")
    print(f"🔄 {datos['ambos_marcan_justificacion']}\n")

    print("Goles Totales:")
    print(f"  +1.5 goles: {datos['goles_prob_15']}%")
    print(f"  +2.5 goles: {datos['goles_prob_25']}%")

    # Comparación dinámica para la sugerencia
    if datos['goles_prob_15'] > datos['goles_prob_25']:
        sugerencia = 'Se recomienda apostar por +1.5 goles'
        texto = f"📌 Este escenario (+1.5 goles) tiene la mayor probabilidad que se concrete."
    else:
        sugerencia = 'Se recomienda apostar por +2.5 goles'
        texto = f"📌 Este escenario (+2.5 goles) tiene la mayor probabilidad que se concrete."

    print(f"  Recomendación: {sugerencia}")
    print(texto + "\n")


    print("Córners:")
    for k, v in datos['corners'].items():
        print(f"  {k}: {v}%")

    # Sugerencia dinámica según probabilidades
    corners_75 = datos['corners'].get('+7.5', 0)
    corners_85 = datos['corners'].get('+8.5', 0)

    if corners_85 >= 85:
        sugerencia_corners = "Más de 8.5 córners"
    elif corners_75 >= 80:
        sugerencia_corners = "Más de 7.5 córners"
    else:
        sugerencia_corners = "Evitar apuestas por córners altos"

    print(f"Sugerencia: {sugerencia_corners}")
    print(f"📏 {datos['corners_justificacion']}\n")
    

    print("Tarjetas:")
    for k, v in datos['tarjetas'].items():
        print(f"  {k}: {v}%")

    # === Sugerencia de tarjetas con recomendación clara ===
    # Probabilidades de tarjetas (distribución basada en Poisson)
    prob_35 = round(prob_tarjetas(3.5), 2)
    prob_45 = round(prob_tarjetas(4.5), 2)

    datos['tarjetas'] = {
        "+3.5": prob_35,
        "+4.5": prob_45,
        "-4.5": round(100 - prob_45, 2)
    }

    tarjetas = datos['tarjetas']
    t_35 = tarjetas.get("+3.5", 0)
    t_45 = tarjetas.get("+4.5", 0)

    if t_35 >= 65:
        datos['tarjetas_sugerencia'] = f"Se recomienda con alta seguridad apostar a +3.5 tarjetas"
    elif t_45 >= 60:
        datos['tarjetas_sugerencia'] = f"Se puede considerar +4.5 tarjetas si se busca algo más arriesgado"
    else:
        datos['tarjetas_sugerencia'] = f"No se recomienda apostar a tarjetas altas en este partido"

    datos['tarjetas_justificacion'] = f"Distribución: +3.5 = {t_35}%, +4.5 = {t_45}%"

    print(f"\nSugerencia: {datos['tarjetas_sugerencia']}")
    print(f"🟡 {datos['tarjetas_justificacion']}\n")
    print("Resultado del Partido:")
    print(f"  Local: {datos['resultado']['local']}%")
    print(f"  Empate: {datos['resultado']['empate']}%")
    print(f"  Visita: {datos['resultado']['visita']}%")
    print(f"\nPronóstico final: {datos['pronostico_final']}")
    print(f"📊 {datos['resultado_justificacion']}")


# Actualización lógica Gol 1T - Confirmado 29 julio