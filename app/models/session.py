from datetime import datetime
from app import db

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    jeton = db.Column(db.String(255), unique=True, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)
    agent_utilisateur = db.Column(db.String(255))
    adresse_ip = db.Column(db.String(50))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Session {self.id}>" 