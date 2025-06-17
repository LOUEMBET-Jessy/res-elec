from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.election import Election, Candidate, VotingCenter, VotingOffice, VotingResult, ResultatElection
from app.schemas import ElectionSchema, CandidatSchema, BureauDeVoteSchema, ResultatElectionSchema
from app import db
from app.utils.file_upload import save_file
import os
from datetime import datetime

election_bp = Blueprint('election', __name__, url_prefix='/api/elections')
election_schema = ElectionSchema()
elections_schema = ElectionSchema(many=True)

@election_bp.route('/', methods=['GET'])
@jwt_required()
def liste_elections():
    try:
        elections = Election.query.all()
        return jsonify([{
            'id': election.id,
            'nom': election.nom,
            'description': election.description,
            'date_debut': election.date_debut,
            'date_fin': election.date_fin,
            'statut': election.statut,
            'type': election.type,
            'cree_par': election.cree_par,
            'date_creation': election.date_creation,
            'date_modification': election.date_modification
        } for election in elections]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@election_bp.route('/', methods=['POST'])
@jwt_required()
def creer_election():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        # Convertir les dates en supprimant le 'Z' et en utilisant le format ISO
        date_debut = data.get('date_debut').replace('Z', '')
        date_fin = data.get('date_fin').replace('Z', '')

        election = Election(
            nom=data.get('nom'),
            description=data.get('description'),
            date_debut=datetime.fromisoformat(date_debut),
            date_fin=datetime.fromisoformat(date_fin),
            statut=data.get('statut', 'brouillon'),
            type=data.get('type'),
            cree_par=current_user_id
        )
        db.session.add(election)
        db.session.commit()

        return jsonify({
            'message': 'Élection créée avec succès',
            'election': {
                'id': election.id,
                'nom': election.nom,
                'description': election.description,
                'date_debut': election.date_debut,
                'date_fin': election.date_fin,
                'statut': election.statut,
                'type': election.type,
                'cree_par': election.cree_par,
                'date_creation': election.date_creation,
                'date_modification': election.date_modification
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>', methods=['GET'])
@jwt_required()
def details_election(election_id):
    try:
        election = Election.query.get(election_id)
        if not election:
            return jsonify({'message': 'Élection non trouvée'}), 404

        return jsonify({
            'id': election.id,
            'nom': election.nom,
            'description': election.description,
            'date_debut': election.date_debut,
            'date_fin': election.date_fin,
            'statut': election.statut,
            'type': election.type,
            'cree_par': election.cree_par,
            'date_creation': election.date_creation,
            'date_modification': election.date_modification
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>', methods=['PUT'])
@jwt_required()
def modifier_election(election_id):
    try:
        election = Election.query.get(election_id)
        if not election:
            return jsonify({'message': 'Élection non trouvée'}), 404

        data = request.get_json()
        election.nom = data.get('nom', election.nom)
        election.description = data.get('description', election.description)
        election.date_debut = datetime.strptime(data.get('date_debut'), '%Y-%m-%dT%H:%M:%S') if data.get('date_debut') else election.date_debut
        election.date_fin = datetime.strptime(data.get('date_fin'), '%Y-%m-%dT%H:%M:%S') if data.get('date_fin') else election.date_fin
        election.statut = data.get('statut', election.statut)
        election.type = data.get('type', election.type)
        election.date_modification = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Élection mise à jour avec succès',
            'election': {
                'id': election.id,
                'nom': election.nom,
                'description': election.description,
                'date_debut': election.date_debut,
                'date_fin': election.date_fin,
                'statut': election.statut,
                'type': election.type,
                'cree_par': election.cree_par,
                'date_creation': election.date_creation,
                'date_modification': election.date_modification
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>', methods=['DELETE'])
@jwt_required()
def supprimer_election(election_id):
    try:
        election = Election.query.get(election_id)
        if not election:
            return jsonify({'message': 'Élection non trouvée'}), 404

        db.session.delete(election)
        db.session.commit()

        return jsonify({'message': 'Élection supprimée avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>/resultats', methods=['GET'])
@jwt_required()
def consulter_resultats(election_id):
    try:
        resultats = ResultatElection.query.filter_by(election_id=election_id).all()
        return jsonify([{
            'id': resultat.id,
            'election_id': resultat.election_id,
            'bureau_vote_id': resultat.bureau_vote_id,
            'electeurs_inscrits': resultat.electeurs_inscrits,
            'total_votes': resultat.total_votes,
            'votes_valides': resultat.votes_valides,
            'votes_invalides': resultat.votes_invalides,
            'votes_blancs': resultat.votes_blancs,
            'resultats_candidats': resultat.resultats_candidats,
            'soumis_par': resultat.soumis_par,
            'date_soumission': resultat.date_soumission,
            'statut': resultat.statut,
            'remarques': resultat.remarques,
            'date_creation': resultat.date_creation,
            'date_modification': resultat.date_modification
        } for resultat in resultats]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>/resultats', methods=['POST'])
@jwt_required()
def soumettre_resultats(election_id):
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        resultat = ResultatElection(
            election_id=election_id,
            bureau_vote_id=data.get('bureau_vote_id'),
            electeurs_inscrits=data.get('electeurs_inscrits'),
            total_votes=data.get('total_votes'),
            votes_valides=data.get('votes_valides'),
            votes_invalides=data.get('votes_invalides'),
            votes_blancs=data.get('votes_blancs'),
            resultats_candidats=data.get('resultats_candidats'),
            soumis_par=current_user_id,
            date_soumission=datetime.utcnow(),
            statut=data.get('statut', 'brouillon'),
            remarques=data.get('remarques')
        )
        db.session.add(resultat)
        db.session.commit()

        return jsonify({
            'message': 'Résultats soumis avec succès',
            'resultat': {
                'id': resultat.id,
                'election_id': resultat.election_id,
                'bureau_vote_id': resultat.bureau_vote_id,
                'electeurs_inscrits': resultat.electeurs_inscrits,
                'total_votes': resultat.total_votes,
                'votes_valides': resultat.votes_valides,
                'votes_invalides': resultat.votes_invalides,
                'votes_blancs': resultat.votes_blancs,
                'resultats_candidats': resultat.resultats_candidats,
                'soumis_par': resultat.soumis_par,
                'date_soumission': resultat.date_soumission,
                'statut': resultat.statut,
                'remarques': resultat.remarques,
                'date_creation': resultat.date_creation,
                'date_modification': resultat.date_modification
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>/statistiques', methods=['GET'])
@jwt_required()
def statistiques_election(election_id):
    try:
        resultats = ResultatElection.query.filter_by(election_id=election_id).all()
        total_electeurs = sum(resultat.electeurs_inscrits for resultat in resultats)
        total_votes = sum(resultat.total_votes for resultat in resultats)
        total_valides = sum(resultat.votes_valides for resultat in resultats)
        total_invalides = sum(resultat.votes_invalides for resultat in resultats)
        total_blancs = sum(resultat.votes_blancs for resultat in resultats)

        return jsonify({
            'total_electeurs': total_electeurs,
            'total_votes': total_votes,
            'total_valides': total_valides,
            'total_invalides': total_invalides,
            'total_blancs': total_blancs
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Voting center routes
@election_bp.route('/<int:election_id>/centers', methods=['POST'])
@jwt_required()
def add_voting_center(election_id):
    try:
        data = request.get_json()
        data['election_id'] = election_id
        
        center = VotingCenter(**data)
        db.session.add(center)
        db.session.commit()

        return jsonify({
            'message': 'Voting center added successfully',
            'center': BureauDeVoteSchema().dump(center)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Voting office routes
@election_bp.route('/centers/<int:center_id>/offices', methods=['POST'])
@jwt_required()
def add_voting_office(center_id):
    try:
        data = request.get_json()
        data['center_id'] = center_id
        
        office = VotingOffice(**data)
        db.session.add(office)
        db.session.commit()

        return jsonify({
            'message': 'Voting office added successfully',
            'office': BureauDeVoteSchema().dump(office)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Voting results routes
@election_bp.route('/offices/<int:office_id>/results', methods=['POST'])
@jwt_required()
def add_voting_results(office_id):
    try:
        data = request.get_json()
        office = VotingOffice.query.get_or_404(office_id)
        
        # Update office statistics
        office.total_voters = data.get('total_voters', 0)
        office.blank_votes = data.get('blank_votes', 0)
        office.null_votes = data.get('null_votes', 0)
        
        # Add candidate results
        results = data.get('results', [])
        for result in results:
            result['office_id'] = office_id
            voting_result = VotingResult(**result)
            db.session.add(voting_result)
        
        db.session.commit()
        return jsonify({
            'message': 'Voting results added successfully',
            'office': BureauDeVoteSchema().dump(office)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Get election results
@election_bp.route('/<int:election_id>/results', methods=['GET'])
@jwt_required()
def get_election_results(election_id):
    try:
        election = Election.query.get_or_404(election_id)
        centers = VotingCenter.query.filter_by(election_id=election_id).all()
        
        results = {
            'election': election_schema.dump(election),
            'total_voters': 0,
            'blank_votes': 0,
            'null_votes': 0,
            'candidate_results': {},
            'centers': []
        }
        
        for center in centers:
            center_data = BureauDeVoteSchema().dump(center)
            center_total_voters = 0
            center_blank_votes = 0
            center_null_votes = 0
            
            for office in center.voting_offices:
                center_total_voters += office.total_voters
                center_blank_votes += office.blank_votes
                center_null_votes += office.null_votes
                
                for result in office.results:
                    candidate_id = result.candidate_id
                    if candidate_id not in results['candidate_results']:
                        results['candidate_results'][candidate_id] = 0
                    results['candidate_results'][candidate_id] += result.votes
            
            center_data['total_voters'] = center_total_voters
            center_data['blank_votes'] = center_blank_votes
            center_data['null_votes'] = center_null_votes
            results['centers'].append(center_data)
            
            results['total_voters'] += center_total_voters
            results['blank_votes'] += center_blank_votes
            results['null_votes'] += center_null_votes
        
        return jsonify(results), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500
