
import numpy as np
from scipy.stats import poisson

def calcular_probabilidad_goles_rango(df, tipo, umbral):
    """
    tipo: "menos" o "mas"
    umbral: número de goles (ej. 2.5)
    """
    promedio_local = df["Goles Local"].mean()
    promedio_visita = df["Goles Visita"].mean()
    media_total = promedio_local + promedio_visita

    if tipo == "menos":
        prob = poisson.cdf(int(umbral), media_total)
    elif tipo == "mas":
        prob = 1 - poisson.cdf(int(umbral), media_total)
    else:
        raise ValueError("Tipo debe ser 'menos' o 'mas'")

    return round(prob * 100, 2)


def calcular_probabilidad_goles(prom_local, prom_visita):
    prom_local = max(prom_local, 0.01)
    prom_visita = max(prom_visita, 0.01)
    media_total = prom_local + prom_visita
    prob_1_5 = round(1 - poisson.cdf(1, media_total), 2) * 100
    prob_2_5 = round(1 - poisson.cdf(2, media_total), 2) * 100
    return {
        "+1.5": prob_1_5,
        "+2.5": prob_2_5
    }

def calcular_probabilidad_ambos_marcan(prom_local, prom_visita):
    prom_local = max(prom_local, 0.01)
    prom_visita = max(prom_visita, 0.01)
    p_local_anota = 1 - poisson.pmf(0, prom_local)
    p_visita_anota = 1 - poisson.pmf(0, prom_visita)
    prob_ambos = round(p_local_anota * p_visita_anota, 2) * 100
    return {
        "Probabilidad": prob_ambos
    }

def calcular_probabilidad_gol_1t(prom_local_1t, prom_visita_1t):
    prom_local_1t = max(prom_local_1t, 0.01)
    prom_visita_1t = max(prom_visita_1t, 0.01)
    media_1t = prom_local_1t + prom_visita_1t
    prob_1_gol = round(1 - poisson.pmf(0, media_1t), 2) * 100
    return {"1 gol": prob_1_gol}

def calcular_probabilidad_corners(prom_local, prom_visita):
    prom_local = max(prom_local, 0.01)
    prom_visita = max(prom_visita, 0.01)
    media_corners = prom_local + prom_visita
    prob_7_5 = round(1 - poisson.cdf(7, media_corners), 2) * 100
    prob_8_5 = round(1 - poisson.cdf(8, media_corners), 2) * 100
    prob_9_5 = round(1 - poisson.cdf(9, media_corners), 2) * 100
    return {
        "+7.5": prob_7_5,
        "+8.5": prob_8_5,
        "+9.5": prob_9_5
    }

def calcular_probabilidad_tarjetas(tarj_local, tarj_visita):
    media_tarj = tarj_local + tarj_visita
    return {
        "+3.5": round(100 - poisson.cdf(3, media_tarj) * 100, 2),
        "+4.5": round(100 - poisson.cdf(4, media_tarj) * 100, 2),
        "-4.5": round(poisson.cdf(4, media_tarj) * 100, 2)
    }

def calcular_resultado_final(prob_local, prob_visita):
    total = prob_local + prob_visita
    if total == 0:
        return {"Local": 0.0, "Empate": 100.0, "Visita": 0.0}
    empate = round(100 - ((prob_local / total) * 100 + (prob_visita / total) * 100), 2)
    local = round((prob_local / (total + 0.0001)) * 100, 2)
    visita = round((prob_visita / (total + 0.0001)) * 100, 2)
    return {"Local": local, "Empate": empate, "Visita": visita}

def generar_apuesta_segura(prob_goles, prob_resultado):
    recomendacion = None
    motivo = ""
    if prob_goles["+1.5"] >= 75 and prob_resultado["Local"] >= 50:
        recomendacion = "1 + Más de 1.5 goles"
        motivo = "Alta probabilidad de victoria local con más de 1.5 goles."
    elif prob_goles["+1.5"] >= 75 and prob_resultado["Visita"] >= 50:
        recomendacion = "2 + Más de 1.5 goles"
        motivo = "Alta probabilidad de victoria visitante con más de 1.5 goles."
    elif prob_goles["+1.5"] >= 70 and prob_resultado["Local"] >= 45:
        recomendacion = "1X + Más de 1.5 goles"
        motivo = "Alta probabilidad de que el local no pierda y se marquen goles."
    elif prob_goles["+1.5"] >= 70 and prob_resultado["Visita"] >= 45:
        recomendacion = "X2 + Más de 1.5 goles"
        motivo = "Alta probabilidad de que la visita no pierda y se marquen goles."
    return {
        "Combinación": recomendacion,
        "Motivo": motivo if recomendacion else "No se encontró una combinación segura de goles + resultado."
    }

def generar_sugerencia_corners(probabilidades):
    # ejemplo de lógica (ajusta según sea tu real implementación)
    if probabilidades.get('+8.5', 0) >= 85:
        return "Más de 8.5 córners"
    elif probabilidades.get('+7.5', 0) >= 80:
        return "Más de 7.5 córners"
    else:
        return "Evitar apuestas por córners altos"

