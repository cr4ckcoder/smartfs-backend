import io
import pandas as pd

def _to_number(x: str) -> float:
    if x is None:
        return 0.0
    s = str(x).strip().replace(',', '').replace('"', '')
    if s in ('', '-', '—'):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0

def parse_trial_balance_csv(content: bytes) -> list[dict]:
    # Reads CSV bytes and returns a list of dicts with normalized fields
    df = pd.read_csv(io.BytesIO(content), dtype=str, skip_blank_lines=True)
    # Heuristic column name mapping
    cols = {c.lower().strip(): c for c in df.columns}
    name_col = cols.get('account') or cols.get('account_name') or list(df.columns)[0]
    debit_col = cols.get('debit') or 'Debit'
    credit_col = cols.get('credit') or 'Credit'
    closing_col = cols.get('closing_balance') or cols.get('balance') or credit_col

    out = []
    for _, row in df.iterrows():
        out.append({
            "account_name": str(row.get(name_col, "")).strip(),
            "debit": _to_number(row.get(debit_col)),
            "credit": _to_number(row.get(credit_col)),
            "closing_balance": _to_number(row.get(closing_col)),
        })
    return out
