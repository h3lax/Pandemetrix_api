from flask_restx import Namespace, Resource, fields
from flask import request
from app.db import db
from app.repositories.continent_repo import ContinentRepository

# Define Namespace
continent_api = Namespace("continent", description="Continent related operations")

# Define request/response models for Swagger
continent_model = continent_api.model("Continent", {
    "id": fields.Integer(description="Continent ID"),
    "code_continent": fields.String(required=True, description="Continent Code"),
    "nom": fields.String(required=True, description="Continent Name"),
})

continent_create_model = continent_api.model("ContinentCreate", {
    "code_continent": fields.String(required=True, description="Continent Code"),
    "nom": fields.String(required=True, description="Continent Name"),
})

@continent_api.route("/")
class ContinentList(Resource):
    """Handles listing and creating continents"""

    @continent_api.marshal_list_with(continent_model)
    def get(self):
        """Get all continents"""
        repo = ContinentRepository(db.session)
        return repo.get_all(), 200

    @continent_api.expect(continent_create_model)
    @continent_api.marshal_with(continent_model, code=201)
    def post(self):
        """Create a new continent"""
        data = request.get_json()
        repo = ContinentRepository(db.session)
        return repo.create(**data), 201


@continent_api.route("/<int:id_continent>")
class ContinentResource(Resource):
    """Handles operations on a single continent"""

    @continent_api.marshal_with(continent_model)
    def get(self, id_continent):
        """Get a continent by its ID"""
        repo = ContinentRepository(db.session)
        continent = repo.get_by_id(id_continent)
        if not continent:
            continent_api.abort(404, "Continent not found")
        return continent

    @continent_api.expect(continent_create_model)
    @continent_api.marshal_with(continent_model)
    def put(self, id_continent):
        """Update an existing continent"""
        data = request.get_json()
        repo = ContinentRepository(db.session)
        updated_continent = repo.update(id_continent, **data)
        if not updated_continent:
            continent_api.abort(404, "Continent not found")
        return updated_continent

    def delete(self, id_continent):
        """Delete a continent by its ID"""
        repo = ContinentRepository(db.session)
        if not repo.delete(id_continent):
            continent_api.abort(404, "Continent not found")
        return {"message": "Continent deleted"}, 200


@continent_api.route("/code/<string:code_continent>")
class ContinentByCode(Resource):
    """Handles getting a continent by its code"""

    @continent_api.marshal_with(continent_model)
    def get(self, code_continent):
        """Get a continent by its code"""
        repo = ContinentRepository(db.session)
        continent = repo.get_by_code(code_continent)
        if not continent:
            continent_api.abort(404, "Continent not found")
        return continent
