def print_state(state):
    for i in range(0, 48, 16):
        plane = state[i:i + 16]
        val = int.from_bytes(plane, byteorder='big')
        print(f"Plane {i//16 +1}: 0x{val:032X}")
    print()