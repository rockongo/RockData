import requests

API_KEY = "0c5ec5a5c87f6ecf943f29ef8c60c4fd"
fixture_id = 265  # reemplaza con uno que tengas seguro

url = f"https://v3.football.api-sports.io/fixtures?id={fixture_id}"
headers = {
    "x-apisports-key": API_KEY
}

response = requests.get(url, headers=headers)
data = response.json()

print(f"🔍 Resultado para fixture ID {fixture_id}:\n")
print(data)
