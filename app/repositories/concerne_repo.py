from app.models.concerne import Concerne
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class ContinentRepository:
    
    def create(self, code_continent: int, code_pays: int, code_region: int, code_rapport: int) -> models.Concerne:
        concerne = models.Concerne(
            code_continent=code_continent,
            code_pays=code_pays,
            code_region=code_region,
            code_rapport=code_rapport
        )
        self.db.add(concerne)
        self.db.commit()
        self.db.refresh(concerne)
        return concerne

    def get_all(self) -> List[models.Concerne]:
        return self.db.query(models.Concerne).all()

    def delete(self, code_continent: int, code_pays: int, code_region: int, code_rapport: int) -> bool:
        concerne = self.db.query(models.Concerne).filter(
            models.Concerne.code_continent == code_continent,
            models.Concerne.code_pays == code_pays,
            models.Concerne.code_region == code_region,
            models.Concerne.code_rapport == code_rapport
        ).first()
        if concerne:
            self.db.delete(concerne)
            self.db.commit()
            return True
        return False