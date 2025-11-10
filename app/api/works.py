from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..core.dependencies import get_db
from ..models.domain import FinancialWork, WorkStatus, TrialBalanceEntry
from ..schemas.work_schemas import WorkCreate, WorkOut
from ..utils.csv_parser import parse_trial_balance_csv
from ..schemas.mapping_schemas import MapEntryPayload, UnmappedEntryOut
from typing import List

from ..services import report_rendering_service, statement_generation_service
from ..models.domain import ReportTemplate, Account
from fastapi.responses import Response
from typing import Literal


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


@router.get("/{work_id}/unmapped-entries", response_model=List[UnmappedEntryOut])
def get_unmapped_entries(work_id: int, db: Session = Depends(get_db)):
    """
    Get a list of trial balance entries that need to be mapped.
    """
    entries = mapping_service.list_unmapped_entries(db, work_id)
    return entries

@router.post("/{work_id}/map-entry", status_code=201)
def map_entry(work_id: int, payload: MapEntryPayload, db: Session = Depends(get_db)):
    """
    Map a trial balance entry to a chart of accounts sub-head.
    """
    try:
        mapping = mapping_service.create_mapping(db, payload)
        return {"id": mapping.id, "trial_entry_id": mapping.trial_balance_entry_id, "sub_head_id": mapping.account_sub_head_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.get("/{work_id}/statements/{template_id}")
def generate_statement(
    work_id: int,
    template_id: int,
    format: Literal["pdf", "xlsx"] = "pdf",
    db: Session = Depends(get_db)
):
    """
    Generate a financial statement for a work using a template.
    """
    # 1. Get the Report Template
    template = db.get(ReportTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Report template not found")

    # 2. Get the Calculated Data
    calculated_data = statement_generation_service.calculate_statement_data(db, work_id)
    
    # 3. Get all accounts (for labels)
    accounts = db.scalars(select(Account)).all()
    account_map = {acc.id: acc for acc in accounts} # Simple lookup map

    # 4. Render based on format
    if format == "pdf":
        content = report_rendering_service.render_pdf(template, account_map, calculated_data)
        media_type = "application/pdf"
        filename = f"{template.name}.pdf"
    
    elif format == "xlsx":
        content = report_rendering_service.render_excel(template, account_map, calculated_data)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{template.name}.xlsx"

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )