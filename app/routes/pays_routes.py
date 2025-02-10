# app/routes/pays_routes.py
from flask import Blueprint, request, jsonify
from app.db import db
from app.repositories import PaysRepository

pays_bp = Blueprint('pays', __name__, url_prefix='/pays')

@pays_bp.route('/', methods=['POST'])
def create_pays():
    data = request.get_json()
    db = get_db()
    repo = PaysRepository(db)
    pays = repo.create(
        code_pays=data['code_pays'],
        nom=data['nom'],
        pib=data['pib'],
        temperature=data['temperature'],
        code_continent=data['code_continent']
    )
    return jsonify(pays.to_dict()), 201

@pays_bp.route('/', methods=['GET'])
def get_all_pays():
    db = get_db()
    repo = PaysRepository(db)
    pays_list = repo.get_all()
    return jsonify([p.to_dict() for p in pays_list])

@pays_bp.route('/<int:id_pays>', methods=['GET'])
def get_pays(id_pays):
    db = get_db()
    repo = PaysRepository(db)
    pays = repo.get_by_id(id_pays)
    if not pays:
        return {'detail': 'Pays not found'}, 404
    return jsonify(pays.to_dict())

@pays_bp.route('/code/<code_pays>', methods=['GET'])
def get_pays_by_code(code_pays):
    db = get_db()
    repo = PaysRepository(db)
    pays = repo.get_by_code(code_pays)
    if not pays:
        return {'detail': 'Pays not found'}, 404
    return jsonify(pays.to_dict())

@pays_bp.route('/continent/<int:code_continent>', methods=['GET'])
def get_pays_by_continent(code_continent):
    db = get_db()
    repo = PaysRepository(db)
    pays_list = repo.get_by_continent(code_continent)
    return jsonify([p.to_dict() for p in pays_list])

@pays_bp.route('/<int:id_pays>', methods=['PUT'])
def update_pays(id_pays):
    data = request.get_json()
    db = get_db()
    repo = PaysRepository(db)
    updated_pays = repo.update(id_pays, **data)
    if not updated_pays:
        return {'detail': 'Pays not found'}, 404
    return jsonify(updated_pays.to_dict())

@pays_bp.route('/<int:id_pays>', methods=['DELETE'])
def delete_pays(id_pays):
    db = get_db()
    repo = PaysRepository(db)
    if not repo.delete(id_pays):
        return {'detail': 'Pays not found'}, 404
    return {'message': 'Pays deleted'}