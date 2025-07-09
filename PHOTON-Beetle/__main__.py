from photon import *
from utils import *

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


if __name__ == "__main__":
    pass