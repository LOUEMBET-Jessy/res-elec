import os
import logging
from logging.handlers import RotatingFileHandler

def configure_logging(app):
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # Configuration du logging
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # Handler pour les fichiers
    file_handler = RotatingFileHandler(
        'logs/res_elec.log',
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Configurer le logger de l'application
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

    # Désactiver le logging de Werkzeug en production
    if app.config['FLASK_ENV'] == 'production':
        logging.getLogger('werkzeug').setLevel(logging.ERROR) 