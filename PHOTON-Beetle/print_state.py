def print_state(internal_state, print_reason = ""):
    assert len(internal_state) == 32, "internal state isn't 32 bytes!"

    print(print_reason, "\n")

    print("[", end=" ")
    for i, val in enumerate(internal_state):
        print(hex(val), end=", ")
        if i % 4 == 3:
            print()
    
    print("]")