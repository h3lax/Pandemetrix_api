from sqlalchemy import Column, String, Integer, Identity
from sqlalchemy.orm import relationship
from app.db import db

class Continent(db.Model):
    __tablename__ = "continent"

    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    code_continent = Column(String(50), unique=True, nullable=False)
    nom = Column(String(50), nullable=False)
    pays = relationship("Pays", back_populates="continent")

    def to_dict(self):
        """Ensure consistency with API response"""
        return {
            "id": self.id,
            "code_continent": self.code_continent,
            "nom": self.nom
        }
