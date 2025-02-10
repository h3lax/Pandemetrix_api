# app/routes/concerne_routes.py
from flask import Blueprint, request, jsonify
from app.db import db
from app.repositories import ConcerneRepository

concerne_bp = Blueprint('concerne', __name__, url_prefix='/concerne')

@concerne_bp.route('/', methods=['POST'])
def create_concerne():
    data = request.get_json()
    db = get_db()
    repo = ConcerneRepository(db)
    concerne = repo.create(
        code_continent=data['code_continent'],
        code_pays=data['code_pays'],
        code_region=data['code_region'],
        code_rapport=data['code_rapport']
    )
    return jsonify(concerne.to_dict()), 201

@concerne_bp.route('/', methods=['GET'])
def get_all_concerne():
    db = get_db()
    repo = ConcerneRepository(db)
    concerne_list = repo.get_all()
    return jsonify([c.to_dict() for c in concerne_list])

@concerne_bp.route('/', methods=['DELETE'])
def delete_concerne():
    data = request.get_json()
    db = get_db()
    repo = ConcerneRepository(db)
    if not repo.delete(
        data['code_continent'],
        data['code_pays'],
        data['code_region'],
        data['code_rapport']
    ):
        return {'detail': 'Concerne entry not found'}, 404
    return {'message': 'Concerne entry deleted'}