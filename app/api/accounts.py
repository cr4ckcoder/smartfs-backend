from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.dependencies import get_db
from ..models.domain import Account, AccountNodeType, CategoryType

router = APIRouter()

@router.post("")
def create_account(
    name: str,
    type: AccountNodeType,
    category_type: CategoryType | None = None,
    parent_id: int | None = None,
    db: Session = Depends(get_db),
):
    if type == AccountNodeType.CATEGORY and parent_id is not None:
        raise HTTPException(status_code=400, detail="CATEGORY cannot have a parent")
    acc = Account(name=name, type=type, category_type=category_type, parent_id=parent_id)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return {"id": acc.id, "name": acc.name, "type": acc.type.value, "parent_id": acc.parent_id}

@router.get("")
def list_accounts(db: Session = Depends(get_db)):
    # Return a flat list for now; front-end can build a tree.
    q = db.query(Account).all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "type": a.type.value,
            "category_type": a.category_type.value if a.category_type else None,
            "parent_id": a.parent_id,
        }
        for a in q
    ]
