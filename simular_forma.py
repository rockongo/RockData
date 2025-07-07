import json

# Ruta al archivo JSON que ya tienes en static/
ruta = "static/simulacion_forma_reciente.json"

# Leer el JSON
with open(ruta, "r", encoding="utf-8") as f:
    data = json.load(f)

# Acceder directamente a los datos dentro de "forma_reciente"
forma = data.get("forma_reciente", {})

# Mostrar datos por consola
for equipo, stats in forma.items():
    print(f"\n🔷 {equipo.capitalize()}")
    for k, v in stats.items():
        print(f"  {k}: {v}")

print("\n✅ Simulación cargada correctamente.")
