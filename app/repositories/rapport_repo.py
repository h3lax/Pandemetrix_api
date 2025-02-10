from app.models.rapport import Rapport
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class ContinentRepository:
    
    def create(self, **kwargs) -> models.Rapport:
        rapport = models.Rapport(**kwargs)
        self.db.add(rapport)
        self.db.commit()
        self.db.refresh(rapport)
        return rapport

    def get_by_id(self, code_rapport: int) -> Optional[models.Rapport]:
        return self.db.query(models.Rapport).filter(models.Rapport.code_rapport == code_rapport).first()

    def get_all(self) -> List[models.Rapport]:
        return self.db.query(models.Rapport).all()

    def update(self, code_rapport: int, **kwargs) -> Optional[models.Rapport]:
        rapport = self.get_by_id(code_rapport)
        if rapport:
            for key, value in kwargs.items():
                setattr(rapport, key, value)
            self.db.commit()
            self.db.refresh(rapport)
        return rapport

    def delete(self, code_rapport: int) -> bool:
        rapport = self.get_by_id(code_rapport)
        if rapport:
            self.db.delete(rapport)
            self.db.commit()
            return True
        return False