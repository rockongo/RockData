import requests
from datetime import datetime

def obtener_fecha_hoy():
    return "2025-08-15"

def listar_ligas_hoy(api_key):
    fecha = obtener_fecha_hoy()
    url = f"https://v3.football.api-sports.io/fixtures?date={fecha}&page=1&limit=1000"

    headers = {
        "x-apisports-key": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        ligas = set()
        for match in data["response"]:
            liga_id = match["league"]["id"]
            nombre = match["league"]["name"]
            ligas.add((liga_id, nombre))

        ligas_ordenadas = sorted(list(ligas))
        print(f"📚 Ligas con partidos hoy ({fecha}):")
        for liga_id, nombre in ligas_ordenadas:
            print(f"ID {liga_id}: {nombre}")

        print(f"\nTotal ligas con partidos hoy: {len(ligas_ordenadas)}")

    except Exception as e:
        print(f"❌ Error al consultar la API: {e}")

# API Key
API_KEY = "0c5ec5a5c87f6ecf943f29ef8c60c4fd"

listar_ligas_hoy(API_KEY)
