from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db import db

class Maladie(db.Model):
    __tablename__ = 'maladie'
    
    code_maladie = Column(Integer, primary_key=True)
    nom = Column(String(50), nullable=False, unique=True)
    rapports = relationship('Rapport', back_populates='maladie', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'code_maladie': self.code_maladie,
            'nom': self.nom
        }
