

ROUNDS = 12
INTERNAL_STATE_LEN = 64

ROUND_CONSTS = [1, 3, 7, 14, 13, 11, 6, 12, 9,  2, 5, 10]
INTERNAL_CONSTS_D8 = [0, 1, 3, 7, 15, 14, 12, 8]
RC_XOR_IC8 = [1,  0,  2,  6,  14, 15, 13, 9,  
              3,  2,  0, 4,  12, 13, 15, 11, 
              7,  6,  4,  0, 8,  9,  11, 15, 
              14, 15, 13, 9,  1,  0,  2, 6,  
              13, 12, 14, 10, 2,  3,  1,  5,
              11, 10, 8,  12, 4,  5,  7,  3,  
              6,  7,  5, 1,  9,  8,  10, 14, 
              12, 13, 15, 11, 3,  2,  0,  4,  
              9,  8,  10, 14, 6,  7,  5, 1, 
              2,  3,  1,  5,  13, 12, 14, 10,
              5,  4,  6,  2,  10, 11, 9,  13, 
              10, 11, 9, 13, 5,  4,  6,  2]

SBOX = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
M8 = [2, 4, 2, 11, 2, 8, 5, 6,
      12, 9, 8, 13, 7, 7, 5, 2,
      4, 4, 13, 13, 9, 4, 13, 9,
      1, 6, 5, 1, 12, 13, 15, 14,
      15, 12, 9, 13, 14, 5, 14, 13,
      9, 14, 5, 15, 4, 12, 9, 6,
      12, 2, 2, 10, 3, 1, 1, 14,
      15, 1, 13, 10, 5, 10, 2, 3]


def photon256(internal_state):
    '''
    Applies the PHOTON-256 algorithm (12 rounds) on the internal state array by mutating it.

    ARGS:
        - internal_state (list): memory of the cryptographic algorithm contains 64 elements of 4-bits each.
    RETURNS:
        - None
    '''

    for i in range(ROUNDS):
        add_constant(internal_state, i)
        subcells(internal_state)
        shift_rows(internal_state)
        mix_column_serial(internal_state)

def add_constant(internal_state, round_i):
    '''
    Adds fixed constants to the cells of the internal state (using XOR) by mutating it.

    ARGS:
        - internal_state (list): memory of the cryptographic algorithm contains 64 elements of 4-bits each.
        - round_i (int): the round that the photon256 algorithm/function is on right now.
    RETURNS:
        - None
    '''

    offset = round_i * 8
    for row in range(8):
        internal_state[row*8] ^= RC_XOR_IC8[offset + row]

def subcells(internal_state):
    '''
    Applies a 4-bit S-Box to each cell in the internal state by mutating it.

    ARGS:
        - internal_state (list): memory of the cryptographic algorithm contains 64 elements of 4-bits each.
    RETURNS:
        - None
    '''

    for i in range(INTERNAL_STATE_LEN):
        internal_state[i] = SBOX[internal_state[i]]

def shift_rows(internal_state):
    '''
    Rotates the position of the cells in each row of the internal state by mutating it.

    ARGS:
        - internal_state (list): memory of the cryptographic algorithm contains 64 elements of 4-bits each.
    RETURNS:
        - None
    '''

    row = 0
    for row_start in range(0, INTERNAL_STATE_LEN, 8):
        IS_row_copy = internal_state[row_start:row_start+8]
        for col in range(8):
            internal_state[row_start + col] = IS_row_copy[(row + col) % 8]
        row += 1

def mix_column_serial(internal_state):
    '''
    Linearly mixes all the columns of the internal state independently using serial matrix multiplication by mutating it.

    ARGS:
        - internal_state (list): memory of the cryptographic algorithm contains 64 elements of 4-bits each.
    RETURNS:
        - None
    '''

    for i in range(INTERNAL_STATE_LEN):
        internal_state[i] *= M8[i]