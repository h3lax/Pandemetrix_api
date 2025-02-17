# app/routes/periode_routes.py
from flask_restx import Namespace, Resource, fields
from flask import request
from app.db import db
from app.repositories.periode_repo import PeriodeRepository

# Define Namespace
periode_api = Namespace("periode", description="Periode related operations")

# Define request/response models for Swagger
periode_model = periode_api.model("Periode", {
    "id": fields.Integer(description="Periode ID"),
    "nom": fields.String(required=True, description="Periode Name"),
})

periode_create_model = periode_api.model("PeriodeCreate", {
    "nom": fields.String(required=True, description="Periode Name"),
})

@periode_api.route("/")
class PeriodeList(Resource):
    """Handles listing and creating periodes"""

    @periode_api.marshal_list_with(periode_model)
    def get(self):
        """Get all periodes"""
        repo = PeriodeRepository(db.session)
        return repo.get_all(), 200

    @periode_api.expect(periode_create_model)
    @periode_api.marshal_with(periode_model, code=201)
    def post(self):
        """Create a new periode"""
        data = request.get_json()
        repo = PeriodeRepository(db.session)
        return repo.create(**data), 201


@periode_api.route("/<int:id_periode>")
class PeriodeResource(Resource):
    """Handles operations on a single periode"""

    @periode_api.marshal_with(periode_model)
    def get(self, id_periode):
        """Get a periode by its ID"""
        repo = PeriodeRepository(db.session)
        periode = repo.get_by_id(id_periode)
        if not periode:
            periode_api.abort(404, "Periode not found")
        return periode

    @periode_api.expect(periode_create_model)
    @periode_api.marshal_with(periode_model)
    def put(self, id_periode):
        """Update an existing periode"""
        data = request.get_json()
        repo = PeriodeRepository(db.session)
        updated_periode = repo.update(id_periode, **data)
        if not updated_periode:
            periode_api.abort(404, "Periode not found")
        return updated_periode

    def delete(self, id_periode):
        """Delete a periode by its ID"""
        repo = PeriodeRepository(db.session)
        if not repo.delete(id_periode):
            periode_api.abort(404, "Periode not found")
        return {"message": "Periode deleted"}, 200