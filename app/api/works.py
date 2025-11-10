from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..core.dependencies import get_db
from ..models.domain import FinancialWork, WorkStatus, TrialBalanceEntry
from ..schemas.work_schemas import WorkCreate, WorkOut
from ..utils.csv_parser import parse_trial_balance_csv

router = APIRouter()

@router.post("", response_model=WorkOut, status_code=201)
def create_work(payload: WorkCreate, db: Session = Depends(get_db)):
    work = FinancialWork(**payload.model_dump())
    db.add(work)
    db.commit()
    db.refresh(work)
    return WorkOut(**{
        **payload.model_dump(),
        "id": work.id,
        "status": work.status.value
    })

@router.post("/{work_id}/trial-balance")
async def upload_trial_balance(work_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    work = db.get(FinancialWork, work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")

    content = await file.read()
    rows = parse_trial_balance_csv(content)

    entries = []
    for r in rows:
        entry = TrialBalanceEntry(
            financial_work_id=work_id,
            account_name=r["account_name"],
            debit=r["debit"],
            credit=r["credit"],
            closing_balance=r["closing_balance"],
        )
        entries.append(entry)

    db.add_all(entries)
    db.commit()
    return {"inserted": len(entries)}
