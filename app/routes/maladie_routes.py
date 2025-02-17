from flask_restx import Namespace, Resource, fields
from flask import request
from app.db import db
from app.repositories.maladie_repo import MaladieRepository

# Define Namespace
maladie_api = Namespace("maladie", description="Maladie related operations")

# Define request/response models for Swagger
maladie_model = maladie_api.model("Maladie", {
    "id": fields.Integer(description="Maladie ID"),
    "nom": fields.String(required=True, description="Maladie Name"),
})

maladie_create_model = maladie_api.model("MaladieCreate", {
    "nom": fields.String(required=True, description="Maladie Name"),
})

@maladie_api.route("/")
class MaladieList(Resource):
    """Handles listing and creating maladies"""

    @maladie_api.marshal_list_with(maladie_model)
    def get(self):
        """Get all maladies"""
        repo = MaladieRepository(db.session)
        return repo.get_all(), 200

    @maladie_api.expect(maladie_create_model)
    @maladie_api.marshal_with(maladie_model, code=201)
    def post(self):
        """Create a new maladie"""
        data = request.get_json()
        repo = MaladieRepository(db.session)
        return repo.create(**data), 201


@maladie_api.route("/<int:id_maladie>")
class MaladieResource(Resource):
    """Handles operations on a single maladie"""

    @maladie_api.marshal_with(maladie_model)
    def get(self, id_maladie):
        """Get a maladie by its ID"""
        repo = MaladieRepository(db.session)
        maladie = repo.get_by_id(id_maladie)
        if not maladie:
            maladie_api.abort(404, "Maladie not found")
        return maladie

    @maladie_api.expect(maladie_create_model)
    @maladie_api.marshal_with(maladie_model)
    def put(self, id_maladie):
        """Update an existing maladie"""
        data = request.get_json()
        repo = MaladieRepository(db.session)
        updated_maladie = repo.update(id_maladie, **data)
        if not updated_maladie:
            maladie_api.abort(404, "Maladie not found")
        return updated_maladie

    def delete(self, id_maladie):
        """Delete a maladie by its ID"""
        repo = MaladieRepository(db.session)
        if not repo.delete(id_maladie):
            maladie_api.abort(404, "Maladie not found")
        return {"message": "Maladie deleted"}, 200
