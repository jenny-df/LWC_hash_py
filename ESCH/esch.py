from esch_general import *

def esch256(msg):
    return esch(msg, "esch256")

def esch384(msg):
    return esch(msg, "esch384")

def xo_esch256(msg, digest_len):
    return esch(msg, "xoesch256", digest_len)

def xo_esch384(msg, digest_len):
    return esch(msg, "xoesch384", digest_len)


if __name__ == "__main__":
    pass