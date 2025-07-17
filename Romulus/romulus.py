from utils import *

DIGEST_LEN = 32
BLOCK_SIZE = 32

def romulus_h(msg):
    left, right = 0, 0
    for i in range(5): # TODO: fill
        m_i = msg # TODO: splice msg
        left, right = cf(left, right, m_i)

    m_last = msg # TODO: splice msg
    left ^= 2
    left, right = cf(left, right, m_last)
    # right_bytes = right.to_bytes()
    digest = left << 5 + right # TODO: figure out const other than 5
    return digest

if __name__ == "__main__":
    pass