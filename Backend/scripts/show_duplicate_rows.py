#!/usr/bin/env python3
import sqlite3
from pathlib import Path
DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'

dupes = {
    'phone_no': ['61469814207','9605957133','9400386059',''],
    'email_id': ['mani_praveen@hotmail.com',''],
}

def print_rows_for(col, vals):
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    for v in vals:
        print(f"\n--- {col} = {v!r} ---")
        if v == '':
            cur.execute(f"SELECT id, name, member_id, phone_no, email_id, family_id FROM families_familymember WHERE {col} = '' LIMIT 200;")
        else:
            cur.execute(f"SELECT id, name, member_id, phone_no, email_id, family_id FROM families_familymember WHERE {col} = ?;", (v,))
        rows = cur.fetchall()
        if not rows:
            print('  (no rows)')
        else:
            for r in rows:
                print(' ', r)
    conn.close()


def main():
    if not DB.exists():
        print('DB not found:', DB)
        return
    print('DB:', DB)
    for col, vals in dupes.items():
        print_rows_for(col, vals)

if __name__ == '__main__':
    main()
