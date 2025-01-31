from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.orm import relationship
from app.db import db

class StatistiquesGlobales(db.Model):
    __tablename__ = 'statistiques_globales'
    
    code_stats = Column(String(10), primary_key=True)
    total_cas = Column(Integer)
    total_deces = Column(Integer)
    total_gueris = Column(Integer)
    total_tests = Column(Integer)
    date_maj = Column(Date)
    
    maladies = relationship("Cumule", back_populates="statistiques")
