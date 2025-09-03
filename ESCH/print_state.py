def hex_state(state):
    return f"0x{int.from_bytes(state, byteorder='big'):048X}"

def hex_x_y(vals):
    return [hex_32_bit(val) for val in vals]

def hex_rate(val):
    return f"0x{int.from_bytes(val, byteorder='big'):024X}"

def hex_32_bit(val):
    return f"0x{int.from_bytes(val, byteorder='big'):04X}"