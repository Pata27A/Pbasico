
from app.models import Factura  # Importa tu modelo Factura
from app import db  # Asegúrate de importar tu db correcta

def generar_numero_factura():
    ESTABLECIMIENTO = "001"
    PUNTO_EXPEDICION = "001"

    ultima_factura = db.session.query(Factura).order_by(Factura.id.desc()).first()

    if not ultima_factura or not ultima_factura.numero:
        return f"{ESTABLECIMIENTO}-{PUNTO_EXPEDICION}-0000001"

    try:
        partes = ultima_factura.numero.split("-")
        correlativo = int(partes[2]) if len(partes) == 3 else 0
        nuevo_correlativo = correlativo + 1
        return f"{ESTABLECIMIENTO}-{PUNTO_EXPEDICION}-{nuevo_correlativo:07d}"
    except Exception:
        # En caso de error, iniciar desde el primero
        return f"{ESTABLECIMIENTO}-{PUNTO_EXPEDICION}-0000001"

