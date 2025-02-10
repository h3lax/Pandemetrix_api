# app/routes/periode_routes.py
from flask import Blueprint, request, jsonify
from app.db import db
from app.repositories import PeriodeRepository

periode_bp = Blueprint('periodes', __name__, url_prefix='/periodes')

@periode_bp.route('/', methods=['POST'])
def create_periode():
    data = request.get_json()
    db = get_db()
    repo = PeriodeRepository(db)
    periode = repo.create(nom=data['nom'])
    return jsonify(periode.to_dict()), 201

@periode_bp.route('/', methods=['GET'])
def get_periodes():
    db = get_db()
    repo = PeriodeRepository(db)
    periodes = repo.get_all()
    return jsonify([p.to_dict() for p in periodes])

@periode_bp.route('/<int:code_periode>', methods=['GET'])
def get_periode(code_periode):
    db = get_db()
    repo = PeriodeRepository(db)
    periode = repo.get_by_id(code_periode)
    if not periode:
        return {'detail': 'Periode not found'}, 404
    return jsonify(periode.to_dict())

@periode_bp.route('/<int:code_periode>', methods=['PUT'])
def update_periode(code_periode):
    data = request.get_json()
    db = get_db()
    repo = PeriodeRepository(db)
    updated_periode = repo.update(code_periode, nom=data['nom'])
    if not updated_periode:
        return {'detail': 'Periode not found'}, 404
    return jsonify(updated_periode.to_dict())

@periode_bp.route('/<int:code_periode>', methods=['DELETE'])
def delete_periode(code_periode):
    db = get_db()
    repo = PeriodeRepository(db)
    if not repo.delete(code_periode):
        return {'detail': 'Periode not found'}, 404
    return {'message': 'Periode deleted'}