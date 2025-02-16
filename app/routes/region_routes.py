from flask_restx import Namespace, Resource, fields
from flask import request
from app.db import db
from app.repositories.region_repo import RegionRepository

# Define Namespace
region_api = Namespace("regions", description="Region related operations")

# Define request/response models for Swagger
region_model = region_api.model("Region", {
    "id": fields.Integer(description="Region ID"),
    "code_region": fields.String(required=True, description="Region Code"),
    "nom": fields.String(required=True, description="Region Name"),
    "code_pays": fields.String(required=True, description="Country Code"),
})

region_create_model = region_api.model("RegionCreate", {
    "code_region": fields.String(required=True, description="Region Code"),
    "nom": fields.String(required=True, description="Region Name"),
    "code_pays": fields.String(required=True, description="Country Code"),
})

@region_api.route("/")
class RegionList(Resource):
    """Handles listing and creating regions"""

    @region_api.marshal_list_with(region_model)
    def get(self):
        """Get all regions"""
        repo = RegionRepository(db.session)
        return repo.get_all(), 200

    @region_api.expect(region_create_model)
    @region_api.marshal_with(region_model, code=201)
    def post(self):
        """Create a new region"""
        data = request.get_json()
        repo = RegionRepository(db.session)
        return repo.create(**data), 201


@region_api.route("/<int:id_region>")
class RegionResource(Resource):
    """Handles operations on a single region"""

    @region_api.marshal_with(region_model)
    def get(self, id_region):
        """Get a region by its ID"""
        repo = RegionRepository(db.session)
        region = repo.get_by_id(id_region)
        if not region:
            region_api.abort(404, "Region not found")
        return region

    @region_api.expect(region_create_model)
    @region_api.marshal_with(region_model)
    def put(self, id_region):
        """Update an existing region"""
        data = request.get_json()
        repo = RegionRepository(db.session)
        updated_region = repo.update(id_region, **data)
        if not updated_region:
            region_api.abort(404, "Region not found")
        return updated_region

    def delete(self, id_region):
        """Delete a region by its ID"""
        repo = RegionRepository(db.session)
        if not repo.delete(id_region):
            region_api.abort(404, "Region not found")
        return {"message": "Region deleted"}, 200


@region_api.route("/code/<string:code_region>")
class RegionByCode(Resource):
    """Handles getting a region by its code"""

    @region_api.marshal_with(region_model)
    def get(self, code_region):
        """Get a region by its code"""
        repo = RegionRepository(db.session)
        region = repo.get_by_code(code_region)
        if not region:
            region_api.abort(404, "Region not found")
        return region


@region_api.route("/pays/<int:code_pays>")
class RegionsByPays(Resource):
    """Handles getting regions by country code"""

    @region_api.marshal_list_with(region_model)
    def get(self, code_pays):
        """Get regions by country code"""
        repo = RegionRepository(db.session)
        regions = repo.get_by_pays(code_pays)
        return regions