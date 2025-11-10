# SMARTFS Backend (Dockerized FastAPI Starter)

This is a production-ready starter for the **Automated Financial Statement Generation Platform: SMARTFS**.
It follows the blueprint you provided (FastAPI + SQLAlchemy + Pydantic + Postgres) and includes Docker & docker-compose.
A clean, layered structure is set up with placeholders for services and endpoints you will flesh out.

## What’s included
- FastAPI app with modular routers
- SQLAlchemy ORM models for: Company, AccountingPolicy, CapitalStructure, FinancialWork, Account (hierarchy), TrialBalanceEntry, MappedLedgerEntry, ReportTemplate
- Pydantic schemas
- `pydantic-settings`-based config
- Postgres via docker-compose
- Basic CSV parser utility
- Dev conveniences: auto-reload, preconfigured health endpoint

## Quick start

1. Copy `.env.example` to `.env` and adjust if needed.
2. **Build & run**:
   ```bash
   docker compose up --build
   ```
3. Open the docs:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Useful commands
- Stop containers: `docker compose down`
- Clear volumes: `docker compose down -v`
- Rebuild: `docker compose build --no-cache`

## Structure
```
smartfs-backend/
├─ app/
│  ├─ api/
│  ├─ core/
│  ├─ models/
│  ├─ schemas/
│  ├─ services/
│  ├─ utils/
│  └─ main.py
├─ tests/
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ .env.example
└─ README.md
```

## Next steps
- Implement the service-layer methods in `app/services/`.
- Add Alembic migrations (optional) if you want versioned schema changes.
- Plug in report generation (WeasyPrint/openpyxl) as per your blueprint.
