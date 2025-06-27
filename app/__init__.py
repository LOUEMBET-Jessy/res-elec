from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from config.config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.election import election_bp
    from app.routes.candidate import candidate_bp
    from app.routes.voting import voting_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(election_bp, url_prefix='/api/elections')
    app.register_blueprint(candidate_bp, url_prefix='/api/candidates')
    app.register_blueprint(voting_bp)

    return app
