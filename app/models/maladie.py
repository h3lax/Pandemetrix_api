from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db import db

class Maladie(db.Model):
    __tablename__ = 'maladie'
    
    id_maladie = Column(String(10), primary_key=True)
    nom = Column(String(50), nullable=False)
    total_cas = Column(Integer)
    total_deces = Column(Integer)
    total_gueris = Column(Integer)
    total_tests = Column(Integer)
    
    rapports = relationship("RapportQuotidien", back_populates="maladie")
    statistiques = relationship("Cumule", back_populates="maladie")
