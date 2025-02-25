from flask_restx import Namespace, Resource, fields
from flask import request
from app.db import db
from app.repositories.rapport_repo import RapportRepository

# Define Namespace
rapport_api = Namespace("rapport", description="Rapport related operations")

# Define request/response models for Swagger
rapport_model = rapport_api.model("Rapport", {
    "id": fields.Integer(description="Rapport ID"),
    "date_debut": fields.String(required=True, description="Start Date"),
    "date_fin": fields.String(required=True, description="End Date"),
    "source": fields.String(description="Source"),
    "nouveaux_cas": fields.Integer(description="New Cases"),
    "nouveaux_deces": fields.Integer(description="New Deaths"),
    "nouveaux_gueris": fields.Integer(description="New Recoveries"),
    "cas_actifs": fields.Integer(description="Active Cases"),
    "taux_mortalite": fields.Float(description="Mortality Rate"),
    "taux_guerison": fields.Float(description="Recovery Rate"),
    "code_maladie": fields.Integer(required=True, description="Disease Code"),
    "code_periode": fields.Integer(required=True, description="Period Code"),
})

rapport_create_model = rapport_api.model("RapportCreate", {
    "date_debut": fields.String(required=True, description="Start Date"),
    "date_fin": fields.String(required=True, description="End Date"),
    "source": fields.String(description="Source"),
    "nouveaux_cas": fields.Integer(description="New Cases"),
    "nouveaux_deces": fields.Integer(description="New Deaths"),
    "nouveaux_gueris": fields.Integer(description="New Recoveries"),
    "cas_actifs": fields.Integer(description="Active Cases"),
    "taux_mortalite": fields.Float(description="Mortality Rate"),
    "taux_guerison": fields.Float(description="Recovery Rate"),
    "code_maladie": fields.Integer(required=True, description="Disease Code"),
    "code_periode": fields.Integer(required=True, description="Period Code"),
})

@rapport_api.route("/")
class RapportList(Resource):
    """Handles listing and creating rapports"""

    @rapport_api.marshal_list_with(rapport_model)
    def get(self):
        """Get all rapports"""
        repo = RapportRepository(db.session)
        return repo.get_all(), 200

    @rapport_api.expect(rapport_create_model)
    @rapport_api.marshal_with(rapport_model, code=201)
    def post(self):
        """Create a new rapport"""
        data = request.get_json()
        repo = RapportRepository(db.session)
        return repo.create(**data), 201


@rapport_api.route("/<int:code_rapport>")
class RapportResource(Resource):
    """Handles operations on a single rapport"""

    @rapport_api.marshal_with(rapport_model)
    def get(self, code_rapport):
        """Get a rapport by its ID"""
        repo = RapportRepository(db.session)
        rapport = repo.get_by_id(code_rapport)
        if not rapport:
            rapport_api.abort(404, "Rapport not found")
        return rapport

    @rapport_api.expect(rapport_create_model)
    @rapport_api.marshal_with(rapport_model)
    def put(self, code_rapport):
        """Update an existing rapport"""
        data = request.get_json()
        repo = RapportRepository(db.session)
        updated_rapport = repo.update(code_rapport, **data)
        if not updated_rapport:
            rapport_api.abort(404, "Rapport not found")
        return updated_rapport

    def delete(self, code_rapport):
        """Delete a rapport by its ID"""
        repo = RapportRepository(db.session)
        if not repo.delete(code_rapport):
            rapport_api.abort(404, "Rapport not found")
        return {"message": "Rapport deleted"}, 200