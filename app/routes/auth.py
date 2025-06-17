from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.models.session import Session
from app.schemas import UserSchema
from app import db
from datetime import datetime, timedelta
from app.utils.file_upload import save_file
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
user_schema = UserSchema()

@auth_bp.route('/connexion', methods=['POST'])
def connexion():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email et mot de passe requis'}), 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Identifiants invalides'}), 401

        # Mise à jour de la dernière connexion
        user.derniere_connexion = datetime.utcnow()
        db.session.commit()

        # Création de la session
        jeton = create_access_token(identity=str(user.id))
        expiration = datetime.utcnow() + timedelta(hours=1)
        session = Session(
            utilisateur_id=user.id,
            jeton=jeton,
            expiration=expiration,
            agent_utilisateur=request.headers.get('User-Agent'),
            adresse_ip=request.remote_addr
        )
        db.session.add(session)
        db.session.commit()

        return jsonify({
            'message': 'Connexion réussie',
            'user': user_schema.dump(user),
            'access_token': jeton,
            'refresh_token': create_refresh_token(identity=str(user.id))
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/deconnexion', methods=['POST'])
@jwt_required()
def deconnexion():
    try:
        current_user_id = get_jwt_identity()
        session = Session.query.filter_by(utilisateur_id=current_user_id, jeton=request.headers.get('Authorization').split(' ')[1]).first()
        if session:
            db.session.delete(session)
            db.session.commit()
        return jsonify({'message': 'Déconnexion réussie'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/mot-de-passe-oublie', methods=['POST'])
def mot_de_passe_oublie():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'message': 'Email requis'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'Aucun utilisateur trouvé avec cet email'}), 404

        # TODO: Implémenter la logique d'envoi d'email de réinitialisation
        return jsonify({'message': 'Instructions de réinitialisation envoyées à votre email'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/profil', methods=['GET'])
@jwt_required()
def profil():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        return jsonify(user_schema.dump(user)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/sessions', methods=['GET'])
@jwt_required()
def sessions():
    try:
        current_user_id = get_jwt_identity()
        sessions = Session.query.filter_by(utilisateur_id=current_user_id).all()
        return jsonify([{
            'id': session.id,
            'jeton': session.jeton,
            'expiration': session.expiration,
            'agent_utilisateur': session.agent_utilisateur,
            'adresse_ip': session.adresse_ip,
            'date_creation': session.date_creation
        } for session in sessions]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@jwt_required()
def supprimer_session(session_id):
    try:
        current_user_id = get_jwt_identity()
        session = Session.query.filter_by(id=session_id, utilisateur_id=current_user_id).first()
        if not session:
            return jsonify({'message': 'Session non trouvée'}), 404
        db.session.delete(session)
        db.session.commit()
        return jsonify({'message': 'Session supprimée'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.form.to_dict()
        
        # Check if user already exists
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'message': 'Email already registered'}), 400
        if User.query.filter_by(phone_number=data.get('phone_number')).first():
            return jsonify({'message': 'Phone number already registered'}), 400

        # Handle file uploads
        campaign_logo = request.files.get('campaign_logo')
        profile_photo = request.files.get('profile_photo')

        if campaign_logo:
            logo_path = save_file(campaign_logo, 'logos')
            data['campaign_logo'] = logo_path

        if profile_photo:
            photo_path = save_file(profile_photo, 'profiles')
            data['profile_photo'] = photo_path

        # Convert date strings to datetime objects only if they exist
        # try:
        #     if data.get('campaign_start_date'):
        #         date_str = data['campaign_start_date'].replace('Z', '')
        #         data['campaign_start_date'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        #     if data.get('campaign_end_date'):
        #         date_str = data['campaign_end_date'].replace('Z', '')
        #         data['campaign_end_date'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        # except ValueError as e:
        #     return jsonify({'message': 'Invalid date format. Use format YYYY-MM-DDThh:mm:ssZ (e.g., 2025-06-01T00:00:00Z)'}), 400

        # Validate data
        errors = user_schema.validate(data)
        if errors:
            return jsonify({'message': 'Validation error', 'errors': errors}), 400

        # Add additional fields
        data['password_hash'] = generate_password_hash(data.pop('password'))
        data['date_creation'] = datetime.now()
        data['date_modification'] = datetime.now()
        data['role'] = data.get('role', 'operateur_donnees')

        # Create user
        user = User(**data)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': user_schema.dump(user)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        # user = User.query.get(current_user_id)
        user = User.query.get(int(current_user_id))
        data = request.form.to_dict()

        # Handle file uploads
        campaign_logo = request.files.get('campaign_logo')
        profile_photo = request.files.get('profile_photo')

        if campaign_logo:
            # Delete old logo if exists
            if user.campaign_logo and os.path.exists(user.campaign_logo):
                os.remove(user.campaign_logo)
            logo_path = save_file(campaign_logo, 'logos')
            data['campaign_logo'] = logo_path

        if profile_photo:
            # Delete old photo if exists
            if user.profile_photo and os.path.exists(user.profile_photo):
                os.remove(user.profile_photo)
            photo_path = save_file(profile_photo, 'profiles')
            data['profile_photo'] = photo_path

        # Update user fields
        # for key, value in data.items():
        #     if hasattr(user, key):
        #         setattr(user, key, value)
        for key, value in data.items():
            if hasattr(user, key):
                current_value = getattr(user, key)
                if str(current_value) != str(value):
                    setattr(user, key, value)

        db.session.commit()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user_schema.dump(user)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Get all users (admin only)
@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'director':
            return jsonify({'message': 'Unauthorized access'}), 403
            
        users = User.query.all()
        return jsonify({
            'users': user_schema.dump(users, many=True)
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Get available roles
@auth_bp.route('/roles', methods=['GET'])
@jwt_required()
def liste_roles():
    try:
        roles = ['super_admin', 'agent_ministere', 'agent_election', 'president_bureau', 'operateur_donnees', 'validateur_candidats']
        return jsonify(roles), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Get user by ID (admin or self)
@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or (current_user.role != 'director' and current_user_id != user_id):
            return jsonify({'message': 'Unauthorized access'}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        return jsonify(user_schema.dump(user)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Delete user (admin only)
@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'director':
            return jsonify({'message': 'Unauthorized access'}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# Update user (admin or self)
@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or (current_user.role != 'director' and current_user_id != user_id):
            return jsonify({'message': 'Unauthorized access'}), 403
            
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        data = request.form.to_dict()

        # Handle file uploads
        campaign_logo = request.files.get('campaign_logo')
        profile_photo = request.files.get('profile_photo')

        if campaign_logo:
            if user.campaign_logo and os.path.exists(user.campaign_logo):
                os.remove(user.campaign_logo)
            logo_path = save_file(campaign_logo, 'logos')
            data['campaign_logo'] = logo_path

        if profile_photo:
            if user.profile_photo and os.path.exists(user.profile_photo):
                os.remove(user.profile_photo)
            photo_path = save_file(profile_photo, 'profiles')
            data['profile_photo'] = photo_path

        # Convert date strings to datetime objects if present
        try:
            if data.get('campaign_start_date'):
                date_str = data['campaign_start_date'].replace('Z', '')
                data['campaign_start_date'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
            if data.get('campaign_end_date'):
                date_str = data['campaign_end_date'].replace('Z', '')
                data['campaign_end_date'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            return jsonify({'message': 'Invalid date format. Use format YYYY-MM-DDThh:mm:ssZ'}), 400

        # Handle password update
        if 'password' in data:
            data['password_hash'] = generate_password_hash(data.pop('password'))

        # Prevent role change if not director
        if 'role' in data and current_user.role != 'director':
            return jsonify({'message': 'Unauthorized to change role'}), 403

        # Update user fields
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.date_modification = datetime.now()
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user_schema.dump(user)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

user_bp = Blueprint('user', __name__, url_prefix='/api/utilisateurs')

@user_bp.route('/', methods=['GET'])
@jwt_required()
def liste_utilisateurs():
    try:
        utilisateurs = User.query.all()
        return jsonify([{
            'id': utilisateur.id,
            'email': utilisateur.email,
            'prenom': utilisateur.prenom,
            'nom': utilisateur.nom,
            'role': utilisateur.role,
            'est_actif': utilisateur.est_actif,
            'derniere_connexion': utilisateur.derniere_connexion,
            'date_creation': utilisateur.date_creation,
            'date_modification': utilisateur.date_modification
        } for utilisateur in utilisateurs]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/', methods=['POST'])
@jwt_required()
def creer_utilisateur():
    try:
        data = request.get_json()
        utilisateur = User(
            email=data.get('email'),
            prenom=data.get('prenom'),
            nom=data.get('nom'),
            role=data.get('role', 'collaborator'),
            est_actif=data.get('est_actif', True)
        )
        db.session.add(utilisateur)
        db.session.commit()

        return jsonify({
            'message': 'Utilisateur créé avec succès',
            'utilisateur': {
                'id': utilisateur.id,
                'email': utilisateur.email,
                'prenom': utilisateur.prenom,
                'nom': utilisateur.nom,
                'role': utilisateur.role,
                'est_actif': utilisateur.est_actif,
                'derniere_connexion': utilisateur.derniere_connexion,
                'date_creation': utilisateur.date_creation,
                'date_modification': utilisateur.date_modification
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@user_bp.route('/<int:utilisateur_id>', methods=['GET'])
@jwt_required()
def details_utilisateur(utilisateur_id):
    try:
        utilisateur = User.query.get(utilisateur_id)
        if not utilisateur:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

        return jsonify({
            'id': utilisateur.id,
            'email': utilisateur.email,
            'prenom': utilisateur.prenom,
            'nom': utilisateur.nom,
            'role': utilisateur.role,
            'est_actif': utilisateur.est_actif,
            'derniere_connexion': utilisateur.derniere_connexion,
            'date_creation': utilisateur.date_creation,
            'date_modification': utilisateur.date_modification
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@user_bp.route('/<int:utilisateur_id>', methods=['PUT'])
@jwt_required()
def modifier_utilisateur(utilisateur_id):
    try:
        utilisateur = User.query.get(utilisateur_id)
        if not utilisateur:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

        data = request.get_json()
        utilisateur.email = data.get('email', utilisateur.email)
        utilisateur.prenom = data.get('prenom', utilisateur.prenom)
        utilisateur.nom = data.get('nom', utilisateur.nom)
        utilisateur.role = data.get('role', utilisateur.role)
        utilisateur.est_actif = data.get('est_actif', utilisateur.est_actif)
        utilisateur.date_modification = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'message': 'Utilisateur mis à jour avec succès',
            'utilisateur': {
                'id': utilisateur.id,
                'email': utilisateur.email,
                'prenom': utilisateur.prenom,
                'nom': utilisateur.nom,
                'role': utilisateur.role,
                'est_actif': utilisateur.est_actif,
                'derniere_connexion': utilisateur.derniere_connexion,
                'date_creation': utilisateur.date_creation,
                'date_modification': utilisateur.date_modification
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@user_bp.route('/<int:utilisateur_id>', methods=['DELETE'])
@jwt_required()
def supprimer_utilisateur(utilisateur_id):
    try:
        utilisateur = User.query.get(utilisateur_id)
        if not utilisateur:
            return jsonify({'message': 'Utilisateur non trouvé'}), 404

        db.session.delete(utilisateur)
        db.session.commit()

        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@user_bp.route('/roles', methods=['GET'])
@jwt_required()
def liste_roles():
    try:
        roles = ['super_admin', 'agent_ministere', 'agent_election', 'president_bureau', 'operateur_donnees', 'validateur_candidats']
        return jsonify(roles), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500