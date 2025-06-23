import calendar
import csv
import datetime
from io import BytesIO, StringIO
import os
from xhtml2pdf import pisa
import json
from sqlite3 import IntegrityError
import traceback
from flask import Blueprint, jsonify, make_response, render_template, redirect, send_file, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import extract, func
from app.forms import LoginForm, ProductoForm
from app.models import Caja, Cliente, Cobranza, DetalleFactura, Empresa, Factura, FacturaCompra, MetodoPago, MovimientoCaja, Producto, Proveedor, Usuario, Categoria
from app import db
from app.utils import generar_numero_factura
import generar_archivo_rg90
# Importa tus funciones de generación y validación RG90
from generar_archivo_rg90 import generar_archivo_rg90
from app.scripts.rg90_validacion import validar_linea
from generar_archivo_rg90_compras import generar_archivo_rg90_compras
from app.scripts.compras.rg90_validacion_compras import validar_linea, validar_archivo


main_bp = Blueprint('main_bp', __name__)

# ---------------------- AUTENTICACIÓN ----------------------
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.menu_principal'))
    return redirect(url_for('main_bp.login'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.menu_principal'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.nombre_usuario.data).first()
        if user and user.check_password(form.password.data) and user.activo:
            login_user(user)
            flash(f'Bienvenido, {user.username}', 'success')
            return redirect(url_for('main_bp.menu_principal'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('main_bp.login'))

@main_bp.route('/menu')
@login_required
def menu_principal():
    return render_template('dashboard.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# ---------------------- STOCK ----------------------
@main_bp.route('/productos')
@login_required
def listar_productos():
    productos = Producto.query.all()
    return render_template('stock/listar_productos.html', productos=productos)

@main_bp.route('/producto/agregar', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    form = ProductoForm()
    form.categoria_id.choices = [(0, 'Sin Categoría')] + [(c.id, c.nombre) for c in Categoria.query.all()]
    
    if form.validate_on_submit():
        categoria_id = form.categoria_id.data if form.categoria_id.data != 0 else None
        nuevo_producto = Producto(
            codigo=form.codigo.data,
            nombre=form.nombre.data,
            categoria_id=categoria_id,
            precio_costo=form.precio_costo.data,
            precio_venta=form.precio_venta.data,
            stock_minimo=form.stock_minimo.data or 0,
            stock_actual=form.stock_actual.data or 0,
            iva_tipo=form.iva_tipo.data  # <-- Aquí
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado correctamente.', 'success')
        return redirect(url_for('main_bp.listar_productos'))

    return render_template('stock/producto_form.html', form=form, titulo='Agregar Producto')


@main_bp.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    form.categoria_id.choices = [(0, 'Sin Categoría')] + [(c.id, c.nombre) for c in Categoria.query.all()]

    if form.validate_on_submit():
        producto.codigo = form.codigo.data
        producto.nombre = form.nombre.data
        producto.categoria_id = form.categoria_id.data if form.categoria_id.data != 0 else None
        producto.precio_costo = form.precio_costo.data
        producto.precio_venta = form.precio_venta.data
        producto.stock_minimo = form.stock_minimo.data or 0
        producto.stock_actual = form.stock_actual.data or 0
        producto.iva_tipo = form.iva_tipo.data  # <-- Aquí

        db.session.commit()
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('main_bp.listar_productos'))

    return render_template('stock/producto_form.html', form=form, titulo='Editar Producto')

# ---------------------- CAJA ----------------------
def calcular_saldo_cierre(caja):
    movimientos = MovimientoCaja.query.filter_by(caja_id=caja.id).all()
    ingresos = sum(m.monto for m in movimientos if m.tipo.lower() == 'ingreso')
    egresos = sum(m.monto for m in movimientos if m.tipo.lower() == 'egreso')
    return caja.monto_apertura + ingresos - egresos

def obtener_caja_abierta():
    hoy = datetime.date.today()
    caja = Caja.query.filter_by(fecha=hoy, abierta=True).first()
    if not caja:
        raise Exception("No hay una caja abierta para el día de hoy.")
    return caja

@main_bp.route('/caja/resumen')
@login_required
def caja_resumen():
    hoy = datetime.date.today()
    caja = Caja.query.filter_by(fecha=hoy).first()
    movimientos = MovimientoCaja.query.filter_by(caja_id=caja.id).order_by(MovimientoCaja.fecha).all() if caja else []
    saldo_final = calcular_saldo_cierre(caja) if caja else 0
    return render_template('caja/resumen.html', caja=caja, movimientos=movimientos, saldo_final=saldo_final)

@main_bp.route('/caja/apertura', methods=['GET', 'POST'])
@login_required
def caja_apertura():
    hoy = datetime.date.today()
    caja = Caja.query.filter_by(fecha=hoy).first()

    if request.method == 'POST':
        if caja and caja.abierta:
            flash('La caja ya está abierta.', 'warning')
        else:
            monto = float(request.form.get('monto_apertura', 0))
            nueva = Caja(fecha=hoy, monto_apertura=monto, abierta=True)
            db.session.add(nueva)
            db.session.commit()
            flash('Caja abierta correctamente.', 'success')
            return redirect(url_for('main_bp.caja_resumen'))

    return render_template('caja/apertura.html', caja=caja)

@main_bp.route('/caja/cierre', methods=['GET', 'POST'])
@login_required
def caja_cierre():
    hoy = datetime.date.today()
    caja = Caja.query.filter_by(fecha=hoy, abierta=True).first()

    if request.method == 'POST' and caja:
        caja.monto_cierre = calcular_saldo_cierre(caja)
        caja.abierta = False
        db.session.commit()
        flash('Caja cerrada correctamente.', 'success')
        return redirect(url_for('main_bp.caja_resumen'))

    return render_template('caja/cierre.html', caja=caja, calcular_saldo_cierre=calcular_saldo_cierre)

@main_bp.route('/caja/movimiento/nuevo', methods=['GET', 'POST'])
@login_required
def caja_nuevo_movimiento():
    hoy = datetime.date.today()
    caja = Caja.query.filter_by(fecha=hoy, abierta=True).first()

    if not caja:
        flash('Debe abrir la caja para registrar movimientos.', 'danger')
        return redirect(url_for('main_bp.caja_apertura'))

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        descripcion = request.form.get('descripcion', '').strip()
        try:
            monto = float(request.form.get('monto', 0))
        except ValueError:
            flash('Monto inválido.', 'danger')
            return redirect(request.url)

        if not tipo or monto <= 0:
            flash('Tipo y monto son obligatorios y deben ser válidos.', 'warning')
            return redirect(request.url)

        nuevo = MovimientoCaja(
            caja_id=caja.id,
            tipo=tipo,
            monto=monto,
            descripcion=descripcion,
            usuario_id=current_user.id
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Movimiento registrado.', 'success')
        return redirect(url_for('main_bp.caja_resumen'))

    return render_template('caja/nuevo_movimiento.html')

@main_bp.route('/caja/movimiento/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_movimiento(id):
    movimiento = MovimientoCaja.query.get_or_404(id)

    if not movimiento.caja.abierta:
        flash('No se puede editar. Caja cerrada.', 'danger')
        return redirect(url_for('main_bp.caja_resumen'))

    if request.method == 'POST':
        movimiento.tipo = request.form.get('tipo')
        movimiento.descripcion = request.form.get('descripcion', '').strip()
        try:
            movimiento.monto = float(request.form.get('monto', 0))
        except ValueError:
            flash('Monto inválido.', 'danger')
            return redirect(request.url)

        db.session.commit()
        flash('Movimiento editado.', 'success')
        return redirect(url_for('main_bp.caja_resumen'))

    return render_template('caja/editar_movimiento.html', movimiento=movimiento)

@main_bp.route('/caja/movimiento/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_movimiento(id):
    movimiento = MovimientoCaja.query.get_or_404(id)

    if not movimiento.caja.abierta:
        flash('No se puede eliminar. Caja cerrada.', 'danger')
        return redirect(url_for('main_bp.caja_resumen'))

    db.session.delete(movimiento)
    db.session.commit()
    flash('Movimiento eliminado.', 'success')
    return redirect(url_for('main_bp.caja_resumen'))


# ---------------------- FACTURACIÓN ----------------------
@main_bp.route('/facturacion')
@login_required
def facturacion():
    productos = Producto.query.all()
    clientes = Cliente.query.all()
    metodos_pago = MetodoPago.query.all()
    vuelto = request.args.get('vuelto', default=0, type=float)
    return render_template('facturacion/nueva_factura_pos.html',
                           productos=productos,
                           clientes=clientes,
                           metodos_pago=metodos_pago,
                           vuelto=vuelto)
@main_bp.route('/facturacion/guardar', methods=['POST'])
@login_required
def guardar_factura():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos JSON'}), 400

        cliente_id = data.get('cliente_id')
        detalles = data.get('detalles', [])
        pagos = data.get('pagos', [])
        total_factura = float(data.get('total', 0))

        # Variables para acumular IVA según tipo
        iva_10 = 0
        iva_5 = 0
        exentas = 0

        # Validar suma de pagos >= total factura
        suma_pagos = sum(float(p.get('monto', 0)) for p in pagos)
        if round(suma_pagos, 2) < round(total_factura, 2):
            return jsonify({'success': False, 'error': 'El monto pagado no cubre el total de la factura'}), 400

        # Calcular vuelto (si hay)
        vuelto = round(suma_pagos - total_factura, 2) if suma_pagos > total_factura else 0

        # Generar número de factura (tu función)
        nuevo_numero = generar_numero_factura()

        # Crear factura sin impuesto todavía
        nueva_factura = Factura(
            numero=nuevo_numero,
            fecha=datetime.datetime.utcnow(),
            cliente_id=cliente_id if cliente_id else None,
            total=total_factura,
            usuario_id=current_user.id
        )
        db.session.add(nueva_factura)
        db.session.flush()  # Para obtener ID factura

        # Guardar detalles y descontar stock, calcular IVA
        for item in detalles:
            producto = db.session.query(Producto).with_for_update().filter_by(codigo=item['codigo']).first()
            if not producto:
                raise ValueError(f"Producto con código {item['codigo']} no encontrado")
            cantidad = float(item['cantidad'])
            if producto.stock_actual < cantidad:
                raise ValueError(f"Stock insuficiente para {producto.nombre} (disponible: {producto.stock_actual}, requerido: {cantidad})")

            producto.stock_actual -= cantidad

            subtotal = float(item['subtotal'])  # Precio con IVA incluido

            # Calcular IVA según tipo
            if producto.iva_tipo == '10':
                iva_10 += round(subtotal / 11, 2)
            elif producto.iva_tipo == '5':
                iva_5 += round(subtotal / 21, 2)
            else:  # Exentas o "0"
                exentas += subtotal

            detalle = DetalleFactura(
                factura_id=nueva_factura.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=float(item['precio_unitario']),
                subtotal=subtotal
            )
            db.session.add(detalle)

        impuesto_total = round(iva_10 + iva_5, 2)
        nueva_factura.impuesto = impuesto_total

        # Guardar pagos y movimientos caja (Ingresos)
        for pago in pagos:
            pago_db = Cobranza(
                factura_id=nueva_factura.id,
                metodo_pago_id=int(pago['metodo_pago_id']),
                monto=float(pago['monto']),
                descripcion=pago.get('descripcion', ''),
                usuario_id=current_user.id
            )
            db.session.add(pago_db)

            caja = obtener_caja_abierta()
            if caja:
                movimiento = MovimientoCaja(
                    caja_id=caja.id,
                    tipo='Ingreso',
                    monto=pago_db.monto,
                    descripcion=f'Cobro factura {nueva_factura.numero}',
                    usuario_id=current_user.id
                )
                db.session.add(movimiento)

        # Registrar vuelto como Egreso si es mayor a 0
        if vuelto > 0:
            caja = obtener_caja_abierta()
            if caja:
                movimiento_vuelto = MovimientoCaja(
                    caja_id=caja.id,
                    tipo='Egreso',
                    monto=vuelto,
                    descripcion=f'Vuelto para factura {nueva_factura.numero}',
                    usuario_id=current_user.id
                )
                db.session.add(movimiento_vuelto)

        db.session.commit()

        return jsonify({'success': True, 'factura_id': nueva_factura.id, 'vuelto': vuelto})

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Número de factura duplicado'}), 400

    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500



@main_bp.route('/facturacion/api/buscar_producto')
@login_required
def buscar_producto():
    codigo = request.args.get('codigo', '').strip()

    cantidad = 1
    if codigo.startswith('+'):
        try:
            cantidad = int(codigo[1])
            codigo = codigo[2:]
        except ValueError:
            pass

    producto = Producto.query.filter(Producto.codigo.ilike(f"%{codigo}%")).first()
    if producto:
        return jsonify({
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'precio': producto.precio_venta,  # <- Renombrado a 'precio'
            'cantidad': cantidad
        })
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404

@main_bp.route('/facturacion/imprimir/<int:id>')
@login_required
def imprimir_factura1(id):
    factura = Factura.query.get_or_404(id)
    empresa = Empresa.query.first()

    # Inicializar montos de IVA
    iva_10 = 0
    iva_5 = 0
    iva_exento = 0

    # Recorrer detalles y acumular IVA según tipo
    for detalle in factura.detalles:
        subtotal = detalle.subtotal
        tipo_iva = detalle.producto.iva_tipo  # "10", "5", "0"

        if tipo_iva == "10":
            iva_10 += round(subtotal / 11, 2)
        elif tipo_iva == "5":
            iva_5 += round(subtotal / 21, 2)
        else:
            iva_exento += subtotal

    return render_template(
        'facturacion/imprimir.html',
        factura=factura,
        empresa=empresa,
        iva_10=iva_10,
        iva_5=iva_5,
        iva_exento=iva_exento
    )


@main_bp.route('/facturas/listar')
@login_required
def listado_facturas():
    return render_template('facturacion/listado_facturas.html')


@main_bp.route('/facturas/api')
@login_required
def facturas_api():
    desde_str = request.args.get('desde')
    hasta_str = request.args.get('hasta')

    query = Factura.query

    try:
        if desde_str:
            desde = datetime.datetime.strptime(desde_str, '%Y-%m-%d')
            query = query.filter(Factura.fecha >= desde)
        if hasta_str:
            hasta = datetime.datetime.strptime(hasta_str, '%Y-%m-%d') + datetime.timedelta(days=1)
            query = query.filter(Factura.fecha < hasta)
    except ValueError:
        return jsonify([])

    facturas = query.order_by(Factura.fecha.desc()).all()

    result = []
    for f in facturas:
        result.append({
            'id': f.id,
            'fecha': f.fecha.strftime('%Y-%m-%d %H:%M'),
            'cliente': f.cliente.nombre if f.cliente else None,
            'total': f.total,
        })

    return jsonify(result)


@main_bp.route('/facturas/imprimir/<int:factura_id>')
@login_required
def imprimir_factura(factura_id):
    # Redirige a la misma función para evitar duplicación
    return imprimir_factura1(factura_id)

# ------------------ COBRANZAS ------------------ #

@main_bp.route('/factura/<int:factura_id>/cobrar', methods=['GET', 'POST'])
@login_required
def cobrar_factura(factura_id):
    factura = Factura.query.get_or_404(factura_id)

    if request.method == 'POST':
        try:
            monto = float(request.form['monto'])
            metodo_pago_id = int(request.form['metodo_pago_id'])
            descripcion = request.form.get('descripcion', '')

            nueva_cobranza = Cobranza(
                factura_id=factura.id,
                fecha=datetime.now(),
                monto=monto,
                metodo_pago_id=metodo_pago_id,
                descripcion=descripcion,
                usuario_id=current_user.id
            )
            db.session.add(nueva_cobranza)

            # Registrar movimiento de caja
            caja = obtener_caja_abierta()
            movimiento = MovimientoCaja(
                caja_id=caja.id,
                tipo='Ingreso',
                monto=monto,
                descripcion=f'Cobro de factura {factura.numero}',
                usuario_id=current_user.id
            )
            db.session.add(movimiento)

            db.session.commit()
            flash('Cobro registrado correctamente', 'success')
            return redirect(url_for('ver_factura', factura_id=factura.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar el cobro: {str(e)}', 'danger')

    metodos_pago = MetodoPago.query.all()
    return render_template('factura/cobrar.html', factura=factura, metodos_pago=metodos_pago)


@main_bp.route('/cobranzas')
@login_required
def cobranzas():
    cobranzas = Cobranza.query.order_by(Cobranza.fecha.desc()).all()
    return render_template('cobranzas/listar.html', cobranzas=cobranzas)

@main_bp.route('/cobranza/registrar/<int:factura_id>', methods=['GET', 'POST'])
@login_required
def registrar_cobranza(factura_id):
    factura = Factura.query.get_or_404(factura_id)
    metodos = MetodoPago.query.all()

    if request.method == 'POST':
        monto = float(request.form['monto'])
        metodo_pago_id = int(request.form['metodo_pago_id'])
        descripcion = request.form['descripcion']

        cobranza = Cobranza(
            factura_id=factura.id,
            fecha=datetime.utcnow(),
            monto=monto,
            metodo_pago_id=metodo_pago_id,
            descripcion=descripcion,
            usuario_id=current_user.id
        )
        db.session.add(cobranza)
        db.session.commit()
        flash('Cobranza registrada exitosamente.', 'success')
        return redirect(url_for('main_bp.listado_facturas'))

    return render_template('cobranzas/registrar.html', factura=factura, metodos=metodos)

@main_bp.route('/api/metodos_pago', methods=['GET'])
@login_required
def obtener_metodos_pago():
    metodos = MetodoPago.query.all()
    resultado = [{'id': m.id, 'nombre': m.nombre} for m in metodos]
    return jsonify(resultado)

#------------Clientes------------------------
# Buscar clientes por nombre o documento
@main_bp.route('/api/clientes/buscar')
@login_required
def buscar_clientes():
    query = request.args.get('q', '').strip()
    resultados = Cliente.query.filter(
        (Cliente.nombre.ilike(f'%{query}%')) |
        (Cliente.documento.ilike(f'%{query}%'))
    ).all()

    clientes_json = [{
        'id': c.id,
        'nombre': c.nombre,
        'documento': c.documento or '',
        'telefono': c.telefono or '',
        'email': c.email or ''
    } for c in resultados]

    return jsonify(clientes_json)


# Registrar nuevo cliente desde modal
@main_bp.route('/api/clientes/crear', methods=['POST'])
@login_required
def crear_cliente():
    data = request.get_json()

    try:
        nuevo_cliente = Cliente(
            nombre=data['nombre'],
            documento=data.get('documento', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', '')
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({'success': True, 'cliente': {
            'id': nuevo_cliente.id,
            'nombre': nuevo_cliente.nombre
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

# ------------- Ganancias -----------------

# Mostrar el HTML del reporte
@main_bp.route('/reportes/ganancia')
@login_required
def mostrar_reporte():
    return render_template('reportes/reportes.html')

# Ruta para devolver los datos JSON de ganancias
@main_bp.route('/reportes/ganancia/datos', methods=['GET'])
@login_required
def reporte_ganancia():
    try:
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')

        if not desde or not hasta:
            return jsonify({'success': False, 'error': 'Debe especificar el rango de fechas'})

        # Parseo seguro de fechas
        try:
            desde_dt = datetime.datetime.strptime(desde, "%Y-%m-%d")
            hasta_dt = datetime.datetime.strptime(hasta, "%Y-%m-%d") + datetime.timedelta(days=1)
        except ValueError:
            return jsonify({'success': False, 'error': 'Formato de fecha inválido. Use YYYY-MM-DD.'})

        ingresos = db.session.query(func.coalesce(func.sum(MovimientoCaja.monto), 0))\
            .filter(func.lower(MovimientoCaja.tipo) == 'ingreso')\
            .filter(MovimientoCaja.fecha >= desde_dt)\
            .filter(MovimientoCaja.fecha < hasta_dt).scalar()

        egresos = db.session.query(func.coalesce(func.sum(MovimientoCaja.monto), 0))\
            .filter(func.lower(MovimientoCaja.tipo) == 'egreso')\
            .filter(MovimientoCaja.fecha >= desde_dt)\
            .filter(MovimientoCaja.fecha < hasta_dt).scalar()

        ganancia = ingresos - egresos

        return jsonify({
            'success': True,
            'ingresos': ingresos,
            'egresos': egresos,
            'ganancia': ganancia
        })

    except Exception as e:
        print("Error en reporte_ganancia:", e)
        return jsonify({'success': False, 'error': str(e)})
    

@main_bp.route('/empresa', methods=['GET', 'POST'])
@login_required
def configurar_empresa():
    empresa = Empresa.query.first()

    if request.method == 'POST':
        if not empresa:
            empresa = Empresa()
            db.session.add(empresa)

        empresa.nombre = request.form['nombre']
        empresa.ruc = request.form['ruc']
        empresa.ciudad = request.form['ciudad']
        empresa.direccion = request.form['direccion']
        empresa.telefono = request.form['telefono']
        empresa.timbrado_numero = request.form['timbrado_numero']

        from datetime import datetime

        # Conversión de string a date
        vigencia_desde_str = request.form['timbrado_vigencia_desde']
        vigencia_hasta_str = request.form['timbrado_vigencia_hasta']

        empresa.timbrado_vigencia_desde = datetime.strptime(vigencia_desde_str, '%Y-%m-%d').date() if vigencia_desde_str else None
        empresa.timbrado_vigencia_hasta = datetime.strptime(vigencia_hasta_str, '%Y-%m-%d').date() if vigencia_hasta_str else None

        db.session.commit()
        flash('Datos de la empresa guardados correctamente.', 'success')
        return redirect(url_for('main_bp.configurar_empresa'))

    return render_template('empresa/configuracion.html', empresa=empresa)

#-----------Informes----------------------

#---------------REPORTE DE CAJA POR FECHA---------------
@main_bp.route('/reportes/caja')
@login_required
def mostrar_reporte_caja():
    fecha = datetime.date.today()  # o podés obtener de request.args si querés permitir cambiar fecha
    caja = Caja.query.filter_by(fecha=fecha).first()
    movimientos = MovimientoCaja.query.filter_by(caja_id=caja.id).order_by(MovimientoCaja.fecha).all() if caja else []
    saldo_final = calcular_saldo_cierre(caja) if caja else 0

    return render_template(
        'reportes/reporte_caja.html',
        caja=caja,
        movimientos=movimientos,
        saldo_final=saldo_final
    )


@main_bp.route('/reportes/caja/datos')
@login_required
def datos_reporte_caja():
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        return jsonify({'success': False, 'error': 'Fecha requerida'})

    try:
        fecha_dt = datetime.datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'success': False, 'error': 'Formato de fecha inválido (YYYY-MM-DD)'})

    caja = Caja.query.filter_by(fecha=fecha_dt).first()
    if not caja:
        return jsonify({'success': True, 'caja': None})

    movimientos = MovimientoCaja.query.filter_by(caja_id=caja.id).order_by(MovimientoCaja.fecha).all()
    saldo_final = calcular_saldo_cierre(caja)

    movimientos_json = [{
        'fecha': m.fecha.strftime('%Y-%m-%d %H:%M'),
        'tipo': m.tipo,
        'monto': m.monto,
        'descripcion': m.descripcion
    } for m in movimientos]

    return jsonify({
        'success': True,
        'caja': {
            'fecha': caja.fecha.strftime('%Y-%m-%d'),
            'monto_apertura': caja.monto_apertura,
            'saldo_final': saldo_final
        },
        'movimientos': movimientos_json
    })
@main_bp.route('/reportes/caja/pdf')
@login_required
def exportar_reporte_caja_pdf():
    fecha_str = request.args.get('fecha')
    if not fecha_str:
        return "Fecha no proporcionada", 400

    try:
        fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return "Fecha inválida", 400

    caja = Caja.query.filter_by(fecha=fecha).first()
    movimientos = MovimientoCaja.query.filter_by(caja_id=caja.id).order_by(MovimientoCaja.fecha).all() if caja else []
    saldo_final = calcular_saldo_cierre(caja) if caja else 0

    html = render_template("reportes/reporte_caja_pdf.html", caja=caja, movimientos=movimientos, saldo_final=saldo_final)

    # Generar PDF
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)
    if pisa_status.err:
        return "Error al generar PDF", 500

    pdf.seek(0)
    return send_file(pdf, mimetype='application/pdf', download_name=f"reporte_caja_{fecha}.pdf")

#---------------REPORTE DE STOCK-----------------
@main_bp.route('/reportes/stock')
@login_required
def exportar_reporte_stock_pdf():
    productos = Producto.query.all()

    hoy = datetime.datetime.today()
    mes = hoy.month
    año = hoy.year

    # Total de productos vendidos en el mes actual
    ventas = (
        db.session.query(
            DetalleFactura.producto_id,
            func.sum(DetalleFactura.cantidad).label('total_vendido')
        )
        .join(Factura, DetalleFactura.factura_id == Factura.id)
        .filter(extract('month', Factura.fecha) == mes)
        .filter(extract('year', Factura.fecha) == año)
        .group_by(DetalleFactura.producto_id)
        .all()
    )

    ventas_dict = {v.producto_id: v.total_vendido for v in ventas}

    mas_vendido_id = max(ventas_dict, key=ventas_dict.get, default=None)
    menos_vendido_id = min(ventas_dict, key=ventas_dict.get, default=None)

    mas_vendido = Producto.query.get(mas_vendido_id) if mas_vendido_id else None
    menos_vendido = Producto.query.get(menos_vendido_id) if menos_vendido_id else None

    cantidad_mas_vendida = ventas_dict.get(mas_vendido_id, 0)
    cantidad_menos_vendida = ventas_dict.get(menos_vendido_id, 0)

    html = render_template(
        'reportes/reporte_stock_pdf.html',
        productos=productos,
        mas_vendido=mas_vendido,
        menos_vendido=menos_vendido,
        cantidad_mas_vendida=cantidad_mas_vendida,
        cantidad_menos_vendida=cantidad_menos_vendida
    )

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return f'Error al generar PDF: {pisa_status.err}', 500

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=stock.pdf'
    return response

#-----------------REPORTES DE VENTAS----------------
@main_bp.route('/reportes/ventas/form')
@login_required
def reporte_ventas_form():
    return render_template('reportes/reporte_ventas_form.html')

@main_bp.route('/reportes/ventas')
@login_required
def reporte_ventas():
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)

    if not mes or not anio:
        return "Debe especificar mes y año (parámetros 'mes' y 'anio')", 400

    # Calcular días del mes
    dias_mes = calendar.monthrange(anio, mes)[1]

    # Consultar ingresos agrupados por día
    ingresos_por_dia = db.session.query(
        func.date(MovimientoCaja.fecha).label('dia'),
        func.sum(MovimientoCaja.monto).label('total_ingreso')
    ).filter(
        MovimientoCaja.tipo.ilike('Ingreso'),
        extract('year', MovimientoCaja.fecha) == anio,
        extract('month', MovimientoCaja.fecha) == mes
    ).group_by('dia').all()

    # Consultar egresos agrupados por día
    egresos_por_dia = db.session.query(
        func.date(MovimientoCaja.fecha).label('dia'),
        func.sum(MovimientoCaja.monto).label('total_egreso')
    ).filter(
        MovimientoCaja.tipo.ilike('Egreso'),
        extract('year', MovimientoCaja.fecha) == anio,
        extract('month', MovimientoCaja.fecha) == mes
    ).group_by('dia').all()

    # Convertir a diccionarios para fácil acceso por fecha
    ingresos_dict = {ingreso.dia: ingreso.total_ingreso for ingreso in ingresos_por_dia}
    egresos_dict = {egreso.dia: egreso.total_egreso for egreso in egresos_por_dia}

    # Construir lista días con ingresos y egresos (para todos los días del mes)
    reporte_diario = []
    for dia in range(1, dias_mes + 1):
        fecha = datetime.date(anio, mes, dia)
        ingreso = ingresos_dict.get(fecha, 0)
        egreso = egresos_dict.get(fecha, 0)
        reporte_diario.append({
            'fecha': fecha,
            'ingreso': ingreso,
            'egreso': egreso
        })

    # Totales del mes
    total_ingresos = sum(r['ingreso'] for r in reporte_diario)
    total_egresos = sum(r['egreso'] for r in reporte_diario)
    ganancia = total_ingresos - total_egresos

    # Renderizar PDF
    html = render_template(
        'reportes/reporte_ventas_pdf.html',
        mes=mes,
        anio=anio,
        reporte_diario=reporte_diario,
        total_ingresos=total_ingresos,
        total_egresos=total_egresos,
        ganancia=ganancia
    )

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return f"Error al generar PDF: {pisa_status.err}", 500

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=ventas_{anio}_{mes}.pdf'
    return response

#----------------RG90--------------
@main_bp.route('/rg90')
@login_required
def rg90():
    # Muestra la interfaz para generar y validar RG90
    return render_template('rg90/interfaz.html')


@main_bp.route('/rg90/ajax', methods=['POST'])
@login_required
def rg90_ajax():
    periodo = request.form.get('periodo')
    if not periodo or len(periodo) != 6:
        return jsonify({"ok": False, "errores": ["Período inválido."]})

    try:
        ruta_zip = generar_archivo_rg90(periodo=periodo)
        ruta_csv = ruta_zip.replace('.zip', '.csv')

        errores = []
        with open(ruta_csv, encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for i, linea in enumerate(reader, start=1):
                errores.extend(validar_linea(linea, i))

        if errores:
            return jsonify({"ok": False, "errores": errores})

        nombre_zip = os.path.basename(ruta_zip)
        return jsonify({"ok": True, "archivo": nombre_zip})

    except Exception as e:
        return jsonify({"ok": False, "errores": [str(e)]})


@main_bp.route('/rg90/validar_local', methods=['POST'])
@login_required
def rg90_validar_local():
    data = request.get_json()
    contenido_csv = data.get('contenido_csv')
    if not contenido_csv:
        return jsonify({"ok": False, "errores": ["No se recibió contenido del archivo CSV."]})

    errores = []
    try:
        f = StringIO(contenido_csv)
        reader = csv.reader(f, delimiter=';')
        for i, linea in enumerate(reader, start=1):
            errores.extend(validar_linea(linea, i))

        return jsonify({"ok": not errores, "errores": errores})

    except Exception as e:
        return jsonify({"ok": False, "errores": [str(e)]})

#---------------Compras RG90-------------------
@main_bp.route('/rg90/compras')
@login_required
def rg90_compras():
    return render_template('rg90/interfaz_compras.html')

@main_bp.route('/rg90/compras', methods=['POST'])
@login_required
def rg90_compras_ajax():
    periodo = request.form.get('periodo')
    if not periodo or len(periodo) != 6:
        return jsonify({"ok": False, "errores": ["Período inválido."]})
    try:
        ruta_zip = generar_archivo_rg90_compras(periodo=periodo)
        ruta_csv = ruta_zip.replace('.zip', '.csv')

        errores = []
        with open(ruta_csv, encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for i, linea in enumerate(reader, start=1):
                errores.extend(validar_linea(linea, i))  # Aquí se usa validar_linea

        if errores:
            return jsonify({"ok": False, "errores": errores})
        nombre_zip = os.path.basename(ruta_zip)
        return jsonify({"ok": True, "archivo": nombre_zip})
    except Exception as e:
        return jsonify({"ok": False, "errores": [str(e)]})

@main_bp.route('/rg90/compras/validar_local', methods=['POST'])
@login_required
def rg90_validar_local_compras():
    data = request.get_json()
    contenido_csv = data.get('contenido_csv')
    if not contenido_csv:
        return jsonify({"ok": False, "errores": ["No se recibió contenido del archivo CSV."]})
    errores = []
    try:
        f = StringIO(contenido_csv)
        reader = csv.reader(f, delimiter=';')
        for i, linea in enumerate(reader, start=1):
            errores.extend(validar_linea(linea, i))  # Aquí también validar_linea
        return jsonify({"ok": not errores, "errores": errores})
    except Exception as e:
        return jsonify({"ok": False, "errores": [str(e)]})

#----------------------factura de compra-------------------
# Buscar proveedor por nombre o RUC (para el buscador AJAX)
@main_bp.route('/proveedores/buscar')
@login_required
def buscar_proveedores():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    proveedores = Proveedor.query.filter(
        (Proveedor.nombre.ilike(f'%{q}%')) | (Proveedor.ruc.ilike(f'%{q}%'))
    ).all()

    resultado = [{"id": p.id, "nombre": p.nombre, "ruc": p.ruc} for p in proveedores]
    return jsonify(resultado)


# Crear proveedor rápido desde el frontend
@main_bp.route('/proveedores/crear', methods=['POST'])
@login_required
def crear_proveedor():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    ruc = data.get('ruc', '').strip()

    if not nombre or not ruc:
        return jsonify({"ok": False, "error": "Nombre y RUC son obligatorios."})

    if Proveedor.query.filter_by(ruc=ruc).first():
        return jsonify({"ok": False, "error": "El RUC ya existe."})

    nuevo = Proveedor(nombre=nombre, ruc=ruc)
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({"ok": True, "id": nuevo.id, "nombre": nuevo.nombre, "ruc": nuevo.ruc})


# Crear factura compra
@main_bp.route('/compras/nueva', methods=['GET', 'POST'])
@login_required
def nueva_factura_compra():
    hoy = datetime.date.today()
    caja = Caja.query.filter_by(fecha=hoy, abierta=True).first()

    if request.method == 'POST':
        try:
            proveedor_id = request.form.get('proveedor_id')
            fecha = request.form.get('fecha')
            numero_factura = request.form.get('numero_factura')
            concepto = request.form.get('concepto', '')
            monto_total = float(request.form.get('monto_total', 0))
            tipo_comprobante = request.form.get('tipo_comprobante', '').strip()
            condicion = request.form.get('condicion', '').strip()
            timbrado = request.form.get('timbrado', '').strip() or None
            iva_tipo = request.form.get('iva_tipo')

            # Validaciones
            if not proveedor_id or not proveedor_id.isdigit():
                flash('⚠️ Debe seleccionar un proveedor válido.', 'warning')
                return redirect(url_for('main_bp.nueva_factura_compra'))

            if not numero_factura.strip():
                flash('⚠️ Debe ingresar el número de factura.', 'warning')
                return redirect(url_for('main_bp.nueva_factura_compra'))

            if not tipo_comprobante:
                flash('⚠️ Debe ingresar el tipo de comprobante.', 'warning')
                return redirect(url_for('main_bp.nueva_factura_compra'))

            if not condicion:
                flash('⚠️ Debe ingresar la condición de la compra.', 'warning')
                return redirect(url_for('main_bp.nueva_factura_compra'))

            if iva_tipo not in ['10', '5', '0']:
                flash('⚠️ Debe seleccionar un tipo de IVA válido.', 'warning')
                return redirect(url_for('main_bp.nueva_factura_compra'))

            # Calcular IVA
            iva_10 = iva_5 = exentas = 0.0
            if iva_tipo == '10':
                iva_10 = round(monto_total / 11, 2)
            elif iva_tipo == '5':
                iva_5 = round(monto_total / 21, 2)
            elif iva_tipo == '0':
                exentas = monto_total

            # Crear factura
            factura = FacturaCompra(
                proveedor_id=int(proveedor_id),
                fecha=fecha,
                numero_factura=numero_factura.strip(),
                concepto=concepto.strip(),
                monto_total=monto_total,
                tipo_comprobante=tipo_comprobante,
                condicion=condicion,
                timbrado=timbrado,
                iva_10=iva_10,
                iva_5=iva_5,
                exentas=exentas,
                usuario_id=current_user.id,
                fecha_registro=datetime.datetime.utcnow()
            )
            db.session.add(factura)
            db.session.flush()

            if caja:
                movimiento = MovimientoCaja(
                    caja_id=caja.id,
                    tipo='egreso',
                    monto=monto_total,
                    descripcion=f'Compra: {concepto}',
                    usuario_id=current_user.id
                )
                db.session.add(movimiento)
                db.session.flush()
                factura.movimiento_id = movimiento.id
            else:
                flash('⚠️ Caja no abierta. Se registró la compra, pero no se generó movimiento en caja.', 'warning')

            db.session.commit()
            flash('✅ Factura de compra registrada correctamente.', 'success')
            return redirect(url_for('main_bp.caja_resumen'))

        except Exception as e:
            db.session.rollback()
            print(">>> ERROR AL GUARDAR:", e)
            flash(f'❌ Error al registrar la compra: {e}', 'danger')
            return redirect(url_for('main_bp.nueva_factura_compra'))

    return render_template('compras/nueva.html')
