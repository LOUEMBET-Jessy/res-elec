from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.election import BureauVote, CentreVote, Circonscription
from app.schemas import BureauVoteSchema, ResultatElectionSchema, CirconscriptionSchema, CentreVoteSchema
from app import db
from sqlalchemy import func
from datetime import datetime

voting_bp = Blueprint('voting', __name__, url_prefix='/api/vote')

office_schema = BureauVoteSchema()
result_schema = ResultatElectionSchema()
circonscription_schema = CirconscriptionSchema()
centre_schema = CentreVoteSchema()
bureau_schema = BureauVoteSchema()

@voting_bp.route('/circonscriptions', methods=['GET'])
@jwt_required()
def liste_circonscriptions():
    circonscriptions = Circonscription.query.all()
    return jsonify([circonscription_schema.dump(c) for c in circonscriptions]), 200

@voting_bp.route('/circonscriptions', methods=['POST'])
@jwt_required()
def creer_circonscription():
    data = request.get_json()
    # Vérifier unicité du nom
    if Circonscription.query.filter_by(nom=data.get('nom')).first():
        return jsonify({'message': 'Nom de circonscription déjà utilisé'}), 400
    circonscription = Circonscription(
        nom=data.get('nom'),
        description=data.get('description')
    )
    db.session.add(circonscription)
    db.session.commit()
    return jsonify({'message': 'Circonscription créée', 'circonscription': circonscription_schema.dump(circonscription)}), 201

@voting_bp.route('/circonscriptions/<int:id>', methods=['GET'])
@jwt_required()
def details_circonscription(id):
    c = Circonscription.query.get_or_404(id)
    return jsonify(circonscription_schema.dump(c)), 200

@voting_bp.route('/circonscriptions/<int:id>', methods=['PUT'])
@jwt_required()
def modifier_circonscription(id):
    c = Circonscription.query.get_or_404(id)
    data = request.get_json()
    c.nom = data.get('nom', c.nom)
    c.description = data.get('description', c.description)
    c.date_modification = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Circonscription modifiée', 'circonscription': circonscription_schema.dump(c)}), 200

@voting_bp.route('/circonscriptions/<int:id>', methods=['DELETE'])
@jwt_required()
def supprimer_circonscription(id):
    c = Circonscription.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'Circonscription supprimée'}), 200

@voting_bp.route('/centres', methods=['GET'])
@jwt_required()
def liste_centres():
    centres = CentreVote.query.all()
    return jsonify([centre_schema.dump(c) for c in centres]), 200

@voting_bp.route('/centres', methods=['POST'])
@jwt_required()
def creer_centre():
    data = request.get_json()
    # Vérifier unicité du nom
    if CentreVote.query.filter_by(nom=data.get('nom')).first():
        return jsonify({'message': 'Nom de centre de vote déjà utilisé'}), 400
    if not Circonscription.query.get(data.get('circonscription_id')):
        return jsonify({'message': 'Circonscription inexistante'}), 400
    centre = CentreVote(
        nom=data.get('nom'),
        adresse=data.get('adresse'),
        circonscription_id=data.get('circonscription_id')
    )
    db.session.add(centre)
    db.session.commit()
    return jsonify({'message': 'Centre de vote créé', 'centre': centre_schema.dump(centre)}), 201

@voting_bp.route('/centres/<int:id>', methods=['GET'])
@jwt_required()
def details_centre(id):
    c = CentreVote.query.get_or_404(id)
    return jsonify(centre_schema.dump(c)), 200

@voting_bp.route('/centres/<int:id>', methods=['PUT'])
@jwt_required()
def modifier_centre(id):
    c = CentreVote.query.get_or_404(id)
    data = request.get_json()
    c.nom = data.get('nom', c.nom)
    c.adresse = data.get('adresse', c.adresse)
    c.circonscription_id = data.get('circonscription_id', c.circonscription_id)
    c.date_modification = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Centre de vote modifié', 'centre': centre_schema.dump(c)}), 200

@voting_bp.route('/centres/<int:id>', methods=['DELETE'])
@jwt_required()
def supprimer_centre(id):
    c = CentreVote.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': 'Centre de vote supprimé'}), 200

@voting_bp.route('/bureaux', methods=['GET'])
@jwt_required()
def liste_bureaux():
    bureaux = BureauVote.query.all()
    return jsonify([bureau_schema.dump(b) for b in bureaux]), 200

@voting_bp.route('/bureaux', methods=['POST'])
@jwt_required()
def creer_bureau():
    data = request.get_json()
    # Vérifier unicité du nom
    if BureauVote.query.filter_by(nom=data.get('nom')).first():
        return jsonify({'message': 'Nom de bureau de vote déjà utilisé'}), 400
    if not CentreVote.query.get(data.get('centre_id')):
        return jsonify({'message': 'Centre de vote inexistant'}), 400
    bureau = BureauVote(
        nom=data.get('nom'),
        centre_id=data.get('centre_id'),
        electeurs_inscrits=data.get('electeurs_inscrits', 0),
        personne_contact=data.get('personne_contact'),
        telephone_contact=data.get('telephone_contact'),
        localisation=data.get('localisation'),
        est_actif=data.get('est_actif', True)
    )
    db.session.add(bureau)
    db.session.commit()
    return jsonify({'message': 'Bureau de vote créé', 'bureau': bureau_schema.dump(bureau)}), 201

