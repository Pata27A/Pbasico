
from app.models import Factura  # Importa tu modelo Factura
from app import db  # Asegúrate de importar tu db correcta

def generar_numero_factura():
    ultima_factura = db.session.query(Factura).order_by(Factura.id.desc()).first()

    if not ultima_factura or not ultima_factura.numero:
        return 'F-0001'

    try:
        ultimo_numero = int(ultima_factura.numero.split('-')[1])
        nuevo_numero = ultimo_numero + 1
        return f"F-{nuevo_numero:04d}"
    except:
        # En caso de que haya alguna factura con formato incorrecto
        return 'F-0001'
