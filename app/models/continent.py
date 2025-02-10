from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db import db

class Continent(db.Model):
    __tablename__ = 'continent'

    id_continent = Column(Integer, primary_key=True)
    code_continent = Column(String(50), unique=True, nullable=False)
    nom = Column(String(50), nullable=False)
    pays = relationship("Pays", back_populates="continent")

    def to_dict(self):
        return {
            'id_continent': self.id_continent,
            'code_continent': self.code_continent,
            'nom': self.nom
        }
