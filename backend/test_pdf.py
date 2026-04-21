"""
Run this script to see exactly what pdfplumber extracts from your bank statement.
Usage:
  python test_pdf.py "path/to/your/statement.pdf" [password]
"""
import sys
import pdfplumber
import pikepdf
import os
import tempfile

def test_pdf(pdf_path, password=""):
    path = pdf_path
    tmp = None

    # Decrypt if needed
    try:
        with pikepdf.open(pdf_path) as _:
            print("✅ PDF is NOT password-protected")
    except pikepdf.PasswordError:
        print("🔒 PDF is password-protected, decrypting...")
        if not password:
            print("❌ Provide password as second argument!")
            return
        fd, tmp = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        with pikepdf.open(pdf_path, password=password) as p:
            p.save(tmp)
        path = tmp
        print("✅ Decrypted successfully")

    with pdfplumber.open(path) as pdf:
        print(f"\n📄 Total pages: {len(pdf.pages)}")
        for i, page in enumerate(pdf.pages[:3]):   # check first 3 pages
            print(f"\n======== PAGE {i+1} ========")

            # Check tables
            tables = page.extract_tables()
            print(f"  Tables found: {len(tables)}")
            for j, table in enumerate(tables):
                print(f"\n  -- Table {j+1} ({len(table)} rows) --")
                for row_idx, row in enumerate(table[:5]):  # show first 5 rows
                    print(f"  Row {row_idx}: {row}")

            # Check raw text
            text = page.extract_text()
            if text:
                lines = [l for l in text.split('\n') if l.strip()]
                print(f"\n  Raw text lines (first 10):")
                for line in lines[:10]:
                    print(f"    {repr(line)}")

    if tmp and os.path.exists(tmp):
        os.remove(tmp)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pdf.py <pdf_path> [password]")
        sys.exit(1)
    password = sys.argv[2] if len(sys.argv) > 2 else ""
    test_pdf(sys.argv[1], password)
