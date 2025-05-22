from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    campaign_logo = db.Column(db.String(255))
    profile_photo = db.Column(db.String(255))
    province = db.Column(db.String(100), nullable=False)
    commune = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    # campaign_start_date = db.Column(db.DateTime, nullable=False)
    # campaign_end_date = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(20), default='collaborator')  # director or collaborator
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.email}>"
