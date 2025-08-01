import os
import pandas as pd
import requests
from datetime import datetime

API_KEY = "cb7db6deebmshd7772fb19f1a9e4p18e815jsn85b9be43cc23"
API_HOST = "api-football-v1.p.rapidapi.com"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

# === CONTADOR DE LLAMADAS SEGURAS ===
MAX_LLAMADAS_DIARIAS = 7000
contador_llamadas = 0

def llamada_api_segura(url, headers=None, params=None):
    global contador_llamadas
    if contador_llamadas >= MAX_LLAMADAS_DIARIAS:
        print("🚨 Límite diario de llamadas alcanzado. Deteniendo ejecución.")
        exit()
    response = requests.get(url, headers=headers, params=params)
    contador_llamadas += 1
    return response

# IDs y fechas límite por archivo
ligas_config = {
    "Liga_colombia_2025.xlsx": {"id": 239, "desde": "2025-07-24"},
    "Primera_A_2025.xlsx": {"id": 265, "desde": "2025-07-24"},
    "Primera_B_2025.xlsx": {"id": 266, "desde": "2025-07-24"},
    "Liga_bolivia_2025.xlsx": {"id": 344, "desde": "2025-07-24"},
    "Liga_ecuador_2025.xlsx": {"id": 242, "desde": "2025-07-24"},
    "Liga_MLS_2025.xlsx": {"id": 253, "desde": "2025-07-24"},
    "Liga_noruega_2025.xlsx": {"id": 103, "desde": "2025-07-24"},
    "Liga_peruana_2025.xlsx": {"id": 281, "desde": "2025-07-24"},
    "Liga_brasil_2025.xlsx": {"id": 71, "desde": "2025-07-24"},
    "Liga_brasil_B_2025.xlsx": {"id": 72, "desde": "2025-07-24"},
    "Liga_china_2025.xlsx": {"id": 169, "desde": "2025-07-24"},
    "Liga_finlandia_2025.xlsx": {"id": 244, "desde": "2025-07-24"},
    "Liga_mexico_2025.xlsx": {"id": 262, "desde": "2025-07-24"},
    "Liga_Suecia_2025.xlsx": {"id": 113, "desde": "2025-07-24"},
    "Liga_argentina_2025.xlsx": {"id": 128, "desde": "2025-07-22}",
}

# Ruta de los archivos Excel
RUTA_LIGAS = os.path.join(os.path.dirname(__file__), "Ligas")

# Obtener partidos de la API
def obtener_partidos(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"league": league_id, "season": 2025}
    res = llamada_api_segura(url, headers=headers, params=params)
    return res.json().get("response", [])

# Obtener estadísticas del partido
def get_stat(stats_data, team_name, stat_name):
    for team_stats in stats_data:
        if team_stats["team"]["name"] == team_name:
            for item in team_stats["statistics"]:
                if item["type"] == stat_name:
                    return item["value"]
    return 0

# Procesar cada archivo
for archivo, config in ligas_config.items():
    path_excel = os.path.join(RUTA_LIGAS, archivo)
    if not os.path.exists(path_excel):
        print(f"❌ No encontrado: {archivo}")
        continue

    print(f"\n📄 Revisando: {archivo}")
    df_existente = pd.read_excel(path_excel)
    fixture_ids_existentes = set(df_existente["Fixture ID"].fillna(0).astype(int))

    nuevos_partidos = []
    nuevas_filas = []

    for partido in obtener_partidos(config["id"]):
        fixture = partido["fixture"]
        fecha_str = fixture["date"]
        status = fixture["status"]["short"]

        if status != "FT":
            continue  # solo partidos terminados

        fecha_dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        fecha_txt = fecha_dt.strftime("%Y-%m-%d")

        if fecha_txt <= config["desde"]:
            continue  # antes de la fecha de corte

        fixture_id = fixture["id"]
        if fixture_id in fixture_ids_existentes:
            continue

        teams = partido["teams"]
        goals = partido["goals"]

        local = teams["home"]["name"]
        visita = teams["away"]["name"]
        goles_local = goals["home"] or 0
        goles_visita = goals["away"] or 0

        # Obtener estadísticas
        stats_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
        stats_params = {"fixture": fixture_id}
        r_stats = llamada_api_segura(stats_url, headers=headers, params=stats_params)
        stats_data = r_stats.json().get("response", [])

        corners_local = get_stat(stats_data, local, "Corner Kicks") or 0
        corners_visita = get_stat(stats_data, visita, "Corner Kicks") or 0
        amarillas_local = get_stat(stats_data, local, "Yellow Cards") or 0
        amarillas_visita = get_stat(stats_data, visita, "Yellow Cards") or 0
        rojas_local = get_stat(stats_data, local, "Red Cards") or 0
        rojas_visita = get_stat(stats_data, visita, "Red Cards") or 0
        posesion_local = get_stat(stats_data, local, "Ball Possession") or "0%"
        posesion_visita = get_stat(stats_data, visita, "Ball Possession") or "0%"

        goles_1t_local = fixture.get("score", {}).get("halftime", {}).get("home", 0) or 0
        goles_1t_visita = fixture.get("score", {}).get("halftime", {}).get("away", 0) or 0
        goles_2t_local = goles_local - goles_1t_local
        goles_2t_visita = goles_visita - goles_1t_visita

        fila = [
            fecha_txt, local, visita,
            goles_local, goles_visita,
            fixture_id,
            corners_local, corners_visita,
            amarillas_local, amarillas_visita,
            rojas_local, rojas_visita,
            goles_1t_local, goles_1t_visita,
            goles_2t_local, goles_2t_visita,
            posesion_local, posesion_visita
        ]

        nuevas_filas.append(fila)
        nuevos_partidos.append(partido)

    print(f"📌 Nuevos partidos detectados: {len(nuevas_filas)}")
    for p in nuevos_partidos[:5]:
        print(f"- {p['fixture']['date']} | {p['teams']['home']['name']} vs {p['teams']['away']['name']}")

    if nuevas_filas:
        columnas = [
            "Fecha", "Local", "Visita",
            "Goles Local", "Goles Visita", "Fixture ID",
            "Corners Local", "Corners Visita",
            "Amarillas Local", "Amarillas Visita",
            "Rojas Local", "Rojas Visita",
            "Goles 1T Local", "Goles 1T Visita",
            "Goles 2T Local", "Goles 2T Visita",
            "Posesión Local (%)", "Posesión Visita (%)"
        ]
        df_nuevos = pd.DataFrame(nuevas_filas, columns=columnas)
        df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        df_final.to_excel(path_excel, index=False)
        print(f"✅ {len(nuevas_filas)} partidos agregados a {archivo}")
    else:
        print("✅ No hay nuevos partidos para agregar.")
# === AGREGAR / ACTUALIZAR COLUMNA 'Resultado' ===
def agregar_resultado_a_filas_nuevas():
    for archivo in ligas_config:
        path_excel = os.path.join(RUTA_LIGAS, archivo)
        if not os.path.exists(path_excel):
            continue

        try:
            df = pd.read_excel(path_excel)

            if 'Goles Local' in df.columns and 'Goles Visita' in df.columns:
                # Si no existe la columna, crearla vacía
                if 'Resultado' not in df.columns:
                    df['Resultado'] = ''

                # Calcular solo en filas vacías
                df['Resultado'] = df.apply(lambda row: (
                    'L' if row['Goles Local'] > row['Goles Visita'] else
                    'V' if row['Goles Local'] < row['Goles Visita'] else
                    'E'
                ) if pd.isna(row['Resultado']) or row['Resultado'] == '' else row['Resultado'], axis=1)

                df.to_excel(path_excel, index=False)
                print(f"🟨 Resultado actualizado en {archivo}")
        except Exception as e:
            print(f"❌ Error al actualizar Resultado en {archivo}: {e}")

# Ejecutar al final del proceso
agregar_resultado_a_filas_nuevas()
print(f"✅ Total de llamadas realizadas a la API: {contador_llamadas}")

