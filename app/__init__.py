from flask import Flask
from .config import Config
from .extensions import db, jwt
from .views import main 
from flask_login import LoginManager, current_user
from .models.users import User
from flask_migrate import Migrate

migrate = Migrate()

def crear_app():
    app = Flask(__name__)
    
    # Cargar la configuración desde el objeto Config
    app.config.from_object(Config)
    
    # Inicializar las extensiones
    db.init_app(app)
    jwt.init_app(app)
    
    # Inicializar Flask-Migrate
    migrate.init_app(app, db)

    # Inicializar LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    # Registrar el Blueprint principal
    app.register_blueprint(main)
    
    # Context Processor
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    # Función para cargar el usuario
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app