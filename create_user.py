from app import create_app, db
from app.models import Rol, Usuario

app = create_app()

def crear_rol_admin():
    rol = Rol.query.filter_by(nombre='Administrador').first()
    if not rol:
        rol = Rol(nombre='Administrador', descripcion='Rol con todos los permisos')
        db.session.add(rol)
        db.session.commit()
    return rol

def crear_usuario_admin():
    with app.app_context():
        rol_admin = crear_rol_admin()

        usuario = Usuario.query.filter_by(email='admin@example.com').first()
        if usuario:
            print("Usuario admin ya existe")
            return

        usuario = Usuario(
            username='admin',
            email='admin@example.com',
            rol_id=rol_admin.id,
            activo=True
        )
        usuario.set_password('admin')  # ✅ Usa el método del modelo

        db.session.add(usuario)
        db.session.commit()
        print("Usuario admin creado")

if __name__ == "__main__":
    crear_usuario_admin()
