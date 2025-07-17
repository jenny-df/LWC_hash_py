from utils import * 


def ascon_hash(msg):
    return ascon(msg, "ascon_hash")

def ascon_hasha(msg):
    return ascon(msg, "ascon_hasha")

def ascon_xof(msg, digest_len):
    return ascon(msg, "ascon_xof", digest_len)

def ascon_xofa(msg, digest_len):
    return ascon(msg, "ascon_xofa", digest_len)

if __name__ == "__main__":
    pass