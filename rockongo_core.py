
from funciones_estadisticas import filtrar_partidos
import scipy.stats
import pandas as pd
import os
import ast


from probabilidades import (
    calcular_probabilidad_goles,
    calcular_probabilidad_corners,
    calcular_probabilidad_tarjetas,
    calcular_probabilidad_gol_1t,
    calcular_probabilidad_ambos_marcan,
    calcular_probabilidad_goles_rango,
    generar_sugerencia_corners
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
        print("📊 Columnas df_local:", df_local.columns.tolist())
        print("📊 Columnas df_visita:", df_visita.columns.tolist())
        print("📊 Primeras filas df_local:")
        print(df_local.head())
        print("📊 Primeras filas df_visita:")
        print(df_visita.head())       

        df_partido = pd.concat([df_local, df_visita])

        local_partidos = filtrar_partidos(df, equipo_local)
        visita_partidos = filtrar_partidos(df, equipo_visita)

        promedios_local = calcular_promedios(local_partidos, "Local")
        promedios_visita = calcular_promedios(visita_partidos, "Visita")
        if promedios_local is None or promedios_visita is None:
            raise ValueError("No se pudieron calcular los promedios de uno o ambos equipos.")

        stats_local_data = {
            "Corners": promedios_local.get("corners", 0),
            "Tarjetas": promedios_local.get("amarillas", 0) + promedios_local.get("rojas", 0),
            "Amarillas": promedios_local.get("amarillas", 0)
        }
        stats_visita_data = {
            "Corners": promedios_visita.get("corners", 0),
            "Tarjetas": promedios_visita.get("amarillas", 0) + promedios_visita.get("rojas", 0),
            "Amarillas": promedios_visita.get("amarillas", 0)
        }


        prob_goles_menos_25 = calcular_probabilidad_goles_rango(df_partido, "menos", 2.5)
        
        prob_tarjetas_mas_4_5 = calcular_probabilidad_tarjetas(stats_local_data["Amarillas"], stats_visita_data["Amarillas"])

    except Exception as e:
        prob_goles_menos_25 = prob_corners_mas_9_5 = prob_tarjetas_mas_4_5 = None
        print("Error al calcular probabilidades:", e)
    # --------------------------
    # NUEVO BLOQUE PROBABILÍSTICO
    # --------------------------

    promedios_local = df_local.mean(numeric_only=True).to_dict()
    promedios_visita = df_visita.mean(numeric_only=True).to_dict()

    stats_local = promedios_local
    stats_visita = promedios_visita

    print("🔍 promedios_local:", promedios_local)
    print("🔍 promedios_visita:", promedios_visita)

    stats_local_data = {
        "Goles": float(stats_local.get("Goles Local", 0)),
        "Goles 1T": float(stats_local.get("Goles 1T Local", 0)),
        "Goles 2T": float(stats_local.get("Goles 2T Local", 0)),
        "Corners": float(stats_local.get("Corners Local", 0)),
        "Amarillas": float(stats_local.get("Amarillas Local", 0)),
        "Rojas": float(stats_local.get("Rojas Local", 0)),
    }

    stats_visita_data = {
        "Goles": float(stats_visita.get("Goles Visita", 0)),
        "Goles 1T": float(stats_visita.get("Goles 1T Visita", 0)),
        "Goles 2T": float(stats_visita.get("Goles 2T Visita", 0)),
        "Corners": float(stats_visita.get("Corners Visita", 0)),
        "Amarillas": float(stats_visita.get("Amarillas Visita", 0)),
        "Rojas": float(stats_visita.get("Rojas Visita", 0)),
    }

    # ✅ Calcula forma reciente antes de predecir
    forma_local = simulacion_forma_reciente(df, equipo_local, equipo_local)["Local (últimos 5)"]
    forma_visita = simulacion_forma_reciente(df, equipo_visita, equipo_visita)["Local (últimos 5)"]


    # ✅ Agrega al diccionario antes de pasar a predecir
    stats_local_data["forma_victorias"] = forma_local
    stats_visita_data["forma_victorias"] = forma_visita

    forma_reciente = simulacion_forma_reciente(df, equipo_local, equipo_visita)
    escenarios_goles = calcular_probabilidad_goles(
        stats_local_data["Goles"], stats_visita_data["Goles"]
    )
    prob_goles = escenarios_goles
    prob_1t = calcular_probabilidad_gol_1t(
        stats_local_data["Goles 1T"], stats_visita_data["Goles 1T"]
    )
    valor_prob_1t = prob_1t.get("1 gol", 0)
    
    if valor_prob_1t >= 35:
        gol_1t_texto = "Probabilidad alta de que se abra el marcador antes del descanso."
    else:
        gol_1t_texto = "No se anticipa un primer tiempo muy activo."

    
    ambos_marcan = calcular_probabilidad_ambos_marcan(
        stats_local_data["Goles"], stats_visita_data["Goles"]
    )
    ambos_justificacion = f"{equipo_local} promedia {stats_local_data['Goles']:.2f} goles y {equipo_visita} recibe {stats_visita_data['Goles']:.2f}."

    prob_corners_raw = calcular_probabilidad_corners(stats_local_data["Corners"], stats_visita_data["Corners"])
    prob_corners = {
        "+7.5": round(prob_corners_raw["+7.5"], 1),
        "+8.5": round(prob_corners_raw["+8.5"], 1),
        "+9.5": round(prob_corners_raw["+9.5"], 1)
    }
    
    corners_justificacion = "Probabilidad basada en el promedio combinado de córners del partido."

    # --- TARJETAS ---
    media_tarjetas_local = stats_local_data["Amarillas"] + stats_local_data["Rojas"]
    media_tarjetas_visita = stats_visita_data["Amarillas"] + stats_visita_data["Rojas"]
    total_tarjetas_esperadas = media_tarjetas_local + media_tarjetas_visita

    prob_tarjetas = {
        "+3.5": float(scipy.stats.poisson.sf(3, total_tarjetas_esperadas)) * 100,
        "+4.5": float(scipy.stats.poisson.sf(4, total_tarjetas_esperadas)) * 100,
    }

    # Redondear decimales
    for k in prob_tarjetas:
        prob_tarjetas[k] = round(prob_tarjetas[k], 1)

    # Sugerencia inteligente
    if prob_tarjetas["+4.5"] >= 80:
        sugerencia_tarjetas = "Más de 4.5 tarjetas"
    elif prob_tarjetas["+3.5"] >= 75:
        sugerencia_tarjetas = "Más de 3.5 tarjetas"
    else:
        sugerencia_tarjetas = "Evitar apuestas por tarjetas altas."

    # Agregar al resultado
    prob_tarjetas["Sugerencia"] = sugerencia_tarjetas

    print("🔍 prob_tarjetas:", prob_tarjetas, type(prob_tarjetas))
    print("✅ Justificación generada:", ambos_justificacion)
    sugerencia_corners = generar_sugerencia_corners(prob_corners)

    escenarios = eval(escenarios_goles) if isinstance(escenarios_goles, str) else escenarios_goles

    resultado_probabilistico = {
        "Gol 1er Tiempo": {
            "1 gol": float(prob_1t.get("1 gol", 0)),
            "Texto": gol_1t_texto
        },
        "Ambos Marcan": {
            "Probabilidad": ambos_marcan.get("Probabilidad", 0),
            "Justificacion": ambos_justificacion
        },
        "Goles": {
            "+1.5": float(escenarios.get("+1.5", 0)),
            "+2.5": float(escenarios.get("+2.5", 0)),
            
        },
        "Córners": {
            "+7.5": float(prob_corners.get("+7.5", 0)),
            "+8.5": float(prob_corners.get("+8.5", 0)),
            "+9.5": float(prob_corners.get("+9.5", 0)),
            "Sugerencia": sugerencia_corners,
            "Justificacion": corners_justificacion,
            
        },
        "Tarjetas": {
            "+3.5": float(prob_tarjetas.get("+3.5", 0)),
            "+4.5": float(prob_tarjetas.get("+4.5", 0)),
            "Sugerencia": sugerencia_tarjetas
        }
    }
    pronostico_final = "Sin sugerencia disponible"
    resultado_probabilistico["pronostico_final"] = pronostico_final

    try:
        print("🎯 resultado_probabilistico:", resultado_probabilistico["Gol 1er Tiempo"].get("1 gol", 0), type(resultado_probabilistico["Gol 1er Tiempo"].get("1 gol", 0)))
    except Exception as e:
        print("⚠️ Error al acceder a 'Gol 1er Tiempo':", e)
        return None

# === Análisis textual de Gol en Primer Tiempo ===
    gol_1t_data = resultado_probabilistico.get("Gol 1er Tiempo", {})
    gol_1t_prob = gol_1t_data.get("1 gol", None)

    if gol_1t_prob is None or not isinstance(gol_1t_prob, (int, float)):
        print("⚠️ Error: '1 gol' no encontrado o no es número")
        return None

    if gol_1t_prob >= 60:
        gol_1t_texto = "Alta probabilidad de que se abra el marcador antes del descanso."
    elif 45 <= gol_1t_prob < 60:
        gol_1t_texto = "Hay chances razonables de gol antes del descanso, aunque no está garantizado."
    else:
        gol_1t_texto = "No se anticipa un primer tiempo muy activo."

    sugerencia_tarjetas = "Evitar apuestas por tarjetas altas." if prob_tarjetas.get("+4.5", 0) < 70 else "Más de 4.5 tarjetas recomendadas."
        

    try:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df_filtrado = df[
            ((df['Local'] == equipo_local) & (df['Visita'] == equipo_visita)) |
            ((df['Local'] == equipo_visita) & (df['Visita'] == equipo_local))
        ].dropna(subset=["Fecha"]).sort_values("Fecha")

        if not df_filtrado.empty:
            ultima_fila = df_filtrado.iloc[-1]
            fecha_valida = pd.to_datetime(ultima_fila["Fecha"], errors='coerce')
            fecha_str = str(fecha_valida.date()) if not pd.isnull(fecha_valida) else "Fecha desconocida"
            nombre_partido = f"{fecha_str} | {equipo_local} vs {equipo_visita}"
        else:
            nombre_partido = f"{equipo_local} vs {equipo_visita}"

    except Exception as e:
        print(f"⚠️ Error al determinar fecha del partido: {e}")
        nombre_partido = f"{equipo_local} vs {equipo_visita}"


    return {
        "Equipo Local": equipo_local,
        "Equipo Visita": equipo_visita,
        "Nombre Partido": nombre_partido,
        "Promedios Local": {
            "Goles": stats_local_data["Goles"],
            "Goles 1T": stats_local_data["Goles 1T"],
            "Corners": stats_local_data["Corners"],
            "Tarjetas": stats_local_data["Amarillas"] + stats_local_data["Rojas"]
        },
        "Promedios Visita": {
            "Goles": stats_visita_data["Goles"],
            "Goles 1T": stats_visita_data["Goles 1T"],
            "Corners": stats_visita_data["Corners"],
            "Tarjetas": stats_visita_data["Amarillas"] + stats_visita_data["Rojas"]
        },
        "Estadísticas Totales": {
            "Goles Totales": stats_local_data["Goles"] + stats_visita_data["Goles"],
            "Corners Totales": stats_local_data["Corners"] + stats_visita_data["Corners"],
            "Tarjetas Totales": (
                 stats_local_data["Amarillas"] + stats_local_data["Rojas"] +
                 stats_visita_data["Amarillas"] + stats_visita_data["Rojas"]
            )
        },

        "Probabilidades": resultado_probabilistico,
        "Gol 1T": {
            "Probabilidad": float(gol_1t_prob),
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

def calcular_escenarios_goles(distribucion_goles):
    escenarios = {}

    if distribucion_goles:
        p_menos_15 = 0
        p_mas_15 = 0
        p_mas_25 = 0

        for marcador, probabilidad in distribucion_goles.items():
            if "-" in marcador:
                try:
                    goles_local, goles_visita = map(int, marcador.split("-"))
                    total_goles = goles_local + goles_visita

                    if total_goles < 2:
                        p_menos_15 += probabilidad
                    if total_goles >= 2:
                        p_mas_15 += probabilidad
                    if total_goles >= 3:
                        p_mas_25 += probabilidad
                except ValueError:
                    continue  # ignora claves mal formateadas

        escenarios["+1.5"] = round(p_mas_15 * 100, 2)
        escenarios["+2.5"] = round(p_mas_25 * 100, 2)
        escenarios["-1.5"] = round(p_menos_15 * 100, 2)

    return escenarios

def predecir_partido(stats_local, stats_visita, forma_reciente):
    # === Validación de claves ===
    claves_necesarias = ["Goles", "Goles 1T", "Corners", "Amarillas", "Rojas"]
    for clave in claves_necesarias:
        if clave not in stats_local or clave not in stats_visita:
            raise ValueError(f"Falta la clave '{clave}' en stats_local o stats_visita.")

    # === GOL 1ER TIEMPO ===
    media_goles_1t = stats_local["Goles 1T"] + stats_visita["Goles 1T"]
    distribucion_goles_1t = calcular_distribucion_poisson(media_goles_1t)
    p_1g_1t = distribucion_goles_1t.get("1 goles", 0.0)

    # === AMBOS MARCAN ===
    p_btts = calcular_probabilidad_btts_poisson(stats_local["Goles"], stats_visita["Goles"])

    # === CÓRNERS ===
    media_corners = stats_local["Corners"] + stats_visita["Corners"]
    corners_poisson = calcular_poisson_equipo(media_corners)
    p_7_5 = round(sum(corners_poisson[8:]) * 100, 2)
    p_8_5 = round(sum(corners_poisson[9:]) * 100, 2)
    p_9_5 = round(sum(corners_poisson[10:]) * 100, 2)

    # === GOLES TOTALES ===
    distribucion_goles = calcular_distribucion_poisson(stats_local["Goles"] + stats_visita["Goles"])
    escenarios = calcular_escenarios_goles(distribucion_goles)

    # === RESULTADO FINAL ===
    resultado = calcular_resultado_probable(stats_local["Goles"], stats_visita["Goles"])
    ganador = max(resultado, key=resultado.get)
    max_prob = resultado[ganador]

    if max_prob >= 55:
        sugerencia_resultado = ganador
    elif 45 <= max_prob < 55:
        sugerencia_resultado = "1X" if ganador == "Local" else "2X" if ganador == "Visita" else "Empate"
    else:
        sugerencia_resultado = "Empate"

    # === JUSTIFICACIÓN DEL RESULTADO ===
    if sugerencia_resultado == "Local":
        texto_justificacion = "El equipo local muestra mejor promedio ofensivo y defensivo. Además, su probabilidad de victoria supera el 55%, justificando la apuesta directa por su triunfo."
    elif sugerencia_resultado == "Visita":
        texto_justificacion = "El equipo visitante destaca sobre el local tanto en goles anotados como en solidez defensiva. La probabilidad supera el 55%, lo que respalda su victoria."
    elif sugerencia_resultado == "1X":
        texto_justificacion = "El equipo local tiene ventaja ligera, pero sin una dominancia clara. La doble oportunidad a su favor ofrece mayor seguridad."
    elif sugerencia_resultado == "2X":
        texto_justificacion = "El equipo visitante lidera levemente en promedios, aunque sin gran diferencia. Por eso se sugiere asegurar con doble oportunidad a su favor."
    else:
        texto_justificacion = "Ambos equipos están muy parejos en estadísticas. Ninguno supera el 45% de probabilidad, lo que sugiere un escenario de empate."

    # === TARJETAS (usando Poisson) ===
    media_tarjetas = stats_local["Amarillas"] + stats_local["Rojas"] + stats_visita["Amarillas"] + stats_visita["Rojas"]
    tarjetas_poisson = calcular_poisson_equipo(media_tarjetas)
    prob_tarjetas = {
        "+3.5": round(sum(tarjetas_poisson[4:]) * 100, 2),
        "+4.5": round(sum(tarjetas_poisson[5:]) * 100, 2),
        "-4.5": round(sum(tarjetas_poisson[:5]) * 100, 2),
    }
    mayor_prob = max(prob_tarjetas, key=prob_tarjetas.get)
    sugerencia_tarjetas = f"Más de {mayor_prob}" if "+" in mayor_prob else "Menos de 4.5 tarjetas"
    if prob_tarjetas[mayor_prob] >= 70:
        justificacion_tarjetas = f"Alta probabilidad de que se superen las {mayor_prob} tarjetas."
    elif prob_tarjetas[mayor_prob] >= 50:
        justificacion_tarjetas = f"Escenario probable para {mayor_prob} tarjetas."
    else:
        justificacion_tarjetas = f"Partido parejo en tarjetas, cuidado con {mayor_prob}."

    
    # === APUESTA SEGURA COMBINADA ===
    prob_mas_25 = escenarios.get("+2.5", 0)
    prob_mas_15 = escenarios.get("+1.5", 0)
    prob_menos_35 = escenarios.get("-3.5", 0)
    promedio_goles_total = (stats_local["Goles"] + stats_visita["Goles"]) / 2
    forma_local_victorias = forma_reciente["Local (últimos 5)"]["Goles"]
    forma_visita_victorias = forma_reciente["Visita (últimos 5)"]["Goles"]

    apuesta_segura = generar_apuesta_segura(
        resultado["Local"],
        resultado["Empate"],
        resultado["Visita"],
        prob_mas_25,
        prob_mas_15,
        prob_menos_35,
        promedio_goles_total,
        forma_local_victorias,
        forma_visita_victorias
    )


    # === RETORNO FINAL ===
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
        "Sugerencia Resultado": sugerencia_resultado,
        "Justificacion Resultado": texto_justificacion,
        "Tarjetas": prob_tarjetas,
        "Sugerencia Tarjetas": sugerencia_tarjetas,
        "Justificacion Tarjetas": justificacion_tarjetas,
        "Apuesta Segura Recomendada": apuesta_segura
    }

    return resultados

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
    print(f"\n📊 Pronóstico Final: {datos.get('pronostico_final', 'Sin sugerencia disponible')}")
    print(f"📊 {datos['resultado_justificacion']}")

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
        "-3.5 goles": round(sum([v for k, v in distribucion.items()
                                 if k.split()[0].isdigit() and int(k.split()[0]) <= 3]), 2),
        "exactamente 2 goles": distribucion.get("2 goles", 0.0),
    }
    return probabilidades


def generar_apuesta_segura(prob_local, prob_empate, prob_visita,
                            prob_mas_25, prob_mas_15, prob_menos_35,
                            promedio_goles_total,
                            forma_local_victorias, forma_visita_victorias):
    """
    Devuelve una combinación segura de 2 selecciones tipo BetBuilder.
    """
    sugerencias = []

    # Primera parte: Resultado del partido
    if prob_local > 50:
        sugerencias.append(("Victoria Local", prob_local))
    elif prob_visita > 50:
        sugerencias.append(("Victoria Visita", prob_visita))
    elif forma_local_victorias >= 3 and forma_visita_victorias <= 1:
        sugerencias.append(("1X", max(prob_local, prob_empate)))
    elif forma_visita_victorias >= 3 and forma_local_victorias <= 1:
        sugerencias.append(("2X", max(prob_visita, prob_empate)))
    else:
        if prob_local > prob_visita:
            sugerencias.append(("1X", max(prob_local, prob_empate)))
        else:
            sugerencias.append(("2X", max(prob_visita, prob_empate)))

    # Segunda parte: Goles
    if prob_menos_35 >= 70:
        sugerencias.append(("Menos de 3.5 goles", prob_menos_35))
    elif prob_mas_15 >= 75 and promedio_goles_total > 2:
        sugerencias.append(("Más de 1.5 goles", prob_mas_15))
    else:
        return {
            "Combinación": None,
            "Motivo": "No se encontró una combinación segura de goles + resultado."
        }

    # Calcular probabilidad conjunta
    prob_final = (sugerencias[0][1] / 100) * (sugerencias[1][1] / 100)
    cuota_justa = round(1 / prob_final, 2)

    return {
        "Selección 1": sugerencias[0][0],
        "Selección 2": sugerencias[1][0],
        "Probabilidad conjunta": round(prob_final * 100, 2),
        "Cuota justa estimada": cuota_justa
    }

def calcular_probabilidad_resultado_partido(stats_local, stats_visita):
    """Calcula la probabilidad de 1, X, 2 según la media de goles esperados por equipo"""
    from scipy.stats import poisson

    media_local = stats_local['goles']
    media_visita = stats_visita['goles']

    max_goles = 6
    prob_local, prob_empate, prob_visita = 0, 0, 0

    for gl in range(0, max_goles + 1):
        for gv in range(0, max_goles + 1):
            p = poisson.pmf(gl, media_local) * poisson.pmf(gv, media_visita)
            if gl > gv:
                prob_local += p
            elif gl == gv:
                prob_empate += p
            else:
                prob_visita += p

    total = prob_local + prob_empate + prob_visita
    prob_local = round(prob_local / total * 100, 1)
    prob_empate = round(prob_empate / total * 100, 1)
    prob_visita = round(prob_visita / total * 100, 1)

    if max(prob_local, prob_empate, prob_visita) > 50:
        if prob_local > prob_empate and prob_local > prob_visita:
            sugerencia = '1'
        elif prob_visita > prob_local and prob_visita > prob_empate:
            sugerencia = '2'
        else:
            sugerencia = 'X'
    else:
        if prob_local > prob_visita:
            sugerencia = '1X'
        else:
            sugerencia = '2X'

    return {
        "Local": prob_local,
        "Empate": prob_empate,
        "Visita": prob_visita,
        "Sugerencia": sugerencia
    }

