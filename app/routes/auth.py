from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.schemas import UserSchema
from app import db
from datetime import datetime
from app.utils.file_upload import save_file
import os

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()

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
        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        data['role'] = data.get('role', 'director')

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
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not phone_number or not password:
            return jsonify({'message': 'Missing phone number or password'}), 400

        user = User.query.filter_by(phone_number=phone_number).first()

        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            'message': 'Login successful',
            'user': user_schema.dump(user),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'message': 'Email is required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'No user found with this email'}), 404

        # TODO: Implement password reset email logic
        # For now, we'll just return a success message
        return jsonify({'message': 'Password reset instructions sent to your email'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        return jsonify(user_schema.dump(user)), 200
    except Exception as e:
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
            
        # Delete user's files if they exist
        if user.campaign_logo and os.path.exists(user.campaign_logo):
            os.remove(user.campaign_logo)
        if user.profile_photo and os.path.exists(user.profile_photo):
            os.remove(user.profile_photo)
            
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

        user.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user_schema.dump(user)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500