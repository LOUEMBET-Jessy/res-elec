from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.election import Candidate
from app.schemas import CandidateSchema
from app import db
from app.utils.file_upload import save_file
import os

candidate_bp = Blueprint('candidate', __name__)
candidate_schema = CandidateSchema()
candidates_schema = CandidateSchema(many=True)

@candidate_bp.route('/', methods=['POST'])
@jwt_required()
def create_candidate():
    try:
        data = request.form.to_dict()
        profile_photo = request.files.get('profile_photo')

        if profile_photo:
            photo_path = save_file(profile_photo, 'candidates')
            data['profile_photo'] = photo_path

        errors = candidate_schema.validate(data)
        if errors:
            return jsonify({'message': 'Validation error', 'errors': errors}), 400

        candidate = Candidate(**data)
        db.session.add(candidate)
        db.session.commit()

        return jsonify({
            'message': 'Candidate created successfully',
            'candidate': candidate_schema.dump(candidate)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/', methods=['GET'])
@jwt_required()
def get_candidates():
    try:
        election_id = request.args.get('election_id')
        if election_id:
            candidates = Candidate.query.filter_by(election_id=election_id).all()
        else:
            candidates = Candidate.query.all()
        return jsonify(candidates_schema.dump(candidates)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/<int:candidate_id>', methods=['GET'])
@jwt_required()
def get_candidate(candidate_id):
    try:
        candidate = Candidate.query.get_or_404(candidate_id)
        return jsonify(candidate_schema.dump(candidate)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/<int:candidate_id>', methods=['PUT'])
@jwt_required()
def update_candidate(candidate_id):
    try:
        candidate = Candidate.query.get_or_404(candidate_id)
        data = request.form.to_dict()
        profile_photo = request.files.get('profile_photo')

        if profile_photo:
            # Delete old photo if exists
            if candidate.profile_photo and os.path.exists(candidate.profile_photo):
                os.remove(candidate.profile_photo)
            photo_path = save_file(profile_photo, 'candidates')
            data['profile_photo'] = photo_path

        errors = candidate_schema.validate(data, partial=True)
        if errors:
            return jsonify({'message': 'Validation error', 'errors': errors}), 400

        for key, value in data.items():
            setattr(candidate, key, value)

        db.session.commit()
        return jsonify({
            'message': 'Candidate updated successfully',
            'candidate': candidate_schema.dump(candidate)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@candidate_bp.route('/<int:candidate_id>', methods=['DELETE'])
@jwt_required()
def delete_candidate(candidate_id):
    try:
        candidate = Candidate.query.get_or_404(candidate_id)
        
        # Delete profile photo if exists
        if candidate.profile_photo and os.path.exists(candidate.profile_photo):
            os.remove(candidate.profile_photo)
        
        db.session.delete(candidate)
        db.session.commit()
        return jsonify({'message': 'Candidate deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500
