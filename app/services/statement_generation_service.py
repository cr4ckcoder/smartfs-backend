# Placeholder for Statement generation service.
# Implement calculate_statement_data and aggregations over the Account hierarchy here.
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, and_
from ..models.domain import (
    MappedLedgerEntry,
    TrialBalanceEntry,
    Account,
    CategoryType
)
from typing import Dict, TypedDict

class CalculatedData(TypedDict):
    """
    A simple typed dictionary for the calculated data.
    The key is the Account ID, the value is the summed balance.
    """
    by_sub_head: Dict[int, float]
    by_head: Dict[int, float]
    by_category: Dict[int, float]

def calculate_statement_data(db: Session, work_id: int) -> CalculatedData:
    """
    Aggregates all mapped trial balance entries up the Account hierarchy
    (Sub-Head -> Head -> Category) for a specific financial work.
    """
    
    # Aliases for the account hierarchy
    SubHead = aliased(Account)
    Head = aliased(Account)
    Category = aliased(Account)

    # 1. Base query: Get the sum of closing_balance for each SubHead
    # This joins MappedLedgerEntry -> TrialBalanceEntry -> Account (SubHead)
    sub_head_totals_sq = (
        select(
            MappedLedgerEntry.account_sub_head_id,
            func.sum(TrialBalanceEntry.closing_balance).label("sub_head_total")
        )
        .join(TrialBalanceEntry, MappedLedgerEntry.trial_balance_entry_id == TrialBalanceEntry.id)
        .where(TrialBalanceEntry.financial_work_id == work_id)
        .group_by(MappedLedgerEntry.account_sub_head_id)
    ).subquery()

    # 2. Main query: Join the SubHead totals up the hierarchy
    # (SubHead Totals) -> SubHead -> Head -> Category
    stmt = (
        select(
            # SubHead Info
            SubHead.id.label("sub_head_id"),
            sub_head_totals_sq.c.sub_head_total,
            
            # Head Info
            Head.id.label("head_id"),
            
            # Category Info
            Category.id.label("category_id"),
            Category.category_type
        )
        .join(SubHead, sub_head_totals_sq.c.account_sub_head_id == SubHead.id)
        .join(Head, SubHead.parent_id == Head.id)
        .join(Category, Head.parent_id == Category.id)
    )

    results = db.execute(stmt).all()

    # 3. Aggregate in Python
    # This provides the flexibility described in the blueprint
    by_sub_head: Dict[int, float] = {}
    by_head: Dict[int, float] = {}
    by_category: Dict[int, float] = {}

    for row in results:
        sh_id, total, h_id, c_id, c_type = row
        
        # Add to sub-head totals
        by_sub_head[sh_id] = by_sub_head.get(sh_id, 0) + total
        
        # Add to head totals
        by_head[h_id] = by_head.get(h_id, 0) + total
        
        # Add to category totals
        by_category[c_id] = by_category.get(c_id, 0) + total

    return {
        "by_sub_head": by_sub_head,
        "by_head": by_head,
        "by_category": by_category
    }