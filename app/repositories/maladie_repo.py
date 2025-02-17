from app.models.maladie import Maladie
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class MaladieRepository:
    """Repository for managing Maladie data"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, **kwargs) -> models.Maladie:
        """Create a new maladie"""
        maladie = models.Maladie(**kwargs)
        self.db_session.add(maladie)
        self.db_session.commit()
        self.db_session.refresh(maladie)
        return maladie

    def get_by_id(self, id_maladie: int) -> Optional[models.Maladie]:
        """Retrieve a maladie by its ID"""
        return self.db_session.query(models.Maladie).filter(models.Maladie.id == id_maladie).first()

    def get_all(self) -> List[models.Maladie]:
        """Retrieve all maladies"""
        return self.db_session.query(models.Maladie).all()

    def update(self, id_maladie: int, **kwargs) -> Optional[models.Maladie]:
        """Update an existing maladie"""
        maladie = self.get_by_id(id_maladie)
        if maladie:
            allowed_fields = {"nom"}
            for key, value in kwargs.items():
                if key in allowed_fields and value is not None:
                    setattr(maladie, key, value)
            self.db_session.commit()
            self.db_session.refresh(maladie)
        return maladie

    def delete(self, id_maladie: int) -> bool:
        """Delete a maladie by ID"""
        maladie = self.get_by_id(id_maladie)
        if maladie:
            self.db_session.delete(maladie)
            self.db_session.commit()
            return True
        return False