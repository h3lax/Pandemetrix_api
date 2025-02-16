from app.models import Continent

class ContinentRepository:
    """Repository for managing Continent data"""

    def __init__(self, db_session):
        self.db_session = db_session

    def get_all(self):
        """Retrieve all continents"""
        return self.db_session.query(Continent).all()

    def get_by_id(self, id):
        """Retrieve a continent by its ID"""
        return self.db_session.query(Continent).filter_by(id=id).first()

    def get_by_code(self, code_continent):
        """Retrieve a continent by its code"""
        return self.db_session.query(Continent).filter_by(code_continent=code_continent).first()

    def create(self, code_continent, nom):
        """Create a new continent"""
        new_continent = Continent(code_continent=code_continent, nom=nom)
        self.db_session.add(new_continent)
        self.db_session.commit()
        self.db_session.refresh(new_continent)
        return new_continent

    def update(self, id, **data):
        """Update an existing continent"""
        continent = self.get_by_id(id)
        if not continent:
            return None
        for key, value in data.items():
            setattr(continent, key, value)
        self.db_session.commit()
        return continent

    def delete(self, id):
        """Delete a continent by ID"""
        continent = self.get_by_id(id)
        if not continent:
            return False
        self.db_session.delete(continent)
        self.db_session.commit()
        return True
