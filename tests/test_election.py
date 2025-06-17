import pytest
from app import create_app, db
from app.models.election import Election

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_creer_election(client):
    response = client.post('/api/elections', json={
        'nom': 'Test Election',
        'description': 'Description de test',
        'date_debut': '2023-01-01T00:00:00Z',
        'date_fin': '2023-01-02T00:00:00Z',
        'statut': 'brouillon',
        'type': 'presidentielle',
        'cree_par': 1
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Élection créée avec succès'

def test_modifier_election(client):
    # Créer une élection pour le test
    election = Election(nom='Test Election', description='Description de test', date_debut='2023-01-01T00:00:00Z', date_fin='2023-01-02T00:00:00Z', statut='brouillon', type='presidentielle', cree_par=1)
    db.session.add(election)
    db.session.commit()

    response = client.put('/api/elections/1', json={
        'nom': 'Updated Election',
        'description': 'Updated Description',
        'date_debut': '2023-01-01T00:00:00Z',
        'date_fin': '2023-01-02T00:00:00Z',
        'statut': 'en_cours',
        'type': 'presidentielle',
        'cree_par': 1
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Élection mise à jour avec succès'

def test_supprimer_election(client):
    # Créer une élection pour le test
    election = Election(nom='Test Election', description='Description de test', date_debut='2023-01-01T00:00:00Z', date_fin='2023-01-02T00:00:00Z', statut='brouillon', type='presidentielle', cree_par=1)
    db.session.add(election)
    db.session.commit()

    response = client.delete('/api/elections/1')
    assert response.status_code == 200
    assert response.json['message'] == 'Élection supprimée avec succès' 