from sqlalchemy import Column, String, Integer, Identity
from sqlalchemy.orm import relationship
from app.db import db

class Periode(db.Model):
    __tablename__ = 'periode'
    
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    nom = Column(String(50), nullable=False, unique=True)
    rapports = relationship('Rapport', back_populates='periode', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom
        }