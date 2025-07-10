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
class CodigoAcceso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    usado = db.Column(db.Boolean, default=False)


with app.app_context():
    db.create_all()
RUTA_LIGAS = os.path.join(os.path.dirname(__file__), "Ligas")
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

# === RUTA: REGISTRO ===
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]
        codigo_acceso = request.form["codigo_acceso"]

        # Clave de acceso secreta para crear cuentas (modifícala si lo deseas)
        CLAVE_REGISTRO = "Rock2025"

        if codigo_acceso != CLAVE_REGISTRO:
            return "Código de acceso inválido. No estás autorizado a registrarte."

        if Usuario.query.filter_by(email=email).first():
            return "Ese correo ya está registrado."

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
            return render_template("login.html", error="Credenciales incorrectas")

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
        print("📁 Leyendo archivo:", ruta_archivo)  # <--- AGREGAR ESTO
        df = pd.read_excel(ruta_archivo)
        equipos = sorted(set(df["Local"].dropna().unique()) | set(df["Visita"].dropna().unique()))
        print("✅ Equipos encontrados:", equipos)   # <--- AGREGAR ESTO
        return jsonify(equipos)
    except Exception as e:
        print("❌ ERROR leyendo Excel:", e)         # <--- AGREGAR ESTO
        return jsonify([])
# === RUTA: CREAR ORDEN DE PAGO FLOW ===
import requests
import hashlib

FLOW_API_KEY = '305FEDAC-E69B-4D0E-A71C-9A28A3320L4F'
FLOW_SECRET_KEY = 'b515dd6df6252d41ccd2de5e7793d154d6c30957'
FLOW_CREATE_URL = 'https://www.flow.cl/api/payment/create'

@app.route('/crear_orden', methods=['POST'])
def crear_orden():	
    try:
        # Email y monto fijo
        email = "contacto.rockdata@gmail.com"
        monto = 5000

        print("📨 Email usado:", email)
        print("💰 Monto:", monto)

        
        order_id = 'ORD' + str(int.from_bytes(os.urandom(4), 'big'))
        payload = {
            "apiKey": FLOW_API_KEY,
            "commerceOrder": order_id,
            "subject": "Acceso mensual a RockData",
            "amount": str(monto),
            "currency": "CLP",
            "email": email,
            "urlReturn": "https://rockdata.onrender.com/retorno",
            "urlConfirmation": "https://rockdata.onrender.com/confirmacion",
            "urlCallback": "https://rockdata.onrender.com/confirmacion",
            "confirmationMethod": "1"
        }

        print("📦 Payload antes de firma:", payload)

        orden_firma = [
            "amount",
            "apiKey",
            "commerceOrder",
            "confirmationMethod",
            "currency",
            "email",
            "subject",
            "urlCallback",
            "urlConfirmation",
            "urlReturn"
        ]

        cadena = "&".join(f"{campo}={payload[campo]}" for campo in orden_firma)
        print("🔑 Cadena para firmar:", cadena)

        firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena.encode(), hashlib.sha256).hexdigest()
        payload["s"] = firma

        
        print("✅ Payload con firma:", payload)

        response = requests.post(FLOW_CREATE_URL, data=payload)
        print("📥 Respuesta Flow:", response.text)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Error al crear orden', 'detalle': response.text}), 500

    except Exception as e:
        print("❌ Excepción general:", str(e))
        return jsonify({'error': 'Excepción interna', 'detalle': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)



    

# Despliegue forzado para Render - 9 julio



