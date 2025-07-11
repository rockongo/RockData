import sqlite3

# Conectarse a la base de datos
conn = sqlite3.connect('usuarios.db')  # Asegúrate de estar en el mismo directorio que este archivo
cursor = conn.cursor()

# Ejecutar consulta sobre los códigos de activación
cursor.execute("SELECT id, codigo, usado FROM CodigoAcceso")
codigos = cursor.fetchall()

# Imprimir los códigos y su estado
print("🎟️ Códigos de acceso:")
print("------------------------")
for c in codigos:
    estado = "✅ USADO" if c[2] else "🕓 DISPONIBLE"
    print(f"ID: {c[0]} | Código: {c[1]} | Estado: {estado}")

# Cerrar conexión
conn.close()
