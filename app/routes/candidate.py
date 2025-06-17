from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.election import Candidate
from app import db
from datetime import datetime

candidate_bp = Blueprint('candidate', __name__, url_prefix='/api/candidats')

@candidate_bp.route('/', methods=['GET'])
@jwt_required()
def liste_candidats():
    try:
        candidats = Candidate.query.all()
        return jsonify([{
            'id': candidat.id,
            'prenom': candidat.prenom,
            'nom': candidat.nom,
            'parti': candidat.parti,
            'logo_parti': candidat.logo_parti,
            'photo': candidat.photo,
            'biographie': candidat.biographie,
            'election_id': candidat.election_id,
            'statut': candidat.statut,
            'cree_par': candidat.cree_par,
            'date_creation': candidat.date_creation,
            'date_modification': candidat.date_modification
        } for candidat in candidats]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/', methods=['POST'])
@jwt_required()
def ajouter_candidat():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        candidat = Candidate(
            prenom=data.get('prenom'),
            nom=data.get('nom'),
            parti=data.get('parti'),
            logo_parti=data.get('logo_parti'),
            photo=data.get('photo'),
            biographie=data.get('biographie'),
            election_id=data.get('election_id'),
            statut=data.get('statut', 'en_attente'),
            cree_par=current_user_id
        )
        db.session.add(candidat)
        db.session.commit()

        return jsonify({
            'message': 'Candidat ajouté avec succès',
            'candidat': {
                'id': candidat.id,
                'prenom': candidat.prenom,
                'nom': candidat.nom,
                'parti': candidat.parti,
                'logo_parti': candidat.logo_parti,
                'photo': candidat.photo,
                'biographie': candidat.biographie,
                'election_id': candidat.election_id,
                'statut': candidat.statut,
                'cree_par': candidat.cree_par,
                'date_creation': candidat.date_creation,
                'date_modification': candidat.date_modification
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/<int:candidat_id>', methods=['GET'])
@jwt_required()
def details_candidat(candidat_id):
    try:
        candidat = Candidate.query.get(candidat_id)
        if not candidat:
            return jsonify({'message': 'Candidat non trouvé'}), 404

        return jsonify({
            'id': candidat.id,
            'prenom': candidat.prenom,
            'nom': candidat.nom,
            'parti': candidat.parti,
            'logo_parti': candidat.logo_parti,
            'photo': candidat.photo,
            'biographie': candidat.biographie,
            'election_id': candidat.election_id,
            'statut': candidat.statut,
            'cree_par': candidat.cree_par,
            'date_creation': candidat.date_creation,
            'date_modification': candidat.date_modification
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/<int:candidat_id>', methods=['PUT'])
@jwt_required()
def modifier_candidat(candidat_id):
    try:
        candidat = Candidate.query.get(candidat_id)
        if not candidat:
            return jsonify({'message': 'Candidat non trouvé'}), 404

        data = request.get_json()
        candidat.prenom = data.get('prenom', candidat.prenom)
        candidat.nom = data.get('nom', candidat.nom)
        candidat.parti = data.get('parti', candidat.parti)
        candidat.logo_parti = data.get('logo_parti', candidat.logo_parti)
        candidat.photo = data.get('photo', candidat.photo)
        candidat.biographie = data.get('biographie', candidat.biographie)
        candidat.election_id = data.get('election_id', candidat.election_id)
        candidat.statut = data.get('statut', candidat.statut)
        candidat.date_modification = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Candidat mis à jour avec succès',
            'candidat': {
                'id': candidat.id,
                'prenom': candidat.prenom,
                'nom': candidat.nom,
                'parti': candidat.parti,
                'logo_parti': candidat.logo_parti,
                'photo': candidat.photo,
                'biographie': candidat.biographie,
                'election_id': candidat.election_id,
                'statut': candidat.statut,
                'cree_par': candidat.cree_par,
                'date_creation': candidat.date_creation,
                'date_modification': candidat.date_modification
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/<int:candidat_id>', methods=['DELETE'])
@jwt_required()
def supprimer_candidat(candidat_id):
    try:
        candidat = Candidate.query.get(candidat_id)
        if not candidat:
            return jsonify({'message': 'Candidat non trouvé'}), 404

        db.session.delete(candidat)
        db.session.commit()

        return jsonify({'message': 'Candidat supprimé avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/<int:candidat_id>/statut', methods=['PUT'])
@jwt_required()
def mettre_a_jour_statut(candidat_id):
    try:
        candidat = Candidate.query.get(candidat_id)
        if not candidat:
            return jsonify({'message': 'Candidat non trouvé'}), 404

        data = request.get_json()
        candidat.statut = data.get('statut', candidat.statut)
        candidat.date_modification = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Statut mis à jour avec succès',
            'candidat': {
                'id': candidat.id,
                'prenom': candidat.prenom,
                'nom': candidat.nom,
                'parti': candidat.parti,
                'logo_parti': candidat.logo_parti,
                'photo': candidat.photo,
                'biographie': candidat.biographie,
                'election_id': candidat.election_id,
                'statut': candidat.statut,
                'cree_par': candidat.cree_par,
                'date_creation': candidat.date_creation,
                'date_modification': candidat.date_modification
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
