#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'

def info_for(ids):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    for i in ids:
        cur.execute('SELECT id, name, member_id, family_id FROM families_familymember WHERE id=?', (i,))
        m = cur.fetchone()
        print('Member', m)
        cur.execute('SELECT id, from_familymember_id, to_familymember_id FROM families_familymember_parents WHERE from_familymember_id=? OR to_familymember_id=?', (i,i))
        print(' Parent-links:', cur.fetchall())
        cur.execute('SELECT id, from_member_id, to_member_id, relation_type FROM families_relationship WHERE from_member_id=? OR to_member_id=?', (i,i))
        print(' Relationships:', cur.fetchall())
        print('---')
    conn.close()

if __name__ == '__main__':
    ids = [37,38,209]
    info_for(ids)
