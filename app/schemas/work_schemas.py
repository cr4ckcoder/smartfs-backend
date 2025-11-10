from pydantic import BaseModel
from datetime import date

class WorkCreate(BaseModel):
    company_id: int
    start_date: date
    end_date: date

class WorkOut(WorkCreate):
    id: int
    status: str
    class Config:
        from_attributes = True
