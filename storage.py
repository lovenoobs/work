import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

DB_PATH = Path("data.sqlite3")

def now_iso():
    return datetime.now().isoformat(timespec="seconds")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bom_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        part_no TEXT NOT NULL,
        qty INTEGER NOT NULL,
        min_year_text TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bom_item_id INTEGER NOT NULL,
        vendor_name TEXT,
        quote_text TEXT NOT NULL,
        rmb_untaxed REAL,
        rmb_taxed REAL,
        usd REAL,
        dc_text TEXT,
        lead_time TEXT,
        quote_qty INTEGER,
        created_at TEXT NOT NULL,
        FOREIGN KEY(bom_item_id) REFERENCES bom_items(id)
    )""")
    conn.commit()
    conn.close()

def clear_all():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM quotes")
    cur.execute("DELETE FROM bom_items")
    conn.commit()
    conn.close()

def insert_bom_items(items: List[Dict[str, Any]]) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for it in items:
        cur.execute(
            "INSERT INTO bom_items(part_no, qty, min_year_text, created_at) VALUES (?, ?, ?, ?)",
            (it["part_no"], int(it["qty"]), it["min_year_text"], now_iso())
        )
    conn.commit()
    conn.close()

def list_bom_items() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute("SELECT id, part_no, qty, min_year_text, created_at FROM bom_items ORDER BY id").fetchall()
    conn.close()
    return [
        {"id": r[0], "part_no": r[1], "qty": r[2], "min_year_text": r[3], "created_at": r[4]}
        for r in rows
    ]

def insert_quote(bom_item_id: int, vendor_name: Optional[str], quote_text: str,
                 rmb_untaxed: Optional[float], rmb_taxed: Optional[float], usd: Optional[float],
                 dc_text: Optional[str], lead_time: Optional[str], quote_qty: Optional[int]):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO quotes(
            bom_item_id, vendor_name, quote_text, rmb_untaxed, rmb_taxed, usd, dc_text, lead_time, quote_qty, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (bom_item_id, vendor_name, quote_text, rmb_untaxed, rmb_taxed, usd, dc_text, lead_time, quote_qty, now_iso())
    )
    conn.commit()
    conn.close()

def list_quotes() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT q.id, q.bom_item_id, b.part_no, b.qty, b.min_year_text,
               q.vendor_name, q.quote_text, q.rmb_untaxed, q.rmb_taxed, q.usd,
               q.dc_text, q.lead_time, q.quote_qty, q.created_at
        FROM quotes q
        JOIN bom_items b ON b.id = q.bom_item_id
        ORDER BY q.id
    """).fetchall()
    conn.close()
    cols = ["id","bom_item_id","part_no","qty","min_year_text","vendor_name","quote_text",
            "rmb_untaxed","rmb_taxed","usd","dc_text","lead_time","quote_qty","created_at"]
    return [dict(zip(cols, r)) for r in rows]