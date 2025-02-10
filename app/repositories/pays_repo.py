from app.models.pays import Pays
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class PaysRepository:
    
    def create(self, code_pays: str, nom: str, pib: int, temperature: float, code_continent: int) -> models.Pays:
        pays = models.Pays(
            code_pays=code_pays,
            nom=nom,
            pib=pib,
            temperature=temperature,
            code_continent=code_continent
        )
        self.db.add(pays)
        self.db.commit()
        self.db.refresh(pays)
        return pays

    def get_by_id(self, id_pays: int) -> Optional[models.Pays]:
        return self.db.query(models.Pays).filter(models.Pays.id_pays == id_pays).first()

    def get_by_code(self, code_pays: str) -> Optional[models.Pays]:
        return self.db.query(models.Pays).filter(models.Pays.code_pays == code_pays).first()

    def get_all(self) -> List[models.Pays]:
        return self.db.query(models.Pays).all()

    def update(self, id_pays: int, **kwargs) -> Optional[models.Pays]:
        pays = self.get_by_id(id_pays)
        if pays:
            for key, value in kwargs.items():
                setattr(pays, key, value)
            self.db.commit()
            self.db.refresh(pays)
        return pays

    def delete(self, id_pays: int) -> bool:
        pays = self.get_by_id(id_pays)
        if pays:
            self.db.delete(pays)
            self.db.commit()
            return True
        return False