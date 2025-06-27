from app import db
with db.engine.connect() as connection:
    connection.execute("DROP TABLE IF EXISTS alembic_version")
    print("✔ Table alembic_version supprimée.")
