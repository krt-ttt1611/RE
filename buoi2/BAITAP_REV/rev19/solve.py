with open("program.bin", "rb") as f:
    data = f.read()


def ror(d: int, step:int) -> int:
    d &= 0xff
    return 0xff & ((d >> step) | (d << (8 - step)))

flag = [0]*60
for check_ip in range(12, len(data), 15):
    arg_1 = data[check_ip + 1]
    for offset in range (3, -1, -1):
        ip = check_ip - 4*3 + offset * 3
        byte_0 = data[ip]
        byte_1 = data[ip + 1] & 0xff
        if byte_0 == 0x10:
            flag[byte_1] = chr(arg_1 & 0xff)
            print(chr(arg_1), end = "")
        elif byte_0 == 0x20:
            arg_1 ^= byte_1
        elif byte_0 == 0x30:
            arg_1 = (arg_1 - byte_1) & 0xff
        elif byte_0 == 0x40:
            arg_1 = (arg_1 & 0xffffff00) |  ror(arg_1, byte_1)
