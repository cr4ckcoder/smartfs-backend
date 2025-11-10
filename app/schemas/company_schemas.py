from pydantic import BaseModel
from typing import Optional

class CompanyCreate(BaseModel):
    legal_name: str
    cin: Optional[str] = None
    registered_address: Optional[str] = None
    company_type: Optional[str] = None
    nature_of_business: Optional[str] = None

class CompanyOut(CompanyCreate):
    id: int
    class Config:
        from_attributes = True
