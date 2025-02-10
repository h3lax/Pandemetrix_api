from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db import db

class Periode(db.Model):
    __tablename__ = 'periode'
    
    code_periode = Column(Integer, primary_key=True)
    nom = Column(String(50), nullable=False, unique=True)
    rapports = relationship('Rapport', back_populates='periode', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'code_periode': self.code_periode,
            'nom': self.nom
        }