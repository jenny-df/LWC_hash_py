import sys

def photon_beetle_hash_32(msg):
    DIGEST_LEN_BYTES = 32
    digest = ""
    br = [2, 1]
    state = 0

    if len(msg) == 0:
        # bytes([s ^ v for _d, _k in zip(data_long, key_short)])
        state ^= (1 << 5)
        photon_common::gen_tag<32>(state, digest)
    elif len(msg) <= 16:
        flg = len(msg) < 16

        if sys.byteorder == "little":
            bit_off = (flg * len(msg)) * 8
        else:
            bit_off = (15 - (flg * len(msg))) * 8
        
        mword = 1 << bit_off
        mword[0:len(msg)] = rlen_msg
        state[0:len(mword)] = mword

        c0 = br[flg]
        state ^= (c0 << 5)

        photon_common::gen_tag<32>(state, digest)
    else:
        state[0:16] = msg[0:16]

        rlen_msg = len(msg) - 16
        c0 = br[(rlen_msg & 3) == 0] # domain seperation const

        photon_common::absorb<4>(state, msg + 16, c0)
        photon_common::gen_tag<32>(state, digest)

    return digest

RC = [1,  0,  2,  6,  14, 15, 13, 9,  3,  2,  0, 4,  12, 13, 15, 11, 7,  6,  4,  0,
      8,  9,  11, 15, 14, 15, 13, 9,  1,  0,  2, 6,  13, 12, 14, 10, 2,  3,  1,  5,
      11, 10, 8,  12, 4,  5,  7,  3,  6,  7,  5, 1,  9,  8,  10, 14, 12, 13, 15, 11,
      3,  2,  0,  4,  9,  8,  10, 14, 6,  7,  5, 1,  2,  3,  1,  5,  13, 12, 14, 10,
      5,  4,  6,  2,  10, 11, 9,  13, 10, 11, 9, 13, 5,  4,  6,  2]

LS4B = 0x0f
ROUNDS = 12
IRP = 0b00010011 & LS4B

def absorb(state, msg, C):
    pass

def add_constant(state, round_ind):
    off = round_ind << 3
    tmp = state[:8]

    if sys.byteorder == "little":
        for i in range(8):
        tmp[i] = photon_utils::bswap32(tmp[i])

    for i in range(8):
        tmp[i] ^= RC[off + i]

    state[:8] = tmp

def subcells(state):
    for i in range(32):
        state[i] = SBOX[state[i]]

def shift_rows(state):
    tmp = state[:8]
    for i in range(8):
        if sys.byteorder == "little":
            tmp[i] = std::rotr(tmp[i], i * 4)
        else:
            tmp[i] = std::rotl(tmp[i], i * 4)

    state[:8] = tmp

def mix_column_serial_inner(state):
    s_prime = [0 * 64]

    for off in range(8*8, 8):
        for k in range(8):
            for j in range(8):
                idx = (M8[off + k] << 4) | (state[(k * 8) + j] & LS4B)
                s_prime[off + j] ^= GF16_MUL_TAB[idx]

    state[:s_prime] = s_prime[:s_prime]

def mix_column_serial(state):
    tmp = [0 * 64]

    if sys.byteorder == "little" and defined __SSSE3__:
        mask0 = 0x0f0f0f0fu
        mask1 = mask0 << 4
        mask2 = 0x0703060205010400ul

        for i in range(8):
            row = state + i * sizeof(row), sizeof(row))
            t0 = row & mask0
            t1 = (row & mask1) >> 4
            t2 = (t1 << 32) | t0
            t3 = _mm_shuffle_pi8((__m64)t2, (__m64)mask2);

        std::memcpy(tmp + i * sizeof(t3), &t3, sizeof(t3));
    else:
        for i in range(32):
            tmp[2 * i] = state[i] & LS4B
            tmp[2 * i + 1] = state[i] >> 4

    mix_column_serial_inner(tmp)
    for i in range(32):
        state[i] = (tmp[2 * i + 1] << 4) | tmp[2 * i]

def photon256(state):
    for i in range(ROUNDS):
        add_constant(state, i)
        subcells(state)
        shift_rows(state)
        mix_column_serial(state)

def gen_32_tag(state):
    tag = bytes(32)
    photon256(state)
    tag[0:16] = state[0:16]

    photon256(state)
    tag[16:] = state[16:]
    return tag


if __name__ == "__main__":
    pass