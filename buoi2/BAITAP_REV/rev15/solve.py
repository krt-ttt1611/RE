arr_1 = [
  107, 173, 187, 242, 122, 197, 253,  54,  46,  38, 
  215,  69,  63,  98, 209, 132,  45, 114, 141, 227, 
  234,  70, 203, 115, 249, 126, 100, 163, 219, 158, 
    1, 242, 160, 118, 125,  83, 184, 170,  57, 163, 
  153, 246
]

def ror(data: int, step: int) -> int:
  data &= 0xff
  return 0xff & (data << (8 - step)) | (data >> (step))

def rol(data: int, step: int) -> int:
  data &= 0xff
  return 0xff & (data << step) | (data >> (8-step))

def func_1(char: int, count: int) -> int:
  return 0xff & (char ^ (5 * count + 34))

def func_2(char: int, count: int) -> int:
  return 0xff & (ror(char, 2) - 23 - count)

def func_3(char: int, count: int) -> int:
  return 0xff & (rol(char ^ count, 3) ^ 0xffffff9d)

def func_4(char: int, count: int) -> int:
  return 0xff & (ror(char, 4) + count + 17)


text = ''
char = 0;
for count_1 in range(0, 42):
  step = count_1 % 4
  if step == 0:
    char = func_1(arr_1[count_1], count_1)
  elif step == 1:
    char = func_2(arr_1[count_1], count_1)
  elif step == 2:
    char = func_3(arr_1[count_1], count_1)
  else:
    char = func_4(arr_1[count_1], count_1)
  text += chr(char)

print(text)