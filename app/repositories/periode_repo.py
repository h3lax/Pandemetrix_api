from app.models.periode import Periode
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class ContinentRepository:
    
    def create(self, nom: str) -> models.Periode:
        periode = models.Periode(nom=nom)
        self.db.add(periode)
        self.db.commit()
        self.db.refresh(periode)
        return periode

    def get_by_id(self, code_periode: int) -> Optional[models.Periode]:
        return self.db.query(models.Periode).filter(models.Periode.code_periode == code_periode).first()

    def get_all(self) -> List[models.Periode]:
        return self.db.query(models.Periode).all()

    def update(self, code_periode: int, nom: str) -> Optional[models.Periode]:
        periode = self.get_by_id(code_periode)
        if periode:
            periode.nom = nom
            self.db.commit()
            self.db.refresh(periode)
        return periode

    def delete(self, code_periode: int) -> bool:
        periode = self.get_by_id(code_periode)
        if periode:
            self.db.delete(periode)
            self.db.commit()
            return True
        return False