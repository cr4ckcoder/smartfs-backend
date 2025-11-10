from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.dependencies import get_db
from ..models.domain import Company
from ..schemas.company_schemas import CompanyCreate, CompanyOut

router = APIRouter()

@router.post("", response_model=CompanyOut, status_code=201)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
