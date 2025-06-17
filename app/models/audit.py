from datetime import datetime
from app import db

class JournalAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)  # Ex : 'connexion_utilisateur', 'creation_election', 'soumission_resultats'
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agent_utilisateur = db.Column(db.String(255))
    adresse_ip = db.Column(db.String(50))
    metadonnees = db.Column(db.JSON)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<JournalAudit {self.action}>" 