from flask import Blueprint, abort
from sqlalchemy.orm import Session
from typing import List
from app.repositories import RegionRepository
from app.schemas import RegionCreate, RegionResponse
from app.db import db

router = APIRouter(prefix="/regions", tags=["regions"])

@router.post("/", response_model=RegionResponse)
def create_region(region: RegionCreate, db: Session = Depends(get_db)):
    repo = RegionRepository(db)
    return repo.create(
        code_region=region.code_region,
        nom=region.nom,
        code_pays=region.code_pays
    )

@router.get("/", response_model=List[RegionResponse])
def get_regions(db: Session = Depends(get_db)):
    repo = RegionRepository(db)
    return repo.get_all()

@router.get("/{id_region}", response_model=RegionResponse)
def get_region(id_region: int, db: Session = Depends(get_db)):
    repo = RegionRepository(db)
    region = repo.get_by_id(id_region)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region

@router.get("/code/{code_region}", response_model=RegionResponse)
def get_region_by_code(code_region: str, db: Session = Depends(get_db)):
    repo = RegionRepository(db)
    region = repo.get_by_code(code_region)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region

@router.get("/pays/{code_pays}", response_model=List[RegionResponse])
def get_regions_by_pays(code_pays: int, db: Session = Depends(get_db)):
    repo = RegionRepository(db)
    return repo.get_by_pays(code_pays)

@router.put("/{id_region}", response_model=RegionResponse)
def update_region(id_region: int, region: RegionCreate, db: Session = Depends(get_db)):
    repo = RegionRepository(db)
    updated_region = repo.update(id_region, **region.dict())
    if not updated_region:
        raise HTTPException(status_code=404, detail="Region not found")
    return updated_region

@router.delete("/{id_region}")
def delete_region(id_region: int, db: Session = Depends(get_db)):
    repo = RegionRepository(db)
    if not repo.delete(id_region):
        raise HTTPException(status_code=404, detail="Region not found")
    return {"message": "Region deleted"}