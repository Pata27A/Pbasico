import csv
import re
from datetime import datetime

def validar_fecha(fecha_str):
    """Valida que la fecha sea en formato dd/mm/yyyy."""
    try:
        datetime.strptime(fecha_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def validar_linea(linea, numero_linea):
    """Valida cada línea según la estructura RG90 para compras."""
    errores = []
    if len(linea) < 19:
        errores.append(f"Línea {numero_linea}: cantidad de columnas insuficientes (esperadas al menos 19, encontradas {len(linea)})")
        return errores

    # 1. Tipo de registro
    if linea[0] != "1":
        errores.append(f"Línea {numero_linea}: columna 1 debe ser '1', encontrado '{linea[0]}'")

    # 2. Tipo de comprobante
    if linea[1] != "109":
        errores.append(f"Línea {numero_linea}: columna 2 debe ser '109', encontrado '{linea[1]}'")

    # 3. Fecha
    if not validar_fecha(linea[2]):
        errores.append(f"Línea {numero_linea}: columna 3 fecha inválida '{linea[2]}'")

    # 8, 9, 10 y 11: Gravada 10, Gravada 5, Exenta, Total
    try:
        gravada_10 = int(linea[7])
        gravada_5 = int(linea[8])
        exenta = int(linea[9])
        total = int(linea[10])
        if gravada_10 < 0 or gravada_5 < 0 or exenta < 0 or total < 0:
            errores.append(f"Línea {numero_linea}: montos no pueden ser negativos.")
        if gravada_10 + gravada_5 + exenta != total:
            errores.append(
                f"Línea {numero_linea}: gravada_10 ({gravada_10}) + gravada_5 ({gravada_5}) + exenta ({exenta}) != total ({total})"
            )
    except ValueError:
        errores.append(f"Línea {numero_linea}: montos de gravada_10, gravada_5, exenta o total no son enteros válidos.")

    # 5 y 6: RUC
    ruc = linea[5]
    if not re.fullmatch(r"\d{7,14}", ruc):
        errores.append(f"Línea {numero_linea}: RUC/Documento '{ruc}' no válido (debe tener 7-14 dígitos)")

    return errores


def validar_archivo(ruta_archivo):
    """Lee y valida todas las líneas del archivo de compras RG90."""
    errores_totales = []
    try:
        with open(ruta_archivo, encoding="utf-8") as f:
            lector = csv.reader(f, delimiter=";")
            for idx, linea in enumerate(lector, start=1):
                errores = validar_linea(linea, idx)
                if errores:
                    errores_totales.extend(errores)

    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo: {ruta_archivo}")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado al leer el archivo: {e}")
        return False

    if errores_totales:
        print("Se encontraron errores en el archivo RG90 de compras:")
        for error in errores_totales:
            print(" -", error)
        return False
    else:
        print("✅ Archivo RG90 de compras validado correctamente, sin errores.")
        return True


# --------------------------------------------------------
# TEST DIRECTO
# --------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python rg90_validacion_compras.py ruta_al_archivo.csv")
        sys.exit(1)

    ruta = sys.argv[1]
    validar_archivo(ruta)
