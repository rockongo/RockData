import os
import pandas as pd
from datetime import datetime

def obtener_partidos_del_dia(ruta_ligas="Ligas/"):
    hoy = datetime.now().date()
    partidos_hoy = []

    for archivo in os.listdir(ruta_ligas):
        if archivo.endswith(".xlsx"):
            path = os.path.join(ruta_ligas, archivo)
            try:
                df = pd.read_excel(path)

                # Asegura que la columna Fecha esté bien formateada
                df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce").dt.date
                partidos = df[df["Fecha"] == hoy]

                for _, row in partidos.iterrows():
                    partidos_hoy.append({
                        "liga": archivo.replace("Liga_", "").replace(".xlsx", ""),
                        "local": row["Local"],
                        "visita": row["Visita"],
                        "fixture_id": row.get("Fixture ID", "N/A")
                    })
            except Exception as e:
                print(f"Error al leer {archivo}: {e}")

    return partidos_hoy
