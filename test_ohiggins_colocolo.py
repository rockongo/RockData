from rockongo_core import formato_rockdata_41

datos_para_formato = {
    'partido': "O'Higgins vs Colo Colo",
    'liga': "Primera A de Chile, Jornada X",
    'gol_1t_prob': 33.4,
    'gol_1t_texto': 'NO se recomienda apostar a 1 gol en el primer tiempo.',
    'ambos_marcan_prob': 56.8,
    'ambos_marcan_texto': 'Recomendamos APOSTAR a que ambos anotan.',
    'ambos_marcan_justificacion': "O'Higgins marca en promedio 1.2 y Colo Colo 1.9 goles por partido.",
    'goles_prob_15': 64.2,
    'goles_prob_25': 57.6,


    'corners': {
        '+7.5': 89.5,
        '+8.5': 78.2,
        '+9.5': 66.9
    },
    'corners_sugerencia': 'Más de 8.5 córners',
    'corners_justificacion': "O'Higgins genera 4.6 y Colo Colo 5.1. Total esperado: 9.7.",
    'tarjetas': {
        '+3.5': 82.4,
        '+4.5': 68.9,
        '-4.5': 31.1
    },
    'tarjetas_sugerencia': 'Más de 3.5 tarjetas',
    'tarjetas_justificacion': "O'Higgins suma 2.0 y Colo Colo 2.3 tarjetas por partido.",
    'resultado': {
        'local': 27.6,
        'empate': 25.8,
        'visita': 46.6
    },
    'pronostico_final': 'Colo Colo',  # este valor ya no se usa directamente, lo calcula la nueva lógica
    'resultado_justificacion': "O'Higgins promedia 1.2 goles. Colo Colo promedia 1.9 goles.",
    'forma_reciente': "O'Higgins anota 0.5 en 1T. Colo Colo anota 0.9 en 1T."
}

formato_rockdata_41(datos_para_formato)

