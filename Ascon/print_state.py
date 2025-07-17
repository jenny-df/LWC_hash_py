def print_state(internal_state, print_reason = ""):
    assert len(internal_state) == 5, "internal state isn't 40 bytes!"
    assert isinstance(internal_state, dict), "internal state isn't a dict"

    if print_reason:
        print(print_reason, "\n")
    for val in internal_state.values():
        print(hex(val), end=" ")
    
    print("")