

PARAMETERS = {
    "ascon_hash": {"digest len": 32, "block": 8, "a": 12, "b": 12, "IV": b'00400c0000000100', "S": b'ee9398aadb67f03d8bb21831c60f1002b48a92db98d5da6243189921b8f8e3e8348fa5c9d525e140'}, 
    "ascon_hasha": {"digest len": 32, "block": 8, "a": 12, "b": 8, "IV": b'00400c0400000100', "S": b'01470194fc6528a6738ec38ac0adffa72ec8e3296c76384cd6f6a54d7f52377da13c42a223be8d87'}, 
    "ascon_xof": {"digest len": 0, "block": 8, "a": 12, "b": 12, "IV": b'00400c0000000000', "S": b'b57e273b814cd4162b51042562ae242066a3a7768ddf22185aad0a7a8153650c4f3e0e32539493b6'}, 
    "ascon_xofa": {"digest len": 0, "block": 8, "a": 12, "b": 12, "IV": b'00400c0400000000', "S": b'44906568b77b9832cd8d6cae53455532f7b5212756422129246885e1de0d225ba8cb5ce33449973f'}, 
}

def ascon(msg, hash_type):
    params = PARAMETERS[hash_type]
    digest = ""

    return digest
