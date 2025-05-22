from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.election import Election, Candidate, VotingCenter, VotingOffice, VotingResult
from app.schemas import ElectionSchema, CandidateSchema, VotingCenterSchema, VotingOfficeSchema, VotingResultSchema
from app import db
from app.utils.file_upload import save_file
import os

election_bp = Blueprint('election', __name__)
election_schema = ElectionSchema()
elections_schema = ElectionSchema(many=True)

@election_bp.route('/', methods=['POST'])
@jwt_required()
def create_election():
    try:
        data = request.get_json()
        errors = election_schema.validate(data)
        if errors:
            return jsonify({'message': 'Validation error', 'errors': errors}), 400

        election = Election(**data)
        db.session.add(election)
        db.session.commit()

        return jsonify({
            'message': 'Election created successfully',
            'election': election_schema.dump(election)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@election_bp.route('/', methods=['GET'])
@jwt_required()
def get_elections():
    try:
        elections = Election.query.all()
        return jsonify(elections_schema.dump(elections)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>', methods=['GET'])
@jwt_required()
def get_election(election_id):
    try:
        election = Election.query.get_or_404(election_id)
        return jsonify(election_schema.dump(election)), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>', methods=['PUT'])
@jwt_required()
def update_election(election_id):
    try:
        election = Election.query.get_or_404(election_id)
        data = request.get_json()
        
        errors = election_schema.validate(data, partial=True)
        if errors:
            return jsonify({'message': 'Validation error', 'errors': errors}), 400

        for key, value in data.items():
            setattr(election, key, value)

        db.session.commit()
        return jsonify({
            'message': 'Election updated successfully',
            'election': election_schema.dump(election)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@election_bp.route('/<int:election_id>', methods=['DELETE'])
@jwt_required()
def delete_election(election_id):
    try:
        election = Election.query.get_or_404(election_id)
        db.session.delete(election)
        db.session.commit()
        return jsonify({'message': 'Election deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
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
            'center': VotingCenterSchema().dump(center)
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
            'office': VotingOfficeSchema().dump(office)
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
            'office': VotingOfficeSchema().dump(office)
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
            center_data = VotingCenterSchema().dump(center)
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
