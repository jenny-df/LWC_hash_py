from utils import *

def romulus_h(msg):
    left, right = bytearray(L_R_SIZE), bytearray(L_R_SIZE)
    msg_padded = ipad(msg, BLOCK_SIZE) 
    
    for i in range(0, len(msg_padded)-BLOCK_SIZE, BLOCK_SIZE):
        m_i = msg_padded[i:i+BLOCK_SIZE]
        cf(left, right, m_i)

    m_last = msg_padded[-BLOCK_SIZE:]
    xor_in_place(left, [CONST_2])
    cf(left, right, m_last)

    digest = left + right
    return digest

if __name__ == "__main__":
    pass