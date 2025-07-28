
BLOCK_SIZE = 16

BYTE_MASK = 0xff
TWO_BYTE_MASK = 0xffff


def int_to_bytes(val):
    num_bytes = (val.bit_length() + 7) // 8
    bytes_val = val.to_bytes(num_bytes, byteorder='big')
    return bytes_val


def pad(msg, rate):
    if len(msg) < rate:
        i = (-(len(msg)+1)) % rate
        padding = hex(1 << i)
        msg += bytes.fromhex(padding[2:])
    return msg


def xor_in_place(original, vals):
    for i, vs in enumerate(zip(*vals)):
        for v in vs:
            original[i] ^= v


def split_x_and_y(internal_state):
    x_vals, y_vals = [], []

    for i in range(0, len(internal_state), 8):
        x_vals.append(internal_state[i:i+4])
        y_vals.append(internal_state[i+4:i+8])
    
    return x_vals, y_vals


def circular_rotation(value, shift, n):
    """
    Shifts the given value by the given amount of shift and wraps the values removed from the LSB side onto 
    the MSB side, such that all original bits are preserved but their position is circularly shifted.

    Args:
        - value (int): value being circularly shifted.
        - shift (int): the number of bits being circularly shifted to the right.
        - n (int): the block size / size of the value.

    Returns:
        The new integer formed by shifting the given value by the given shift amount.
    """
    if shift >= 0:
        lower_bits = value >> shift
        mask = (1 << shift) - 1
        upper_bits = (value & mask) << (n-shift)
        return upper_bits | lower_bits
    
    shift *= -1
    mask = (1 << shift) - 1
    upper_bits = (value & mask) << shift
    lower_bits = value >> (n-shift)
    return upper_bits | lower_bits