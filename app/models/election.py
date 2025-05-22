from datetime import datetime
from app import db

class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # legislative, municipal, local, presidential
    year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidates = db.relationship('Candidate', backref='election', lazy=True)
    voting_centers = db.relationship('VotingCenter', backref='election', lazy=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    code_name = db.Column(db.String(50), unique=True, nullable=False)
    profile_photo = db.Column(db.String(255))
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
