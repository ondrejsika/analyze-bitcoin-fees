# from __future__ import unicode_literals

import binascii
import json

pools = json.load(file('pools.json'))

# print pools['coinbase_tags'].keys()

def find_pool(cb, wallet):
    for cbid, pool in pools['coinbase_tags'].items():
        # print binascii.unhexlify(cb)
        if binascii.hexlify(cbid.encode('utf-8')) in (cb):
            return pool['name']
    for addr, pool in pools['payout_addresses'].items():
        # print binascii.unhexlify(cb)
        if addr == wallet:
            return pool['name']

def nbits_to_target(c):
    shift = (c >> 24) & 0xFF
    v = (c & 0xFFFFFFL) << (8 * (shift - 3))
    return v

bin_to_hex = binascii.hexlify

def bin_be_to_int(val):
    val_hex = bin_to_hex(val)
    return int(val_hex, 16)

BASE_DIFF_TARGET = 0x00000000ffff0000000000000000000000000000000000000000000000000000
MAX_DIFF_TARGET = 0xffffffffffff0000000000000000000000000000000000000000000000000000

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

# print """
#  create table fee_data (id int primary key AUTO_INCREMENT, hash varchar(80), time int, difficulty int, value float, fees float, pool VARCHAR(30))
# """

with file('blocks', 'r') as f:
    for line in f.readlines():
        line = line.replace('\n', '')
        if not line:
            continue

        block_hash, time, bits, coinbase, value, address = line.split()
        pool = find_pool(coinbase, address)
        value = float(value)
        time = float(time)
        block_value = 25 if time < 1468082773 else 12.5
        fees = value - block_value
        print """insert into fee_data(hash, time, difficulty, value, fees, pool) values ('%s', %s, %d, %s, %s, '%s');""" % (block_hash, time, bits_to_difficulty(binascii.unhexlify(bits)), block_value, fees, str(pool).replace('\'', ''))

