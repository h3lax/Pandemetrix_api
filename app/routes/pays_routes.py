from flask_restx import Namespace, Resource, fields
from flask import request
from app.db import db
from app.repositories.pays_repo import PaysRepository

# Define Namespace
pays_api = Namespace("pays", description="Country related operations")

# Define request/response models for Swagger
pays_model = pays_api.model("Pays", {
    "id": fields.Integer(description="Country ID"),
    "code_pays": fields.String(required=True, description="Country Code"),
    "nom": fields.String(required=True, description="Country Name"),
    "pib": fields.Integer(description="GDP"),
    "temperature": fields.Float(description="Temperature"),
    "code_continent": fields.String(required=True, description="Continent Code"),
})

pays_create_model = pays_api.model("PaysCreate", {
    "code_pays": fields.String(required=True, description="Country Code"),
    "nom": fields.String(required=True, description="Country Name"),
    "pib": fields.Integer(description="GDP"),
    "temperature": fields.Float(description="Temperature"),
    "code_continent": fields.String(required=True, description="Continent Code"),
})

@pays_api.route("/")
class PaysList(Resource):
    """Handles listing and creating countries"""

    @pays_api.marshal_list_with(pays_model)
    def get(self):
        """Get all countries"""
        repo = PaysRepository(db.session)
        return repo.get_all(), 200

    @pays_api.expect(pays_create_model)
    @pays_api.marshal_with(pays_model, code=201)
    def post(self):
        """Create a new country"""
        data = request.get_json()
        repo = PaysRepository(db.session)
        return repo.create(**data), 201


@pays_api.route("/<int:id_pays>")
class PaysResource(Resource):
    """Handles operations on a single country"""

    @pays_api.marshal_with(pays_model)
    def get(self, id_pays):
        """Get a country by its ID"""
        repo = PaysRepository(db.session)
        pays = repo.get_by_id(id_pays)
        if not pays:
            pays_api.abort(404, "Country not found")
        return pays

    @pays_api.expect(pays_create_model)
    @pays_api.marshal_with(pays_model)
    def put(self, id_pays):
        """Update an existing country"""
        data = request.get_json()
        repo = PaysRepository(db.session)
        updated_pays = repo.update(id_pays, **data)
        if not updated_pays:
            pays_api.abort(404, "Country not found")
        return updated_pays

    def delete(self, id_pays):
        """Delete a country by its ID"""
        repo = PaysRepository(db.session)
        if not repo.delete(id_pays):
            pays_api.abort(404, "Country not found")
        return {"message": "Country deleted"}, 200


@pays_api.route("/code/<string:code_pays>")
class PaysByCode(Resource):
    """Handles getting a country by its code"""

    @pays_api.marshal_with(pays_model)
    def get(self, code_pays):
        """Get a country by its code"""
        repo = PaysRepository(db.session)
        pays = repo.get_by_code(code_pays)
        if not pays:
            pays_api.abort(404, "Country not found")
        return pays


@pays_api.route("/continent/<int:code_continent>")
class PaysByContinent(Resource):
    """Handles getting countries by continent code"""

    @pays_api.marshal_list_with(pays_model)
    def get(self, code_continent):
        """Get countries by continent code"""
        repo = PaysRepository(db.session)
        pays_list = repo.get_by_continent(code_continent)
        return pays_list