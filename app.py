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
from rockongo_core import predecir_partido_desde_excel

app = Flask(__name__)
app.secret_key = "Racg@1981"
app.permanent_session_lifetime = timedelta(days=7)
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:VayKZKFUjLHWSXKBbpFhXgCcBvTDJAYe@yamabiko.proxy.rlwy.net:46036/railway"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# MODELOS
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
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
        session["nuevo_usuario_email"] = email
        password = request.form.get("password")
        nombre = request.form.get("nombre")  # aunque no lo uses, evita que cause errores
        codigo_ingresado = request.form.get("codigo_acceso", "").strip()

        print(f"[DEBUG] Email: {email}, Código ingresado: {codigo_ingresado}")

        if Usuario.query.filter_by(email=email).first():
            print(f"[REGISTRO] Correo ya registrado: {email}")
            return render_template("registro.html", error="El correo ya está registrado.")

        from sqlalchemy import and_

        codigo = CodigoAcceso.query.filter(and_(
            CodigoAcceso.codigo == codigo_ingresado,
            CodigoAcceso.usado == False
        )).first()

        if not codigo:
            print(f"[REGISTRO] Código inválido o ya usado: {codigo_ingresado}")
            return render_template("registro.html", error="Código de acceso inválido o ya utilizado.")
        else:
            print(f"[REGISTRO] Código válido: {codigo_ingresado}")
            

        nuevo_codigo = generar_codigo_unico()

        nuevo_usuario = Usuario(
            email=email,
            cuenta_activada=True,
            codigo_unico=codigo_ingresado,
            
        )
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)

        print(f"[REGISTRO] Registrando usuario {email} con código {codigo_ingresado} - temporal={temporal}")
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
        ccodigo = CodigoAcceso.query.filter(and_(
            CodigoAcceso.codigo == codigo_ingresado,
            CodigoAcceso.usado == False
        )).first()
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
    "Alemania": {
        "Bundesliga B": "Liga_alemania_B_2025.xlsx"
    },
    "Argentina": {
        "Primera División de Argentina": "Liga_argentina_2025.xlsx"
    },
    "Bolivia": {
        "División Profesional": "Liga_bolivia_2025.xlsx"
    },
    "Brasil": {
        "Serie A Betano": "Liga_brasil_2025.xlsx",
        "Brasileirao Serie B": "Liga_brasil_B_2025.xlsx"
    },
    "Chile": {
        "Liga de Primera": "Primera_A_2025.xlsx",
        "Liga de Ascenso": "Primera_B_2025.xlsx"
    },
    "China": {
        "SuperLiga": "Liga_china_2025.xlsx"
    },
    "Colombia": {
        "Primera A": "Liga_colombia_2025.xlsx"
    },
    "Ecuador": {
        "Liga Pro": "Liga_ecuador_2025.xlsx"
    },
    "Finlandia": {
        "Veikkausliiga": "Liga_finlandia_2025.xlsx"
    },
    "Mexico": {
        "Liga MX-Apertura": "Liga_mexico_2025.xlsx"
    },
    "Noruega": {
        "Eliteserien": "Liga_noruega_2025.xlsx"
    },
    "Perú": {
        "Liga 1": "Liga_peruana_2025.xlsx"
    },
    "Suecia": {
        "Allsvenskan": "Liga_Suecia_2025.xlsx"
    },
    "Uruguay": {
        "Primera Division": "Liga_uruguay_2025.xlsx"
    },
    "USA": {
        "MLS": "Liga_MLS_2025.xlsx"
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
                resultado = predecir_partido_desde_excel(archivo_excel, equipo_local, equipo_visita)

                if not resultado or "Probabilidades" not in resultado:
                    flash("❌ No se pudo generar el análisis. Asegúrate de que ambos equipos tengan suficientes partidos jugados.")
                    return render_template("index.html", 
                        resultado=None,
                        sugerencias=[],
                        paises=paises,
                        equipo_local=None,
                        equipo_visita=None
                    )

                print("DEBUG RESULTADO ===>", resultado)


                
                if resultado:
                    # Variables externas
                    probabilidad_ambos = resultado["Probabilidades"]["Ambos Marcan"]["Probabilidad"]

                    if probabilidad_ambos >= 60:
                        texto_ambos = "Alta probabilidad de que ambos equipos anoten."
                    elif probabilidad_ambos >= 45:
                        texto_ambos = "Probabilidad media de que ambos equipos anoten."
                    else:
                        texto_ambos = "Probabilidad baja de que ambos equipos marquen."

                    # Escenarios de goles
                    escenarios = resultado["Probabilidades"]["Goles"]
                    prob_15 = escenarios["+1.5"]
                    prob_25 = escenarios["+2.5"]

                    if prob_15 >= 75:
                        goles_recomendacion = "Más de 1.5 goles"
                        goles_texto = "Alta probabilidad de que el partido supere los 1.5 goles."
                    elif prob_25 >= 65:
                        goles_recomendacion = "Más de 2.5 goles"
                        goles_texto = "Hay buenas chances de ver al menos 3 goles en el partido."
                    else:
                        goles_recomendacion = "Menos de 2.5 goles"
                        goles_texto = "No se anticipa un partido con muchos goles."

                    # Sugerencia de córners
                    corners = resultado["Probabilidades"]["Córners"]
                    if corners["+8.5"] >= 85:
                        corners_sugerencia = "Más de 8.5 córners"
                        corners_justificacion = "Alta probabilidad de al menos 9 córners en total."
                    elif corners["+7.5"] >= 80:
                        corners_sugerencia = "Más de 7.5 córners"
                        corners_justificacion = "Probable que el partido supere los 7 córners."
                    else:
                        corners_sugerencia = "Evitar apuestas por córners altos."
                        corners_justificacion = "Ningún escenario tiene probabilidad suficiente."

                    datos = {
                        'gol_1t_prob': resultado["Gol 1T"]["Probabilidad"],
                        'gol_1t_texto': resultado["Gol 1T"]["Texto"],

                        'ambos_marcan_prob': resultado["Probabilidades"]["Ambos Marcan"]["Probabilidad"],
                        'ambos_marcan_texto': texto_ambos,
                        'ambos_marcan_justificacion': f'{resultado["Equipo Local"]} promedia {resultado["Promedios Local"]["Goles"]:.2f} goles y {resultado["Equipo Visita"]} recibe {resultado["Promedios Visita"]["Goles"]:.2f}.',

                        'goles_prob_15': round(prob_15, 1),
                        'goles_prob_25': round(prob_25, 1),
                        'goles_recomendacion': goles_recomendacion,
                        'goles_texto': goles_texto,

                        'corners': {
                            "+7.5": round(corners.get("+7.5", 0), 1),
                            "+8.5": round(corners.get("+8.5", 0), 1),
                            "+9.5": round(corners.get("+9.5", 0), 1),
                        },
                        'corners_sugerencia': corners_sugerencia,
                        'corners_justificacion': corners_justificacion,

                        'tarjetas': {
                            "+3.5": round(resultado["Probabilidades"]["Tarjetas"].get("+3.5", 0), 1),
                            "+4.5": round(resultado["Probabilidades"]["Tarjetas"].get("+4.5", 0), 1),
                        },
                        'tarjetas_sugerencia': resultado["Probabilidades"]["Tarjetas"].get("Sugerencia", ""),
                        'tarjetas_justificacion': resultado["Probabilidades"].get("Sugerencia Tarjetas", ""),

                        'pronostico_final': resultado.get("Resultado Partido", {}).get("Sugerencia", "Sin sugerencia disponible"),
                        'resultado_justificacion': resultado.get("Resultado Partido", {}).get("Justificación", "")

                    }

                    print("🧾 Reseña del pronóstico:", datos.get('Justificacion Resultado'))
                
                    return render_template("rockdata_2.html",
                        datos=datos,
                        sugerencias=sugerencias,
                        paises=paises,
                        equipo_local=equipo_local,
                        equipo_visita=equipo_visita,
                        liga=liga,
                        fecha_partido="Próximo partido"
                        
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

from collections import OrderedDict
from urllib.parse import urlencode

@app.route("/crear_orden", methods=["POST"])
def crear_orden():
    try:
        
        email = request.form.get("email_pago", "").strip() 

        
        monto = "5500"
        subject = "Acceso mensual a RockData (plan estándar)"
        order_id = "ORD" + str(int.from_bytes(os.urandom(4), "big"))

        # Parámetros originales
        datos = {
            "amount": monto,
            "apiKey": FLOW_API_KEY,
            "commerceOrder": order_id,
            "confirmationMethod": "1",
            "currency": "CLP",
            "email": email,
            "subject": subject,
            "urlConfirmation": "https://rockdata.onrender.com/confirmacion",
            "urlReturn": "https://rockdata.onrender.com/post_pago"
        }

        # Ordenar alfabéticamente para la firma
        datos_ordenados = dict(sorted(datos.items()))
        cadena_firma = "".join(f"{k}{v}" for k, v in datos_ordenados.items())

        # Generar firma
        firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena_firma.encode(), hashlib.sha256).hexdigest()
        datos["s"] = firma  # agregar firma

        # Enviar a Flow
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(FLOW_CREATE_URL, data=datos, headers=headers)

        resultado = response.json()
        print("[FLOW DEBUG RESPONSE]", resultado)

        if "url" in resultado:
            return redirect(f'{resultado["url"]}?token={resultado["token"]}')
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

@app.route("/post_pago", methods=["GET", "POST"])
def post_pago():
    # Intentamos mostrar el último código generado (último en DB)
    ultimo = CodigoAcceso.query.order_by(CodigoAcceso.id.desc()).first()
    if ultimo:
        return render_template("codigo_entregado.html", codigo=ultimo.codigo)
    else:
        return "⚠️ No se ha generado ningún código aún. Intenta contactar con soporte."


@app.route("/confirmacion", methods=["POST"])
def confirmacion_pago():
    try:
        print("🛰️ CONFIRMACION FLOW (registro):", request.data)

        # Extraer token
        token = request.form.get("token")
        if not token and request.is_json:
            token = request.json.get("token")

        if not token:
            print("❌ Token no recibido")
            return "Token no recibido", 400

        print(f"✅ Token recibido: {token}")

        # Firmar usando token
        cadena = f"apiKey={FLOW_API_KEY}&token={token}"
        firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena.encode(), hashlib.sha256).hexdigest()

        payload = {
            "apiKey": FLOW_API_KEY,
            "token": token,
            "s": firma
        }

        response = requests.post("https://www.flow.cl/api/payment/getStatus", data=payload)
        datos = response.json()

        print(f"[CONFIRMACION] Estado de pago: {datos}")

        if datos.get("status") == 1:
            nuevo_codigo = generar_codigo_unico()
            codigo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
            db.session.add(codigo)
            db.session.commit()
            session["codigo_generado"] = nuevo_codigo
            print(f"[CONFIRMACION] ✅ Código generado: {nuevo_codigo}")
            return "OK", 200
        else:
            print(f"[CONFIRMACION] ⚠️ Pago no confirmado. Pero respondemos 200 para evitar error en Flow.")
            return "OK", 200



    except Exception as e:
        print(f"[CONFIRMACION] ❌ Error inesperado: {str(e)}")
        return f"Error interno: {str(e)}", 500


