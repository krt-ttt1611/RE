#array1[v4] == (array3[v4] ^ __ROR1__(*v3 + array2[v4], v4 % 7 + 1))

array1 = [
  136, 246, 218, 136,  10, 117, 113,  77,   7,  65, 
  132, 139, 206, 191, 128, 145, 108, 224, 153, 157, 
  184, 108, 216, 117, 243,  59, 176,  72,  38, 102, 
  232,   2, 196,  44, 195, 137, 234,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0
]
array2 = [
   17,  22,  27,  32,  37,  42,  47,  52,  57,  62, 
   67,  72,  77,  82,  87,  92,  97, 102, 107, 112, 
  117, 122, 127, 132, 137, 142, 147, 152, 157, 162, 
  167, 172, 177, 182, 187, 192, 197, 202,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0
]
array3 = [
  165, 172, 183, 190, 129, 136, 147, 154, 237, 244, 
  255, 198, 201, 208, 219,  34,  53,  60,   7,  14, 
   17,  24,  99, 106, 125,  68,  79,  86,  89, 160, 
  171, 178, 133, 140, 151, 158, 225, 232
]


def rol(data, step):
  return data >> (8 - step) | ((data << step) & 0xff)

def solve():
  text = ''
  for i in range(0, 38):
    step = i % 7 + 1
    char = array1[i] ^ array3[i]
    char = rol(char, step)
    char -= array2[i]
    text += chr(char & 0xff) # có thể bị tràn dẫn đến âm
  return text

print(solve())


print("openssl req -config intermediate/openssl.cnf -key intermediate/private/plc2.example.com.key.pem -subj ’/CN=plc2.example.com/O=Example./C=US/ST=CA’ -new -sha256 -out intermediate/csr/plc2.example.com.csr.pem")