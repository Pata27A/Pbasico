import datetime
import json
from sqlite3 import IntegrityError
import traceback
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from app.forms import LoginForm, ProductoForm
from app.models import Caja, Cliente, Cobranza, DetalleFactura, Factura, MetodoPago, MovimientoCaja, Producto, Usuario, Categoria
from app import db
from app.utils import generar_numero_factura

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
@main_bp.route('/stock')
@login_required
def stock():
    return "Aquí va la Gestión de Stock"

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
            stock_actual=form.stock_actual.data or 0
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado correctamente.', 'success')
        productos = Producto.query.all()
        return render_template('stock/listar_productos.html', productos=productos)

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
    return render_template('facturacion/nueva_factura_pos.html',
                           productos=productos,
                           clientes=clientes,
                           metodos_pago=metodos_pago)

@main_bp.route('/facturacion/guardar', methods=['POST'])
@login_required
def guardar_factura():
    try:
        data = request.get_json()

        cliente_id = data.get('cliente_id')
        detalles = data.get('detalles', [])
        pagos = data.get('pagos', [])
        total_factura = data.get('total', 0)
        impuesto = data.get('impuesto', 0)

        # Generamos el número automáticamente
        nuevo_numero = generar_numero_factura()

        nueva_factura = Factura(
            numero=nuevo_numero,
            fecha=datetime.datetime.utcnow(),
            cliente_id=cliente_id if cliente_id else None,
            total=total_factura,
            impuesto=impuesto,
            usuario_id=current_user.id
        )
        db.session.add(nueva_factura)
        db.session.flush()

        for item in detalles:
            producto = db.session.query(Producto).with_for_update().filter_by(codigo=item['codigo']).first()
            if not producto:
                raise ValueError(f"Producto con código {item['codigo']} no encontrado")

            cantidad = float(item['cantidad'])

            if producto.stock_actual < cantidad:
                raise ValueError(f"Stock insuficiente para el producto {producto.nombre}. Disponible: {producto.stock_actual}, requerido: {cantidad}")

            producto.stock_actual -= cantidad

            detalle = DetalleFactura(
                factura_id=nueva_factura.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=float(item['precio_unitario']),
                subtotal=float(item['subtotal'])
            )
            db.session.add(detalle)

        for pago in pagos:
            pago_db = Cobranza(
                factura_id=nueva_factura.id,
                metodo_pago_id=int(pago['metodo_pago_id']),
                monto=float(pago['monto']),
                descripcion=pago.get('descripcion', ''),
                usuario_id=current_user.id
            )
            db.session.add(pago_db)

            # Registrar movimiento de caja solo si hay caja abierta
            caja = obtener_caja_abierta()
            if caja:
                movimiento = MovimientoCaja(
                    caja_id=caja.id,
                    tipo='Ingreso',
                    monto=pago_db.monto,
                    descripcion=f'Cobro de factura {nueva_factura.numero}',
                    usuario_id=current_user.id
                )
                db.session.add(movimiento)
            else:
                print("No hay caja abierta para registrar movimiento")

        db.session.commit()
        return jsonify({'success': True, 'factura_id': nueva_factura.id})

    except IntegrityError as e:
        db.session.rollback()
        print("Error de integridad:", e)
        return jsonify({'success': False, 'error': 'Número de factura duplicado'})
    except Exception as e:
        db.session.rollback()
        print("Error general:", e)
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})



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
def imprimir_factura(id):
    factura = Factura.query.get_or_404(id)
    return render_template('facturacion/imprimir.html', factura=factura)

@main_bp.route('/facturacion/listado')
@login_required
def listado_facturas():
    facturas = Factura.query.order_by(Factura.fecha.desc()).all()
    return render_template('facturacion/listado.html', facturas=facturas)

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

#-----------Informes----------------------

@main_bp.route('/informes')
@login_required
def informes():
    return "Aquí van los Informes"

@main_bp.route('/rg90')
@login_required
def rg90():
    return "Aquí va la Exportación RG90"