@app.route('/pago_directo')
def pago_directo():
    return render_template('pago_directo.html')

@app.route('/crear_orden_directa', methods=['POST'])
def crear_orden_directa():
    import requests
    email = request.form.get('email')
    
    if not email:
        return "❌ Email requerido", 400

    # Guardamos el email por si lo necesitamos luego (por sesión)
    session['pago_directo_email'] = email

    # Generar ID único interno para la orden
    order_id = 'ORD' + str(int.from_bytes(os.urandom(4), 'big'))
    monto = "5000"

    payload = {
        "apiKey": FLOW_API_KEY,
        "commerceOrder": order_id,
        "subject": "Acceso a RockData",
        "amount": monto,
        "currency": "CLP",
        "email": email,
        "urlConfirmation": "https://rockdata.onrender.com/confirmacion_directa",
        "urlReturn": "https://rockdata.onrender.com/codigo_entregado"

    }

    # Generar firma HMAC SHA256
    sorted_items = sorted(payload.items())
    concatenated = "&".join(f"{k}={v}" for k, v in sorted_items)
    signature = hmac.new(FLOW_SECRET_KEY.encode(), concatenated.encode(), hashlib.sha256).hexdigest()
    payload["s"] = signature

    # Enviar orden a Flow
    response = requests.post(FLOW_CREATE_URL, data=payload)
    data = response.json()

    print("Respuesta completa de Flow:", data)

    if "url" in data and "token" in data:
        return redirect(f"{data['url']}?token={data['token']}")

    else:
        return jsonify(data), 500

