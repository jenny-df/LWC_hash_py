from romulus import *

def test_romulus_h_kat():
    """
    Test functional correctness of the implementation of the Romulus-H hash function,
    by comparing digests against NIST LWC submission package's Known Answer Tests

    See https://csrc.nist.gov/projects/lightweight-cryptography/finalists
    """
    with open("LWC_HASH_KAT_256.txt", "r") as fd:
        while True:
            cnt = fd.readline()
            if not cnt:
                # no more KATs
                break

            # if cnt != "Count = 1\n":
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
            digest = romulus_h(msg)

            assert (
                md == digest
            ), f"[Romulus-H KAT {cnt}] expected {md}, found {digest} !"
            fd.readline()

if __name__ == "__main__":
    test_romulus_h_kat()
    print("PASSED ALL Romulus-H")