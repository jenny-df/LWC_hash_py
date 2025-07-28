def hex_state(state):
    return hex(int.from_bytes(state, byteorder="big"))[2:]

def hex_x_y(vals):
    return [hex_state(val) for val in vals]