from sqlalchemy import Column, String, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db

class Rapport(db.Model):
    __tablename__ = 'rapport'
    
    code_rapport = Column(Integer, primary_key=True)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    source = Column(String(50))
    nouveaux_cas = Column(Integer, default=0)
    nouveaux_deces = Column(Integer, default=0)
    nouveaux_gueris = Column(Integer, default=0)
    cas_actifs = Column(Integer, default=0)
    taux_mortalite = Column(Integer)
    taux_guerison = Column(Integer)
    code_maladie = Column(Integer, ForeignKey('maladie.code_maladie', ondelete='CASCADE'), nullable=False)
    code_periode = Column(Integer, ForeignKey('periode.code_periode', ondelete='CASCADE'), nullable=False)
    maladie = relationship('Maladie', back_populates='rapports')
    periode = relationship('Periode', back_populates='rapports')

    def to_dict(self):
        return {
            'code_rapport': self.code_rapport,
            'date_debut': str(self.date_debut) if self.date_debut else None,
            'date_fin': str(self.date_fin) if self.date_fin else None,
            'source': self.source,
            'nouveaux_cas': self.nouveaux_cas,
            'nouveaux_deces': self.nouveaux_deces,
            'nouveaux_gueris': self.nouveaux_gueris,
            'cas_actifs': self.cas_actifs,
            'taux_mortalite': self.taux_mortalite,
            'taux_guerison': self.taux_guerison,
            'code_maladie': self.code_maladie,
            'code_periode': self.code_periode
        }
