from sqlalchemy.orm import Session
from fastapi import UploadFile
from ..models.domain import FinancialWork, TrialBalanceEntry
from ..utils.csv_parser import parse_trial_balance_csv

async def process_trial_balance_upload(db: Session, work_id: int, file: UploadFile) -> int:
    """
    Processes the uploaded trial balance CSV file, parses it,
    and bulk-inserts the entries into the database.
    """
    work = db.get(FinancialWork, work_id)
    if not work:
        return -1  # Indicates work not found

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
    return len(entries)