from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import timedelta
import pandas as pd
import os
import json
import hmac
import hashlib
import random
import string
import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from rockongo_core import predecir_partido, generar_sugerencias

app = Flask(__name__)
app.secret_key = "Racg@1981"
app.permanent_session_lifetime = timedelta(days=7)
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "usuarios.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# MODELOS
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

# === RUTA: LOGIN ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"[LOGIN] Intentando ingreso con email: {email}")
        usuario = Usuario.query.filter_by(email=email).first()
        print(f"[LOGIN] Usuario encontrado: {usuario is not None}")
        if usuario and usuario.check_password(password):
            if usuario.cuenta_activada:
                session['usuario_id'] = usuario.id
                return redirect(url_for('inicio'))
            else:
                flash('Tu cuenta aún no ha sido activada.', 'danger')
        else:
            flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('login.html')

# === RUTA: REGISTRO ===
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        nombre = request.form.get("nombre")  # aunque no lo uses, evita que cause errores
        codigo_ingresado = request.form.get("codigo_acceso", "").strip()

        print(f"[DEBUG] Email: {email}, Código ingresado: {codigo_ingresado}")

        if Usuario.query.filter_by(email=email).first():
            print(f"[REGISTRO] Correo ya registrado: {email}")
            return render_template("registro.html", error="El correo ya está registrado.")

        codigo = CodigoAcceso.query.filter_by(codigo=codigo_ingresado, usado=0).first()
        if not codigo:
            print(f"[REGISTRO] Código inválido o ya usado: {codigo_ingresado}")
            return render_template("registro.html", error="Código de acceso inválido o ya utilizado.")
        else:
            print(f"[REGISTRO] Código válido: {codigo_ingresado}")

        nuevo_usuario = Usuario(email=email, cuenta_activada=True, codigo_unico=codigo_ingresado)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)

        print(f"[REGISTRO] Registrando usuario {email} con código {codigo_ingresado}")
        codigo.usado = True
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("registro.html")


# === RUTA: ACTIVAR ===
@app.route("/activar", methods=["GET", "POST"])
def activar():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    mensaje = None

    if request.method == "POST":
        codigo_ingresado = request.form["codigo"].strip()
        ccodigo = CodigoAcceso.query.filter_by(codigo=codigo_ingresado, usado=0).first()
        usuario = Usuario.query.get(session["usuario_id"])

        if codigo and usuario:
            usuario.cuenta_activada = True
            codigo.usado = True
            db.session.commit()
            mensaje = "Cuenta activada con éxito. Ya puedes usar RockData."
        else:
            mensaje = "Código inválido o ya usado."

    return render_template("activar.html", mensaje=mensaje)

# === RUTA: LOGOUT ===
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# === LÓGICA PRINCIPAL ===
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

@app.route("/", methods=["GET", "POST"], endpoint="inicio")
def inicio():
    if "usuario_id" in session:
        usuario = Usuario.query.get(session["usuario_id"])
        if usuario and usuario.cuenta_activada:
            resultado = None
            sugerencias = []
            paises = list(ligas.keys())
            equipo_local = None
            equipo_visita = None

            if request.method == "POST":
                pais = request.form["pais"]
                liga = request.form["liga"]
                equipo_local = request.form["equipo_local"]
                equipo_visita = request.form["equipo_visita"]

                archivo_excel = os.path.join(RUTA_LIGAS, ligas[pais][liga])
                resultado = predecir_partido(archivo_excel, equipo_local, equipo_visita)

                print("DEBUG RESULTADO ===>", resultado)

                if resultado:
                    resultado_dict = {
                        "Local": {
                            "Goles": resultado["Goles Local"],
                            "Goles 1T": resultado["Goles 1T Local"],
                            "Goles 2T": resultado["Goles 2T Local"],
                            "Córners": resultado["Córners Local"],
                            "Amarillas": resultado["Amarillas Local"],
                            "Rojas": resultado["Rojas Local"],
                        },
                        "Visita": {
                            "Goles": resultado["Goles Visita"],
                            "Goles 1T": resultado["Goles 1T Visita"],
                            "Goles 2T": resultado["Goles 2T Visita"],
                            "Córners": resultado["Córners Visita"],
                            "Amarillas": resultado["Amarillas Visita"],
                            "Rojas": resultado["Rojas Visita"],
                        },

                        "Goles Totales": resultado["Goles Totales"],
                        "Corners": resultado["Corners"],
                        "Tarjetas Promedio": resultado["Tarjetas Promedio"],
                        "Rojas": resultado["Rojas"],
                        "Pronóstico Final": resultado["Pronóstico"]
                    }

                    sugerencias = generar_sugerencias(
                        resultado["Goles Totales"],
                        resultado["Corners"],
                        resultado["Tarjetas Promedio"],
                        resultado["Rojas"]
                    )

                    return render_template("rockdata_2.html", 
                        resultado=resultado_dict,
                        sugerencias=sugerencias,
                        paises=paises,
                        equipo_local=equipo_local,
                        equipo_visita=equipo_visita
                    )

            return render_template("index.html", 
                resultado=None,
                sugerencias=[],
                paises=paises,
                equipo_local=None,
                equipo_visita=None
            )

    return redirect(url_for("login"))



# === API ===
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
    except Exception as e:
        return jsonify([])

# === CREAR ORDEN DE PAGO FLOW ===
FLOW_API_KEY = "305FEDAC-E69B-4D0E-A71C-9A28A3320L4F"
FLOW_SECRET_KEY = "b515dd6df6252d41ccd2de5e7793d154d6c30957"
FLOW_CREATE_URL = "https://www.flow.cl/api/payment/create"

