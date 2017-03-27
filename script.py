#!/usr/bin/env python

import time
import binascii
import argparse

import jsonrpc_requests
import dataset

from utils import get_block, find_pool, bits_to_difficulty, get_first_block_hash_from_db, get_last_block_hash_from_db,\
    get_prev_hash


root_parser = argparse.ArgumentParser()
root_parser.add_argument('bitcoind_connection', help='Eg.: http://btcrpc:btc@127.0.0.1:8332')
root_parser.add_argument('database_connection', help='Eg.: postgres://postgres:pg@127.0.0.1:5432/root')
root_parser.add_argument('--table', default='fees', help='Destination table, eg.: fees')
root_parser.add_argument('--end-time', type=int, default=time.mktime((2015, 1, 1, 0, 0, 0, 0, 0, 0)),
                         help='Blocktime to stop script, unix timestamp')
root_parser.add_argument('--recreate', action='store_true', help='Truncate data before start')
root_parser.add_argument('--continue', action='store_true', dest='cont', help='Continue processing until end time.')

args = root_parser.parse_args()

bitcoind = jsonrpc_requests.Server(args.bitcoind_connection)
db = dataset.connect(args.database_connection)
table = db[args.table]


if args.recreate:
    db.query('TRUNCATE TABLE %s;' % args.table)


stop_hash = get_last_block_hash_from_db(db, args.table)

prev_block_hash = bitcoind.getbestblockhash()

while True:
    block_hash, prev_block_hash, block_time, bits, coinbase, value, addresses = get_block(bitcoind, prev_block_hash)
    if stop_hash and stop_hash == block_hash:
        if args.cont:
            prev_block_hash = get_prev_hash(bitcoind, get_first_block_hash_from_db(db, args.table))
            continue
        else:
            break

    if block_time <= args.end_time:
        break

    pool = find_pool(coinbase, addresses)
    block_value = 25 if block_time < 1468082773 else 12.5
    fees = value - block_value
    block = {
        'hash': block_hash,
        'time': block_time,
        'difficulty': bits_to_difficulty(binascii.unhexlify(bits)),
        'value': block_value,
        'fees': fees,
        'pool': pool,
    }
    table.insert(block)
