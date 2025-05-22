from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config.config import Config
from config.logging import configure_logging
from app.utils.file_storage import FileStorage

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
file_storage = FileStorage()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    configure_logging(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    file_storage.init_app(app)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.election import election_bp
    from app.routes.candidate import candidate_bp
    from app.routes.voting import voting_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(election_bp, url_prefix='/api/elections')
    app.register_blueprint(candidate_bp, url_prefix='/api/candidates')
    app.register_blueprint(voting_bp, url_prefix='/api/voting')

    # Log startup
    app.logger.info('Application démarrée en mode %s', os.getenv('APP_ENV', 'development'))

    return app
