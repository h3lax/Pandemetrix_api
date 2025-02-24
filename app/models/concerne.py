from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.db import db

class Concerne(db.Model):
    __tablename__ = 'concerne'
    
    code_continent = Column(String, ForeignKey('continent.code_continent', ondelete='CASCADE'), primary_key=True, nullable=False)
    code_pays = Column(String, ForeignKey('pays.code_pays', ondelete='CASCADE'), primary_key=True, nullable=False)
    code_region = Column(String, ForeignKey('region.code_region', ondelete='CASCADE'), primary_key=True, nullable=True)
    code_rapport = Column(Integer, ForeignKey('rapport.id', ondelete='CASCADE'), primary_key=True, nullable=False)

    continent = relationship('Continent', backref='concernes')
    pays = relationship('Pays', backref='concernes')
    region = relationship('Region', backref='concernes')
    rapport = relationship('Rapport', backref='concernes')

    def to_dict(self):
        return {
            'code_continent': self.code_continent,
            'code_pays': self.code_pays,
            'code_region': self.code_region,
            'code_rapport': self.code_rapport
        }

