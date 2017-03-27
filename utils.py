import binascii
import json


BASE_DIFF_TARGET = 0x00000000ffff0000000000000000000000000000000000000000000000000000
MAX_DIFF_TARGET = 0xffffffffffff0000000000000000000000000000000000000000000000000000
pools = json.load(file('pools.json'))


bin_to_hex = binascii.hexlify


def find_pool(cb, wallets):
    for cbid, pool in pools['coinbase_tags'].items():
        if binascii.hexlify(cbid.encode('utf-8')) in (cb):
            return pool['name'].replace('\'', '')
    for wallet in wallets:
        for addr, pool in pools['payout_addresses'].items():
            if addr == wallet:
                return pool['name'].replace('\'', '')


def nbits_to_target(c):
    shift = (c >> 24) & 0xFF
    v = (c & 0xFFFFFFL) << (8 * (shift - 3))
    return v


def bin_be_to_int(val):
    val_hex = bin_to_hex(val)
    return int(val_hex, 16)


def target_to_difficulty(target, make_float=False):
    if make_float:
        return BASE_DIFF_TARGET / float(target)
    else:
        return BASE_DIFF_TARGET / target


def bits_to_target(bits):
    compact = bin_be_to_int(bits)
    return nbits_to_target(compact)


def bits_to_difficulty(bits, make_float=True):
    target = bits_to_target(bits)
    return target_to_difficulty(target, make_float)


def bits_to_difficulty(bits, make_float=True):
    target = bits_to_target(bits)
    return target_to_difficulty(target, make_float)


def _get_cb(server, tx_id):
    tx = server.decoderawtransaction(server.getrawtransaction(tx_id))
    addresses = []
    value = 0
    for out in tx['vout']:
        try:
            address = out['scriptPubKey']['addresses'][0]
        except:
            address = None
        addresses.append(address)
        value += out['value']

    return tx['vin'][0]['coinbase'], value, addresses


def _get_block(server, block_hash):
    block = server.getblock(block_hash)
    return block_hash, block['previousblockhash'], block['time'], block['bits'], block['tx'][0]


def get_block(server, block_hash):
    block_hash, prev_block_hash, time, bits, coinbase_id = _get_block(server, block_hash)
    coinbase, value, address = _get_cb(server, coinbase_id)
    return block_hash, prev_block_hash, time, bits, coinbase, value, address


def get_last_block_hash_from_db(db, table):
    res = list(db.query('SELECT hash FROM %s ORDER BY time DESC LIMIT 1;' % table))
    if res:
        return res[0]['hash']
    return None


def get_first_block_hash_from_db(db, table):
    res = list(db.query('SELECT hash FROM %s ORDER BY time ASC LIMIT 1;' % table))
    if res:
        return res[0]['hash']
    return None


def get_prev_hash(server, block_hash):
    return get_block(server, block_hash)[1]
