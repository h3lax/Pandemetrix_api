from sqlalchemy.orm import Session
from typing import List
from app import models

class ConcerneRepository:
    """Repository for managing Concerne data"""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, **kwargs) -> models.Concerne:
        """Create a new concerne entry"""
        concerne = models.Concerne(**kwargs)
        self.db_session.add(concerne)
        self.db_session.commit()
        self.db_session.refresh(concerne)
        return concerne

    def get_all(self) -> List[models.Concerne]:
        """Retrieve all concerne entries"""
        return self.db_session.query(models.Concerne).all()

    def delete(self, code_continent: str, code_pays: str, code_region: str, code_rapport: int) -> bool:
        """Delete a concerne entry by its composite key"""
        concerne = self.db_session.query(models.Concerne).filter(
            models.Concerne.code_continent == code_continent,
            models.Concerne.code_pays == code_pays,
            models.Concerne.code_region == code_region,
            models.Concerne.code_rapport == code_rapport
        ).first()
        if concerne:
            self.db_session.delete(concerne)
            self.db_session.commit()
            return True
        return False