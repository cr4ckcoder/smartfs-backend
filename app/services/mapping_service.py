# Placeholder for Mapping service.
# Implement create_mapping, list_unmapped, and validations here.
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from ..models.domain import TrialBalanceEntry, MappedLedgerEntry, Account, AccountNodeType
from ..schemas.mapping_schemas import MapEntryPayload, UnmappedEntryOut

def list_unmapped_entries(db: Session, work_id: int) -> list[UnmappedEntryOut]:
    """
    Finds all TrialBalanceEntry records for a work_id that do not
    have a corresponding entry in the MappedLedgerEntry table.
    """
    # Select trial balance entries
    stmt = (
        select(TrialBalanceEntry)
        .where(TrialBalanceEntry.financial_work_id == work_id)
        .where(~select(MappedLedgerEntry.id)
               .where(MappedLedgerEntry.trial_balance_entry_id == TrialBalanceEntry.id)
               .exists())
    )
    unmapped = db.scalars(stmt).all()
    return [UnmappedEntryOut.model_from_attributes(entry) for entry in unmapped]


def create_mapping(db: Session, payload: MapEntryPayload) -> MappedLedgerEntry:
    """
    Creates a new mapping between a trial balance entry and a sub-head account.
    Performs validation as described in the blueprint.
    """
    # 1. Check if trial entry exists
    trial_entry = db.get(TrialBalanceEntry, payload.trial_balance_entry_id)
    if not trial_entry:
        raise ValueError("Trial balance entry not found.")

    # 2. Check if sub-head account exists and is of the correct type
    sub_head = db.get(Account, payload.account_sub_head_id)
    if not sub_head:
        raise ValueError("Account sub-head not found.")
    if sub_head.type != AccountNodeType.SUB_HEAD:
        raise ValueError("Mapping must be to an account of type SUB_HEAD.")

    # 3. Check if already mapped
    existing_mapping = db.scalar(
        select(MappedLedgerEntry)
        .where(MappedLedgerEntry.trial_balance_entry_id == payload.trial_balance_entry_id)
    )
    if existing_mapping:
        raise ValueError("This trial balance entry is already mapped.")

    # 4. Create and save the new mapping
    new_mapping = MappedLedgerEntry(
        trial_balance_entry_id=payload.trial_balance_entry_id,
        account_sub_head_id=payload.account_sub_head_id
    )
    db.add(new_mapping)
    db.commit()
    db.refresh(new_mapping)
    return new_mapping