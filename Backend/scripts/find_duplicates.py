#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'

checks = {
    'accounts_user': ['username', 'email'],
    'auth_group': ['name'],
    'families_familymember': ['member_id', 'phone_no', 'email_id'],
    'families_family': ['sl_no'],
}


def find_dupes(conn, table, col):
    cur = conn.execute(f"SELECT {col}, COUNT(*) as c FROM '{table}' WHERE {col} IS NOT NULL GROUP BY {col} HAVING c>1 ORDER BY c DESC LIMIT 100;")
    return cur.fetchall()


def main():
    if not DB.exists():
        print('DB not found:', DB)
        return
    conn = sqlite3.connect(str(DB))
    total = 0
    for table, cols in checks.items():
        for col in cols:
            rows = find_dupes(conn, table, col)
            if rows:
                print(f'Duplicates in {table}.{col}:')
                for val, cnt in rows:
                    print(f'  {val!r} — {cnt}')
                print()
                total += len(rows)
    if total == 0:
        print('No duplicates found in checked columns.')
    conn.close()


if __name__ == '__main__':
    main()
