import requests

API_KEY = "cb7db6deebmshd7772fb19f1a9e4p18e815jsn85b9be43cc23"
headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

def mostrar_ligas_pais(pais):
    url = f"https://api-football-v1.p.rapidapi.com/v3/leagues?country={pais}"
    response = requests.get(url, headers=headers)
    data = response.json()

    print(f"🌍 Ligas en {pais}:")
    for item in data["response"]:
        liga = item["league"]
        print(f"- ID {liga['id']}: {liga['name']}")

# Cambia por los países que quieras revisar
paises = ["Chile", "Mexico", "Argentina", "Bolivia"]

for pais in paises:
    mostrar_ligas_pais(pais)
    print()
