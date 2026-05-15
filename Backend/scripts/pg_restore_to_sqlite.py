#!/usr/bin/env python3
import re
import sqlite3
import sys
from pathlib import Path


def map_type(pg_type_raw: str) -> str:
    t = pg_type_raw.lower()
    if 'character varying' in t or 'varchar' in t or 'text' in t or 'character' in t:
        return 'TEXT'
    if 'timestamp' in t or 'date' in t or 'time' in t:
        return 'TEXT'
    if 'boolean' in t:
        return 'INTEGER'
    if 'bigint' in t or 'integer' in t or 'int' in t or 'smallint' in t:
        return 'INTEGER'
    if 'numeric' in t or 'decimal' in t or 'double precision' in t or 'real' in t:
        return 'REAL'
    if 'bytea' in t:
        return 'BLOB'
    # fallback
    return 'TEXT'


def unescape_copy_field(s: str):
    if s == '\\N':
        return None
    # PostgreSQL COPY escapes: backslash escapes
    s = s.replace('\\\\', '\\')
    s = s.replace('\\t', '\t')
    s = s.replace('\\n', '\n')
    s = s.replace('\\r', '\r')
    s = s.replace("\\'", "'")
    s = s.replace('\\"', '"')
    return s


def main(dump_path: str, sqlite_path: str):
    dump = Path(dump_path)
    if not dump.exists():
        print('Dump file not found:', dump)
        sys.exit(1)

    out = Path(sqlite_path)
    if out.exists():
        print('Overwriting', out)
        out.unlink()

    conn = sqlite3.connect(str(out))
    cur = conn.cursor()

    with dump.open('r', encoding='utf-8', errors='replace') as f:
        in_create = False
        create_lines = []
        in_copy = False
        copy_table = None
        copy_cols = None
        insert_stmt = None
        buffer_rows = []

        for line in f:
            line = line.rstrip('\n')
            if not in_create and line.startswith('CREATE TABLE'):
                in_create = True
                create_lines = [line]
                continue
            if in_create:
                create_lines.append(line)
                if line.strip().endswith(');'):
                    # process create
                    create_sql = '\n'.join(create_lines)
                    m = re.search(r'CREATE TABLE\s+public\.([\w_]+)\s*\((.*)\);', create_sql, re.S)
                    if m:
                        table = m.group(1)
                        cols_blob = m.group(2)
                        cols = []
                        for colline in cols_blob.split('\n'):
                            colline = colline.strip().rstrip(',')
                            if not colline or colline.upper().startswith('CONSTRAINT') or colline.upper().startswith('PRIMARY KEY'):
                                continue
                            parts = colline.split()
                            colname = parts[0]
                            rest = ' '.join(parts[1:])
                            coltype = map_type(rest)
                            cols.append((colname, coltype))
                        col_defs = ', '.join([f'"{n}" {t}' for n, t in cols])
                        create_stmt = f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs});'
                        cur.execute(create_stmt)
                        conn.commit()
                    in_create = False
                continue

            if not in_copy and line.startswith('COPY '):
                # Example: COPY public.accounts_user (id, password, ...) FROM stdin;
                m = re.match(r'COPY\s+public\.([\w_]+)\s*\(([^)]+)\)\s+FROM stdin;', line)
                if m:
                    copy_table = m.group(1)
                    copy_cols = [c.strip() for c in m.group(2).split(',')]
                    placeholders = ','.join(['?'] * len(copy_cols))
                    insert_stmt = f'INSERT INTO "{copy_table}" ({",".join(["\""+c+"\"" for c in copy_cols])}) VALUES ({placeholders})'
                    in_copy = True
                    buffer_rows = []
                continue

            if in_copy:
                if line == '\\.':
                    # flush rows
                    if buffer_rows:
                        cur.executemany(insert_stmt, buffer_rows)
                        conn.commit()
                    in_copy = False
                    copy_table = None
                    copy_cols = None
                    insert_stmt = None
                    buffer_rows = []
                else:
                    # split by tab
                    fields = line.split('\t')
                    vals = [unescape_copy_field(f) for f in fields]
                    buffer_rows.append(vals)
                continue

    conn.close()
    print('Restored to', out)


if __name__ == '__main__':
    dump = sys.argv[1] if len(sys.argv) > 1 else 'Backend/backup_2026-05-02.sql'
    out = sys.argv[2] if len(sys.argv) > 2 else 'Backend/db_from_vps.sqlite3'
    main(dump, out)
