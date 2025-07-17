from ascon import *

def test_ascon_hash_kat():
    """
    Test functional correctness of the implementation of Ascon's hash function,
    by comparing digests against NIST LWC submission package's Known Answer Tests

    See https://csrc.nist.gov/projects/lightweight-cryptography/finalists
    """
    with open("LWC_HASH_KAT.txt", "r") as fd:
        while True:
            cnt = fd.readline()
            if not cnt:
                # no more KATs
                break

            # if cnt != "Count = 9\n":
            #     continue

            msg = fd.readline()
            md = fd.readline()

            cnt = int([i.strip() for i in cnt.split("=")][-1])
            msg = [i.strip() for i in msg.split("=")][-1]
            md = [i.strip() for i in md.split("=")][-1]

            msg = bytes(
                [
                    int(f"0x{msg[(i << 1): ((i+1) << 1)]}", base=16)
                    for i in range(len(msg) >> 1)
                ]
            )

            md = bytes(
                [
                    int(f"0x{md[(i << 1): ((i+1) << 1)]}", base=16)
                    for i in range(len(md) >> 1)
                ]
            )
            digest = ascon_hash(msg)

            assert (
                md == digest
            ), f"[ASCON HASH KAT {cnt}] expected {md}, found {digest} !"
            fd.readline()

def test_ascon_xof_kat():
    """
    Test functional correctness of the implementation of Ascon's xof function,
    by comparing digests against NIST LWC submission package's Known Answer Tests

    See https://csrc.nist.gov/projects/lightweight-cryptography/finalists
    """
    with open("LWC_XOF_KAT.txt", "r") as fd:
        while True:
            cnt = fd.readline()
            if not cnt:
                # no more KATs
                break

            # if cnt != "Count = 9\n":
            #     continue

            msg = fd.readline()
            md = fd.readline()

            cnt = int([i.strip() for i in cnt.split("=")][-1])
            msg = [i.strip() for i in msg.split("=")][-1]
            md = [i.strip() for i in md.split("=")][-1]

            msg = bytes(
                [
                    int(f"0x{msg[(i << 1): ((i+1) << 1)]}", base=16)
                    for i in range(len(msg) >> 1)
                ]
            )

            md = bytes(
                [
                    int(f"0x{md[(i << 1): ((i+1) << 1)]}", base=16)
                    for i in range(len(md) >> 1)
                ]
            )
            digest = ascon_xof(msg, 64)

            assert (
                md == digest
            ), f"[ASCON XOF KAT {cnt}] expected {md}, found {digest} !"
            fd.readline()

if __name__ == "__main__":
    test_ascon_hash_kat()
    print("PASSED ALL HASH")
    test_ascon_xof_kat()
    print("PASSED ALL XOF")