@app.route("/crear_orden", methods=["POST"])
def crear_orden():
    try:
        # Datos base
        email = "contacto.rockdata@gmail.com"
        monto = "5000"
        subject = "RockData"
        order_id = "ORD" + str(int.from_bytes(os.urandom(4), "big"))

        # Parámetros obligatorios
        payload = {
            "apiKey": FLOW_API_KEY,
            "commerceOrder": order_id,
            "subject": subject,
            "amount": monto,
            "currency": "CLP",
            "email": email,
            "urlConfirmation": "https://rockdata.onrender.com/confirmacion",
            "urlReturn": "https://rockdata.onrender.com/post_pago",
            "confirmationMethod": "1"
        }

        # === FIRMA CORRECTA (Flow 2024) ===
        parametros_ordenados = dict(sorted(payload.items()))  # 1. Ordenar por clave alfabéticamente
        cadena = "".join(f"{k}{v}" for k, v in parametros_ordenados.items())  # 2. Concatenar sin & ni =
        firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena.encode(), hashlib.sha256).hexdigest()  # 3. HMAC
        payload["s"] = firma  # 4. Agregar firma

        # Enviar solicitud
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(FLOW_CREATE_URL, data=payload, headers=headers)
        resultado = response.json()

        # Verificación del resultado
        if "url" in resultado:
            return redirect(resultado["url"])
        else:
            return f"❌ Error al crear orden: {resultado}"

    except Exception as e:
        return f"⚠️ Error inesperado: {str(e)}"


# === CONFIRMACIÓN DE PAGO FLOW ===
def generar_codigo_unico():
    while True:
        codigo = "-".join("".join(random.choices(string.digits, k=4)) for _ in range(3))
        if not CodigoAcceso.query.filter_by(codigo=codigo).first():
            return codigo

@app.route("/retorno")
def retorno_pago():
    nuevo_codigo = generar_codigo_unico()
    nuevo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
    db.session.add(nuevo)
    db.session.commit()
    return render_template("codigo_entregado.html", codigo=nuevo_codigo)

@app.route("/post_pago")
def post_pago():
    codigo = session.pop("codigo_generado", None)
    return render_template("post_pago.html", codigo=codigo)

@app.route("/confirmacion", methods=["POST"])
def confirmacion_pago():
    try:
        token = request.form.get("token")
        if not token:
            return "Token no recibido", 400

        cadena = f"apiKey={FLOW_API_KEY}&token={token}"
        firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena.encode(), hashlib.sha256).hexdigest()

        payload = {
            "apiKey": FLOW_API_KEY,
            "token": token,
            "s": firma
        }

        response = requests.post("https://www.flow.cl/api/payment/getStatus", data=payload)
        datos = response.json()

        if datos.get("status") == 1:
            nuevo_codigo = generar_codigo_unico()
            codigo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
            db.session.add(codigo)
            db.session.commit()
            session["codigo_generado"] = nuevo_codigo
            return "OK", 200
        else:
            return "NO_OK", 400
    except Exception as e:
        return "ERROR", 500

@app.route("/recuperar_contrasena", methods=["GET", "POST"])
def recuperar_contrasena():
    mensaje = None

    if request.method == "POST":
        email = request.form.get("email")
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            session["recuperar_id"] = usuario.id
            return redirect(url_for("nueva_contrasena"))
        else:
            mensaje = "❌ Correo no encontrado. Verifica e intenta de nuevo."

    return render_template("recuperar_contrasena.html", mensaje=mensaje)

@app.route("/nueva_contrasena", methods=["GET", "POST"])
def nueva_contrasena():
    mensaje = None

    # Si no hay ID en sesión, redirige al login
    if "recuperar_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        nueva = request.form.get("nueva")
        repetir = request.form.get("repetir")

        if nueva != repetir:
            mensaje = "❌ Las contraseñas no coinciden."
        else:
            usuario = Usuario.query.get(session["recuperar_id"])
            if usuario:
                usuario.set_password(nueva)
                db.session.commit()
                session.pop("recuperar_id", None)
                return redirect(url_for("login"))
            else:
                mensaje = "❌ No se encontró el usuario."

    return render_template("nueva_contrasena.html", mensaje=mensaje)


@app.route("/debug_codigos")
def debug_codigos():
    codigo = CodigoAcceso.query.filter_by(codigo="1069-4074-7553").first()
    if codigo:
        return f"Código encontrado. Usado = {codigo.usado}"
    else:
        return "❌ Código no encontrado en la base activa"

# === ADMIN: Generar código manual protegido ===
@app.route("/admin/crear_codigo", methods=["GET", "POST"])
def admin_crear_codigo():
    CLAVE_SECRETA = "rockadmin2025"

    if request.method == "POST":
        clave = request.form.get("clave")
        if clave != CLAVE_SECRETA:
            return "❌ Clave incorrecta", 403

        # Generar nuevo código único
        while True:
            nuevo_codigo = "-".join("".join(random.choices(string.digits, k=4)) for _ in range(3))
            if not CodigoAcceso.query.filter_by(codigo=nuevo_codigo).first():
                break

        nuevo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
        db.session.add(nuevo)
        db.session.commit()

        return f"✅ Código generado: {nuevo_codigo}"

    return """
    <form method='POST'>
        <input type='password' name='clave' placeholder='Clave admin' required>
        <button type='submit'>Generar código</button>
    </form>
    """


# === INIT DB ===
with app.app_context():
    db.create_all()

# === RUN ===
if __name__ == "__main__":
    app.run(debug=True)
