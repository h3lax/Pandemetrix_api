# app/routes/maladie_routes.py
from flask import Blueprint, request, jsonify
from app.db import db
from app.repositories import MaladieRepository

maladie_bp = Blueprint('maladies', __name__, url_prefix='/maladies')

@maladie_bp.route('/', methods=['POST'])
def create_maladie():
    data = request.get_json()
    db = get_db()
    repo = MaladieRepository(db)
    maladie = repo.create(nom=data['nom'])
    return jsonify(maladie.to_dict()), 201

@maladie_bp.route('/', methods=['GET'])
def get_maladies():
    db = get_db()
    repo = MaladieRepository(db)
    maladies = repo.get_all()
    return jsonify([m.to_dict() for m in maladies])

@maladie_bp.route('/<int:code_maladie>', methods=['GET'])
def get_maladie(code_maladie):
    db = get_db()
    repo = MaladieRepository(db)
    maladie = repo.get_by_id(code_maladie)
    if not maladie:
        return {'detail': 'Maladie not found'}, 404
    return jsonify(maladie.to_dict())

@maladie_bp.route('/<int:code_maladie>', methods=['PUT'])
def update_maladie(code_maladie):
    data = request.get_json()
    db = get_db()
    repo = MaladieRepository(db)
    updated_maladie = repo.update(code_maladie, nom=data['nom'])
    if not updated_maladie:
        return {'detail': 'Maladie not found'}, 404
    return jsonify(updated_maladie.to_dict())

@maladie_bp.route('/<int:code_maladie>', methods=['DELETE'])
def delete_maladie(code_maladie):
    db = get_db()
    repo = MaladieRepository(db)
    if not repo.delete(code_maladie):
        return {'detail': 'Maladie not found'}, 404
    return {'message': 'Maladie deleted'}