@app.route('/confirmacion_directa', methods=['POST'])
def confirmacion_directa():
    try:
        print("CONFIRMACION FLOW:", request.data)

        token = request.form.get("token")
        if not token and request.is_json:
            token = request.json.get("token")

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

        print(f"[CONFIRMACION] Estado de pago: {datos}")

        if datos.get("status") == 1:
            nuevo_codigo = generar_codigo_unico()
            nuevo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
            db.session.add(nuevo)
            db.session.commit()
            session["codigo_generado"] = nuevo_codigo
            print(f"[CONFIRMACION] ✅ Código generado: {nuevo_codigo}")
            return "OK", 200
        else:
            print(f"[CONFIRMACION] ⚠️ Pago no confirmado. Pero respondemos 200 para evitar error en Flow.")
            return "OK", 200


    except Exception as e:
        print(f"[CONFIRMACION] ❌ Error: {str(e)}")
        return f"Error interno: {str(e)}", 500

@app.route('/codigo_entregado', methods=["GET", "POST"])
def codigo_entregado():
    codigo = session.get("codigo_generado")

    # Alternativa si el código no está en sesión pero existe uno reciente
    if not codigo:
        ultimo = CodigoAcceso.query.order_by(CodigoAcceso.id.desc()).first()
        if ultimo:
            codigo = ultimo.codigo
        else:
            return "No se ha generado ningún código aún."

    return render_template("codigo_entregado.html", codigo=codigo)


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
    codigos = CodigoAcceso.query.order_by(CodigoAcceso.id.desc()).limit(5).all()
    salida = "<h3>Últimos códigos generados</h3><ul>"
    for c in codigos:
        salida += f"<li>{c.codigo} - Usado: {c.usado}</li>"
    salida += "</ul>"
    return salida


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

