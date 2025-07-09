import os
import pandas as pd

# Ruta a la carpeta donde están los archivos Excel de ligas
carpeta_ligas = './Ligas'

# Recorremos todos los archivos Excel en la carpeta
for archivo in os.listdir(carpeta_ligas):
    if archivo.endswith('.xlsx'):
        ruta_completa = os.path.join(carpeta_ligas, archivo)
        print(f"Procesando: {archivo}")

        try:
            df = pd.read_excel(ruta_completa)

            # Verificamos que existan las columnas necesarias
            if 'Goles Local' in df.columns and 'Goles Visita' in df.columns:
                # Función para determinar resultado
                def obtener_resultado(row):
                    if row['Goles Local'] > row['Goles Visita']:
                        return 'L'
                    elif row['Goles Local'] < row['Goles Visita']:
                        return 'V'
                    else:
                        return 'E'

                # Aplicar la función y agregar la columna 'Resultado'
                df['Resultado'] = df.apply(obtener_resultado, axis=1)

                # Guardar el archivo sobrescribiendo el anterior
                df.to_excel(ruta_completa, index=False)
                print(f"✅ Resultado agregado a {archivo}")
            else:
                print(f"⚠️  No se encontraron columnas 'Goles Local' y 'Goles Visita' en {archivo}")

        except Exception as e:
            print(f"❌ Error al procesar {archivo}: {e}")
