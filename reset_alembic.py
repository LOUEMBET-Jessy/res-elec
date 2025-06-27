import sys
import os
from sqlalchemy import text

# Ajout du chemin vers le dossier contenant le package app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import db, create_app

app = create_app()

with app.app_context():
    with db.engine.connect() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
        print("Table 'alembic_version' supprimée avec succès.")
