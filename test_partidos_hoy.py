from utils import obtener_partidos_del_dia

partidos = obtener_partidos_del_dia()

if not partidos:
    print("⚠️  No hay partidos para hoy.")
else:
    print("📅 Partidos del día:")
    for p in partidos:
        print(f"{p['liga']}: {p['local']} vs {p['visita']} (ID: {p['fixture_id']})")
