from app import create_app
from generar_archivo_rg90 import generar_archivo_rg90

app = create_app()
with app.app_context():
    ruta = generar_archivo_rg90(periodo="062025")
    print("Archivo generado en:", ruta)
