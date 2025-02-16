from sqlalchemy import Column, String, Integer, DECIMAL, ForeignKey, Identity
from sqlalchemy.orm import relationship
from app.db import db

class Pays(db.Model):
    __tablename__ = 'pays'
    
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    code_pays = Column(String(50), unique=True, nullable=False)
    nom = Column(String(50), nullable=False)
    pib = Column(Integer, nullable=True)
    temperature = Column(DECIMAL(15, 2), nullable=True)  # Added precision
    code_continent = Column(String, ForeignKey('continent.code_continent', ondelete='CASCADE'), nullable=False)
    continent = relationship('Continent', back_populates='pays')
    regions = relationship('Region', back_populates='pays', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'code_pays': self.code_pays,
            'nom': self.nom,
            'pib': self.pib,
            'temperature': float(self.temperature) if self.temperature else None,
            'code_continent': self.code_continent
        }
