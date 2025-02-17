from app.models.rapport import Rapport
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class RapportRepository:
    """Repository for managing Rapport data"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, **kwargs) -> models.Rapport:
        """Create a new rapport"""
        rapport = models.Rapport(**kwargs)
        self.db_session.add(rapport)
        self.db_session.commit()
        self.db_session.refresh(rapport)
        return rapport

    def get_by_id(self, code_rapport: int) -> Optional[models.Rapport]:
        """Retrieve a rapport by its ID"""
        return self.db_session.query(models.Rapport).filter(models.Rapport.id == code_rapport).first()

    def get_all(self) -> List[models.Rapport]:
        """Retrieve all rapports"""
        return self.db_session.query(models.Rapport).all()

    def update(self, code_rapport: int, **kwargs) -> Optional[models.Rapport]:
        """Update an existing rapport"""
        rapport = self.get_by_id(code_rapport)
        if rapport:
            allowed_fields = {
                "date_debut", "date_fin", "source", "nouveaux_cas", "nouveaux_deces",
                "nouveaux_gueris", "cas_actifs", "taux_mortalite", "taux_guerison",
                "code_maladie", "code_periode"
            }
            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    setattr(rapport, key, value)
            self.db_session.commit()
            self.db_session.refresh(rapport)
        return rapport

    def delete(self, code_rapport: int) -> bool:
        """Delete a rapport by ID"""
        rapport = self.get_by_id(code_rapport)
        if rapport:
            self.db_session.delete(rapport)
            self.db_session.commit()
            return True
        return False