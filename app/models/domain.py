from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import String, Text, Enum, Integer, Date, ForeignKey, Numeric
import enum

Base = declarative_base()

class CompanyType(str, enum.Enum):
    PVT_LTD = "PVT_LTD"
    LLP = "LLP"
    PUBLIC_LTD = "PUBLIC_LTD"
    OTHER = "OTHER"

class WorkStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class AccountNodeType(str, enum.Enum):
    CATEGORY = "CATEGORY"
    HEAD = "HEAD"
    SUB_HEAD = "SUB_HEAD"

class CategoryType(str, enum.Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class Company(Base):
    __tablename__ = "company"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    cin: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    registered_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    company_type: Mapped[CompanyType | None] = mapped_column(Enum(CompanyType), nullable=True)
    nature_of_business: Mapped[str | None] = mapped_column(Text, nullable=True)

    policies: Mapped["AccountingPolicy"] = relationship(back_populates="company", uselist=False)
    capital: Mapped["CapitalStructure"] = relationship(back_populates="company", uselist=False)
    works: Mapped[list["FinancialWork"]] = relationship(back_populates="company")

class AccountingPolicy(Base):
    __tablename__ = "accounting_policy"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), unique=True)
    depreciation_method: Mapped[str | None] = mapped_column(String(128))
    inventory_valuation_method: Mapped[str | None] = mapped_column(String(128))
    revenue_recognition_basis: Mapped[str | None] = mapped_column(String(128))
    company: Mapped["Company"] = relationship(back_populates="policies")

class CapitalStructure(Base):
    __tablename__ = "capital_structure"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"), unique=True)
    authorized_capital: Mapped[float | None] = mapped_column(Numeric(18,2))
    issued_capital: Mapped[float | None] = mapped_column(Numeric(18,2))
    paid_up_capital: Mapped[float | None] = mapped_column(Numeric(18,2))
    company: Mapped["Company"] = relationship(back_populates="capital")

class FinancialWork(Base):
    __tablename__ = "financial_work"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
    start_date: Mapped[str] = mapped_column(Date, nullable=False)
    end_date: Mapped[str] = mapped_column(Date, nullable=False)
    status: Mapped[WorkStatus] = mapped_column(Enum(WorkStatus), default=WorkStatus.PENDING)

    company: Mapped["Company"] = relationship(back_populates="works")
    trial_entries: Mapped[list["TrialBalanceEntry"]] = relationship(back_populates="work")

class Account(Base):
    __tablename__ = "account"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[AccountNodeType] = mapped_column(Enum(AccountNodeType), nullable=False)
    category_type: Mapped[CategoryType | None] = mapped_column(Enum(CategoryType), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("account.id"), nullable=True)

    parent: Mapped["Account"] = relationship(remote_side=[id], backref="children")

class TrialBalanceEntry(Base):
    __tablename__ = "trial_balance_entry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    financial_work_id: Mapped[int] = mapped_column(ForeignKey("financial_work.id"))
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    debit: Mapped[float] = mapped_column(Numeric(18,2), default=0)
    credit: Mapped[float] = mapped_column(Numeric(18,2), default=0)
    closing_balance: Mapped[float] = mapped_column(Numeric(18,2))

    work: Mapped["FinancialWork"] = relationship(back_populates="trial_entries")
    mapped_entry: Mapped["MappedLedgerEntry"] = relationship(back_populates="trial_entry", uselist=False)

class MappedLedgerEntry(Base):
    __tablename__ = "mapped_ledger_entry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trial_balance_entry_id: Mapped[int] = mapped_column(ForeignKey("trial_balance_entry.id"), unique=True)
    account_sub_head_id: Mapped[int] = mapped_column(ForeignKey("account.id"))

    trial_entry: Mapped["TrialBalanceEntry"] = relationship(back_populates="mapped_entry")
    sub_head: Mapped["Account"] = relationship()

class StatementType(str, enum.Enum):
    BALANCE_SHEET = "BALANCE_SHEET"
    PROFIT_LOSS = "PROFIT_LOSS"
    CASH_FLOW = "CASH_FLOW"

class ReportTemplate(Base):
    __tablename__ = "report_template"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    statement_type: Mapped[StatementType] = mapped_column(Enum(StatementType), nullable=False)
    template_definition: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
