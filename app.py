from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import timedelta
import pandas as pd
import os
import json
from rockongo_core import predecir_partido, generar_sugerencias

app = Flask(__name__)
app.secret_key = "Racg@1981"  # clave de acceso
app.permanent_session_lifetime = timedelta(days=7)

# Ruta donde están los archivos .xlsx (relativa a la carpeta del script)
RUTA_LIGAS = os.path.join(os.path.dirname(__file__), "Ligas")

# Diccionario para desplegables
ligas = {
    "Chile": {
        "Primera A": "Primera_A_2025.xlsx",
        "Primera B": "Primera_B_2025.xlsx"
    },
    "Bolivia": {
        "Primera A": "Liga_bolivia_2025.xlsx"
    },
    "Perú": {
        "Primera A": "Liga_peruana_2025.xlsx"
    },
    "USA": {
        "MLS": "Liga_MLS_2025.xlsx"
    },
    "Noruega": {
        "Eliteserien": "Liga_noruega_2025.xlsx"
    },
    "Ecuador": {
        "Liga Pro": "Liga_ecuador_2025.xlsx"
    },
    "Colombia": {
        "Primera A": "Liga_colombia_2025.xlsx"
    }
}

# === LOGIN ===
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        clave_ingresada = request.form.get("clave")
        if clave_ingresada == "Racg@1981":
            session.permanent = True
            session["autenticado"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Clave incorrecta")
    return render_template("login.html")


# === PÁGINA PRINCIPAL ===
@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("autenticado"):
        return redirect(url_for("login"))

    resultado = None
    sugerencias = []
    paises = list(ligas.keys())

    if request.method == "POST":
        pais = request.form["pais"]
        liga = request.form["liga"]
        equipo_local = request.form["equipo_local"]
        equipo_visita = request.form["equipo_visita"]

        archivo_excel = os.path.join(RUTA_LIGAS, ligas[pais][liga])
        resultado = predecir_partido(archivo_excel, equipo_local, equipo_visita)

        if resultado:
            sugerencias = generar_sugerencias(archivo_excel, equipo_local, equipo_visita)

    return render_template("index.html", paises=paises, resultado=resultado, sugerencias=sugerencias)


# === API: Obtener ligas por país ===
@app.route("/get_ligas", methods=["POST"])
def get_ligas():
    data = request.get_json()
    pais = data.get("pais")
    ligas_pais = list(ligas.get(pais, {}).keys())
    return jsonify(ligas_pais)


# === API: Obtener equipos por liga ===
@app.route("/get_equipos", methods=["POST"])
def get_equipos():
    data = request.get_json()
    pais = data.get("pais")
    liga = data.get("liga")
    archivo_nombre = ligas.get(pais, {}).get(liga)

    if not archivo_nombre:
        return jsonify([])

    ruta_archivo = os.path.join(RUTA_LIGAS, archivo_nombre)

    try:
        df = pd.read_excel(ruta_archivo)
        equipos = sorted(set(df["Local"].dropna().unique()) | set(df["Visita"].dropna().unique()))
        return jsonify(equipos)
    except:
        return jsonify([])

# === EJECUCIÓN LOCAL ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

