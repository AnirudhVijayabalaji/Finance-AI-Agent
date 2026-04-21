from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/finance_ai"  # change this!
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─── Models ───────────────────────────────────────────────────────────────────

class Upload(Base):
    """One row per PDF bank statement uploaded."""
    __tablename__ = "uploads"

    id                 = Column(Integer, primary_key=True, index=True)
    filename           = Column(String(255))
    total_transactions = Column(Integer, default=0)
    total_income       = Column(Numeric(12, 2), default=0)
    total_expenses     = Column(Numeric(12, 2), default=0)
    net_savings        = Column(Numeric(12, 2), default=0)
    uploaded_at        = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="upload")
    summaries    = relationship("DashboardSummary", back_populates="upload")


class Transaction(Base):
    """One row per extracted transaction line."""
    __tablename__ = "transactions"

    id        = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"))
    raw_line  = Column(Text)
    category  = Column(String(100), default="Other")
    amount    = Column(Numeric(12, 2), default=0)
    tx_type   = Column(String(10), default="debit")    # 'credit' or 'debit'

    upload = relationship("Upload", back_populates="transactions")


class ChatMessage(Base):
    """One row per chat message (user or assistant)."""
    __tablename__ = "chat_history"

    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), default="default")
    role       = Column(String(20))    # 'user' or 'assistant'
    message    = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class DashboardSummary(Base):
    """Cache of Gemini's JSON analysis per upload."""
    __tablename__ = "dashboard_summaries"

    id           = Column(Integer, primary_key=True, index=True)
    upload_id    = Column(Integer, ForeignKey("uploads.id"))
    summary_json = Column(JSONB)
    generated_at = Column(DateTime, default=datetime.utcnow)

    upload = relationship("Upload", back_populates="summaries")


# ─── Helper ───────────────────────────────────────────────────────────────────

def create_tables():
    """Call once on startup to create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
