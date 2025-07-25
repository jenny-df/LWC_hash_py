from utils import *

def xoodyak_hash_mode(msg, digest_len=32):
    '''
    Hashes the inputted message using the Xoodyak algorithm in `Hash` mode and outputs a digest with
    the required digest_len (defaults to 32 bytes).

    Args:
        - msg (bytes): the message that's being hashed (unspecified length). Assumed to be in big 
                       endian byte order.
        - digest_len (int): The number of bytes in the output (digest).

    Returns:
        - The hash/digest (bytes) of the inputted message with the required/given length.
    '''

    msg = flip_endian_byteorder(msg)
    state = bytearray(STATE_BYTES)
    absorb(state, msg)
    digest = squeeze(state, digest_len)
    return bytes(digest)

if __name__ == "__main__":
    pass
