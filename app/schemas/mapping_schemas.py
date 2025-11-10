from pydantic import BaseModel

class MapEntryPayload(BaseModel):
    trial_balance_entry_id: int
    account_sub_head_id: int

class UnmappedEntryOut(BaseModel):
    id: int
    account_name: str
    debit: float
    credit: float
    closing_balance: float
    
    class Config:
        from_attributes = True