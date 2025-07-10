from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import timedelta
import pandas as pd
import os
import json
import hmac
from rockongo_core import predecir_partido, generar_sugerencias
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usuarios.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    codigo_unico = db.Column(db.String(20), unique=True, nullable=True)
    cuenta_activada = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CodigoAcceso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(100), unique=True, nullable=False)
    usado = db.Column(db.Boolean, default=False)

app.secret_key = "Racg@1981"  # clave de acceso
app.permanent_session_lifetime = timedelta(days=7)

with app.app_context():
    db.create_all()

with app.app_context():
    db.create_all()

# Ruta de registro
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        codigo_ingresado = request.form.get("codigo_acceso")

        # Verifica si el email ya está registrado
        if Usuario.query.filter_by(email=email).first():
            return render_template("registro.html", error="El correo ya está registrado.")

        # Verifica si el código es válido y no usado
        codigo = CodigoAcceso.query.filter_by(codigo=codigo_ingresado, usado=False).first()
        if not codigo:
            return render_template("registro.html", error="Código de acceso inválido o ya utilizado.")

        # Crear el usuario
        nuevo_usuario = Usuario(email=email, cuenta_activada=True, codigo_unico=codigo_ingresado)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)

        # Marcar el código como usado
        codigo.usado = True
        db.session.commit()

        return redirect(url_for("login"))  # Redirige al login

    return render_template("registro.html")


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


# === RUTA: LOGIN ===


# === RUTA: LOGOUT ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



# === PÁGINA PRINCIPAL ===
@app.route("/", methods=["GET", "POST"])
def inicio():
    if "usuario_id" in session:
        usuario = Usuario.query.get(session["usuario_id"])
        if usuario and usuario.cuenta_activada:
            # Ya autenticado y activado → mostrar app
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

    # Si no está autenticado → mostrar login
    return redirect(url_for("login"))


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


import os
import requests
import hashlib
import hmac
from flask import redirect, request

FLOW_API_KEY = '305FEDAC-E69B-4D0E-A71C-9A28A3320L4F'
FLOW_SECRET_KEY = 'b515dd6df625d41ccd2de5e7793d154d6c30957'
FLOW_CREATE_URL = 'https://www.flow.cl/api/payment/create'

@app.route('/crear_orden', methods=['POST'])
def crear_orden():
    try:
        email = "contacto.rockdata@gmail.com"
        monto = "5000"
        order_id = 'ORD' + str(int.from_bytes(os.urandom(4), 'big'))
        subject = "Acceso mensual RockData"

        payload = {
            "apiKey": FLOW_API_KEY,
            "commerceOrder": order_id,
            "subject": "Acceso mensual a RockData",
            "amount": monto,
            "currency": "CLP",
            "email": email,
            "urlConfirmation": "https://rockdata.onrender.com/confirmacion",
            "urlReturn": "https://rockdata.onrender.com/post_pago",
            "confirmationMethod": "1"
        }

        # Orden exacto que requiere Flow
        orden_firma = [
            "amount",
            "apiKey",
            "commerceOrder",
            "confirmationMethod",
            "currency",
            "email",
            "subject",
            "urlConfirmation",
            "urlReturn"
        ]

        # Crear la cadena de firma
        cadena = "&".join(f"{campo}={payload[campo]}" for campo in orden_firma)

        # Crear firma HMAC-SHA256
        firma = hmac.new(
            FLOW_SECRET_KEY.encode('utf-8'),
            cadena.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        payload["s"] = firma  # NO usar "signature"

        # Enviar solicitud a Flow
        response = requests.post(FLOW_CREATE_URL, data=payload)
        resultado = response.json()

        if "url" in resultado:
            return redirect(resultado["url"])
        else:
            return f"❌ Error al crear orden: {resultado}"

    except Exception as e:
        return f"⚠️ Error inesperado: {str(e)}"
  

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.check_password(password):
            if not usuario.cuenta_activada:
                return render_template("login.html", error="Cuenta no activada. Ingresa tu código.")
            session["usuario_id"] = usuario.id
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Correo o contraseña incorrectos.")
    
    return render_template("login.html")

@app.route("/activar", methods=["GET", "POST"])
def activar():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    mensaje = None

    if request.method == "POST":
        codigo_ingresado = request.form["codigo"].strip()
        codigo = CodigoAcceso.query.filter_by(codigo=codigo_ingresado, usado=False).first()
        usuario = Usuario.query.get(session["usuario_id"])

        if codigo and usuario:
            usuario.cuenta_activada = True
            codigo.usado = True
            db.session.commit()
            mensaje = "Cuenta activada con éxito. Ya puedes usar RockData."
        else:
            mensaje = "Código inválido o ya usado."

    return render_template("activar.html", mensaje=mensaje)
	
import random
import string

def generar_codigo_unico():
    while True:
        codigo = "-".join(
            "".join(random.choices(string.digits, k=4)) for _ in range(3)
        )
        # Verifica que no exista en la base de datos
        if not CodigoAcceso.query.filter_by(codigo=codigo).first():
            return codigo

@app.route("/retorno")
def retorno_pago():
    # Aquí podrías validar que el pago realmente fue exitoso, si Flow lo permite
    nuevo_codigo = generar_codigo_unico()
    nuevo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
    db.session.add(nuevo)
    db.session.commit()
    return render_template("codigo_entregado.html", codigo=nuevo_codigo)

@app.route("/post_pago")
def post_pago():
    codigo = session.pop("codigo_generado", None)
    return render_template("post_pago.html", codigo=codigo)


@app.route('/confirmacion', methods=['POST'])
def confirmacion_pago():
    try:
        token = request.form.get("token")
        if not token:
            return "Token no recibido", 400

        # Consulta a Flow para obtener detalles del pago
        url_estado = "https://www.flow.cl/api/payment/getStatus"
        api_key = FLOW_API_KEY

        # Crear la firma
        cadena = f"apiKey={api_key}&token={token}"
        firma = hmac.new(
            FLOW_SECRET_KEY.encode("utf-8"),
            cadena.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        # Armar el payload
        payload = {
            "apiKey": api_key,
            "token": token,
            "s": firma
        }

        # Hacer la consulta a Flow
        response = requests.post(url_estado, data=payload)
        datos = response.json()

        # Validar si el pago fue exitoso (status = 1)
        if datos.get("status") == 1:
            print("✅ Pago confirmado por Flow")

            # Generar y guardar nuevo código
            nuevo_codigo = generar_codigo_unico()
            codigo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
            db.session.add(codigo)
            db.session.commit()

            session["codigo_generado"] = nuevo_codigo


            print("🔐 Código generado:", nuevo_codigo)


            # Aquí puedes generar el código de activación si quieres (paso 4)

            return "OK", 200  # Flow espera este texto exacto
        else:
            print("⚠️ Pago no confirmado. Estado:", datos.get("status"))
            return "NO_OK", 400



if __name__ == "__main__":
    app.run(debug=True)






