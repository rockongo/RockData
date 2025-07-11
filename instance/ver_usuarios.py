import sqlite3

# Ruta a tu base de datos (ajusta si está en otra carpeta)
conn = sqlite3.connect('usuarios.db')
cursor = conn.cursor()

# Consultamos todos los usuarios
cursor.execute("SELECT id, email, cuenta_activada FROM Usuario")
usuarios = cursor.fetchall()

print("📋 Lista de usuarios registrados:")
print("----------------------------------")
for usuario in usuarios:
    estado = "✅ ACTIVADA" if usuario[2] else "❌ NO ACTIVADA"
    print(f"ID: {usuario[0]} | Correo: {usuario[1]} | Estado: {estado}")

conn.close()
