array = [
   36,  39,  19, 198, 198,  19,  22, 230,  71, 245, 
   38, 150,  71, 245,  70,  39,  19,  38,  38, 198, 
   86, 245, 195, 195, 245, 227, 227,   0,   0,   0, 
    0,   0
]

text = ''
char = ''

for index, i in enumerate(array):
   char = ((i & 0xf0) >> 4) | ((i & 0xf) << 4) 
   text += chr(char)

print(text)