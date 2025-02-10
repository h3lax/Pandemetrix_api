from app.models.maladie import Maladie
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class ContinentRepository:
    
    def create(self, nom: str) -> models.Maladie:
        maladie = models.Maladie(nom=nom)
        self.db.add(maladie)
        self.db.commit()
        self.db.refresh(maladie)
        return maladie

    def get_by_id(self, code_maladie: int) -> Optional[models.Maladie]:
        return self.db.query(models.Maladie).filter(models.Maladie.code_maladie == code_maladie).first()

    def get_all(self) -> List[models.Maladie]:
        return self.db.query(models.Maladie).all()

    def update(self, code_maladie: int, nom: str) -> Optional[models.Maladie]:
        maladie = self.get_by_id(code_maladie)
        if maladie:
            maladie.nom = nom
            self.db.commit()
            self.db.refresh(maladie)
        return maladie

    def delete(self, code_maladie: int) -> bool:
        maladie = self.get_by_id(code_maladie)
        if maladie:
            self.db.delete(maladie)
            self.db.commit()
            return True
        return False