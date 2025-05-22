from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.election import VotingOffice, VotingResult
from app.schemas import VotingOfficeSchema, VotingResultSchema
from app import db
from sqlalchemy import func

voting_bp = Blueprint('voting', __name__)
office_schema = VotingOfficeSchema()
result_schema = VotingResultSchema()

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
