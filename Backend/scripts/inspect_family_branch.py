#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'

def main(family_id=4):
    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()
    print(f'Family {family_id} members:')
    cur.execute(
        'SELECT id, name, member_id, phone_no, email_id, family_id FROM families_familymember WHERE family_id=? ORDER BY id',
        (family_id,),
    )
    for row in cur.fetchall():
        print(row)
    print('\nParent links in family branch:')
    cur.execute(
        'SELECT id, from_familymember_id, to_familymember_id FROM families_familymember_parents WHERE from_familymember_id IN (SELECT id FROM families_familymember WHERE family_id=? ) OR to_familymember_id IN (SELECT id FROM families_familymember WHERE family_id=? ) ORDER BY id',
        (family_id, family_id),
    )
    for row in cur.fetchall():
        print(row)
    conn.close()


if __name__ == '__main__':
    main()
