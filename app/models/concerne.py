from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db import db

class Concerne(db.Model):
    __tablename__ = 'concerne'
    
    id_rapport = Column(String(10), ForeignKey('rapport_quotidien.id_rapport'), primary_key=True)
    code_continent = Column(String(10), ForeignKey('continent.code_continent'), primary_key=True)
    code_pays = Column(String(10), ForeignKey('pays.code_pays'), nullable=True)
    code_region = Column(String(10), ForeignKey('region.code_region'), nullable=True)
    
    rapport = relationship("RapportQuotidien", back_populates="concerne")
