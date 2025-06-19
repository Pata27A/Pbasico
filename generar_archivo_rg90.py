import csv
import os
from datetime import datetime
from zipfile import ZipFile
from app import db
from app.models import Factura, Cliente, Empresa

# FUNCION AUXILIAR para calcular IVA por factura
def calcular_iva_por_factura(factura):
    gravada_10 = 0
    gravada_5 = 0
    exenta = 0

    for detalle in factura.detalles:
        producto = detalle.producto
        subtotal = detalle.subtotal

        if producto.iva_tipo == "10":
            neto = subtotal * 10 / 11
            gravada_10 += neto
        elif producto.iva_tipo == "5":
            neto = subtotal * 20 / 21
            gravada_5 += neto
        else:
            exenta += subtotal

    total_factura = int(round(gravada_10 + gravada_5 + exenta))


    return {
        "gravada_10": int(round(gravada_10)),
        "gravada_5": int(round(gravada_5)),
        "exenta": int(round(exenta)),
        "total": total_factura
    }

# FUNCION PRINCIPAL para generar el archivo RG90
def generar_archivo_rg90(periodo="062025", carpeta_salida=None):
    from flask import current_app
    if carpeta_salida is None:
        carpeta_salida = os.path.join(current_app.root_path, 'static', 'rg90')

    os.makedirs(carpeta_salida, exist_ok=True)

    # Obtener datos de la empresa
    empresa = Empresa.query.first()
    if not empresa:
        raise Exception("No se encontró información de la empresa.")

    ruc = empresa.ruc.replace("-", "")
    nombre_archivo = f"{ruc}_REG_{periodo}_V0001.csv"
    ruta_archivo = os.path.join(carpeta_salida, nombre_archivo)

    # Extraer mes y año del periodo (formato MMYYYY)
    mes = int(periodo[:2])
    anho = int(periodo[2:])

    with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        facturas = Factura.query.filter(
            db.extract('month', Factura.fecha) == mes,
            db.extract('year', Factura.fecha) == anho
        ).all()

        for factura in facturas:
            cliente = factura.cliente
            tipo_id = "11" if cliente and cliente.documento and len(cliente.documento) > 6 else "12"
            doc = cliente.documento if cliente and cliente.documento else "0000000"
            nombre = cliente.nombre if cliente else "Consumidor Final"

            iva_data = calcular_iva_por_factura(factura)

            fila = [
                1,  # Tipo de registro
                109,  # Tipo de comprobante: factura
                factura.fecha.strftime("%d/%m/%Y"),
                factura.numero,  # Ej: F-0001 o 001-001-0000001
                tipo_id,
                doc,
                nombre,
                iva_data["gravada_10"] + iva_data["gravada_5"],  # Ventas gravadas
                iva_data["exenta"],  # Ventas exentas
                iva_data["total"],   # Total de la factura
                "S",  # Imputa IVA
                "N",  # IRE
                "N",  # IRP-RSP
                "N",  # No Imputa
                "", "", "", "", ""  # Vacíos para completar 18 columnas
            ]
            writer.writerow(fila)

    # Crear archivo ZIP
    nombre_zip = nombre_archivo.replace(".csv", ".zip")
    ruta_zip = os.path.join(carpeta_salida, nombre_zip)
    with ZipFile(ruta_zip, 'w') as zipf:
        zipf.write(ruta_archivo, arcname=nombre_archivo)

    return ruta_zip


# EJECUCIÓN DIRECTA PARA PRUEBA
if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        ruta = generar_archivo_rg90(periodo="062025")  # Cambiar período si es necesario
        print(f"Archivo RG90 generado: {ruta}")

