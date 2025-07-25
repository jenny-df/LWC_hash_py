from xoodyak import xoodyak_hash_mode

def test_xoodyak_hash_kat():
    """
    Test functional correctness of the implementation of the Xoodyak hash function,
    by comparing digests against NIST LWC submission package's Known Answer Tests

    See https://csrc.nist.gov/projects/lightweight-cryptography/finalists
    """
    with open("LWC_HASH_KAT_256.txt", "r", encoding="utf-8") as fd:
        while True:
            cnt = fd.readline()
            if not cnt:
                # no more KATs
                break

            # if cnt != "Count = 18\n":
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
            digest = xoodyak_hash_mode(msg)

            assert (
                md == digest
            ), f"[Xoodyak Hash KAT {cnt}] expected {md}, found {digest} !"
            fd.readline()

if __name__ == "__main__":
    test_xoodyak_hash_kat()
    print("PASSED ALL Xoodyak Hash Tests")
