import pytest
from app import create_app, db
from app.models.user import User
from app.models.session import Session

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_creer_utilisateur(client):
    response = client.post('/api/utilisateurs', json={
        'email': 'test@example.com',
        'prenom': 'Test',
        'nom': 'User',
        'role': 'agent_election'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Utilisateur créé avec succès'

def test_connexion(client):
    # Créer un utilisateur pour le test
    user = User(email='test@example.com', prenom='Test', nom='User', role='agent_election')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    response = client.post('/api/auth/connexion', json={
        'email': 'test@example.com',
        'mot_de_passe': 'password'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_deconnexion(client):
    # Créer un utilisateur et une session pour le test
    user = User(email='test@example.com', prenom='Test', nom='User', role='agent_election')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    # Connexion pour obtenir un token
    login_response = client.post('/api/auth/connexion', json={
        'email': 'test@example.com',
        'mot_de_passe': 'password'
    })
    access_token = login_response.json['access_token']

    response = client.post('/api/auth/deconnexion', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert response.json['message'] == 'Déconnexion réussie' 