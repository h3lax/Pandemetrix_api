from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db

class Region(db.Model):
    __tablename__ = 'region'
    
    id_region = Column(Integer, primary_key=True)
    code_region = Column(String(50), unique=True, nullable=False)
    nom = Column(String(50), nullable=False)
    code_pays = Column(String, ForeignKey('pays.code_pays', ondelete='CASCADE'), nullable=False)
    pays = relationship('Pays', back_populates='regions')

    def to_dict(self):
        return {
            'id_region': self.id_region,
            'code_region': self.code_region,
            'nom': self.nom,
            'code_pays': self.code_pays
        }
