from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.election import Candidate
from app import db
from datetime import datetime
from app.utils.file_upload import save_file

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
        current_user_id = get_jwt_identity()
        print("form:", request.form)
        print("files:", request.files)
        prenom = request.form.get('prenom')
        nom = request.form.get('nom')
        parti = request.form.get('parti')
        biographie = request.form.get('biographie')
        election_id = request.form.get('election_id')
        statut = request.form.get('statut', 'en_attente')
        logo_parti = None
        photo = None

        # Gestion des fichiers
        if 'logo_parti' in request.files:
            logo_file = request.files['logo_parti']
            # Sauvegarde le fichier et récupère le chemin (à adapter selon ta logique)
            logo_parti = save_file(logo_file, 'logos')  # à adapter selon ta fonction
        if 'photo' in request.files:
            photo_file = request.files['photo']
            photo = save_file(photo_file, 'profiles')  # à adapter selon ta fonction

        candidat = Candidate(
            prenom=prenom,
            nom=nom,
            parti=parti,
            logo_parti=logo_parti,
            photo=photo,
            biographie=biographie,
            election_id=election_id,
            statut=statut,
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

        # Si c'est du form-data (pour fichiers)
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            prenom = request.form.get('prenom', candidat.prenom)
            nom = request.form.get('nom', candidat.nom)
            parti = request.form.get('parti', candidat.parti)
            biographie = request.form.get('biographie', candidat.biographie)
            election_id = request.form.get('election_id', candidat.election_id)
            statut = request.form.get('statut', candidat.statut)

            # Gestion des fichiers
            if 'logo_parti' in request.files:
                logo_file = request.files['logo_parti']
                candidat.logo_parti = save_file(logo_file, 'logos')
            if 'photo' in request.files:
                photo_file = request.files['photo']
                candidat.photo = save_file(photo_file, 'profiles')

            candidat.prenom = prenom
            candidat.nom = nom
            candidat.parti = parti
            candidat.biographie = biographie
            candidat.election_id = election_id
            candidat.statut = statut
            candidat.date_modification = datetime.utcnow()

        # Sinon, c'est du JSON
        else:
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
