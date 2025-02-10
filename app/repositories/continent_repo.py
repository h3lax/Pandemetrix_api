from app.models.continent import Continent
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class ContinentRepository:
    
    def create(self, code_continent: str, nom: str) -> models.Continent:
        continent = models.Continent(code_continent=code_continent, nom=nom)
        self.db.add(continent)
        self.db.commit()
        self.db.refresh(continent)
        return continent

    def get_by_id(self, id_continent: int) -> Optional[models.Continent]:
        return self.db.query(models.Continent).filter(models.Continent.id_continent == id_continent).first()

    def get_by_code(self, code_continent: str) -> Optional[models.Continent]:
        return self.db.query(models.Continent).filter(models.Continent.code_continent == code_continent).first()

    def get_all(self) -> List[models.Continent]:
        return self.db.query(models.Continent).all()

    def update(self, id_continent: int, **kwargs) -> Optional[models.Continent]:
        continent = self.get_by_id(id_continent)
        if continent:
            for key, value in kwargs.items():
                setattr(continent, key, value)
            self.db.commit()
            self.db.refresh(continent)
        return continent

    def delete(self, id_continent: int) -> bool:
        continent = self.get_by_id(id_continent)
        if continent:
            self.db.delete(continent)
            self.db.commit()
            return True
        return False