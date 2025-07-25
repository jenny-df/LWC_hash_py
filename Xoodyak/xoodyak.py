from utils import *

def xoodyak_hash_mode(msg, digest_len=32):
    msg = big_to_little_endian_bytes(msg)
    state = bytearray(STATE_BYTES)
    absorb(state, msg, 0x03)
    digest = squeeze(state, digest_len)
    return bytes(digest)

if __name__ == "__main__":
    pass