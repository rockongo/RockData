import hmac
import hashlib

apiKey = "305FEDAC-E69B-4D0E-A71C-9A28A3320L4F"
secret = "b515dd6df6252d41ccd2de5e7793d154d6c30957"
token = "PRUEBA123456"  # Puedes cambiar esto si usas otro token

cadena = f"apiKey={apiKey}&token={token}"
firma = hmac.new(secret.encode(), cadena.encode(), hashlib.sha256).hexdigest()

print(firma)
