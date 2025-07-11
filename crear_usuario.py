from app import app, db, Usuario, CodigoAcceso
from werkzeug.security import generate_password_hash

# === CONFIGURA TUS DATOS ===
email = "contacto.rockdata@gmail.com"
clave = "Rock2024"
codigo = "1941-2001-3690"  # Debe coincidir con un código válido NO usado

with app.app_context():
    # Verificar si ya existe el usuario
    if Usuario.query.filter_by(email=email).first():
        print("❌ Ya existe un usuario con ese email.")
    else:
        # Validar código
        codigo_obj = CodigoAcceso.query.filter_by(codigo=codigo, usado=False).first()
        if not codigo_obj:
            print("❌ Código inválido o ya fue utilizado.")
        else:
            # Crear usuario
            nuevo_usuario = Usuario(
                email=email,
                cuenta_activada=True,
                codigo_unico=codigo
            )
            nuevo_usuario.password_hash = generate_password_hash(clave)

            # Marcar el código como usado
            codigo_obj.usado = True

            db.session.add(nuevo_usuario)
            db.session.commit()

            print("✅ Usuario creado correctamente.")
