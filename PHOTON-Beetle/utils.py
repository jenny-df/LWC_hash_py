import math

R_BYTES = 4

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