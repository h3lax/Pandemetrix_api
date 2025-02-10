from app.models.region import Region
from app.db import db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models

class RegionRepository:
    
    def create(self, code_region: str, nom: str, code_pays: int) -> models.Region:
        region = models.Region(code_region=code_region, nom=nom, code_pays=code_pays)
        self.db.add(region)
        self.db.commit()
        self.db.refresh(region)
        return region

    def get_by_id(self, id_region: int) -> Optional[models.Region]:
        return self.db.query(models.Region).filter(models.Region.id_region == id_region).first()

    def get_by_code(self, code_region: str) -> Optional[models.Region]:
        return self.db.query(models.Region).filter(models.Region.code_region == code_region).first()

    def get_all(self) -> List[models.Region]:
        return self.db.query(models.Region).all()

    def update(self, id_region: int, **kwargs) -> Optional[models.Region]:
        region = self.get_by_id(id_region)
        if region:
            for key, value in kwargs.items():
                setattr(region, key, value)
            self.db.commit()
            self.db.refresh(region)
        return region

    def delete(self, id_region: int) -> bool:
        region = self.get_by_id(id_region)
        if region:
            self.db.delete(region)
            self.db.commit()
            return True
        return False