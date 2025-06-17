import pytest
from app import create_app, db
from app.models.voting import BureauDeVote

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_creer_bureau_vote(client):
    response = client.post('/api/bureaux-vote', json={
        'nom': 'Test Bureau',
        'adresse': '123 Test Street',
        'region': 'Test Region',
        'departement': 'Test Department',
        'commune': 'Test Commune',
        'localisation': {'lat': 0, 'lng': 0},
        'electeurs_inscrits': 100,
        'personne_contact': 'Test Contact',
        'telephone_contact': '1234567890',
        'est_actif': True
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Bureau de vote créé avec succès'

def test_modifier_bureau_vote(client):
    # Créer un bureau de vote pour le test
    bureau = BureauDeVote(nom='Test Bureau', adresse='123 Test Street', region='Test Region', departement='Test Department', commune='Test Commune', localisation={'lat': 0, 'lng': 0}, electeurs_inscrits=100, personne_contact='Test Contact', telephone_contact='1234567890', est_actif=True)
    db.session.add(bureau)
    db.session.commit()

    response = client.put('/api/bureaux-vote/1', json={
        'nom': 'Updated Bureau',
        'adresse': 'Updated Address',
        'region': 'Updated Region',
        'departement': 'Updated Department',
        'commune': 'Updated Commune',
        'localisation': {'lat': 1, 'lng': 1},
        'electeurs_inscrits': 200,
        'personne_contact': 'Updated Contact',
        'telephone_contact': '0987654321',
        'est_actif': False
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Bureau de vote mis à jour avec succès'

def test_supprimer_bureau_vote(client):
    # Créer un bureau de vote pour le test
    bureau = BureauDeVote(nom='Test Bureau', adresse='123 Test Street', region='Test Region', departement='Test Department', commune='Test Commune', localisation={'lat': 0, 'lng': 0}, electeurs_inscrits=100, personne_contact='Test Contact', telephone_contact='1234567890', est_actif=True)
    db.session.add(bureau)
    db.session.commit()

    response = client.delete('/api/bureaux-vote/1')
    assert response.status_code == 200
    assert response.json['message'] == 'Bureau de vote supprimé avec succès' 