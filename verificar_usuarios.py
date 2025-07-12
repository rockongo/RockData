import sqlite3

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

print("📋 Usuarios registrados:")
for row in cursor.execute("SELECT id, email, cuenta_activada FROM usuario"):
    print(row)

print("\n📋 Códigos disponibles:")
for row in cursor.execute("SELECT id, codigo, usado FROM codigo_acceso"):
    print(row)

conn.close()
