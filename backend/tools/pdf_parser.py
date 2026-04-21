import pdfplumber
import pikepdf
import re
import os
import tempfile
from typing import List, Dict


def _parse_amount(text: str) -> float:
    """Extract a numeric value from a cell string like '9,942.85 Cr' or '700.00'."""
    if not text:
        return 0.0
    cleaned = re.sub(r'[^\d.]', '', text.replace(',', ''))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _find_col_index(headers: list, keywords: list) -> int:
    """Find which column index matches any of the given keywords (case-insensitive)."""
    for i, h in enumerate(headers):
        if h and any(kw.lower() in str(h).lower() for kw in keywords):
            return i
    return -1


def parse_bank_statement(pdf_path: str, password: str = "") -> List[Dict]:
    """
    Extracts all transaction data from a bank statement PDF.
    - AUTO-DETECTS if PDF is encrypted and decrypts with pikepdf if needed.
    - Reads STRUCTURED TABLES to correctly identify Withdrawal/Deposit columns.
    - Falls back to raw text line extraction for non-tabular PDFs.
    """
    transactions = []
    path_to_parse = pdf_path
    tmp_decrypted = None

    # ── Step 1: Auto-detect encryption ───────────────────────────────────────
    try:
        with pikepdf.open(pdf_path) as _:
            pass
        print("PDF is not password-protected. Parsing directly...")
    except pikepdf.PasswordError:
        print("PDF is password-protected. Attempting decryption...")
        if not password:
            print("ERROR: PDF is encrypted but no password was provided.")
            return []
        try:
            tmp_fd, tmp_decrypted = tempfile.mkstemp(suffix=".pdf")
            os.close(tmp_fd)
            with pikepdf.open(pdf_path, password=password) as locked_pdf:
                locked_pdf.save(tmp_decrypted)
            path_to_parse = tmp_decrypted
            print("PDF decrypted successfully!")
        except pikepdf.PasswordError:
            print("ERROR: Incorrect password.")
            return []
        except Exception as e:
            print(f"Decryption error: {e}")
            return []

    # ── Step 2: Parse with pdfplumber ─────────────────────────────────────────
    print(f"pdfplumber is processing: {path_to_parse}...")
    seen_lines = set()

    try:
        with pdfplumber.open(path_to_parse) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):

                # ── 2a. Try structured table extraction first ─────────────────
                tables = page.extract_tables()
                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # Detect header row — find Withdrawal/Deposit/Balance columns
                    header = [str(c).strip() if c else "" for c in table[0]]
                    withdrawal_col = _find_col_index(header, ["withdrawal", "debit", "dr"])
                    deposit_col    = _find_col_index(header, ["deposit", "credit", "cr"])
                    balance_col    = _find_col_index(header, ["balance"])

                    for row in table[1:]:  # skip header
                        if not row:
                            continue

                        cells = [str(c).strip() if c else "" for c in row]
                        row_text = " | ".join(c for c in cells if c)

                        if not row_text or row_text in seen_lines:
                            continue

                        # If we found structured columns, extract debit/credit directly
                        if withdrawal_col >= 0 or deposit_col >= 0:
                            debit  = _parse_amount(cells[withdrawal_col]) if withdrawal_col >= 0 and withdrawal_col < len(cells) else 0.0
                            credit = _parse_amount(cells[deposit_col])    if deposit_col >= 0    and deposit_col    < len(cells) else 0.0

                            # Skip balance-only or header rows
                            if debit == 0 and credit == 0:
                                continue

                            seen_lines.add(row_text)
                            transactions.append({
                                "raw_line": row_text,
                                "debit": debit,
                                "credit": credit,
                                "source": "table"
                            })
                        else:
                            # No structured columns found — store raw row
                            if any(ch.isdigit() for ch in row_text) and len(row_text) > 10:
                                seen_lines.add(row_text)
                                transactions.append({
                                    "raw_line": row_text,
                                    "debit": 0.0,
                                    "credit": 0.0,
                                    "source": "table_raw"
                                })

                # ── 2b. Fallback: raw text lines ──────────────────────────────
                text = page.extract_text()
                if text:
                    for line in text.split("\n"):
                        line = line.strip()
                        if (
                            any(ch.isdigit() for ch in line)
                            and len(line) > 10
                            and line not in seen_lines
                        ):
                            seen_lines.add(line)
                            transactions.append({
                                "raw_line": line,
                                "debit": 0.0,
                                "credit": 0.0,
                                "source": "text"
                            })

        structured = sum(1 for t in transactions if t["source"] == "table")
        print(f"Extracted {len(transactions)} lines ({structured} from structured table columns)")

    except Exception as e:
        print(f"Error parsing PDF: {e}")

    finally:
        if tmp_decrypted and os.path.exists(tmp_decrypted):
            os.remove(tmp_decrypted)

    return transactions
