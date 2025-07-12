import sqlite3
import pandas as pd

# Conectar a la base original
conn = sqlite3.connect("usuarios.db")

# Exportar tabla de usuarios
usuarios = pd.read_sql_query("SELECT * FROM usuario", conn)
usuarios.to_csv("usuarios.csv", index=False)

# Exportar tabla de códigos
codigos = pd.read_sql_query("SELECT * FROM codigo_acceso", conn)
codigos.to_csv("codigos.csv", index=False)

conn.close()
print("✅ Exportación completada: usuarios.csv y codigos.csv")
