from utils import *


def ascon_hash(msg):
    return ascon(msg, "ascon_hash")

def ascon_hasha(msg):
    return ascon(msg, "ascon_hasha")

def ascon_xof(msg):
    return ascon(msg, "ascon_xof")

def ascon_xofa(msg):
    return ascon(msg, "ascon_xofa")

if __name__ == "__main__":
    pass