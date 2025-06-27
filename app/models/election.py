from datetime import datetime
from app import db

class Election(db.Model):
    __tablename__ = 'election'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime, nullable=False)
    statut = db.Column(db.String(20), default='brouillon')  # 'brouillon', 'a_venir', 'en_cours', 'terminee', 'annulee'
    type = db.Column(db.String(50), nullable=False)  # 'presidentielle', 'legislative', 'municipale', 'regionale'
    cree_par = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_election_user'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidates = db.relationship('Candidate', backref='election', lazy=True)

    def __repr__(self):
        return f"<Election {self.nom}>"


class Candidate(db.Model):
    __tablename__ = 'candidate'
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    parti = db.Column(db.String(100), nullable=False)
    logo_parti = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    biographie = db.Column(db.Text)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id', name='fk_candidate_election'), nullable=False)
    statut = db.Column(db.String(20), default='en_attente')  # 'en_attente', 'approuve', 'rejete'
    cree_par = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_candidate_user'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Candidate {self.prenom} {self.nom}>"


class Circonscription(db.Model):
    __tablename__ = 'circonscription'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    centres = db.relationship('CentreVote', backref='circonscription', lazy=True)

    def __repr__(self):
        return f"<Circonscription {self.nom}>"


class CentreVote(db.Model):
    __tablename__ = 'centre_vote'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    adresse = db.Column(db.String(255), nullable=False)
    circonscription_id = db.Column(db.Integer, db.ForeignKey('circonscription.id', name='fk_centre_circonscription'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bureaux = db.relationship('BureauVote', backref='centre', lazy=True)

    def __repr__(self):
        return f"<CentreVote {self.nom}>"


class BureauVote(db.Model):
    __tablename__ = 'bureau_de_vote'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    centre_id = db.Column(db.Integer, db.ForeignKey('centre_vote.id', name='fk_bureau_centre'), nullable=False)
    electeurs_inscrits = db.Column(db.Integer, default=0)
    personne_contact = db.Column(db.String(100))
    telephone_contact = db.Column(db.String(20))
    localisation = db.Column(db.JSON)
    est_actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<BureauVote {self.nom}>"


class ResultatElection(db.Model):
    __tablename__ = 'resultat_election'
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id', name='fk_resultat_election'), nullable=False)
    bureau_vote_id = db.Column(db.Integer, db.ForeignKey('bureau_de_vote.id', name='fk_resultat_bureau'), nullable=False)
    electeurs_inscrits = db.Column(db.Integer, default=0)
    total_votes = db.Column(db.Integer, default=0)
    votes_valides = db.Column(db.Integer, default=0)
    votes_invalides = db.Column(db.Integer, default=0)
    votes_blancs = db.Column(db.Integer, default=0)
    resultats_candidats = db.Column(db.JSON)  # [{ candidat_id: string, nombre_voix: int }]
    soumis_par = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_resultat_user'), nullable=False)
    date_soumission = db.Column(db.DateTime, nullable=False)
    statut = db.Column(db.String(20), default='brouillon')  # 'brouillon', 'soumis', 'valide', 'rejete'
    remarques = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ResultatElection {self.id}>"
