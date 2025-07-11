from photon import *

R_BYTES = 4

def hash_32(IV, D, c0):
    '''
    Updates the initialization vector with the information in the data (D).

    ARGS:
        - IV (byte string): initialization vector of the cryptographic algorithm (32 bytes).
        - D (byte string): extra information/data from the message to be hashed that didn't fit into the IV (unspecified length).
        - c0 (byte string): a flag that indicates information about the length of the inputted message (1 byte).
    RETURNS:
        - a 32 byte (256 bit) updated internal state (byte string).
    '''

    d = max(2, ((len(D) + R_BYTES -1) // R_BYTES) + 1) # always a whole number since D is in utf-8

    for i in range(0, (d-1) * R_BYTES, R_BYTES):
        IV = shuffle(IV)
        Y, IV = photon256(IV)
        D_i = ozs_padding(D[i: i + R_BYTES], R_BYTES)
        W = bytes([D_i_val ^ Y_val for D_i_val, Y_val in zip(D_i, Y)])
        IV = W + Y[R_BYTES:]

    internal_state = IV[:-1] + bytes([IV[-1] ^ c0])
    return internal_state


def tag_256(internal_state):
    '''
    Generates a tag/hash digest for the hash function by squeezing the internal state.

    ARGS:
        - internal_state (byte string): memory of the cryptographic algorithm (32 bytes).
    RETURNS:
        - a 32 byte (256 bit) tag/hash digest (byte string)
    '''

    tag = b''
    for i in range(2):
        full_tag, internal_state = photon256(internal_state)
        tag += full_tag[:16]
    return tag


def ozs_padding(msg, desired_len):
    '''
    Pads the msg with a one bit and a bunch of zeros till it's the desired length. It adds the padding after the LSBs.

    ARGS:
        - msg (byte string): the message that's being hashed (unspecified length).
        - desired_len (int): the desired output length (desired number of bytes) of the message.
    RETURNS:
        - the msg (byte string) padded to the desired length if it was originally shorter or the original msg if it was already the desired length
    RAISES:
        - ValueError if the length of the input message is bigger than the desired length.
    '''
    if len(msg) < desired_len:
        msg += b'\x01' + b'\x00' * (desired_len - len(msg) - 1)
    elif len(msg) > desired_len:
        raise ValueError("The given message is longer than the desired length.")
    return msg