@app.route("/admin/usuarios_render")
def ver_usuarios_render():
    usuarios = Usuario.query.all()
    tabla = "<h3>Usuarios activos en Render</h3><table border=1 cellpadding=5>"
    tabla += "<tr><th>Email</th><th>Código</th><th>Activada</th></tr>"
    for u in usuarios:
        tabla += f"<tr><td>{u.email}</td><td>{u.codigo_unico}</td><td>{u.cuenta_activada}</td></tr>"
    tabla += "</table>"
    return tabla

@app.route("/ver_db")
def ver_db():
    try:
        archivo = os.path.abspath("usuarios.db")
        existe = os.path.exists(archivo)
        return f"📂 Ruta de DB: {archivo}<br>✅ Existe: {existe}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Cambio forzado redeploy y subir DB correcta

@app.route("/ver_usuarios")
def ver_usuarios():
    usuarios = Usuario.query.all()
    return "<br>".join([f"{u.email} (activado: {u.cuenta_activada})" for u in usuarios])

@app.route("/admin/ver_codigos_disponibles")
def admin_ver_codigos_disponibles():
    codigos = CodigoAcceso.query.filter_by(usado=False).order_by(CodigoAcceso.id.desc()).all()
    salida = "<h3>Códigos disponibles (no usados):</h3><ul>"
    for c in codigos:
        salida += f"<li>{c.codigo}</li>"
    salida += "</ul>"
    return salida

@app.route('/test_getstatus')
def test_getstatus():
    order_id = request.args.get('order_id')
    if not order_id:
        return "Falta order_id", 400

    cadena = f"apiKey={FLOW_API_KEY}&commerceOrder={order_id}"
    firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena.encode(), hashlib.sha256).hexdigest()

    payload = {
        "apiKey": FLOW_API_KEY,
        "commerceOrder": order_id,
        "s": firma
    }

    try:
        response = requests.post("https://www.flow.cl/api/payment/getStatusByOrder", data=payload)
        datos = response.json()
        print("[TEST GETSTATUS] 🔍 Datos recibidos:", datos)

        if datos.get("status") == 1:
            nuevo_codigo = generar_codigo_unico()
            nuevo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
            db.session.add(nuevo)
            db.session.commit()
            return f"Código generado: {nuevo_codigo}", 200
        else:
            return f"❌ Pago NO confirmado. Estado: {datos}", 400

    except Exception as e:
        return f"Error: {str(e)}", 500




# === INIT DB ===
with app.app_context():
    db.create_all()

# === RUN ===
if __name__ == "__main__":
    app.run(debug=True)

#seguimos