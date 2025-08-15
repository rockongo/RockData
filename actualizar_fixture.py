import os
import pandas as pd
import requests
from datetime import datetime

# === CONFIG BÁSICA ===
API_KEY = "cb7db6deebmshd7772fb19f1a9e4p18e815jsn85b9be43cc23"
API_HOST = "api-football-v1.p.rapidapi.com"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

# === CONTADOR DE LLAMADAS (monitoreo de consumo) ===
MAX_LLAMADAS_DIARIAS = 7000
contador_llamadas = 0

def llamada_api_segura(url, headers=None, params=None):
    """Envuelve requests.get y contabiliza llamadas; corta si excede el máximo."""
    global contador_llamadas
    if contador_llamadas >= MAX_LLAMADAS_DIARIAS:
        print("🚨 Límite diario de llamadas alcanzado. Deteniendo ejecución.")
        raise SystemExit(1)
    r = requests.get(url, headers=headers, params=params, timeout=30)
    contador_llamadas += 1
    return r

# === CONFIG DE LIGAS ===
ligas_config = {
    "Liga_alemania_B_2025.xlsx": {"id": 79, "desde": "2025-08-01"},
    "Liga_argentina_2025.xlsx": {"id": 128, "desde": "2025-08-07"},
    "Liga_bolivia_2025.xlsx": {"id": 344, "desde": "2025-08-07"},
    "Liga_brasil_2025.xlsx": {"id": 71, "desde": "2025-08-07"},
    "Liga_brasil_B_2025.xlsx": {"id": 72, "desde": "2025-08-07"},
    "Liga_china_2025.xlsx": {"id": 169, "desde": "2025-08-07"},
    "Liga_colombia_2025.xlsx": {"id": 239, "desde": "2025-06-29"},  # Colombia desde 29-06-2025
    "Liga_ecuador_2025.xlsx": {"id": 242, "desde": "2025-06-29"},
    "Liga_finlandia_2025.xlsx": {"id": 244, "desde": "2025-06-29"},
    "Liga_islandia_2025.xlsx": {"id": 164, "desde": "2025-06-29"},
    "Liga_MLS_2025.xlsx": {"id": 253, "desde": "2025-06-29"},
    "Liga_mexico_2025.xlsx": {"id": 262, "desde": "2025-06-29"},
    "Liga_noruega_2025.xlsx": {"id": 103, "desde": "2025-06-29"},
    "Liga_peruana_2025.xlsx": {"id": 281, "desde": "2025-06-29"},
    "Liga_Suecia_2025.xlsx": {"id": 113, "desde": "2025-06-29"},
    "Liga_suiza_2025.xlsx": {"id": 207, "desde": "2025-06-29"},
    "Liga_uruguay_2025.xlsx": {"id": 270, "desde": "2025-06-29"},
    "Primera_A_2025.xlsx": {"id": 265, "desde": "2025-06-29"},
    "Primera_B_2025.xlsx": {"id": 266, "desde": "2025-06-29"},
}

# === RUTA DE EXCELS ===
RUTA_LIGAS = os.path.join(os.path.dirname(__file__), "Ligas")

# ----------------------------
# Helpers de parsing/consistencia
# ----------------------------

def parse_stat_value(value):
    """
    Convierte '54%' -> 54 ; None -> None ; int/float -> int redondeado.
    Si no se puede parsear, devuelve None.
    """
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip().replace("%", "").strip()
        if v == "":
            return None
        try:
            return int(round(float(v)))
        except:
            return None
    if isinstance(value, (int, float)):
        return int(round(value))
    return None

def get_stat(stats_data, team_id, stat_name):
    """Obtiene una estadística por ID de equipo (más robusto que por nombre)."""
    for team_stats in stats_data:
        if team_stats.get("team", {}).get("id") == team_id:
            for item in team_stats.get("statistics", []):
                if item.get("type") == stat_name:
                    return item.get("value")
    return None

def contar_goles_por_tiempo_desde_eventos(events, home_id, away_id):
    """
    Cuenta goles por equipo en 1T y 2T con /fixtures/events.
    Considera detail en {'Normal Goal','Penalty','Own Goal'}.
    1T: elapsed <= 45 (incluye descuento).
    """
    valid = {"Normal Goal", "Penalty", "Own Goal"}
    h1 = a1 = h2 = a2 = 0

    for ev in events:
        if ev.get("type") != "Goal":
            continue
        detail = (ev.get("detail") or "").strip()
        if detail not in valid:
            continue

        team_id = ev.get("team", {}).get("id")
        elapsed = ev.get("time", {}).get("elapsed")
        if elapsed is None:
            continue

        if int(elapsed) <= 45:
            if team_id == home_id: h1 += 1
            elif team_id == away_id: a1 += 1
        else:
            if team_id == home_id: h2 += 1
            elif team_id == away_id: a2 += 1

    return h1, a1, h2, a2

