import csv
import re
from datetime import datetime

def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_linea(linea, numero_linea):
    errores = []

    if len(linea) < 18:
        errores.append(f"Línea {numero_linea}: cantidad de columnas insuficientes (esperadas al menos 18, encontradas {len(linea)})")
        return errores
    
    # Cortar línea a las primeras 18 columnas para validar
    linea = linea[:18]

    # Columna 1: debe ser '1'
    if linea[0] != '1':
        errores.append(f"Línea {numero_linea}: columna 1 debe ser '1', encontrado '{linea[0]}'")

    # Columna 2: debe ser '109'
    if linea[1] != '109':
        errores.append(f"Línea {numero_linea}: columna 2 debe ser '109', encontrado '{linea[1]}'")

    # Columna 3: fecha en formato dd/mm/yyyy
    if not validar_fecha(linea[2]):
        errores.append(f"Línea {numero_linea}: columna 3 fecha inválida '{linea[2]}'")

    # Columnas 8, 9, 10: montos enteros
    for i in [7, 8, 9]:  # índices base 0 para columnas 8,9,10
        try:
            valor = int(linea[i])
            if valor < 0:
                errores.append(f"Línea {numero_linea}: columna {i+1} monto negativo '{linea[i]}'")
        except ValueError:
            errores.append(f"Línea {numero_linea}: columna {i+1} no es entero válido '{linea[i]}'")

    # Validar suma de montos: col8 + col9 == col10
    try:
        gravadas = int(linea[7])
        exentas = int(linea[8])
        total = int(linea[9])
        if gravadas + exentas != total:
            errores.append(f"Línea {numero_linea}: suma de gravadas ({gravadas}) + exentas ({exentas}) != total ({total})")
    except ValueError:
        # Ya reportado arriba si no son enteros
        pass

    # Validar campos no vacíos columnas 1 a 14 (índices 0 a 13)
    for i in range(14):
        if linea[i].strip() == "":
            errores.append(f"Línea {numero_linea}: columna {i+1} está vacía")

    # Validar RUC solo dígitos y longitud (columna 6, índice 5)
    ruc = linea[5]
    if not re.fullmatch(r"\d{7,14}", ruc):
        errores.append(f"Línea {numero_linea}: RUC/Documento '{ruc}' no válido (debe tener 7-14 dígitos)")

    return errores

def validar_archivo(ruta_archivo):
    errores_totales = []
    try:
        with open(ruta_archivo, encoding="utf-8") as f:
            lector = csv.reader(f, delimiter=';')
            for idx, linea in enumerate(lector, start=1):
                errores = validar_linea(linea, idx)
                if errores:
                    errores_totales.extend(errores)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo: {ruta_archivo}")
        return False
    except Exception as e:
        print(f"ERROR inesperado al leer el archivo: {e}")
        return False

    if errores_totales:
        print("Se encontraron errores en el archivo RG90:")
        for e in errores_totales:
            print(" -", e)
        return False
    else:
        print("Archivo RG90 validado correctamente, sin errores.")
        return True

# Para pruebas rápidas desde consola
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python rg90_validacion.py ruta_al_archivo.csv")
        sys.exit(1)

    ruta = sys.argv[1]
    validar_archivo(ruta)
