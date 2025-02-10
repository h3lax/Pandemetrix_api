from sqlalchemy import Column, String, Integer, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db

class Pays(db.Model):
    __tablename__ = 'pays'
    
    id_pays = Column(Integer, primary_key=True)
    code_pays = Column(String(50), unique=True, nullable=False)
    nom = Column(String(50), nullable=False)
    pib = Column(Integer)
    temperature = Column(DECIMAL(15, 2))  # Added precision
    code_continent = Column(Integer, ForeignKey('continent.code_continent', ondelete='CASCADE'), nullable=False)
    continent = relationship('Continent', back_populates='pays')
    regions = relationship('Region', back_populates='pays', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id_pays': self.id_pays,
            'code_pays': self.code_pays,
            'nom': self.nom,
            'pib': self.pib,
            'temperature': float(self.temperature) if self.temperature else None,
            'code_continent': self.code_continent
        }