def obtener_tiempos_con_fallback(partido):
    """
    Orden de fuentes:
    1) partido['score']['halftime']  → deduce 2T con FT
    2) /fixtures/events               → cuenta goles por tiempo
    Si no hay fuente, retorna NaN y marca estado 'FALTAN_DATOS'.
    Valida 1T+2T == FT cuando sea posible.
    """
    fuente = "ninguna"
    estado = "FALTAN_DATOS"

    fixture = partido["fixture"]
    teams   = partido["teams"]
    goals   = partido.get("goals", {}) or {}
    score   = partido.get("score", {}) or {}

    fixture_id = fixture["id"]
    home_id = teams["home"]["id"]
    away_id = teams["away"]["id"]

    ft_home = goals.get("home", 0) or 0
    ft_away = goals.get("away", 0) or 0

    # 1) halftime directo desde score
    ht = score.get("halftime") or {}
    ht_home = ht.get("home", None)
    ht_away = ht.get("away", None)

    if ht_home is not None and ht_away is not None:
        g1h = int(ht_home); g1a = int(ht_away)
        g2h = ft_home - g1h
        g2a = ft_away - g1a
        fuente = "score"

        if (g1h + g2h == ft_home) and (g1a + g2a == ft_away):
            estado = "OK"
            return g1h, g1a, g2h, g2a, fuente, estado
        # si no cuadra, seguimos a events para corregir

    # 2) reconstrucción desde events
    events_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/events"
    r_ev = llamada_api_segura(events_url, headers=headers, params={"fixture": fixture_id})
    events = r_ev.json().get("response", []) if r_ev.ok else []

    if events:
        e1h, e1a, e2h, e2a = contar_goles_por_tiempo_desde_eventos(events, home_id, away_id)
        fuente = "events"

        if (e1h + e2h == ft_home) and (e1a + e2a == ft_away):
            estado = "OK"
            return e1h, e1a, e2h, e2a, fuente, estado
        else:
            estado = "INCONSISTENTE"
            return e1h, e1a, e2h, e2a, fuente, estado

    # 3) sin fuente → NaN + flag
    return (pd.NA, pd.NA, pd.NA, pd.NA, fuente, estado)

