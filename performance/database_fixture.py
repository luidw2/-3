"""Versioned schema and private canonical snapshot for the isolated baseline DB."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import pymysql
from dotenv import dotenv_values

PERF = Path(__file__).resolve().parent
ENV = dotenv_values(PERF.parent / '后端flask/.env')
DATABASE = 'perf9_baseline'
SNAPSHOT = PERF / '.local' / 'baseline-snapshot.json'


def connect(database=None):
    return pymysql.connect(host=ENV['DB_HOST'], port=int(ENV['DB_PORT']), user=ENV['DB_USER'],
                           password=ENV['DB_PASSWORD'], database=database, charset='utf8mb4')


def data_state(conn):
    result = {}
    with conn.cursor() as q:
        q.execute('SHOW TABLES')
        tables = sorted(x[0] for x in q.fetchall())
        for table in tables:
            if not re.fullmatch(r'[A-Za-z0-9_]+', table):
                raise ValueError('Unexpected identifier')
            q.execute(f'SELECT * FROM `{table}` ORDER BY 1')
            result[table] = {'columns': [x[0] for x in q.description], 'rows': [list(x) for x in q.fetchall()]}
    # All current columns are text/numeric/date. No binary secret is exported publicly.
    return json.loads(json.dumps(result, default=str))


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['export-schema', 'init', 'snapshot', 'reset', 'check'])
    args = parser.parse_args()
    if args.action == 'export-schema':
        with connect(ENV['DB_NAME']) as conn, conn.cursor() as q:
            q.execute('SHOW TABLES'); tables = [x[0] for x in q.fetchall()]
            statements = []
            for table in sorted(tables):
                q.execute(f'SHOW CREATE TABLE `{table}`')
                sql = re.sub(r' AUTO_INCREMENT=\d+', '', q.fetchone()[1])
                statements.append(sql.replace('CREATE TABLE ', 'CREATE TABLE IF NOT EXISTS ', 1) + ';')
        (PERF / 'schema.sql').write_text('\n\n'.join(statements) + '\n', encoding='utf-8')
        print('Exported schema only:', len(statements), 'tables')
        return
    if args.action == 'init':
        with connect() as conn, conn.cursor() as q:
            q.execute(f'CREATE DATABASE IF NOT EXISTS `{DATABASE}` CHARACTER SET utf8mb4')
            q.execute(f'USE `{DATABASE}`')
            q.execute('SET FOREIGN_KEY_CHECKS=0')
            try:
                for sql in (PERF / 'schema.sql').read_text(encoding='utf-8').split(';'):
                    if sql.strip(): q.execute(sql)
            finally:
                q.execute('SET FOREIGN_KEY_CHECKS=1')
        print('Isolated schema ready:', DATABASE)
        return
    with connect(DATABASE) as conn:
        if args.action == 'snapshot':
            if SNAPSHOT.exists():
                raise RuntimeError('Snapshot already exists; kept immutable. Use reset to restore it.')
            state = data_state(conn)
            SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
            SNAPSHOT.write_text(json.dumps({'database': DATABASE, 'tables': state,
                                           'sha256': fingerprint(state)}, indent=2), encoding='utf-8')
        elif args.action == 'reset':
            saved = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
            assert saved['database'] == DATABASE
            assert saved['sha256'] == fingerprint(saved['tables'])
            # Only the hard-coded, dedicated DB is reset; never accepts the business DB.
            with conn.cursor() as q:
                q.execute('SELECT DATABASE()'); assert q.fetchone()[0] == DATABASE
                q.execute('SET FOREIGN_KEY_CHECKS=0')
                try:
                    for table, spec in saved['tables'].items():
                        q.execute(f'DELETE FROM `{table}`')
                        if spec['rows']:
                            columns = ','.join('`' + x + '`' for x in spec['columns'])
                            marks = ','.join(['%s'] * len(spec['columns']))
                            q.executemany(f'INSERT INTO `{table}` ({columns}) VALUES ({marks})', spec['rows'])
                    conn.commit()
                    for table in saved['tables']:
                        q.execute(f'ALTER TABLE `{table}` AUTO_INCREMENT=1')
                except Exception:
                    conn.rollback()
                    raise
                finally:
                    q.execute('SET FOREIGN_KEY_CHECKS=1')
            assert fingerprint(data_state(conn)) == saved['sha256'], 'Restore validation failed'
        state = data_state(conn)
        output = {'database': DATABASE, 'sha256': fingerprint(state),
                  'counts': {table: len(spec['rows']) for table, spec in state.items()}}
        if SNAPSHOT.exists():
            output['matches_snapshot'] = output['sha256'] == json.loads(SNAPSHOT.read_text())['sha256']
        print(json.dumps(output, ensure_ascii=False))


if __name__ == '__main__':
    main()
