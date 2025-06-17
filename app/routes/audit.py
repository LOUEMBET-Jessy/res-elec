from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.audit import JournalAudit
from app import db

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')

@audit_bp.route('/', methods=['GET'])
@jwt_required()
def liste_audit():
    try:
        entries = JournalAudit.query.all()
        return jsonify([{
            'id': entry.id,
            'action': entry.action,
            'utilisateur_id': entry.utilisateur_id,
            'agent_utilisateur': entry.agent_utilisateur,
            'adresse_ip': entry.adresse_ip,
            'metadonnees': entry.metadonnees,
            'date_creation': entry.date_creation
        } for entry in entries]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@audit_bp.route('/<int:entry_id>', methods=['GET'])
@jwt_required()
def details_audit(entry_id):
    try:
        entry = JournalAudit.query.get(entry_id)
        if not entry:
            return jsonify({'message': 'Entrée non trouvée'}), 404

        return jsonify({
            'id': entry.id,
            'action': entry.action,
            'utilisateur_id': entry.utilisateur_id,
            'agent_utilisateur': entry.agent_utilisateur,
            'adresse_ip': entry.adresse_ip,
            'metadonnees': entry.metadonnees,
            'date_creation': entry.date_creation
        }), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500 