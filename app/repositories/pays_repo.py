from app.models import Pays

class PaysRepository:
    """Repository for managing Pays data"""

    def __init__(self, db_session):
        self.db_session = db_session

    def get_all(self):
        """Retrieve all countries"""
        return self.db_session.query(Pays).all()

    def get_by_id(self, id):
        """Retrieve a country by its ID"""
        return self.db_session.query(Pays).filter_by(id=id).first()

    def get_by_code(self, code_pays):
        """Retrieve a country by its code"""
        return self.db_session.query(Pays).filter_by(code_pays=code_pays).first()

    def get_by_continent(self, code_continent):
        """Retrieve countries by continent code"""
        return self.db_session.query(Pays).filter_by(code_continent=code_continent).all()

    def create(self, code_pays, nom, pib=None, temperature=None, code_continent=None):
        """Create a new country"""
        new_pays = Pays(
            code_pays=code_pays,
            nom=nom,
            pib=pib,
            temperature=temperature,
            code_continent=code_continent
        )
        self.db_session.add(new_pays)
        self.db_session.commit()
        self.db_session.refresh(new_pays)
        return new_pays

    def update(self, id, **data):
        """Update an existing country"""
        pays = self.get_by_id(id)
        if not pays:
            return None

        # Vérifier et mettre à jour uniquement les champs fournis
        allowed_fields = {"code_pays", "nom", "pib", "temperature", "code_continent"}
        for key, value in data.items():
            if key in allowed_fields and value is not None:
                setattr(pays, key, value)

        self.db_session.commit()
        return pays

    def delete(self, id):
        """Delete a country by ID"""
        pays = self.get_by_id(id)
        if not pays:
            return False
        self.db_session.delete(pays)
        self.db_session.commit()
        return True
