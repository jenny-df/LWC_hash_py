HASH_RATE = 16

ROUNDS = 12

NUM_COLS = 4
NUM_ROWS = 32

LANE_BYTES = 4
PLANE_BYTES = 16
NUM_PLANES = 3
STATE_BYTES = PLANE_BYTES * NUM_PLANES

ROUND_CONSTS = [
    0x00000058, 0x00000038, 0x000003C0, 0x000000D0,
    0x00000120, 0x00000014, 0x00000060, 0x0000002C,
    0x00000380, 0x000000F0, 0x000001A0, 0x00000012]

BYTE_MASK = 0xff

ABSORB_COLOR = 3

def absorb(state, msg):
    '''
    Absorbs an input message into the state in blocks. This function implements the "absorbing"
    phase of a sponge construction. It processes the input message in fixed-size blocks (defined
    by HASH_RATE) and then cycling the state in the process of absorbing the message. It mutates
    the state.

    Args:
        - state (bytearray): the internal state / memory of the Xoodyak hash function (48 bytes).
        - msg (bytes): the message that's being hashed (unspecified length) in little endian byte
                       order.

    Returns:
        None
    '''

    x_i = msg[:HASH_RATE]
    down_hash(state, x_i, ABSORB_COLOR)

    for i in range(HASH_RATE, len(msg), HASH_RATE):
        up_hash(state)
        x_i = msg[i:i+HASH_RATE]
        down_hash(state, x_i, 0)


def up_hash(state):
    '''
    In the Xoodyak hash cycle, this is the "Up" phase, where the state is transformed and mixed
    using the Xoodoo permutation. It mutates the state.

    Args:
        - state (bytearray): the internal state / memory of the Xoodyak hash function (48 bytes).

    Returns:
        None
    '''

    xoodoo_12(state)

def down_hash(state, msg, color_down):
    '''
    The "Down" phase of the Xoodyak hash cycle. It takes a single block of the input message,
    applies the required 10* padding to it, adds a domain separation constant (color), and XORs the
    result into the first part of the state. It mutates the state.

    Args:
        - state (bytearray): the internal state / memory of the Xoodyak hash function (48 bytes).
        - msg (bytes): the message that's being hashed (unspecified length) in little endian byte
                       order.
        - color_down (int): A domain separation constant used to differentiate between different
                            operational phases.

    Returns:
        None
    '''

    msg_last_len = len(msg) & 3
    padding_for_msg_rest = msg_last_len * 8

    if msg_last_len or not msg:
        msg_zero_padded = msg[:-msg_last_len] + bytes(4-msg_last_len) + msg[-msg_last_len:]
        one_zero_pad = (1 << padding_for_msg_rest).to_bytes(4, byteorder="big")
        msg_last_padding = bytes(len(msg_zero_padded) - 4) + one_zero_pad
        msg = bytes([a ^ b for a, b in zip(msg_zero_padded, msg_last_padding)])
    else:
        msg_last_padding = (1 << padding_for_msg_rest).to_bytes(4, byteorder="big")
        msg += msg_last_padding

    color = ((color_down & 0x01) << 24).to_bytes(4, byteorder="big")

    zero_padding = STATE_BYTES - len(msg) - len(color)

    for i, v in enumerate(msg + bytes(zero_padding) + color):
        state[i] ^= v


def squeeze(state, digest_length):
    '''
    Extracts (squeezes) the final hash digest from the Xoodyak state.

    This function implements the squeezing phase of a sponge construction. After all input has
    been absorbed, this function is called to extract the resulting hash of a specified length. 
    It works by cycling the state in the process of extracting the digest. It mutates the state.

    Args:
        - state (bytearray): the internal state / memory of the Xoodyak hash function (48 bytes).
        - digest_length (int): The desired length (number of bytes) of the final hash digest.

    Returns:
        The final hash digest (bytes) of the specified length in big-endian order.
    '''

    up_hash(state)
    digest = state[:min(digest_length, HASH_RATE)]

    while len(digest) < digest_length:
        down_hash(state, b"", 0)
        up_hash(state)
        digest += state[:min(digest_length - len(digest), HASH_RATE)]

    return flip_endian_byteorder(digest)


