from utils import * 
from print_state import *

CONSTS = [0xB7E15162, 0xBF715880, 0x38B4DA56, 0x324E7738, 0xBB1185EB, 0x4F7C7B57, 0xCFBFA1C8, 0xC2B3293D]

SPARKLE_MAX_I = 1 << 32
FOUR_BYTE_MASK = SPARKLE_MAX_I - 1

ALZETTE_SHIFTS = [(31, 24), (17, 17), (0, 31), (24, 16)]

SPARKLE_TYPES = {
    "384": {"block size": 48, "n_b": 6, "slim steps": 7, "big steps": 11},
    "512": {"block size": 64, "n_b": 8, "slim steps": 8, "big steps": 12},
}

def sparkle(internal_state, sparkle_type, step_type):
    params = SPARKLE_TYPES[sparkle_type]

    x_vals, y_vals = split_x_and_y(internal_state)
    print(f"SPARKLE START:\n {hex_state(internal_state)=}\n{hex_x_y(x_vals)=}\n{hex_x_y(y_vals)=}")
    for i in range(params[step_type]):
        c = int_to_bytes(CONSTS[i%8] & FOUR_BYTE_MASK)
        xor_val = int_to_bytes((i % SPARKLE_MAX_I) & FOUR_BYTE_MASK)
        xor_in_place(y_vals[0], [c])
        xor_in_place(y_vals[1], [xor_val])
        print(f"\nROUND {i}:\n{hex_state(internal_state)=}\n{hex_x_y(y_vals)=}")
        
        for j, (x, y) in enumerate(zip(x_vals, y_vals)):
            new_x, new_y = alzette(x, y, CONSTS[i%8] & FOUR_BYTE_MASK)
            print(f"POST ALZETTE: {hex(new_x)=}\n{hex(new_y)=}")
            new_x, new_y = int_to_bytes(new_x), int_to_bytes(new_y)
            for k, (byte_x, byte_y) in enumerate(zip(new_x, new_y)):
                internal_state[j*8 + k] = byte_x
                internal_state[j*8 + 4 + k] = byte_y
            print(f"POST ALZETTE AND SETTING: {hex_state(internal_state)=}")

        L(x_vals, y_vals, params['n_b'])
        print(f"POST L FUNCTION: {params['n_b']=}\n{hex_x_y(x_vals)=}\n{hex_x_y(y_vals)=}\n{hex_state(internal_state)=}")


def alzette(x, y, const):
    x = int.from_bytes(x, byteorder="big")
    y = int.from_bytes(y, byteorder="big")
    for y_shift, x_shift in ALZETTE_SHIFTS:
        x = (x + circular_rotation(y, y_shift, 32)) % SPARKLE_MAX_I
        y ^= circular_rotation(x, x_shift, 32)
        x ^= const
    return x, y

def M(msg, h_b):
    t = 0
    # print(len(msg), h_b, msg)
    for i in range(0, h_b * 4, 4):
        x_y = int.from_bytes(msg[i:i+4], byteorder="big")
        t ^= x_y

    t_x = (t >> 16) & TWO_BYTE_MASK
    t_y = t & TWO_BYTE_MASK

    l_t_x = circular_rotation(t_x, -16, 32) ^ (t_x & TWO_BYTE_MASK)
    l_t_y = circular_rotation(t_y, -16, 32) ^ (t_y & TWO_BYTE_MASK)
    # print(hex(circular_rotation(t_x, -16, 32)), hex(l_t_x))
    # print(hex(circular_rotation(t_y, -16, 32)), hex(l_t_y))

    l_t_inv = int_to_bytes((l_t_y << 32) + l_t_x)
    # print(len(l_t_inv))
    output = b''
    for i in range(0, h_b * 4, 4):
        for j, byte in enumerate(l_t_inv):
            if len(msg) > i + j:
                output += bytes([byte ^ msg[i+j]])
            else:
                output += bytes([byte])
    return output
    

def L(x_vals, y_vals, n_b):
    t_x = bytearray([a^b^c for a, b, c in zip(x_vals[0], x_vals[1], x_vals[2])])
    t_y = bytearray([a^b^c for a, b, c in zip(y_vals[0], y_vals[1], y_vals[2])])
    if n_b == 8:
        xor_in_place(t_x, [x_vals[3]])
        xor_in_place(t_y, [y_vals[3]])

    t_x = int.from_bytes(t_x, byteorder="big")
    t_y = int.from_bytes(t_y, byteorder="big")

    t_x, t_y = circular_rotation(t_x ^ (t_x << 16), -16, 32), circular_rotation(t_y ^ (t_y << 16), -16, 32)

    t_x, t_y = int_to_bytes(t_x), int_to_bytes(t_y)

    half_way_i = n_b//2
    for i in range(half_way_i, n_b):
        xor_in_place(x_vals[i], [x_vals[i], x_vals[i-half_way_i], t_y])
        xor_in_place(y_vals[i], [y_vals[i], y_vals[i-half_way_i], t_x])

    if n_b == 8:
        x_vals[0], x_vals[1], x_vals[2], x_vals[3], x_vals[4], x_vals[5], x_vals[6], x_vals[7] = x_vals[5], x_vals[6], x_vals[7], x_vals[4], x_vals[0], x_vals[1], x_vals[2], x_vals[3]
        y_vals[0], y_vals[1], y_vals[2], y_vals[3], y_vals[4], y_vals[5], y_vals[6], y_vals[7] = y_vals[5], y_vals[6], y_vals[7], y_vals[4], y_vals[0], y_vals[1], y_vals[2], y_vals[3]
    else:
        x_vals[0], x_vals[1], x_vals[2], x_vals[3], x_vals[4], x_vals[5] = x_vals[4], x_vals[5], x_vals[3], x_vals[0], x_vals[1], x_vals[2]
        y_vals[0], y_vals[1], y_vals[2], y_vals[3], y_vals[4], y_vals[5] = y_vals[4], y_vals[5], y_vals[3], y_vals[0], y_vals[1], y_vals[2]
    