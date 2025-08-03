def filtrar_partidos(df, equipo):
    return df[(df['Local'] == equipo) | (df['Visita'] == equipo)]
