from app import app, db, Usuario

with app.app_context():
    usuario = Usuario.query.filter_by(email="contacto.rockdata@gmail.com").first()
    if usuario:
        print("Hash de contraseña:", usuario.password_hash)
    else:
        print("❌ Usuario no encontrado.")
