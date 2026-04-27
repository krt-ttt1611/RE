#!/usr/bin/env python3
EXPECTED = [26641, 30734, 25357, 29720, 18951, 8220, 5351, 15086, 11241, 16333, 3796, 3044, 433, 5006, 57765, 65154, 57999]

def pack_pair(left: str, right: str, pair_index: int) -> int:
    a = ord(left) ^ ((0x21 + pair_index * 7) & 0xFF)
    b = ord(right) ^ ((0x42 + pair_index * 11) & 0xFF)
    return (a << 8) | b

def main() -> None:
    user = input("flag> ")
    if len(user) != 34:
        print("Wrong")
        return
    for pair_index in range(0, len(user), 2):
        if pack_pair(user[pair_index], user[pair_index + 1], pair_index // 2) != EXPECTED[pair_index // 2]:
            print("Wrong")
            return
    print("Correct")

if __name__ == "__main__":
    main()
