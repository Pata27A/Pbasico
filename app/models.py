from app import db
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from app import bcrypt
from flask_login import UserMixin



# ---------------- Roles y Usuarios ----------------

class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))

    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)  # sin límite
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    # Relaciones para saber las acciones del usuario (opcional)
    movimientos_stock = db.relationship('MovimientoStock', backref='usuario', lazy=True)
    movimientos_caja = db.relationship('MovimientoCaja', backref='usuario', lazy=True)
    facturas = db.relationship('Factura', backref='usuario', lazy=True)
    cobranzas = db.relationship('Cobranza', backref='usuario', lazy=True)
    bitacoras = db.relationship('Bitacora', backref='usuario', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)



# -------------- Control de Stock ----------------

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))

    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    precio_costo = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    stock_minimo = db.Column(db.Integer, default=0)  # Para alerta de stock bajo

    stock_actual = db.Column(db.Integer, default=0, nullable=False)  # Ahora editable y guardado en DB

    movimientos = db.relationship('MovimientoStock', backref='producto', lazy=True)

    # Si querés calcular stock según movimientos, usá otro método o propiedad con otro nombre
    def calcular_stock_actual(self):
        entradas = sum(m.cantidad for m in self.movimientos if m.tipo == 'entrada')
        salidas = sum(m.cantidad for m in self.movimientos if m.tipo == 'salida')
        return entradas - salidas


class MovimientoStock(db.Model):
    __tablename__ = 'movimientos_stock'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'entrada' o 'salida'
    cantidad = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.String(255))  # ej. "compra proveedor", "venta factura #123"
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)


# -------------- Control de Caja ----------------

class Caja(db.Model):
    __tablename__ = 'cajas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, unique=True, nullable=False)
    monto_apertura = db.Column(db.Float, nullable=False, default=0)
    monto_cierre = db.Column(db.Float)
    abierta = db.Column(db.Boolean, default=True)

    movimientos = db.relationship('MovimientoCaja', backref='caja', lazy=True)

class MovimientoCaja(db.Model):
    __tablename__ = 'movimientos_caja'
    id = db.Column(db.Integer, primary_key=True)
    caja_id = db.Column(db.Integer, db.ForeignKey('cajas.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'ingreso' o 'egreso'
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)


# -------------- Facturación contado ----------------

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    documento = db.Column(db.String(50), nullable=True)  # CI o RUC opcional
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(100))

    facturas = db.relationship('Factura', backref='cliente', lazy=True)

class Factura(db.Model):
    __tablename__ = 'facturas'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    numero = db.Column(db.String(50), unique=True, nullable=False)  # correlativo
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    impuesto = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='emitida')  # por ejemplo

    detalles = db.relationship('DetalleFactura', backref='factura', lazy=True)
    cobranzas = db.relationship('Cobranza', backref='factura', lazy=True)


class DetalleFactura(db.Model):
    __tablename__ = 'detalle_factura'
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto')


# -------------- Cobranzas ----------------

class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)  # efectivo, tarjeta, cheque, etc

class Cobranza(db.Model):
    __tablename__ = 'cobranzas'
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    monto = db.Column(db.Float, nullable=False)
    metodo_pago_id = db.Column(db.Integer, db.ForeignKey('metodos_pago.id'), nullable=False)
    descripcion = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    metodo_pago = db.relationship('MetodoPago')


# -------------- Control de Ganancia Diaria ----------------

class GananciaDiaria(db.Model):
    __tablename__ = 'ganancias_diarias'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, unique=True, nullable=False)
    total_ganancia = db.Column(db.Float, nullable=False)


# -------------- Historial archivos RG90 ----------------

class ArchivoRG90(db.Model):
    __tablename__ = 'archivos_rg90'
    id = db.Column(db.Integer, primary_key=True)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    nombre_archivo = db.Column(db.String(150), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    estado = db.Column(db.String(50))  # 'generado', 'error', etc


# -------------- Bitácora general de acciones ----------------

class Bitacora(db.Model):
    __tablename__ = 'bitacora'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(255), nullable=False)  # Ej: "Registro producto X", "Cierre de caja"
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    detalles = db.Column(db.Text)  # detalles opcionales (json, texto, etc)

#----------------Datos de la Empresa-----------------------
class Empresa(db.Model):
    __tablename__ = 'empresa'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    ruc = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(150), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(50), nullable=False)
    
    timbrado_numero = db.Column(db.String(20), nullable=False)
    timbrado_vigencia_desde = db.Column(db.Date, nullable=False)
    timbrado_vigencia_hasta = db.Column(db.Date, nullable=False)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
