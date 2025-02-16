from sqlalchemy import Column, String, Integer, ForeignKey, Identity
from sqlalchemy.orm import relationship
from app.db import db

class Region(db.Model):
    __tablename__ = 'region'
    
    id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    code_region = Column(String(50), unique=True, nullable=False)
    nom = Column(String(50), nullable=False)
    code_pays = Column(String, ForeignKey('pays.code_pays', ondelete='CASCADE'), nullable=False)
    pays = relationship('Pays', back_populates='regions')

    def to_dict(self):
        return {
            'id': self.id,
            'code_region': self.code_region,
            'nom': self.nom,
            'code_pays': self.code_pays
        }
