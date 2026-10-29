"""Create only perf9_ fixtures. Existing non-test records are never changed."""
import argparse
import csv
import json
import secrets
from pathlib import Path

import bcrypt
import pymysql
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / 'performance' / '.local'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--users', type=int, default=20)
    parser.add_argument('--products', type=int, default=100)
    parser.add_argument('--reset-carts', action='store_true', help='Clear only perf9 fixture products from dedicated user carts')
    parser.add_argument('--database', help='Optional isolated database; must start with perf9_')
    args = parser.parse_args()
    if not 1 <= args.users <= 200 or not 1 <= args.products <= 10000:
        parser.error('users: 1..200, products: 1..10000')
    LOCAL.mkdir(parents=True, exist_ok=True)
    credentials = LOCAL / 'credentials.json'
    if credentials.exists():
        password = json.loads(credentials.read_text(encoding='utf-8'))['password']
    else:
        password = secrets.token_urlsafe(24)
        credentials.write_text(json.dumps({'password': password}), encoding='utf-8')
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    env = dotenv_values(ROOT / '后端flask' / '.env')
    if args.database:
        import re
        if not re.fullmatch(r'perf9_[a-zA-Z0-9_]+', args.database):
            parser.error('Isolated database must match perf9_[a-zA-Z0-9_]+')
        env['DB_NAME'] = args.database
    conn = pymysql.connect(host=env['DB_HOST'], port=int(env['DB_PORT']),
                           user=env['DB_USER'], password=env['DB_PASSWORD'],
                           database=env['DB_NAME'], charset='utf8mb4')
    users = []
    product_ids = []
    try:
        with conn.cursor() as cur:
            counts = {}
            for table in ['user', 'seller', 'product', 'cart', 'cart_item', 'order', 'order_item']:
                cur.execute(f'SELECT COUNT(*) FROM `{table}`')
                counts[table] = cur.fetchone()[0]
            snapshot = LOCAL / 'counts-before-first-seed.json'
            if not snapshot.exists():
                snapshot.write_text(json.dumps(counts, indent=2), encoding='utf-8')
            cur.execute('SELECT id FROM seller WHERE username=%s', ('perf9_seller',))
            row = cur.fetchone()
            if row:
                seller_id = row[0]
            else:
                cur.execute('INSERT INTO seller (username,password,is_active,role,failed_attempts) VALUES (%s,%s,1,%s,0)',
                            ('perf9_seller', hashed, 'seller'))
                seller_id = cur.lastrowid
            for i in range(args.products):
                name = f'perf9_product_{i + 1:04d}'
                cur.execute('SELECT id FROM product WHERE seller_id=%s AND name=%s', (seller_id, name))
                row = cur.fetchone()
                if row:
                    product_id = row[0]
                else:
                    cur.execute('INSERT INTO product (name,description,price,status,seller_id) VALUES (%s,%s,%s,%s,%s)',
                                (name, 'Week 9 synthetic performance fixture', 1000 + i, 'active', seller_id))
                    product_id = cur.lastrowid
                product_ids.append(product_id)
            for i in range(args.users):
                name = f'perf9_user_{i + 1:03d}'
                cur.execute('SELECT id FROM `user` WHERE username=%s', (name,))
                row = cur.fetchone()
                if row:
                    user_id = row[0]
                    cur.execute('UPDATE `user` SET password=%s,is_active=1,failed_attempts=0,lock_until=NULL WHERE id=%s',
                                (hashed, user_id))
                else:
                    cur.execute('INSERT INTO `user` (username,password,is_active,role,failed_attempts) VALUES (%s,%s,1,%s,0)',
                                (name, hashed, 'user'))
                    user_id = cur.lastrowid
                cur.execute('SELECT id FROM cart WHERE user_id=%s', (user_id,))
                if not cur.fetchone():
                    cur.execute('INSERT INTO cart (user_id) VALUES (%s)', (user_id,))
                if args.reset_carts:
                    cur.execute('DELETE ci FROM cart_item ci JOIN cart c ON c.id=ci.cart_id '
                                'JOIN product p ON p.id=ci.product_id '
                                'WHERE c.user_id=%s AND p.seller_id=%s', (user_id, seller_id))
                users.append({'username': name, 'password': password, 'product_id': product_ids[i % len(product_ids)]})
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    with (LOCAL / 'users.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['username', 'password', 'product_id'])
        writer.writeheader()
        writer.writerows(users)
    # Only the client private key and server PUBLIC key are needed by JMeter.
    # Never write the backend private key to a JMeter file or result.
    (LOCAL / 'jmeter.properties').write_text(
        'sm2_server_public=' + env['SM2_FLASK_PUBLIC_KEY'] + '\n'
        + 'sm2_client_private=' + env['SM2_VUE_PRIVATE_KEY'] + '\n', encoding='ascii')
    (LOCAL / 'fixtures.json').write_text(json.dumps({'users': args.users,
        'products': args.products, 'seller_id': seller_id, 'product_ids': product_ids}, indent=2), encoding='utf-8')
    print(f'Ready: {args.users} dedicated users, {args.products} products; credentials saved locally, not printed.')


if __name__ == '__main__':
    main()
