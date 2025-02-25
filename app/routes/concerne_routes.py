from flask_restx import Namespace, Resource, fields
from flask import request
from app.db import db
from app.repositories.concerne_repo import ConcerneRepository

# Define Namespace
concerne_api = Namespace("concerne", description="Concerne related operations")

# Define request/response models for Swagger
concerne_model = concerne_api.model("Concerne", {
    "code_continent": fields.String(required=True, description="Continent Code"),
    "code_pays": fields.String(required=True, description="Country Code"),
    "code_region": fields.String(required=True, description="Region Code"),
    "code_rapport": fields.Integer(required=True, description="Rapport ID"),
})

concerne_create_model = concerne_api.model("ConcerneCreate", {
    "code_continent": fields.String(required=True, description="Continent Code"),
    "code_pays": fields.String(required=True, description="Country Code"),
    "code_region": fields.String(required=True, description="Region Code"),
    "code_rapport": fields.Integer(required=True, description="Rapport ID"),
})

@concerne_api.route("/")
class ConcerneList(Resource):
    """Handles listing and creating concerne entries"""

    @concerne_api.marshal_list_with(concerne_model)
    def get(self):
        """Get all concerne entries"""
        repo = ConcerneRepository(db.session)
        return repo.get_all(), 200

    @concerne_api.expect(concerne_create_model)
    @concerne_api.marshal_with(concerne_model, code=201)
    def post(self):
        """Create a new concerne entry"""
        data = request.get_json()
        repo = ConcerneRepository(db.session)
        return repo.create(**data), 201


@concerne_api.route("/<string:code_continent>/<string:code_pays>/<string:code_region>/<int:code_rapport>")
class ConcerneResource(Resource):
    """Handles operations on a single concerne entry"""

    def delete(self, code_continent, code_pays, code_region, code_rapport):
        """Delete a concerne entry by its composite key"""
        repo = ConcerneRepository(db.session)
        if not repo.delete(code_continent, code_pays, code_region, code_rapport):
            concerne_api.abort(404, "Concerne entry not found")
        return {"message": "Concerne entry deleted"}, 200