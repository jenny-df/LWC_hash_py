import sys, math
from photon import *

DIGEST_LEN_BYTES = 32
R_BYTES = 4

def photon_beetle_hash_32(msg):
    msg = bytes(msg, 'utf-8')

    if len(msg) == 0:
        state = bytes(31) + bytes([1])
    elif len(msg) <= 16:
        c0 = bytes([1]) if len(msg) < 16 else bytes([2])
        state =  ozs(msg, 16) + bytes(15) + c0
    else:
        msg1, msg_rest = msg[:16], msg[16:]
        c0 = bytes([1])
        IV = msg1 + bytes(16)

        state = hash_32(IV, msg_rest, c0)

    return tag_256(state) # digest

def hash_32(IV, D, c0):
    d = math.ceil(len(D) / R_BYTES)

    for i in range(0, d * R_BYTES, R_BYTES):
        photon_hash = photon256(IV)
        Y = photon_hash[:R_BYTES]
        D_i = ozs(D[i: i + R_BYTES], R_BYTES)
        W = bytes([D_i_val ^ Y_val for D_i_val, Y_val in zip(D_i, Y)])
        IV = W + photon_hash[R_BYTES:]
    
    IV = bytes(IV[:-1] + [IV[-1] ^ c0])
    return IV

def tag_256(state):
    tag = b''
    for i in range(2):
        state = photon256(state)
        tag += state[:16]
    return tag

def ozs_padding(msg, desired_len):
    if len(msg) != desired_len: # TODO: not sure if correct since 1 might be a few bits later than where it should be if we had dealt with bits
        msg += b'\x80' + b'\x00' * (desired_len - len(msg) - 1)

    return msg


if __name__ == "__main__":
    pass