def xoodoo_12(state):
    '''
    Performs the Xoodoo permutation with 12 rounds on a 48-byte state. Xoodoo is a cryptographic
    permutation used as the core of the Xoodyak sponge construction. It iteratively applies a
    series of non-linear mixing layers to the state to provide confusion and diffusion. It
    mutates the state.

    Args:
        - state (bytearray): the internal state / memory of the Xoodyak hash function (48 bytes).

    Returns:
        None
    '''

    for i in range(ROUNDS):
        # theta
        p = bytes([
            a0 ^ a1 ^ a2 for a0, a1, a2 in zip(
                state[:PLANE_BYTES],
                state[PLANE_BYTES: 2 * PLANE_BYTES],
                state[2 * PLANE_BYTES:]
            )])
        for j, (e_1, e_2) in enumerate(zip(two_dim_rotation(p, 1, 5), two_dim_rotation(p, 1, 14))):
            xor = e_1 ^ e_2
            state[j] ^= xor
            state[j + PLANE_BYTES] ^= xor
            state[j + 2 * PLANE_BYTES] ^= xor

        # p west
        state[PLANE_BYTES:2*PLANE_BYTES] = two_dim_rotation(state[PLANE_BYTES:2*PLANE_BYTES], 1, 0)
        state[2*PLANE_BYTES:] = two_dim_rotation(state[2*PLANE_BYTES:], 0, 11)

        # i
        a0_vals = ROUND_CONSTS[i].to_bytes(LANE_BYTES, byteorder="big")
        for j, a0 in enumerate(a0_vals):
            state[j] ^= a0

        # chi
        for j in range(STATE_BYTES):
            state[j] ^= ~state[(PLANE_BYTES+j) % STATE_BYTES] & state[(2*PLANE_BYTES+j) % STATE_BYTES]

        # p east
        state[PLANE_BYTES:2*PLANE_BYTES] = two_dim_rotation(state[PLANE_BYTES:2*PLANE_BYTES], 0, 1)
        state[2*PLANE_BYTES:] = two_dim_rotation(state[2*PLANE_BYTES:], 2, 8)


def two_dim_rotation(plane, x_shift, z_shift):
    """
    Shifts the given plane (a byte sequence representing a 2D space on the x and z planes) by a
    given x and z shift values. Both shifts are assumed to be positive values.

    Args:
        - plane (bytes/bytearray): The plane being shifted (16 bytes -> 32 bits in the z-axis by 4
                                   bits in the x-axis).
        - x_shift (int): The number of bits being rotated in the x-axis.
        - z_shift (int): The number of bits being rotated in the z-axis.

    Returns:
        The new bytearray formed by shifting the given plane by the given shift amounts.
    """

    output = bytearray()
    for r in range(-x_shift, NUM_COLS-x_shift):
        r_i = (r%NUM_COLS) * LANE_BYTES
        lane = plane[r_i:r_i+LANE_BYTES]
        lane_val = int.from_bytes(lane, byteorder="big")

        shifted_lane = rotate_left(lane_val, z_shift, NUM_ROWS)
        output += shifted_lane.to_bytes(LANE_BYTES, byteorder='big')
    return output


def rotate_left(value, shift, n):
    """
    Shifts the given value by the given amount of shift to the left and wraps the values removed
    from the MSB side onto the LSB side, such that all original bits are preserved but their
    position is circularly shifted to the left.

    Args:
        - value (int): Value being circularly shifted.
        - shift (int): The number of bits being circularly shifted to the left.
        - n (int): The number of bits in the value given.

    Returns:
        The new integer formed by shifting the given value by the given shift amount.
    """

    mask = (1 << n) - 1
    upper_bits = (value << shift) & mask
    lower_bits = value >> (n-shift)
    return upper_bits | lower_bits


def flip_endian_byteorder(data, chunk_size = 4):
    """
    Converts a big-endian byte sequence to a little-endian byte sequence or vice versa
    by reversing the order of bytes within specified chunks.

    Args:
        - data (bytes/bytearray): The input being flipped.
        - chunk_size (int): The size of each data unit (e.g., 2 for short, 4 for int, 8 for long).

    Returns:
        A new bytes object with the byte order reversed within each chunk.
    """

    flipped_data = bytearray()
    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        flipped_data.extend(chunk[::-1])
    return bytes(flipped_data)
