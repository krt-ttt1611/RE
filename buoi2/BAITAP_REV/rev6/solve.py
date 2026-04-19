array1 = [
   95,  45, 129, 115, 135, 146,  57, 249,   2, 252, 
  188, 173, 225, 208, 159, 144,  44,  80, 222, 125, 
   56, 148, 175, 159, 180,  54, 175,  40, 203,  24, 
   66,  95, 229,  26,  18, 207,  47
]
array2 = [
   49,  66,  83, 100, 117, 134, 151, 168, 185, 202, 
  219, 236, 253,  14,  31,  48,  65,  82,  99, 116, 
  133, 150, 167, 184, 201, 218, 235, 252,  13,  30, 
   47,  64,  81,  98, 115, 132, 149
]


def ror(data, step):
   return (data >> step | data << (8-step)) & 0xff


def solve():
   text = ''
   for i in range(0, 37):
      char = array1[i]
      step = i%5 + 1
      v4 = (i*13)&0xff #ép dữ liệu của v4 chỉ chưa trong 8 bit bằng bitmask
      char = ror(char, step)
      char -= v4 ^ 55
      char ^= array2[i] 
      
      char &= 0xff
      text+=chr(char)
   return text

print(solve())