
import numpy as np
from scipy.stats import poisson

def calcular_probabilidad_goles(prom_local, prom_visita):
    media_total = prom_local + prom_visita
    distribucion = {f"{i} goles": round(poisson.pmf(i, media_total) * 100, 2) for i in range(5)}
    distribucion["5+ goles"] = round(100 - sum(distribucion.values()), 2)

    escenarios = {
        "+1.5": round(100 - poisson.cdf(1, media_total) * 100, 2),
        "+2.5": round(100 - poisson.cdf(2, media_total) * 100, 2),
        "-1.5": round(poisson.cdf(1, media_total) * 100, 2)
    }

    return {
        "Distribución Goles Totales": distribucion,
        "Escenarios Goles": escenarios
    }

def calcular_probabilidad_gol_1t(prom_1t_local, prom_1t_visita):
    media_1t = prom_1t_local + prom_1t_visita
    prob_1_gol = round(100 - poisson.pmf(0, media_1t) * 100, 2)
    return {"1 gol": prob_1_gol}

def calcular_probabilidad_ambos_marcan(prom_local, prom_visita):
    prob_local = 1 - poisson.pmf(0, prom_local)
    prob_visita = 1 - poisson.pmf(0, prom_visita)
    prob_ambos = round(prob_local * prob_visita * 100, 2)
    return {"Probabilidad": prob_ambos}

def calcular_probabilidad_corners(corners_local, corners_visita):
    media_corners = corners_local + corners_visita
    return {
        "+7.5": round(100 - poisson.cdf(7, media_corners) * 100, 2),
        "+8.5": round(100 - poisson.cdf(8, media_corners) * 100, 2),
        "+9.5": round(100 - poisson.cdf(9, media_corners) * 100, 2),
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
