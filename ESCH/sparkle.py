from utils import * 
from print_state import *

CONSTS = [0xB7E15162, 0xBF715880, 0x38B4DA56, 0x324E7738, 0xBB1185EB, 0x4F7C7B57, 0xCFBFA1C8, 0xC2B3293D]

SPARKLE_MAX_I = 1 << 32
FOUR_BYTE_MASK = SPARKLE_MAX_I - 1

ALZETTE_SHIFTS = [(31, 24), (17, 17), (0, 31), (24, 16)]

SPARKLE_TYPES = {
    "384": {"block size": 48, "num_branches": 6, "slim steps": 7, "big steps": 11},
    "512": {"block size": 64, "num_branches": 8, "slim steps": 8, "big steps": 12},
}

def sparkle(internal_state, sparkle_type, step_type):
    params = SPARKLE_TYPES[sparkle_type]

    print("SPARKLE START:")
    
    for i in range(params[step_type]):
        c = int_to_bytes(CONSTS[i%8] & FOUR_BYTE_MASK) # TODO: is it the upper or lower 4 bytes?
        xor_val = int_to_bytes((i % SPARKLE_MAX_I) & FOUR_BYTE_MASK)

        print(f"ROUND {i}:\nbefore xor: {hex_state(internal_state)=}\n{c=}\n{xor_val=}")

        for j, (c_byte, x_byte) in enumerate(zip(c, xor_val)):
            internal_state[4 + j] ^= c_byte # y_0
            internal_state[12 + j] ^= x_byte # y_1

        print(f"after xor: {hex_state(internal_state)=}")
        
        for j in range(0, len(internal_state), 8):
            x, y = internal_state[j:j+4], internal_state[j+4:j+8]
            new_x, new_y = alzette(x, y, CONSTS[j%8] & FOUR_BYTE_MASK)

            print(f"POST ALZETTE: {hex(new_x)=}\n{hex(new_y)=}")

            new_x, new_y = int_to_bytes(new_x), int_to_bytes(new_y)
            for k, (byte_x, byte_y) in enumerate(zip(new_x, new_y)):
                internal_state[j + k] = byte_x
                internal_state[j + 4 + k] = byte_y

        L(internal_state, params['num_branches'] // 2)

        print(f"POST L FUNCTION: {params['num_branches']=}\n{hex_state(internal_state)=}")


def alzette(x, y, const):
    x = int.from_bytes(x, byteorder="big")
    y = int.from_bytes(y, byteorder="big")
    for y_shift, x_shift in ALZETTE_SHIFTS:
        x = (x + circular_rotation(y, y_shift, 32)) % SPARKLE_MAX_I
        y ^= circular_rotation(x, x_shift, 32)
        x ^= const
    return x, y

def feistel_round(state, half_branches):
    print(f"IN feistel_round FUNC")
    t = 0

    for i in range(0, half_branches * 4, 8):
        t ^= int.from_bytes(state[i:i+8], byteorder="little")

    t_x = (t >> 32) & FOUR_BYTE_MASK
    t_y = t & FOUR_BYTE_MASK

    l_t_x = circular_rotation(t_x, -16, 32) ^ t_x
    l_t_y = circular_rotation(t_y, -16, 32) ^ t_y
    l_t_inv = int_to_bytes((l_t_y << 32) + l_t_x, 8)

    output = b''
    for i in range(0, half_branches * 2 * 4, 8):
        for j, byte in enumerate(l_t_inv):
            if i + j < len(state):
                output += bytes([state[i + j] ^ byte])
            else:
                output += bytes([byte])
    return output
    

def L(internal_state, half_branches):
    print(f"IN L FUNC")
    output = feistel_round(internal_state, half_branches)
    half_way_i = len(internal_state) // 2
    for i, byte in enumerate(output):
        internal_state[half_way_i + i] ^= byte


    right = circular_rotation(int.from_bytes(internal_state[half_way_i:], "big"), -16, half_way_i * 8)
    right = int_to_bytes(right, half_way_i)
    left = internal_state[:half_way_i]

    internal_state[:half_way_i] = right
    internal_state[half_way_i:] = left
