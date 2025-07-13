import pandas as pd
import os

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

    return {
        # Local
        "Goles Local": round(stats_local["goles"], 2),
        "Goles 1T Local": round(stats_local["goles_1T"], 2),
        "Goles 2T Local": round(stats_local["goles_2T"], 2),
        "Córners Local": round(stats_local["corners"], 2),
        "Amarillas Local": round(stats_local["amarillas"], 2),
        "Rojas Local": round(stats_local["rojas"], 2),

        # Visita
        "Goles Visita": round(stats_visita["goles"], 2),
        "Goles 1T Visita": round(stats_visita["goles_1T"], 2),
        "Goles 2T Visita": round(stats_visita["goles_2T"], 2),
        "Córners Visita": round(stats_visita["corners"], 2),
        "Amarillas Visita": round(stats_visita["amarillas"], 2),
        "Rojas Visita": round(stats_visita["rojas"], 2),

        # Totales y pronóstico
        "Goles Totales": round(stats_local["goles"] + stats_visita["goles"], 2),
        "Corners": round(stats_local["corners"] + stats_visita["corners"], 2),
        "Tarjetas Promedio": round(stats_local["amarillas"] + stats_visita["amarillas"], 2),
        "Rojas": round(stats_local["rojas"] + stats_visita["rojas"], 2),
        "Fortaleza Local": round(fort_local, 2),
        "Fortaleza Visita": round(fort_visita, 2),
        "Pronóstico": resultado,

        # Nuevas listas crudas para análisis
        "Lista Corners Local": corners_local_lista,
        "Lista Corners Visita": corners_visita_lista
    }


def predecir_partido(archivo_excel, equipo_local, equipo_visita):
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

def generar_sugerencias(goles, corners, amarillas, rojas):
    sugerencias = []

    ## ESCALA DE GOLES
    if goles >= 3.6:
        sugerencias.append("Más de 2.5 goles")
    elif 3.0 <= goles < 3.6:
        sugerencias.append("Más de 1.5 goles")
    elif 2.0 <= goles < 3.0:
        sugerencias.append("Ambos anotan o Más de 1.5 goles")
    elif 1.2 <= goles < 2.0:
        sugerencias.append("Menos de 2.5 goles")
    else:
        sugerencias.append("Menos de 1.5 goles")

    ## ESCALA DE CÓRNERS
    if corners >= 10.5:
        sugerencias.append("Más de 9.5 córners")
    elif 9.0 <= corners < 10.5:
        sugerencias.append("Más de 8.5 córners")
    elif 7.5 <= corners < 9.0:
        sugerencias.append("Más de 7.5 córners")
    elif 6.0 <= corners < 7.5:
        sugerencias.append("Menos de 8.5 córners")
    else:
        sugerencias.append("Menos de 7.5 córners")

    ## ESCALA DE TARJETAS (Amarillas + Rojas)
    total_tarjetas = amarillas + rojas
    if total_tarjetas >= 5.5:
        sugerencias.append("Más de 4.5 tarjetas")
    elif 4.0 <= total_tarjetas < 5.5:
        sugerencias.append("Más de 3.5 tarjetas")
    elif 3.0 <= total_tarjetas < 4.0:
        sugerencias.append("Más de 2.5 tarjetas")
    elif 2.0 <= total_tarjetas < 3.0:
        sugerencias.append("Menos de 3.5 tarjetas")
    else:
        sugerencias.append("Menos de 2.5 tarjetas")

    return sugerencias[:2]  # Solo 2 sugerencias más confiables

