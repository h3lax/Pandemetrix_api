from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db import db

class Continent(db.Model):
    __tablename__ = 'continent'
    
    code_continent = Column(String(10), primary_key=True)
    nom = Column(String(50), nullable=False)
    
    pays = relationship("Pays", back_populates="continent")
    regions = relationship("Region", secondary="concerne", back_populates="continents")
