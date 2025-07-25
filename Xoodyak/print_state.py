def print_state(state):
    '''
    Prints the state of Xoodyak in a readable format: displays each plane (labelled)'s lanes (4 lanes <- 4 bytes each)
    concatenated together in one hexadecimal value (16 bytes).

    Args:
        - state (bytes/bytearray): the internal state / memory of the Xoodyak hash function (48 bytes).

    Returns:
        None
    '''

    for i in range(0, 48, 16):
        plane = state[i:i + 16]
        val = int.from_bytes(plane, byteorder='big')
        print(f"Plane {i//16 +1}: 0x{val:032X}")
    print()