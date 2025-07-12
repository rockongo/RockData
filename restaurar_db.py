import sqlite3

# Conecta o crea una nueva base de datos
conn = sqlite3.connect("usuarios.db")

# Lee y ejecuta el contenido del archivo SQL
with open("backup.sql", "r", encoding="utf-8") as f:
    sql_script = f.read()

conn.executescript(sql_script)
conn.commit()
conn.close()

print("✅ Base de datos restaurada exitosamente.")
