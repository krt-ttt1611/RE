arr_1 = [
   90, 134, 105, 126, 216, 159, 247,  93, 156, 221, 
   45, 183,   7,  76,   9, 183,  48, 126,  44,  70, 
  151,  15, 125, 234, 124, 234, 154, 228, 210,  29, 
  186, 203,  53, 201, 144,  50,  82, 144
]

def ror(data: int, step: int) -> int:
   return (data >> step) | (data << (8 - step)) & 0xff
def rol(data: int, step: int) -> int:
   data &= 0xff
   return ((data << step) & 0xff) | (data >> (8-step))

text = ''
char = 0
for count_i in range(0, 38, 2):
   v7 = arr_1[count_i]
   v6 = 0xff & (arr_1[count_i + 1] ^ 0x19) ^ (0xff & rol(v7 + (count_i >> 1) + 93, 3))
   input_char = v7 ^ (0xff&rol(v6 + (count_i >> 1) + 55, 2)) ^ 0x6C
   char = v6 ^ (0xff & rol(input_char + (count_i >> 1) + 17, 1)) ^ 0xA3
   text += chr(char) + chr(input_char)



print(text)