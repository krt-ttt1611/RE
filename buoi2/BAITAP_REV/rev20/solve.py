with open("blob.dat", "rb") as f:
    data = f.read()

def ror(data: int, step: int) -> step:
    data & 0xff
    return (data >> step%8) | (0xff & (data << (8 - step % 8)))

text = ''
for count_1 in range(0, 37):
    data_ptr = 0xff & data[36 + count_1];
    step = 0xff & data[4*1 + (count_1 & 7)]
    char = ror(data_ptr, step)
    char ^= data[4*7 + (count_1 & 7)] ^ data[4*3 + (count_1 & 0xf)]
    text += chr(char)
print(text)
