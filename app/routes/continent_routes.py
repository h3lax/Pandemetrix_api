from flask import Blueprint, request, jsonify
from app.repository import ContinentRepository

continent_bp = Blueprint("continent", __name__)

@continent_bp.route('/continents', methods=['POST'])
def create_continent():
    data = request.get_json()
    continent = ContinentRepository.create_continent(data['code_continent'], data['nom'])
    return jsonify(continent.to_dict()), 201

@continent_bp.route('/continents', methods=['GET'])
def get_all_continents():
    continents = ContinentRepository.get_all_continents()
    return jsonify([continent.to_dict() for continent in continents]), 200

@continent_bp.route('/continents/<code_continent>', methods=['GET'])
def get_continent(code_continent):
    continent = ContinentRepository.get_continent_by_code(code_continent)
    if continent:
        return jsonify(continent.to_dict()), 200
    return jsonify({'error': 'Continent not found'}), 404

@continent_bp.route('/continents/<code_continent>', methods=['PUT'])
def update_continent(code_continent):
    data = request.get_json()
    continent = ContinentRepository.update_continent(code_continent, data['nom'])
    if continent:
        return jsonify(continent.to_dict()), 200
    return jsonify({'error': 'Continent not found'}), 404

@continent_bp.route('/continents/<code_continent>', methods=['DELETE'])
def delete_continent(code_continent):
    continent = ContinentRepository.delete_continent(code_continent)
    if continent:
        return jsonify({'message': 'Continent deleted'}), 200
    return jsonify({'error': 'Continent not found'}), 404
