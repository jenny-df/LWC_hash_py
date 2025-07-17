import math

INTERNAL_STATE_LEN_BYTE = 40
HASH_RATE = 8
CAPACITY = INTERNAL_STATE_LEN_BYTE - HASH_RATE

A_ROUNDS = 12

PARAMETERS = {
    "ascon_hash": {"h": 32, "b": 12, "S": 0x9b1e5494e934d6814bc3a01e333751d2ae65396c6b34b81a3c7fd4a4d56a4db31a5c464906c5976d}, 
    "ascon_hasha": {"h": 32,"b": 8, "S": 0xe2ffb4d17ffcadc5dd364b655fa88cebdcaabe85a70319d2d98f049404be3214ca8c9d516e8a2221}, 
    "ascon_xof": {"h": 0, "b": 12, "S": 0xda82ce768d9447ebcc7ce6c75f1ef969e7508fd7800856310ee0ea53416b58cce0547524db6f0bde}, 
    "ascon_xofa": {"h": 0, "b": 8, "S": 0xf3040e5017d92943c474f6e3ae01892ebf5cb3ca954805e0d9c28702ccf962ef5923fa01f4b0e72f}, 
}

ROUND_CONSTS = [0xf0, 0xe1, 0xd2, 0xc3, 0xb4, 0xa5, 0x96, 0x87, 0x78, 0x69, 0x5a, 0x4b]
SBOX = [0x4, 0xb, 0x1f, 0x14, 
        0x1a, 0x15, 0x9, 0x2,
        0x1b, 0x5, 0x8, 0x12, 
        0x1d, 0x3, 0x6, 0x1c, 
        0x1e, 0x13, 0x7, 0xe, 
        0x0, 0xd, 0x11, 0x18, 
        0x10, 0xc, 0x1, 0x19, 
        0x16, 0xa, 0xf, 0x17]

X_I_SIZE = 8 # bytes
X_I_SIZE_BITS = 64
X_I_MASK = (1 << X_I_SIZE_BITS) - 1

ONE_BIT_MASK = 0x1
FIVE_BIT_MASK = 0x1f

X_I_REF = {
    "x0": (X_I_SIZE_BITS*4, 19, 28), # start_i, shift1, shift2
    "x1": (X_I_SIZE_BITS*3, 61, 39),
    "x2": (X_I_SIZE_BITS*2, 1, 6),
    "x3": (X_I_SIZE_BITS, 10, 17),
    "x4": (0, 7, 41),
}

def ascon(msg, hash_type, digest_len = 32):
    """
    Hashes the inputted message using a specified ASCON hashing algorithm and outputs the required digest_len if it's compatible
    with the hashing algorithm specified.

    Args:
        - msg (bytes): the message that's being hashed (unspecified length).
        - hash_type (string): The type of ASCON hash function to use.
        - digest_len (int): The number of bytes in the output.
    """

    # INITIALIZE
    params = PARAMETERS[hash_type]
    internal_state = {key: (params['S'] >> offset) & X_I_MASK for key, (offset, _, _) in X_I_REF.items()}

    if params['h'] != 0:
        digest_len = digest_len if 0 <= digest_len <= params['h'] else params['h'] # TODO: make sure the min bound is correct

    # ABSORB
    num_full_rounds = len(msg) // HASH_RATE
    num_full_msg_bytes = num_full_rounds * HASH_RATE

    for i in range (0, num_full_msg_bytes, HASH_RATE):
        msg_i = msg[i:i + HASH_RATE]
        byte_x0 = internal_state["x0"].to_bytes(X_I_SIZE, byteorder='big')
        internal_state["x0"] = int.from_bytes(bytes([m ^ x0 for m, x0 in zip(msg_i[::-1], byte_x0)]), byteorder='big')
        permutate(internal_state, params['b'])

    len_msg_extra = len(msg) % HASH_RATE
    msg_last = msg[-len_msg_extra:] + b'\x00' * (HASH_RATE - len_msg_extra)
    padding = (1 << (8 * len_msg_extra)).to_bytes(X_I_SIZE, byteorder='big')

    byte_x0 = internal_state["x0"].to_bytes(X_I_SIZE, byteorder='big')
    internal_state["x0"] = int.from_bytes(bytes([m ^ x0 ^ p for m, x0, p in zip(msg_last[::-1], byte_x0, padding)]), byteorder='big')

    # SQUEEZE
    permutate(internal_state, A_ROUNDS)

    digest = b''
    squeeze_rounds = math.ceil(digest_len/HASH_RATE)
    for i in range(squeeze_rounds):
        digest += internal_state["x0"].to_bytes(X_I_SIZE, byteorder='little')
        if i == squeeze_rounds - 1:
            break
        permutate(internal_state, params['b'])
    return digest[:digest_len]


def permutate(internal_state, rounds):
    """
    Applies the Ascon-p algorithm on the internal state dictionary by mutating it a given number of rounds.

    Args:
        - internal_state (dict): memory of the cryptographic algorithm (40 bytes) divided into 8 byte integers.
        - rounds (int): The number of times to apply the Ascon-p steps.
    """

    offset = 0 if rounds == 12 else 4

    for i in range(rounds):
        # add constant
        internal_state["x2"] ^= ROUND_CONSTS[i + offset]
       
        # substitute
        tmp_state = {x_i:0 for x_i in internal_state}
        for col in range(64):
            old_five_bits = get_5_bits_from_int(internal_state, col)
            new_five_bits = SBOX[old_five_bits]
            for i, x_i in enumerate(internal_state):
                new_bit = (new_five_bits >> (4-i)) & ONE_BIT_MASK
                tmp_state[x_i] |= (new_bit << col)

        # diffusion
        for x_i, x_i_val in tmp_state.items() :
            _, shift1, shift2 = X_I_REF[x_i]
            internal_state[x_i] = x_i_val ^ circular_rotation(x_i_val, shift1) ^ circular_rotation(x_i_val, shift2)


def circular_rotation(value, shift):
    """
    Shifts the given value by the given amount of shift and wraps the values removed from the LSB side onto 
    the MSB side, such that all original bits are preserved but their position is circularly shifted.

    Args:
        - value (int): value being circularly shifted.
        - shift (int): the number of bits being circularly shifted to the right.

    Returns:
        The new integer formed by shifting the given value by the given shift amount.
    """

    lower_bits = value >> shift
    mask = (1 << shift) - 1
    upper_bits = (value & mask) << (64-shift)
    return upper_bits | lower_bits


def get_5_bits_from_int(internal_state, bit_offset):
    """
    Generates a 5 bit integer by extracting and concatinating one bit at a given offset from 
    each of the 5 integers that make up the source state.

    Args:
        - internal_state (dict): memory of the cryptographic algorithm (40 bytes) divided into 8 byte integers.
        - bit_offset (int): The position/offset of the desired bits (0-indexed from the right/LSB) in each of 
        the 5 integers that make up the state.

    Returns:
        An 5 bit integer created by concatinating the extracted bits.
    """

    extracted_bits = 0
    for i, x_i in enumerate(internal_state):
        source_bit = (internal_state[x_i] >> bit_offset) & ONE_BIT_MASK
        source_bit_dest_i = 4-i
        extracted_bits |= source_bit << source_bit_dest_i
    return extracted_bits & FIVE_BIT_MASK
