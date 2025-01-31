from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db import db

class Region(db.Model):
    __tablename__ = 'region'
    
    code_region = Column(String(10), primary_key=True)
    nom = Column(String(50), nullable=False)
    nom_pays = Column(String(50), nullable=False)

    pays = relationship("Pays", back_populates="regions")
    continents = relationship("Continent", secondary="concerne", back_populates="regions")
