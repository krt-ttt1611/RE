arr_1 = [
  148,  53,   5,  52, 196,  85,  36, 183,  70,  86, 
   54,  39, 151,   7,  71, 150, 230, 118, 245,  39, 
  246,  70,  22,  71,  22, 245, 150,  55, 245, 134, 
   22, 198, 102, 245,  71, 134,  86, 245, 166, 246, 
   38, 215
]

def ror(data: int, step: int) -> int:
  return (data >> step) | (0xff & (data << (8 - step)))


for i in arr_1:
  char = ror(i, 4)
  print(chr(char), end = '')