# ----------------------------
# API: obtener fixtures
# ----------------------------
def obtener_partidos(league_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {"league": league_id, "season": 2025}
    res = llamada_api_segura(url, headers=headers, params=params)
    return res.json().get("response", [])

# ----------------------------
# PROCESO PRINCIPAL
# ----------------------------
for archivo, config in ligas_config.items():
    path_excel = os.path.join(RUTA_LIGAS, archivo)
    if not os.path.exists(path_excel):
        print(f"❌ No encontrado: {archivo}")
        continue

    print(f"\n📄 Revisando: {archivo}")
    df_existente = pd.read_excel(path_excel)

    # Guardamos IDs para no duplicar
    fixt_col = "Fixture ID"
    if fixt_col in df_existente.columns:
        fixture_ids_existentes = set(
            pd.to_numeric(df_existente[fixt_col], errors="coerce").fillna(0).astype(int)
        )
    else:
        fixture_ids_existentes = set()

    nuevos_partidos = []
    nuevas_filas = []

    for partido in obtener_partidos(config["id"]):
        fixture = partido["fixture"]
        status = fixture["status"]["short"]  # solo FT
        if status != "FT":
            continue

        fecha_str = fixture["date"]
        fecha_dt = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
        fecha_txt = fecha_dt.strftime("%Y-%m-%d")
        if fecha_txt <= config["desde"]:
            continue

        fixture_id = fixture["id"]
        if fixture_id in fixture_ids_existentes:
            continue  # ya existe en el Excel

        teams = partido["teams"]
        goals = partido.get("goals", {}) or {}

        local      = teams["home"]["name"]
        visita     = teams["away"]["name"]
        local_id   = teams["home"]["id"]
        visita_id  = teams["away"]["id"]

        # FT (si la API no trae, lo tratamos como 0 pero no inventamos por tiempo)
        goles_local  = goals.get("home", 0) or 0
        goles_visita = goals.get("away", 0) or 0

        # --- Estadísticas del fixture ---
        stats_url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/statistics"
        r_stats = llamada_api_segura(stats_url, headers=headers, params={"fixture": fixture_id})
        stats_data = r_stats.json().get("response", []) if r_stats.ok else []

        # Córners y tarjetas (usando ID)
        corners_local    = parse_stat_value(get_stat(stats_data, local_id,  "Corner Kicks"))
        corners_visita   = parse_stat_value(get_stat(stats_data, visita_id, "Corner Kicks"))
        amarillas_local  = parse_stat_value(get_stat(stats_data, local_id,  "Yellow Cards"))
        amarillas_visita = parse_stat_value(get_stat(stats_data, visita_id, "Yellow Cards"))
        rojas_local      = parse_stat_value(get_stat(stats_data, local_id,  "Red Cards"))
        rojas_visita     = parse_stat_value(get_stat(stats_data, visita_id, "Red Cards"))
        posesion_local   = parse_stat_value(get_stat(stats_data, local_id,  "Ball Possession"))
        posesion_visita  = parse_stat_value(get_stat(stats_data, visita_id, "Ball Possession"))

        # Forzar 0 en ROJAS solo cuando hay stats del partido (cero real)
        if stats_data:
            if rojas_local is None: rojas_local = 0
            if rojas_visita is None: rojas_visita = 0
        # En posesión, si no viene, queda NaN (mejor que inventar).

        # --- Goles por tiempo (fallback) ---
        g1t_h, g1t_a, g2t_h, g2t_a, fuente_tiempos, estado_datos = obtener_tiempos_con_fallback(partido)

        fila = [
            fecha_txt, local, visita,
            goles_local, goles_visita, fixture_id,
            corners_local, corners_visita,
            amarillas_local, amarillas_visita,
            rojas_local, rojas_visita,
            g1t_h, g1t_a,
            g2t_h, g2t_a,
            posesion_local, posesion_visita,
            fuente_tiempos, estado_datos
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
            "Posesión Local (%)", "Posesión Visita (%)",
            "fuente_tiempos", "estado_datos"
        ]
        df_nuevos = pd.DataFrame(nuevas_filas, columns=columnas)

        # Aseguramos columnas existentes y tipos
        for col in columnas:
            if col not in df_existente.columns:
                df_existente[col] = pd.NA

        # No rompemos 'Fecha'
        if "Fecha" in df_existente.columns:
            df_existente["Fecha"] = df_existente["Fecha"].astype(str)

        df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        df_final.to_excel(path_excel, index=False)
        print(f"✅ {len(nuevas_filas)} partidos agregados a {archivo}")
    else:
        print("✅ No hay nuevos partidos para agregar.")

# === RESULTADO (L/V/E) EN FILAS NUEVAS SI FALTA — versión vectorizada (sin NA ambiguo) ===
def agregar_resultado_a_filas_nuevas():
    for archivo in ligas_config:
        path_excel = os.path.join(RUTA_LIGAS, archivo)
        if not os.path.exists(path_excel):
            continue

        try:
            df = pd.read_excel(path_excel)

            # Asegurar columna y dtype "string"
            if 'Resultado' not in df.columns:
                df['Resultado'] = pd.Series([None] * len(df), dtype="string")
            else:
                df['Resultado'] = df['Resultado'].astype("string")

            # Columnas de goles a numérico
            gl = pd.to_numeric(df.get('Goles Local', pd.Series(dtype='float')), errors="coerce")
            gv = pd.to_numeric(df.get('Goles Visita', pd.Series(dtype='float')), errors="coerce")

            # Filas que necesitan cálculo (vacías o NA) y con FT disponible
            need = df['Resultado'].isna() | (df['Resultado'].fillna('').str.strip() == '')
            have_ft = gl.notna() & gv.notna()
            compute_mask = need & have_ft

            # Asignaciones vectorizadas
            mask_l = compute_mask & (gl > gv)
            mask_v = compute_mask & (gl < gv)
            mask_e = compute_mask & (gl == gv)

            df.loc[mask_l, 'Resultado'] = 'L'
            df.loc[mask_v, 'Resultado'] = 'V'
            df.loc[mask_e, 'Resultado'] = 'E'

            df.to_excel(path_excel, index=False)
            print(f"🟨 Resultado actualizado en {archivo} (nuevas asignaciones: {int(mask_l.sum()+mask_v.sum()+mask_e.sum())})")
        except Exception as e:
            print(f"❌ Error al actualizar Resultado en {archivo}: {e}")

# Ejecutar post-proceso
agregar_resultado_a_filas_nuevas()
print(f"✅ Total de llamadas realizadas a la API: {contador_llamadas}")
