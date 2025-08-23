import requests
from datetime import datetime

def obtener_fecha_hoy():
    return datetime.now().strftime("%Y-%m-%d")

def obtener_partidos_hoy(api_key, ligas_activas):
    fecha = obtener_fecha_hoy()
    url = f"https://api-football-v1.p.rapidapi.com/v3/fixtures?date={fecha}"

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    try:
        print(f"🔄 Realizando llamada a la API-Football para la fecha {fecha}...")
        response = requests.get(url, headers=headers)
        llamadas_realizadas = 1

        data = response.json()

        # Mostrar todas las ligas que vinieron hoy (sin filtro)
        ligas_hoy = set()
        for match in data["response"]:
            liga_id = match["league"]["id"]
            nombre = match["league"]["name"]
            ligas_hoy.add((liga_id, nombre))

        print(f"\n🔎 Ligas presentes hoy en la API ({len(ligas_hoy)}):")
        for liga_id, nombre in sorted(ligas_hoy):
            print(f"ID {liga_id}: {nombre}")

        # Filtrar solo por tus ligas
        partidos_filtrados = [
            match for match in data["response"]
            if match["league"]["id"] in ligas_activas
        ]

        print(f"\n✅ Llamadas a la API: {llamadas_realizadas}")
        print(f"📅 Partidos encontrados para hoy en tus ligas: {len(partidos_filtrados)}")

        for match in partidos_filtrados:
            hora = match['fixture']['date'][11:16]
            print(f"- {hora} | {match['league']['name']}: {match['teams']['home']['name']} vs {match['teams']['away']['name']}")

    except Exception as e:
        print(f"❌ Error al consultar la API: {e}")

# Tu API Key de RapidAPI
API_KEY = "cb7db6deebmshd7772fb19f1a9e4p18e815jsn85b9be43cc23"

# IDs de tus ligas activas
ligas_activas = [
    79, 128, 344, 71, 72, 169, 239, 242, 244, 164,
    253, 262, 103, 281, 113, 207, 270, 265, 266
]

obtener_partidos_hoy(API_KEY, ligas_activas)
