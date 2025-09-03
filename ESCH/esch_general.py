from sparkle import * 
import math

ESCH_TYPES = {
    "esch256": {"sparkle": "384", "digest len": 48, "const_m1": int_to_bytes(1 << 192, 48), "const_m2": int_to_bytes(2 << 192, 48), "M padding": 8, "sparkle padding": 24},
    "esch384": {"sparkle": "512", "digest len": 64, "const_m1": int_to_bytes(1 << 256, 48), "const_m2": int_to_bytes(2 << 256, 48), "M padding": 16, "sparkle padding": 32},
    "xoesch256":{"sparkle": "384", "digest len": 0, "const_m1": int_to_bytes(5 << 192, 48), "const_m2": int_to_bytes(6 << 192, 48), "M padding": 8, "sparkle padding": 24},
    "xoesch384": {"sparkle": "512", "digest len": 0, "const_m1": int_to_bytes(5 << 256, 48), "const_m2": int_to_bytes(6 << 256, 48), "M padding": 16, "sparkle padding": 32},
    }

def esch(msg, esch_type, digest_len=None):
    params = ESCH_TYPES[esch_type]
    if not params['digest len']:
        assert digest_len is not None, "When using XOF version, you must specify the digest len"
    else:
        digest_len = params['digest len']

    half_branches = SPARKLE_TYPES[params['sparkle']]['num_branches'] // 2

    # absorb
    internal_state = bytearray(params["digest len"])
    num_full = len(msg) // BLOCK_SIZE
    print(f'{hex(int.from_bytes(msg, "big"))=}\n{num_full=}\n{half_branches=}\n{hex_state(internal_state)=}')

    for i in range(0, num_full * BLOCK_SIZE, BLOCK_SIZE):
        msg_i = msg[i:i+BLOCK_SIZE] + bytes(params["M padding"])
        msg_i_prime = feistel_round(msg_i, half_branches)
        msg_i_prime += bytes(params['sparkle padding'])

        xor_in_place(internal_state, [msg_i_prime])
        print(f'{hex_state(msg_i)=}\n{hex_state(msg_i_prime)=}\nXOR:{hex_state(internal_state)=}')
        sparkle(internal_state, params["sparkle"], "slim steps")
        print(f'SPARKLE (slim):{hex_state(internal_state)=}')

    msg_last = pad(msg[num_full * BLOCK_SIZE:], BLOCK_SIZE) + bytes(params["M padding"])
    msg_last_prime = feistel_round(msg_last, half_branches)
    msg_last_prime += bytes(params['sparkle padding'])

    const_m = params["const_m1"] if len(msg) - num_full * BLOCK_SIZE < BLOCK_SIZE else params["const_m2"]

    xor_in_place(internal_state, [msg_last_prime, const_m])
    print(f'{hex_state(msg_last)=}\n{hex_state(msg_last_prime)=}\n{hex_state(const_m)=}\nIS after XOR:{hex_state(internal_state)=}')
    print("DONE")
    sparkle(internal_state, params["sparkle"], "big steps")
    print(f'SPARKLE (big):{hex_state(internal_state)=}')

    # squeeze
    digest = internal_state[:BLOCK_SIZE]
    print(f'{hex_state(digest)=}')
    for _ in range(math.ceil(digest_len // BLOCK_SIZE) - 1):
        sparkle(internal_state, params["sparkle"], "slim steps")
        digest += internal_state[:BLOCK_SIZE]
        print(f'SPARKLE (slim):{hex_state(internal_state)=}\n{hex_state(digest)=}')

    return bytes(digest)