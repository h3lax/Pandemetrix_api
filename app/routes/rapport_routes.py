# app/routes/rapport_routes.py
from flask import Blueprint, request, jsonify
from app.db import db
from app.repositories import RapportRepository

rapport_bp = Blueprint('rapports', __name__, url_prefix='/rapports')

@rapport_bp.route('/', methods=['POST'])
def create_rapport():
    data = request.get_json()
    db = get_db()
    repo = RapportRepository(db)
    rapport = repo.create(**data)
    return jsonify(rapport.to_dict()), 201

@rapport_bp.route('/', methods=['GET'])
def get_rapports():
    db = get_db()
    repo = RapportRepository(db)
    rapports = repo.get_all()
    return jsonify([r.to_dict() for r in rapports])

@rapport_bp.route('/<int:code_rapport>', methods=['GET'])
def get_rapport(code_rapport):
    db = get_db()
    repo = RapportRepository(db)
    rapport = repo.get_by_id(code_rapport)
    if not rapport:
        return {'detail': 'Rapport not found'}, 404
    return jsonify(rapport.to_dict())

@rapport_bp.route('/<int:code_rapport>', methods=['PUT'])
def update_rapport(code_rapport):
    data = request.get_json()
    db = get_db()
    repo = RapportRepository(db)
    updated_rapport = repo.update(code_rapport, **data)
    if not updated_rapport:
        return {'detail': 'Rapport not found'}, 404
    return jsonify(updated_rapport.to_dict())

@rapport_bp.route('/<int:code_rapport>', methods=['DELETE'])
def delete_rapport(code_rapport):
    db = get_db()
    repo = RapportRepository(db)
    if not repo.delete(code_rapport):
        return {'detail': 'Rapport not found'}, 404
    return {'message': 'Rapport deleted'}