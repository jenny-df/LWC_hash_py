from photon import *
from utils import *

__all__ = ['photon_beetle_hash_32']

def photon_beetle_hash_32(msg):
    '''
    Hashes the inputted message using the PHOTON-Beetle-HASH32 algorithm.

    ARGS:
        - msg (bytes): the message that's being hashed (unspecified length).
    RETURNS:
        - the hash digest (32 bytes/256 bits) of the message created using the PHOTON-Beetle-HASH32 algorithm.
    '''

    # msg = bytes(msg, 'utf-8')

    if len(msg) == 0:
        internal_state = bytes(31) + bytes([0x20]) # TODO: figure out why it's 1 << 5 and not just 1
    elif len(msg) <= 16:
        c0 = bytes([0x20]) if len(msg) < 16 else bytes([0x40])
        internal_state =  ozs_padding(msg, 16) + bytes(15) + c0
    else:
        msg1, msg_rest = msg[:16], msg[16:]
        c0 = 0x20 if len(msg_rest) % 4 == 0 else 0x40
        IV = msg1 + bytes(16)
        internal_state = hash_32(IV, msg_rest, c0)

    internal_state = shuffle(internal_state)
    return tag_256(internal_state) # digest


if __name__ == "__main__":
    pass