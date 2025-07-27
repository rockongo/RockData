# probabilidades.py
# Módulo RockData: Cálculo de probabilidades bayesianas simples para goles, tarjetas y córners

import pandas as pd

def calcular_probabilidad_goles(df, tipo: str, umbral: float) -> float:
    if 'Goles Local' not in df.columns or 'Goles Visita' not in df.columns:
        raise ValueError("Faltan columnas de goles en el DataFrame.")

    df = df[['Goles Local', 'Goles Visita']].dropna()
    df['Goles Totales'] = df['Goles Local'] + df['Goles Visita']

    if tipo == "menos":
        prob = (df['Goles Totales'] < umbral).mean() * 100
    elif tipo == "mas":
        prob = (df['Goles Totales'] > umbral).mean() * 100
    elif tipo == "exacto":
        if not umbral.is_integer():
            raise ValueError("Para 'exacto', el umbral debe ser entero.")
        prob = (df['Goles Totales'] == int(umbral)).mean() * 100
    else:
        raise ValueError("Tipo debe ser 'menos', 'mas' o 'exacto'.")

    return round(prob, 2)

def calcular_probabilidad_corners(df, tipo: str, umbral: float) -> float:
    if 'Corners Local' not in df.columns or 'Corners Visita' not in df.columns:
        raise ValueError("Faltan columnas de córners en el DataFrame.")

    df = df[['Corners Local', 'Corners Visita']].dropna()
    df['Córners Totales'] = df['Corners Local'] + df['Corners Visita']

    if tipo == "menos":
        prob = (df['Córners Totales'] < umbral).mean() * 100
    elif tipo == "mas":
        prob = (df['Córners Totales'] > umbral).mean() * 100
    elif tipo == "exacto":
        if not umbral.is_integer():
            raise ValueError("Para 'exacto', el umbral debe ser entero.")
        prob = (df['Córners Totales'] == int(umbral)).mean() * 100
    else:
        raise ValueError("Tipo debe ser 'menos', 'mas' o 'exacto'.")

    return round(prob, 2)

def calcular_probabilidad_tarjetas(df, tipo: str, umbral: float) -> float:
    columnas_tarjetas = ['Amarillas Local', 'Amarillas Visita', 'Rojas Local', 'Rojas Visita']
    if not all(col in df.columns for col in columnas_tarjetas):
        raise ValueError("Faltan columnas de tarjetas en el DataFrame.")

    df = df[columnas_tarjetas].dropna()
    df['Tarjetas Totales'] = (
        df['Amarillas Local'] + df['Amarillas Visita'] +
        df['Rojas Local'] + df['Rojas Visita']
    )

    if tipo == "menos":
        prob = (df['Tarjetas Totales'] < umbral).mean() * 100
    elif tipo == "mas":
        prob = (df['Tarjetas Totales'] > umbral).mean() * 100
    elif tipo == "exacto":
        if not umbral.is_integer():
            raise ValueError("Para 'exacto', el umbral debe ser entero.")
        prob = (df['Tarjetas Totales'] == int(umbral)).mean() * 100
    else:
        raise ValueError("Tipo debe ser 'menos', 'mas' o 'exacto'.")

    return round(prob, 2)
