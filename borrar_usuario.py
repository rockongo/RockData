from app import app, db, Usuario

with app.app_context():
    usuario = Usuario.query.filter_by(email="contacto.rockdata@gmail.com").first()

    if usuario:
        print("✅ Usuario encontrado:")
        print(f"Email: {usuario.email}")
        print(f"Activada: {usuario.cuenta_activada}")
        print(f"Hash: {usuario.password_hash}")
    else:
        print("❌ Usuario NO encontrado")
