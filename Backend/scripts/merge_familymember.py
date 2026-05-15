#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path


DB = Path(__file__).resolve().parents[1] / 'db.sqlite3'


def is_blank(value):
    return value is None or value == ''


def get_member(cur, member_id):
    cur.execute('SELECT * FROM families_familymember WHERE id=?', (member_id,))
    row = cur.fetchone()
    if row is None:
        raise SystemExit(f'family member {member_id} not found')
    columns = [desc[0] for desc in cur.description]
    return dict(zip(columns, row))


def list_fk_columns(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]
    result = []
    for table in tables:
        cur.execute(f'PRAGMA foreign_key_list("{table}")')
        for ref in cur.fetchall():
            if ref[2] == 'families_familymember':
                result.append((table, ref[3]))
    return result


def merge_member(source_id, target_id):
    conn = sqlite3.connect(str(DB))
    conn.execute('PRAGMA foreign_keys=ON')
    cur = conn.cursor()

    source = get_member(cur, source_id)
    target = get_member(cur, target_id)

    source_family = source.get('family_id')
    target_family = target.get('family_id')

    fk_columns = list_fk_columns(conn)

    print(f'Merging source member {source_id} into target member {target_id}')
    print(f'Source family: {source_family} -> Target family: {target_family}')

    with conn:
        if source_family is not None and target_family is not None and source_family != target_family:
            cur.execute('UPDATE families_familymember SET family_id=? WHERE family_id=?', (target_family, source_family))
            print(f'Updated family_id {source_family} -> {target_family} for all members in the source branch')

        for table, column in fk_columns:
            cur.execute(f'UPDATE "{table}" SET "{column}"=? WHERE "{column}"=?', (target_id, source_id))

        # Collapse duplicate parent links created by the re-pointing.
        cur.execute(
            'DELETE FROM families_familymember_parents WHERE id NOT IN (SELECT MIN(id) FROM families_familymember_parents GROUP BY from_familymember_id, to_familymember_id)'
        )

        # Copy any missing values from the source member onto the target member.
        cur.execute('SELECT * FROM families_familymember WHERE id=?', (target_id,))
        target_row = cur.fetchone()
        target_cols = [desc[0] for desc in cur.description]
        target_map = dict(zip(target_cols, target_row))

        updates = []
        values = []
        for key, source_value in source.items():
            if key == 'id':
                continue
            target_value = target_map.get(key)
            if is_blank(target_value) and not is_blank(source_value):
                updates.append(f'"{key}"=?')
                values.append(source_value)

        if updates:
            values.append(target_id)
            cur.execute(f'UPDATE families_familymember SET {", ".join(updates)} WHERE id=?', values)

        cur.execute('DELETE FROM families_familymember WHERE id=?', (source_id,))

    conn.close()
    print('Merge complete.')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: merge_familymember.py SOURCE_ID TARGET_ID')
    merge_member(int(sys.argv[1]), int(sys.argv[2]))
