import psycopg2
from datetime import datetime

# === DATOS DE CONEXIÓN RAILWAY ===
conexion = psycopg2.connect(
    host="yamabiko.proxy.rlwy.net",
    database="railway",
    user="postgres",
    password="VayKZKFUjLHWSXKBbpFhXgCcBvTDJAYe",
    port="46036"
)

cursor = conexion.cursor()

# === FECHA LÍMITE: sábado 2 de agosto 2025, 09:00 AM ===
fecha_limite = datetime(2025, 8, 2, 9, 0)

# === ELIMINAR USUARIOS TEMPORALES ===
cursor.execute("""
    DELETE FROM usuario
    WHERE temporal = TRUE AND fecha_registro < %s
""", (fecha_limite,))

conexion.commit()
cursor.close()
conexion.close()

print("✅ Usuarios temporales eliminados correctamente.")
