from app.models.continent import Continent
from app.db import db

class ContinentRepository:
    @staticmethod
    def create_continent(code_continent, nom):
        continent = Continent(code_continent=code_continent, nom=nom, pays=[], regions=[])
        db.session.add(continent)
        db.session.commit()
        return continent

    @staticmethod
    def get_all_continents():
        return Continent.query.all()

    @staticmethod
    def get_continent_by_code(code_continent):
        return Continent.query.get(code_continent)

    @staticmethod
    def update_continent(code_continent, nom):
        continent = Continent.query.get(code_continent)
        if continent:
            continent.nom = nom
            db.session.commit()
        return continent

    @staticmethod
    def delete_continent(code_continent):
        continent = Continent.query.get(code_continent)
        if continent:
            db.session.delete(continent)
            db.session.commit()
        return continent