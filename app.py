from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from rockongo_core import predecir_partido

app = Flask(__name__)

# Ruta donde están los archivos .xlsx
RUTA_LIGAS = r"C:\Users\raque\desktop\ligas_datas\Ligas"

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
        "Eliteserien": "Liga_Noruega_2025.xlsx"
    },
    "Ecuador": {
        "Liga Pro": "Liga_ecuador_2025.xlsx"
    },
    "Colombia": {
        "Primera A": "Liga_colombia_2025.xlsx"
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    paises = list(ligas.keys())

    if request.method == "POST":
        pais = request.form["pais"]
        liga = request.form["liga"]
        equipo_local = request.form["equipo_local"]
        equipo_visita = request.form["equipo_visita"]

        resultado = predecir_partido(pais, liga, equipo_local, equipo_visita)

    return render_template("index.html", paises=paises, resultado=resultado)

@app.route("/get_ligas", methods=["POST"])
def get_ligas():
    data = request.get_json()
    pais = data.get("pais")
    ligas_pais = list(ligas.get(pais, {}).keys())
    return jsonify(ligas_pais)

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

if __name__ == "__main__":
    app.run(debug=True)
