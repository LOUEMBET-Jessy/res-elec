from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.election import VotingOffice, VotingResult, BureauDeVote
from app.schemas import BureauDeVoteSchema, ResultatElectionSchema
from app import db
from sqlalchemy import func
from datetime import datetime

voting_bp = Blueprint('voting', __name__, url_prefix='/api/bureaux-vote')
office_schema = BureauDeVoteSchema()
result_schema = ResultatElectionSchema()

@voting_bp.route('/', methods=['GET'])
@jwt_required()
def liste_bureaux_vote():
    try:
        bureaux = BureauDeVote.query.all()
        return jsonify([{
            'id': bureau.id,
            'nom': bureau.nom,
            'adresse': bureau.adresse,
            'region': bureau.region,
            'departement': bureau.departement,
            'commune': bureau.commune,
            'localisation': bureau.localisation,
            'electeurs_inscrits': bureau.electeurs_inscrits,
            'personne_contact': bureau.personne_contact,
            'telephone_contact': bureau.telephone_contact,
            'est_actif': bureau.est_actif,
            'date_creation': bureau.date_creation,
            'date_modification': bureau.date_modification
        } for bureau in bureaux]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/', methods=['POST'])
@jwt_required()
def creer_bureau_vote():
    try:
        data = request.get_json()
        bureau = BureauDeVote(
            nom=data.get('nom'),
            adresse=data.get('adresse'),
            region=data.get('region'),
            departement=data.get('departement'),
            commune=data.get('commune'),
            localisation=data.get('localisation'),
            electeurs_inscrits=data.get('electeurs_inscrits', 0),
            personne_contact=data.get('personne_contact'),
            telephone_contact=data.get('telephone_contact'),
            est_actif=data.get('est_actif', True)
        )
        db.session.add(bureau)
        db.session.commit()

        return jsonify({
            'message': 'Bureau de vote créé avec succès',
            'bureau': {
                'id': bureau.id,
                'nom': bureau.nom,
                'adresse': bureau.adresse,
                'region': bureau.region,
                'departement': bureau.departement,
                'commune': bureau.commune,
                'localisation': bureau.localisation,
                'electeurs_inscrits': bureau.electeurs_inscrits,
                'personne_contact': bureau.personne_contact,
                'telephone_contact': bureau.telephone_contact,
                'est_actif': bureau.est_actif,
                'date_creation': bureau.date_creation,
                'date_modification': bureau.date_modification
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/<int:bureau_id>', methods=['GET'])
@jwt_required()
def details_bureau_vote(bureau_id):
    try:
        bureau = BureauDeVote.query.get(bureau_id)
        if not bureau:
            return jsonify({'message': 'Bureau de vote non trouvé'}), 404

        return jsonify({
            'id': bureau.id,
            'nom': bureau.nom,
            'adresse': bureau.adresse,
            'region': bureau.region,
            'departement': bureau.departement,
            'commune': bureau.commune,
            'localisation': bureau.localisation,
            'electeurs_inscrits': bureau.electeurs_inscrits,
            'personne_contact': bureau.personne_contact,
            'telephone_contact': bureau.telephone_contact,
            'est_actif': bureau.est_actif,
            'date_creation': bureau.date_creation,
            'date_modification': bureau.date_modification
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/<int:bureau_id>', methods=['PUT'])
@jwt_required()
def modifier_bureau_vote(bureau_id):
    try:
        bureau = BureauDeVote.query.get(bureau_id)
        if not bureau:
            return jsonify({'message': 'Bureau de vote non trouvé'}), 404

        data = request.get_json()
        bureau.nom = data.get('nom', bureau.nom)
        bureau.adresse = data.get('adresse', bureau.adresse)
        bureau.region = data.get('region', bureau.region)
        bureau.departement = data.get('departement', bureau.departement)
        bureau.commune = data.get('commune', bureau.commune)
        bureau.localisation = data.get('localisation', bureau.localisation)
        bureau.electeurs_inscrits = data.get('electeurs_inscrits', bureau.electeurs_inscrits)
        bureau.personne_contact = data.get('personne_contact', bureau.personne_contact)
        bureau.telephone_contact = data.get('telephone_contact', bureau.telephone_contact)
        bureau.est_actif = data.get('est_actif', bureau.est_actif)
        bureau.date_modification = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Bureau de vote mis à jour avec succès',
            'bureau': {
                'id': bureau.id,
                'nom': bureau.nom,
                'adresse': bureau.adresse,
                'region': bureau.region,
                'departement': bureau.departement,
                'commune': bureau.commune,
                'localisation': bureau.localisation,
                'electeurs_inscrits': bureau.electeurs_inscrits,
                'personne_contact': bureau.personne_contact,
                'telephone_contact': bureau.telephone_contact,
                'est_actif': bureau.est_actif,
                'date_creation': bureau.date_creation,
                'date_modification': bureau.date_modification
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/<int:bureau_id>', methods=['DELETE'])
@jwt_required()
def supprimer_bureau_vote(bureau_id):
    try:
        bureau = BureauDeVote.query.get(bureau_id)
        if not bureau:
            return jsonify({'message': 'Bureau de vote non trouvé'}), 404

        db.session.delete(bureau)
        db.session.commit()

        return jsonify({'message': 'Bureau de vote supprimé avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@voting_bp.route('/geojson', methods=['GET'])
@jwt_required()
def geojson_bureaux_vote():
    try:
        bureaux = BureauDeVote.query.all()
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
        office = VotingOffice.query.get_or_404(office_id)
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
        office = VotingOffice.query.get_or_404(office_id)
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
            func.sum(VotingOffice.total_voters).label('total_voters'),
            func.sum(VotingOffice.blank_votes).label('blank_votes'),
            func.sum(VotingOffice.null_votes).label('null_votes')
        ).join(VotingOffice.center).filter_by(election_id=election_id).first()

        # Get results by candidate
        candidate_results = db.session.query(
            VotingResult.candidate_id,
            func.sum(VotingResult.votes).label('total_votes')
        ).join(VotingOffice).join(VotingOffice.center).filter_by(election_id=election_id).group_by(VotingResult.candidate_id).all()

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
        office = VotingOffice.query.get_or_404(office_id)
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
