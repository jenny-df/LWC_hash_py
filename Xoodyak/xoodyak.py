from utils import *


def xoodyak_hash_mode(msg, digest_len=32):
    msg = big_to_little_endian_bytes(msg)
    state = bytearray(STATE_BYTES)
    print_state(state)
    absorb(state, msg, 0x03)
    print_state(state)
    digest = squeeze(state, digest_len)
    print_state(state)
    output = int.from_bytes(digest, "big")
    print(f"{hex(output)=}")

    return bytes(digest)

if __name__ == "__main__":
    pass