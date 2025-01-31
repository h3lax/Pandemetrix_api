from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db

class Cumule(db.Model):
    __tablename__ = 'cumule'
    
    id_maladie = Column(String(10), ForeignKey('maladie.id_maladie'), primary_key=True)
    code_stats = Column(String(10), ForeignKey('statistiques_globales.code_stats'), primary_key=True)
    
    maladie = relationship("Maladie", back_populates="statistiques")
    statistiques = relationship("StatistiquesGlobales", back_populates="maladies")
