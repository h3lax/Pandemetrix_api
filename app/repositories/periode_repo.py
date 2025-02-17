from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class PeriodeRepository:
    """Repository for managing Periode data"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, **kwargs) -> models.Periode:
        """Create a new periode"""
        periode = models.Periode(**kwargs)
        self.db_session.add(periode)
        self.db_session.commit()
        self.db_session.refresh(periode)
        return periode

    def get_by_id(self, id_periode: int) -> Optional[models.Periode]:
        """Retrieve a periode by its ID"""
        return self.db_session.query(models.Periode).filter(models.Periode.id == id_periode).first()

    def get_all(self) -> List[models.Periode]:
        """Retrieve all periodes"""
        return self.db_session.query(models.Periode).all()

    def update(self, id_periode: int, **kwargs) -> Optional[models.Periode]:
        """Update an existing periode"""
        periode = self.get_by_id(id_periode)
        if periode:
            allowed_fields = {"nom"}
            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    setattr(periode, key, value)
            self.db_session.commit()
            self.db_session.refresh(periode)
        return periode

    def delete(self, id_periode: int) -> bool:
        """Delete a periode by ID"""
        periode = self.get_by_id(id_periode)
        if periode:
            self.db_session.delete(periode)
            self.db_session.commit()
            return True
        return False