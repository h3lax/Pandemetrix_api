from app.models.region import Region

class RegionRepository:
    """Repository for managing Region data"""

    def __init__(self, db_session):
        self.db_session = db_session

    def get_all(self):
        """Retrieve all regions"""
        return self.db_session.query(Region).all()

    def get_by_id(self, id):
        """Retrieve a region by its ID"""
        return self.db_session.query(Region).filter_by(id=id).first()

    def get_by_code(self, code_region):
        """Retrieve a region by its code"""
        return self.db_session.query(Region).filter_by(code_region=code_region).first()

    def get_by_pays(self, code_pays):
        """Retrieve regions by country code"""
        return self.db_session.query(Region).filter_by(code_pays=code_pays).all()

    def create(self, code_region, nom, code_pays):
        """Create a new region"""
        new_region = Region(code_region=code_region, nom=nom, code_pays=code_pays)
        self.db_session.add(new_region)
        self.db_session.commit()
        self.db_session.refresh(new_region)
        return new_region

    def update(self, id, **data):
        """Update an existing region"""
        region = self.get_by_id(id)
        if not region:
            return None

        # Vérifier et mettre à jour uniquement les champs fournis
        allowed_fields = {"code_region", "nom", "code_pays"}
        for key, value in data.items():
            if key in allowed_fields and value is not None:
                setattr(region, key, value)

        self.db_session.commit()
        return region

    def delete(self, id):
        """Delete a region by ID"""
        region = self.get_by_id(id)
        if not region:
            return False
        self.db_session.delete(region)
        self.db_session.commit()
        return True