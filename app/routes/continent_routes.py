# app/routes/continent_routes.py
from flask import Blueprint, request, jsonify
from app.db import db
from app.repositories import ContinentRepository

continent_bp = Blueprint('continents', __name__, url_prefix='/continents')

@continent_bp.route('/', methods=['POST'])
def create_continent():
    data = request.get_json()
    db = get_db()
    repo = ContinentRepository(db)
    continent = repo.create(
        code_continent=data['code_continent'],
        nom=data['nom']
    )
    return jsonify(continent.to_dict()), 201

@continent_bp.route('/', methods=['GET'])
def get_continents():
    db = get_db()
    repo = ContinentRepository(db)
    continents = repo.get_all()
    return jsonify([c.to_dict() for c in continents])

@continent_bp.route('/<int:id_continent>', methods=['GET'])
def get_continent(id_continent):
    db = get_db()
    repo = ContinentRepository(db)
    continent = repo.get_by_id(id_continent)
    if not continent:
        return {'detail': 'Continent not found'}, 404
    return jsonify(continent.to_dict())

@continent_bp.route('/code/<code_continent>', methods=['GET'])
def get_continent_by_code(code_continent):
    db = get_db()
    repo = ContinentRepository(db)
    continent = repo.get_by_code(code_continent)
    if not continent:
        return {'detail': 'Continent not found'}, 404
    return jsonify(continent.to_dict())

@continent_bp.route('/<int:id_continent>', methods=['PUT'])
def update_continent(id_continent):
    data = request.get_json()
    db = get_db()
    repo = ContinentRepository(db)
    updated_continent = repo.update(id_continent, **data)
    if not updated_continent:
        return {'detail': 'Continent not found'}, 404
    return jsonify(updated_continent.to_dict())

@continent_bp.route('/<int:id_continent>', methods=['DELETE'])
def delete_continent(id_continent):
    db = get_db()
    repo = ContinentRepository(db)
    if not repo.delete(id_continent):
        return {'detail': 'Continent not found'}, 404
    return {'message': 'Continent deleted'}