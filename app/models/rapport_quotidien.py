from sqlalchemy import Column, String, Integer, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db

class RapportQuotidien(db.Model):
    __tablename__ = 'rapport_quotidien'
    
    id_rapport = Column(String(10), primary_key=True)
    date_rapport = Column(Date)
    nouveaux_cas = Column(Integer)
    nouveaux_deces = Column(Integer)
    nouveaux_gueris = Column(Integer)
    cas_actifs = Column(Integer)
    taux_mortalite = Column(DECIMAL(5,2))
    taux_guerison = Column(DECIMAL(5,2))
    id_maladie = Column(String(10), ForeignKey('maladie.id_maladie'))

    maladie = relationship("Maladie", back_populates="rapports")
    concerne = relationship("Concerne", back_populates="rapport")
