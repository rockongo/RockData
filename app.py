from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import timedelta
import pandas as pd
import os
import json
from rockongo_core import predecir_partido, generar_sugerencias
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.secret_key = "Racg@1981"  # clave de acceso
app.permanent_session_lifetime = timedelta(days=7)
# Crear la base de datos si no existe
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.contrasena_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena_hash, password)

with app.app_context():
    db.create_all()

	
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

# === RUTA: REGISTRO ===
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        # Validar que no exista el usuario
        if Usuario.query.filter_by(email=email).first():
            return "Ya existe un usuario con ese correo."

        nuevo_usuario = Usuario(nombre=nombre, email=email)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("registro.html")

# === RUTA: LOGIN ===
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(password):
            session["autenticado"] = True
            session["usuario_email"] = usuario.email
            return redirect(url_for("index"))
        else:
            return "Credenciales incorrectas"

    return render_template("login.html")

# === RUTA: LOGOUT ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



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
            sugerencias = generar_sugerencias(
                resultado["Goles Totales"],
                resultado["Corners"],
                resultado["Tarjetas Promedio"],
                resultado["Rojas"]
            )


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

