import pytest
from app import create_app, db
from app.models.candidate import Candidat

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_creer_candidat(client):
    response = client.post('/api/candidats', json={
        'prenom': 'Test',
        'nom': 'Candidate',
        'parti': 'Test Party',
        'election_id': 1,
        'statut': 'en_attente',
        'cree_par': 1
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Candidat créé avec succès'

def test_modifier_candidat(client):
    # Créer un candidat pour le test
    candidat = Candidat(prenom='Test', nom='Candidate', parti='Test Party', election_id=1, statut='en_attente', cree_par=1)
    db.session.add(candidat)
    db.session.commit()

    response = client.put('/api/candidats/1', json={
        'prenom': 'Updated',
        'nom': 'Candidate',
        'parti': 'Updated Party',
        'election_id': 1,
        'statut': 'approuve',
        'cree_par': 1
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Candidat mis à jour avec succès'

def test_supprimer_candidat(client):
    # Créer un candidat pour le test
    candidat = Candidat(prenom='Test', nom='Candidate', parti='Test Party', election_id=1, statut='en_attente', cree_par=1)
    db.session.add(candidat)
    db.session.commit()

    response = client.delete('/api/candidats/1')
    assert response.status_code == 200
    assert response.json['message'] == 'Candidat supprimé avec succès' 