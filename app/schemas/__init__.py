from marshmallow import Schema, fields, validate, EXCLUDE
from datetime import datetime

class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1))
    last_name = fields.Str(required=True, validate=validate.Length(min=1))
    phone_number = fields.Str(required=True, validate=validate.Length(min=8))
    email = fields.Email(required=True)
    password = fields.Str(load_only=True)
    password_hash = fields.Str(dump_only=True)
    campaign_logo = fields.Str(allow_none=True)
    profile_photo = fields.Str(allow_none=True)
    province = fields.Str(required=True)
    commune = fields.Str(required=True)
    # campaign_start_date = fields.String(allow_none=True)
    # campaign_end_date = fields.String(allow_none=True)
    role = fields.Str(validate=validate.OneOf(['director', 'collaborator']), missing='director')
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ElectionSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(['legislative', 'municipal', 'local', 'presidential']))
    year = fields.Int(required=True)
    status = fields.Str(validate=validate.OneOf(['pending', 'active', 'completed']))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    candidates = fields.Nested('CandidateSchema', many=True, exclude=('election',))
    voting_centers = fields.Nested('VotingCenterSchema', many=True, exclude=('election',))

# class CandidateSchema(Schema):
#     id = fields.Int(dump_only=True)
#     first_name = fields.Str(required=True)
#     last_name = fields.Str(required=True)
#     code_name = fields.Str(required=True)
#     profile_photo = fields.Str()
#     election_id = fields.Int(required=True)
#     created_at = fields.DateTime(dump_only=True)
#     updated_at = fields.DateTime(dump_only=True)
class CandidateSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    code_name = fields.Str(required=True)
    profile_photo = fields.Str()
    election_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # 👇 Ajoute cette ligne
    election = fields.Nested("ElectionSchema", only=("id", "title"), dump_only=True)


# class VotingCenterSchema(Schema):
#     id = fields.Int(dump_only=True)
#     name = fields.Str(required=True)
#     election_id = fields.Int(required=True)
#     created_at = fields.DateTime(dump_only=True)
#     updated_at = fields.DateTime(dump_only=True)
#     voting_offices = fields.Nested('VotingOfficeSchema', many=True, exclude=('center',))
class VotingCenterSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    election_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    voting_offices = fields.Nested('VotingOfficeSchema', many=True, exclude=('center',))

    # ✅ Ajoute ceci si tu veux aussi les infos de l'élection
    election = fields.Nested('ElectionSchema', only=("id", "title"), dump_only=True)


class VotingOfficeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    center_id = fields.Int(required=True)
    total_voters = fields.Int()
    blank_votes = fields.Int()
    null_votes = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    center = fields.Nested('VotingCenterSchema', exclude=('voting_offices',), dump_only=True)
    results = fields.Nested('VotingResultSchema', many=True, exclude=('office',))

class VotingResultSchema(Schema):
    id = fields.Int(dump_only=True)
    office_id = fields.Int(required=True)
    candidate_id = fields.Int(required=True)
    votes = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
