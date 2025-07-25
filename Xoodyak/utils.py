HASH_RATE = 16

UP = 0
DOWN = 1

ROUNDS = 12

NUM_COLS = 4 # half a byte
NUM_ROWS = 32

LANE_BYTES = 4
PLANE_BYTES = 16
NUM_PLANES = 3
STATE_BYTES = PLANE_BYTES * NUM_PLANES

ROUND_CONSTS = [0x00000058, 0x00000038, 0x000003C0, 0x000000D0, 0x00000120, 0x00000014, 0x00000060, 0x0000002C, 0x00000380, 0x000000F0, 0x000001A0, 0x00000012]

BYTE_MASK = 0xff

def absorb(state, msg, color_down):

    x_i = msg[:HASH_RATE]
    down_hash(state, x_i, color_down)

    for i in range(HASH_RATE, len(msg), HASH_RATE):
        x_i = msg[i:i+HASH_RATE]
        up_hash(state)
        down_hash(state, x_i, 0)


def up_hash(state):
    xoodoo_12(state)


def down_hash(state, msg, color_down):
    msg_last_len = len(msg) & 3
    padding_for_msg_rest = msg_last_len * 8

    if msg_last_len or not msg:
        msg_zero_padded = msg[:-msg_last_len] + bytes(4-msg_last_len) + msg[-msg_last_len:]
        msg_last_padding = bytes(len(msg_zero_padded) - 4) + (1 << padding_for_msg_rest).to_bytes(4, byteorder="big")
        msg = bytes([a ^ b for a, b in zip(msg_zero_padded, msg_last_padding)])
    else:
        msg_last_padding = (1 << padding_for_msg_rest).to_bytes(4, byteorder="big")
        msg += msg_last_padding
    b = ((color_down & 0x01) << 24).to_bytes(4, byteorder="big")
    zero_padding = STATE_BYTES - len(msg) - len(b)

    for i, v in enumerate(msg + bytes(zero_padding) + b):
        state[i] ^= v


def squeeze(state, length):
    up_hash(state)
    digest = state[:min(length, HASH_RATE)]
    while len(digest) < length:
        down_hash(state, b"", 0) # TODO: check if this will be the correct length
        up_hash(state)
        digest += state[:min(length - len(digest), HASH_RATE)]
    return big_to_little_endian_bytes(digest)


def xoodoo_12(state):
    for i in range(ROUNDS):
        # theta
        p = bytes([a0 ^ a1 ^ a2 for a0, a1, a2 in zip(state[:PLANE_BYTES], state[PLANE_BYTES: 2*PLANE_BYTES], state[2*PLANE_BYTES:])])
        shift1, shift2 = two_dim_cyclic_shift(p, 1, 5), two_dim_cyclic_shift(p, 1, 14)
        for j, (e_1, e_2) in enumerate(zip(shift1, shift2)):
            xor = e_1 ^ e_2
            state[j] ^= xor
            state[j + PLANE_BYTES] ^= xor
            state[j + 2 * PLANE_BYTES] ^= xor
        
        # p west and i
        a0_vals = ROUND_CONSTS[i].to_bytes(LANE_BYTES, byteorder="big") + bytes(LANE_BYTES*11)
        shifted_a1 = two_dim_cyclic_shift(state[PLANE_BYTES:2*PLANE_BYTES], 1, 0)
        shifted_a2 = two_dim_cyclic_shift(state[2*PLANE_BYTES:], 0, 11)
        for j, (a0_val, a1_val, a2_val) in enumerate(zip(a0_vals, shifted_a1, shifted_a2)):
            state[j] ^= a0_val
            state[PLANE_BYTES + j] = a1_val
            state[2 * PLANE_BYTES + j] = a2_val

        # chi
        bit_comp = bitwise_complement(state[PLANE_BYTES:2*PLANE_BYTES] + state[2*PLANE_BYTES:] + state[:PLANE_BYTES])
        and_val =  state[2*PLANE_BYTES:]+ state[:PLANE_BYTES] + state[PLANE_BYTES:2*PLANE_BYTES] 
        Bs = bytes([a & b for a, b in zip(bit_comp, and_val)])

        for j, b_val in enumerate(Bs):
            state[j] ^= b_val

        # p east
        shifted_a1 = two_dim_cyclic_shift(state[PLANE_BYTES:2*PLANE_BYTES], 0, 1)
        shifted_a2 = two_dim_cyclic_shift(state[2*PLANE_BYTES:], 2, 8)
        for j, (a1_val, a2_val) in enumerate(zip(shifted_a1, shifted_a2)):
            state[PLANE_BYTES + j] = a1_val
            state[2 * PLANE_BYTES + j] = a2_val


def two_dim_cyclic_shift(plane, x_shift, z_shift):
    output = bytearray()
    for r in range(-x_shift, NUM_COLS-x_shift):
        r_i = (r%NUM_COLS) * LANE_BYTES
        lane = plane[r_i:r_i+LANE_BYTES]
        lane_val = int.from_bytes(lane, byteorder="big")
        shifted_lane = circular_rotation(lane_val, z_shift, NUM_ROWS)
        output += shifted_lane.to_bytes(LANE_BYTES, byteorder='big')
        
    return output


def circular_rotation(value, shift, n):
    """
    Shifts the given value by the given amount of shift and wraps the values removed from the LSB side onto 
    the MSB side, such that all original bits are preserved but their position is circularly shifted.

    Args:
        - value (int): value being circularly shifted.
        - shift (int): the number of bits being circularly shifted to the right.

    Returns:
        The new integer formed by shifting the given value by the given shift amount.
    """

    mask = (1 << n) - 1
    upper_bits = (value << shift) & mask
    lower_bits = value >> (n-shift)
    return upper_bits | lower_bits


def bitwise_complement(plane):
    return bytes([val ^ BYTE_MASK for val in plane])


def big_to_little_endian_bytes(data: bytes, chunk_size: int = 4) -> bytes:
    """
    Converts a big-endian byte sequence to a little-endian byte sequence
    by reversing the order of bytes within specified chunks.

    Args:
        data: The input bytes, assumed to be big-endian.
        chunk_size: The size of each data unit (e.g., 2 for short, 4 for int, 8 for long).

    Returns:
        A new bytes object with the byte order reversed within each chunk.
    """

    little_endian_data = bytearray()
    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        little_endian_data.extend(chunk[::-1])
    return bytes(little_endian_data)
