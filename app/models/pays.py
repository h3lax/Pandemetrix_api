from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.db import db

class Pays(db.Model):
    __tablename__ = 'pays'
    
    code_pays = Column(String(10), primary_key=True)
    nom = Column(String(50), nullable=False)
    nom_continent = Column(String(50), nullable=False)

    continent = relationship("Continent", back_populates="pays")
    regions = relationship("Region", back_populates="pays")
