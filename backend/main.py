from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from typing import Optional

from agent.gemini_agent import process_query_with_agent, get_dashboard_summary
from tools.pdf_parser import parse_bank_statement
import os
import tempfile

# ── Optional PostgreSQL support ───────────────────────────────────────────────
try:
    from sqlalchemy.orm import Session
    from db.database import create_tables, get_db
    import db.crud as crud
    DB_AVAILABLE = True
    print("✅ PostgreSQL database module loaded.")
except Exception as e:
    DB_AVAILABLE = False
    print(f"⚠️  Database not available ({e}). Running in in-memory mode.")
    def get_db():
        yield None

# ── In-memory fallback with file persistence ──────────────────────────────────
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_store.json")

def _load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"savings": 0, "recent_transactions": [], "cached_summary": None}

def _save_memory(mem: dict):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(mem, f)
    except Exception as e:
        print(f"Warning: could not save memory: {e}")

ai_memory = _load_memory()
print(f"✅ Loaded {len(ai_memory.get('recent_transactions', []))} transactions from memory store.")

app = FastAPI(title="Finance AI Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    if DB_AVAILABLE:
        create_tables()

class ChatRequest(BaseModel):
    query: str
    context: dict = {}
    session_id: str = "default"

# ─────────────────────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Finance AI Agent is running"}


@app.get("/debug")
def debug_data(db=Depends(get_db)):
    """Show raw parsed data to diagnose calculation issues."""
    from agent.gemini_agent import _precalculate_totals

    if DB_AVAILABLE and db:
        latest = crud.get_latest_upload(db)
        if not latest:
            return {"error": "No upload found in DB"}
        txns = crud.get_transactions_for_upload(db, latest.id)
        transactions = [{"raw_line": t.raw_line, "debit": 0, "credit": 0} for t in txns]
    else:
        transactions = ai_memory.get("recent_transactions", [])

    totals = _precalculate_totals(transactions)
    return {
        "total_transactions": len(transactions),
        "totals": totals,
        "sample_lines": [t.get("raw_line", "") for t in transactions[:10]]
    }


@app.get("/summary")
async def get_summary(refresh: bool = False, db=Depends(get_db)):
    if DB_AVAILABLE and db:
        if not refresh:
            cached = crud.get_latest_summary(db)
            if cached:
                return cached
        latest_upload = crud.get_latest_upload(db)
        if not latest_upload or latest_upload.total_transactions == 0:
            return {"total_savings": 0, "stats": [], "insight": "No data uploaded.",
                    "reason": "Please upload a bank statement.", "recommendation": "Go to the Upload tab."}
        transactions = crud.get_transactions_for_upload(db, latest_upload.id)
        context = {"recent_transactions": [{"raw_line": t.raw_line} for t in transactions]}
        summary = get_dashboard_summary(context)
        if "error" not in summary:
            crud.save_summary(db, latest_upload.id, summary)
        return summary

    # ── In-memory fallback ────────────────────────────────────────────────────
    if refresh:
        ai_memory["cached_summary"] = None
    if not ai_memory["cached_summary"]:
        if not ai_memory["recent_transactions"]:
            return {"total_savings": 0, "stats": [], "insight": "No data uploaded.",
                    "reason": "Please upload a bank statement.", "recommendation": "Go to the Upload tab."}
        summary = get_dashboard_summary(ai_memory)
        if "error" not in summary:
            ai_memory["cached_summary"] = summary
            ai_memory["savings"] = summary.get("total_savings", 0)
        return summary
    return ai_memory["cached_summary"]


@app.post("/chat")
async def chat_endpoint(request: ChatRequest, db=Depends(get_db)):
    if DB_AVAILABLE and db:
        crud.save_message(db, role="user", message=request.query, session_id=request.session_id)
        latest_upload = crud.get_latest_upload(db)
        context = {"recent_transactions": []}
        if latest_upload:
            txns = crud.get_transactions_for_upload(db, latest_upload.id)
            context["recent_transactions"] = [{"raw_line": t.raw_line} for t in txns]
        response = process_query_with_agent(request.query, context)
        ai_text = f"Insight: {response.insight}. {response.reason}. {response.recommendation}"
        crud.save_message(db, role="assistant", message=ai_text, session_id=request.session_id)
    else:
        response = process_query_with_agent(request.query, ai_memory)

    return {"insight": response.insight, "reason": response.reason, "recommendation": response.recommendation}


@app.post("/upload/statement")
async def upload_statement(file: UploadFile = File(...), password: str = Form(""), db=Depends(get_db)):
    if not file.filename.endswith('.pdf'):
        return {"filename": file.filename, "message": "Only PDF files are supported.", "status": "error"}
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        transactions = parse_bank_statement(tmp_path, password=password)
        os.remove(tmp_path)

        if transactions == [] and not password:
            return {"filename": file.filename, "status": "encrypted",
                    "message": "This PDF is password-protected. Please enter the password."}

        if DB_AVAILABLE and db:
            upload = crud.create_upload(db, filename=file.filename, transactions=transactions)
            return {"filename": file.filename, "status": "processed", "upload_id": upload.id,
                    "message": f"Successfully parsed {len(transactions)} transactions and saved to database!"}
        else:
            # Replace — don't append — so old statement data doesn't pollute new upload
            ai_memory["recent_transactions"] = transactions
            ai_memory["cached_summary"] = None
            ai_memory["savings"] = 0
            _save_memory(ai_memory)   # persist to disk
            return {"filename": file.filename, "status": "processed",
                    "message": f"Successfully parsed {len(transactions)} transactions into memory!"}
    except Exception as e:
        return {"filename": file.filename, "status": "error", "message": str(e)}


@app.get("/chat/history")
async def get_history(session_id: str = "default", db=Depends(get_db)):
    if DB_AVAILABLE and db:
        messages = crud.get_chat_history(db, session_id=session_id)
        return [{"role": m.role, "message": m.message, "ts": m.created_at} for m in messages]
    return []


@app.get("/uploads")
async def list_uploads(db=Depends(get_db)):
    if DB_AVAILABLE and db:
        uploads = db.query(crud.Upload).order_by(crud.Upload.uploaded_at.desc()).all()
        return [{"id": u.id, "filename": u.filename, "total_transactions": u.total_transactions,
                 "uploaded_at": u.uploaded_at} for u in uploads]
    return [{"note": "Running in in-memory mode. Set up PostgreSQL to enable persistence."}]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
