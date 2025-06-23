import csv
import os
from zipfile import ZipFile
from app import db
from app.models import FacturaCompra, Empresa


# Importamos nuestro validador
from app.scripts.compras.rg90_validacion_compras import validar_archivo


def generar_archivo_rg90_compras(periodo="062025", carpeta_salida=None):
    """Genera el archivo RG90 para compras para un periodo dado (MMYYYY)."""
    from flask import current_app
    if carpeta_salida is None:
        carpeta_salida = os.path.join(current_app.root_path, 'static', 'rg90')
    os.makedirs(carpeta_salida, exist_ok=True)

    empresa = Empresa.query.first()
    if not empresa:
        raise Exception("No se encontró información de la empresa.")

    ruc = empresa.ruc.replace("-", "")
    nombre_archivo = f"{ruc}_REGC_{periodo}_V0001.csv"
    ruta_archivo = os.path.join(carpeta_salida, nombre_archivo)

    mes = int(periodo[:2])
    anho = int(periodo[2:])

    with open(ruta_archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        facturas = FacturaCompra.query.filter(
            db.extract('month', FacturaCompra.fecha) == mes,
            db.extract('year', FacturaCompra.fecha) == anho
        ).all()

        for factura in facturas:
            proveedor = factura.proveedor
            ruc_proveedor = (proveedor.ruc or "").replace("-", "") if proveedor else "0000000"

            gravada_10 = int(round(factura.iva_10 or 0))
            gravada_5 = int(round(factura.iva_5 or 0))
            exenta = int(round(factura.exentas or 0))
            total = gravada_10 + gravada_5 + exenta

            writer.writerow([
                1,
                109,
                factura.fecha.strftime("%d/%m/%Y"),
                factura.numero_factura,
                "11",
                ruc_proveedor,
                proveedor.nombre if proveedor else "Proveedor Desconocido",
                gravada_10,
                gravada_5,
                exenta,
                total,
                "S",
                "N",
                "N",
                "N",
                "", "", "", ""
            ])

    # Crear ZIP
    nombre_zip = nombre_archivo.replace(".csv", ".zip")
    ruta_zip = os.path.join(carpeta_salida, nombre_zip)
    with ZipFile(ruta_zip, 'w') as zipf:
        zipf.write(ruta_archivo, arcname=nombre_archivo)

    # --------------------------------------------------------
    # ✅ Ahora validamos inmediatamente
    # --------------------------------------------------------
    print(f"✅ Archivo RG90 de compras generado en: {ruta_archivo}")
    validacion_ok = validar_archivo(ruta_archivo)

    if validacion_ok:
        print("✅ El archivo de compras RG90 es válido.")
    else:
        print("❌ El archivo de compras RG90 tuvo errores de validación.")

    return ruta_zip


# --------------------------------------------------------
# TEST DIRECTO
# --------------------------------------------------------
if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        periodo_prueba = "062025"  # Cambia al periodo requerido
        ruta_zip = generar_archivo_rg90_compras(periodo_prueba)
        print(f"✅ Finalizado. ZIP generado en: {ruta_zip}")

