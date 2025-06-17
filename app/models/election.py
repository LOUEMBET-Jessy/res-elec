from datetime import datetime
from app import db

class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date_debut = db.Column(db.DateTime, nullable=False)
    date_fin = db.Column(db.DateTime, nullable=False)
    statut = db.Column(db.String(20), default='brouillon')  # 'brouillon', 'a_venir', 'en_cours', 'terminee', 'annulee'
    type = db.Column(db.String(50), nullable=False)  # 'presidentielle', 'legislative', 'municipale', 'regionale'
    cree_par = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidates = db.relationship('Candidate', backref='election', lazy=True)
    voting_centers = db.relationship('VotingCenter', backref='election', lazy=True)

    def __repr__(self):
        return f"<Election {self.nom}>"

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    parti = db.Column(db.String(100), nullable=False)
    logo_parti = db.Column(db.String(255))
    photo = db.Column(db.String(255))
    biographie = db.Column(db.Text)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    statut = db.Column(db.String(20), default='en_attente')  # 'en_attente', 'approuve', 'rejete'
    cree_par = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Candidate {self.prenom} {self.nom}>"

class VotingCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    voting_offices = db.relationship('VotingOffice', backref='center', lazy=True)

class VotingOffice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    center_id = db.Column(db.Integer, db.ForeignKey('voting_center.id'), nullable=False)
    total_voters = db.Column(db.Integer, default=0)
    blank_votes = db.Column(db.Integer, default=0)
    null_votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    results = db.relationship('VotingResult', backref='office', lazy=True)

class VotingResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    office_id = db.Column(db.Integer, db.ForeignKey('voting_office.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BureauDeVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    adresse = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    departement = db.Column(db.String(100), nullable=False)
    commune = db.Column(db.String(100), nullable=False)
    localisation = db.Column(db.JSON)  # { type: 'Point', coordonnees: [longitude, latitude] }
    electeurs_inscrits = db.Column(db.Integer, default=0)
    personne_contact = db.Column(db.String(100))
    telephone_contact = db.Column(db.String(20))
    est_actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<BureauDeVote {self.nom}>"

class ResultatElection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    bureau_vote_id = db.Column(db.Integer, db.ForeignKey('bureau_de_vote.id'), nullable=False)
    electeurs_inscrits = db.Column(db.Integer, default=0)
    total_votes = db.Column(db.Integer, default=0)
    votes_valides = db.Column(db.Integer, default=0)
    votes_invalides = db.Column(db.Integer, default=0)
    votes_blancs = db.Column(db.Integer, default=0)
    resultats_candidats = db.Column(db.JSON)  # [{ candidat_id: string, nombre_voix: int }]
    soumis_par = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_soumission = db.Column(db.DateTime, nullable=False)
    statut = db.Column(db.String(20), default='brouillon')  # 'brouillon', 'soumis', 'valide', 'rejete'
    remarques = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ResultatElection {self.id}>"
