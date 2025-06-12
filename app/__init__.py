from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_bcrypt import Bcrypt  # <-- Importa Bcrypt

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'login'  # Redirige aquí si no está logueado
bcrypt = Bcrypt()  # <-- Instancia Bcrypt



def formato_guaranies(value):
    try:
        # Primero convierte a int para evitar decimales
        entero = int(float(value))
        # Formateo con separadores de miles usando la función nativa de python, pero con punto
        return f"{entero:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value  # Si no es un número válido, retorna el valor original


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)  # <-- Inicializa Bcrypt

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Agregar filtro personalizado Jinja2
    app.jinja_env.filters['guaranies'] = formato_guaranies

    # Importar aquí para evitar import circular
    from app.models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    return app