@voting_bp.route('/bureaux/<int:id>', methods=['GET'])
@jwt_required()
def details_bureau(id):
    b = BureauVote.query.get_or_404(id)
    return jsonify(bureau_schema.dump(b)), 200

@voting_bp.route('/bureaux/<int:id>', methods=['PUT'])
@jwt_required()
def modifier_bureau(id):
    b = BureauVote.query.get_or_404(id)
    data = request.get_json()
    b.nom = data.get('nom', b.nom)
    b.centre_id = data.get('centre_id', b.centre_id)
    b.electeurs_inscrits = data.get('electeurs_inscrits', b.electeurs_inscrits)
    b.personne_contact = data.get('personne_contact', b.personne_contact)
    b.telephone_contact = data.get('telephone_contact', b.telephone_contact)
    b.localisation = data.get('localisation', b.localisation)
    b.est_actif = data.get('est_actif', b.est_actif)
    b.date_modification = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Bureau de vote modifié', 'bureau': bureau_schema.dump(b)}), 200

@voting_bp.route('/bureaux/<int:id>', methods=['DELETE'])
@jwt_required()
def supprimer_bureau(id):
    b = BureauVote.query.get_or_404(id)
    db.session.delete(b)
    db.session.commit()
    return jsonify({'message': 'Bureau de vote supprimé'}), 200

@voting_bp.route('/geojson', methods=['GET'])
@jwt_required()
def geojson_bureaux_vote():
    try:
        bureaux = BureauVote.query.all()
        features = []
        for bureau in bureaux:
            if bureau.localisation and bureau.localisation.get('type') == 'Point':
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': bureau.localisation.get('coordonnees')
                    },
                    'properties': {
                        'id': bureau.id,
                        'nom': bureau.nom,
                        'adresse': bureau.adresse,
                        'region': bureau.region,
                        'departement': bureau.departement,
                        'commune': bureau.commune,
                        'electeurs_inscrits': bureau.electeurs_inscrits,
                        'personne_contact': bureau.personne_contact,
                        'telephone_contact': bureau.telephone_contact,
                        'est_actif': bureau.est_actif
                    }
                })
        return jsonify({
            'type': 'FeatureCollection',
            'features': features
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/office/<int:office_id>/results', methods=['POST'])
@jwt_required()
def submit_results(office_id):
    try:
        office = CentreVote.query.get_or_404(office_id)
        data = request.get_json()

        # Update office statistics
        office.total_voters = data.get('total_voters', 0)
        office.blank_votes = data.get('blank_votes', 0)
        office.null_votes = data.get('null_votes', 0)

        # Delete existing results if any
        VotingResult.query.filter_by(office_id=office_id).delete()

        # Add new results
        results = data.get('results', [])
        for result_data in results:
            result_data['office_id'] = office_id
            result = VotingResult(**result_data)
            db.session.add(result)

        db.session.commit()
        return jsonify({
            'message': 'Voting results submitted successfully',
            'office': office_schema.dump(office)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/office/<int:office_id>/results', methods=['GET'])
@jwt_required()
def get_office_results(office_id):
    try:
        office = CentreVote.query.get_or_404(office_id)
        return jsonify({
            'office': office_schema.dump(office)
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/realtime/<int:election_id>', methods=['GET'])
@jwt_required()
def get_realtime_results(election_id):
    try:
        # Get total statistics
        total_stats = db.session.query(
            func.sum(CentreVote.total_voters).label('total_voters'),
            func.sum(CentreVote.blank_votes).label('blank_votes'),
            func.sum(CentreVote.null_votes).label('null_votes')
        ).join(CentreVote.center).filter_by(election_id=election_id).first()

        # Get results by candidate
        candidate_results = db.session.query(
            VotingResult.candidate_id,
            func.sum(VotingResult.votes).label('total_votes')
        ).join(CentreVote).join(CentreVote.center).filter_by(election_id=election_id).group_by(VotingResult.candidate_id).all()

        results = {
            'total_voters': total_stats.total_voters or 0,
            'blank_votes': total_stats.blank_votes or 0,
            'null_votes': total_stats.null_votes or 0,
            'candidate_results': {str(cr.candidate_id): cr.total_votes for cr in candidate_results}
        }

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/office/<int:office_id>/results', methods=['PUT'])
@jwt_required()
def update_results(office_id):
    try:
        office = CentreVote.query.get_or_404(office_id)
        data = request.get_json()

        # Update office statistics
        if 'total_voters' in data:
            office.total_voters = data['total_voters']
        if 'blank_votes' in data:
            office.blank_votes = data['blank_votes']
        if 'null_votes' in data:
            office.null_votes = data['null_votes']

        # Update results
        if 'results' in data:
            for result_data in data['results']:
                result = VotingResult.query.filter_by(
                    office_id=office_id,
                    candidate_id=result_data['candidate_id']
                ).first()
                
                if result:
                    result.votes = result_data['votes']
                else:
                    result_data['office_id'] = office_id
                    new_result = VotingResult(**result_data)
                    db.session.add(new_result)

        db.session.commit()
        return jsonify({
            'message': 'Results updated successfully',
            'office': office_schema.dump(office)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
