import pytest
from app import create_app, db
from app.models.audit import JournalAudit

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_liste_audit(client):
    # Créer une entrée de journal pour le test
    entry = JournalAudit(action='Test Action', utilisateur_id=1, agent_utilisateur='Test Agent', adresse_ip='127.0.0.1', metadonnees={'key': 'value'})
    db.session.add(entry)
    db.session.commit()

    response = client.get('/api/audit')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['action'] == 'Test Action'

def test_details_audit(client):
    # Créer une entrée de journal pour le test
    entry = JournalAudit(action='Test Action', utilisateur_id=1, agent_utilisateur='Test Agent', adresse_ip='127.0.0.1', metadonnees={'key': 'value'})
    db.session.add(entry)
    db.session.commit()

    response = client.get('/api/audit/1')
    assert response.status_code == 200
    assert response.json['action'] == 'Test Action' 