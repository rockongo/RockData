from app import app, db, CodigoAcceso
import random
import string

def generar_codigo_unico():
    while True:
        codigo = "-".join(
            "".join(random.choices(string.digits, k=4)) for _ in range(3)
        )
        if not CodigoAcceso.query.filter_by(codigo=codigo).first():
            return codigo

with app.app_context():
    nuevo_codigo = generar_codigo_unico()
    nuevo = CodigoAcceso(codigo=nuevo_codigo, usado=False)
    db.session.add(nuevo)
    db.session.commit()
    print("✅ Código generado:", nuevo_codigo)
