from sqlalchemy.orm import Session
from db.database import Upload, Transaction, ChatMessage, DashboardSummary
from typing import List
import json


# ─── Upload CRUD ─────────────────────────────────────────────────────────────

def create_upload(db: Session, filename: str, transactions: list) -> Upload:
    upload = Upload(
        filename=filename,
        total_transactions=len(transactions),
    )
    db.add(upload)
    db.flush()  # get the upload.id before adding children

    for t in transactions:
        tx = Transaction(
            upload_id=upload.id,
            raw_line=t.get("raw_line", ""),
        )
        db.add(tx)

    db.commit()
    db.refresh(upload)
    return upload


def get_latest_upload(db: Session) -> Upload | None:
    return db.query(Upload).order_by(Upload.uploaded_at.desc()).first()


def get_transactions_for_upload(db: Session, upload_id: int) -> List[Transaction]:
    return db.query(Transaction).filter(Transaction.upload_id == upload_id).all()


# ─── Chat CRUD ───────────────────────────────────────────────────────────────

def save_message(db: Session, role: str, message: str, session_id: str = "default") -> ChatMessage:
    msg = ChatMessage(session_id=session_id, role=role, message=message)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_chat_history(db: Session, session_id: str = "default", limit: int = 50) -> List[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .all()
    )


# ─── Summary CRUD ────────────────────────────────────────────────────────────

def save_summary(db: Session, upload_id: int, summary: dict) -> DashboardSummary:
    s = DashboardSummary(upload_id=upload_id, summary_json=summary)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def get_latest_summary(db: Session) -> dict | None:
    latest = (
        db.query(DashboardSummary)
        .order_by(DashboardSummary.generated_at.desc())
        .first()
    )
    return latest.summary_json if latest else None
