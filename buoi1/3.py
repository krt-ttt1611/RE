array = [
   73,  96, 103, 116,  99, 103,  66, 102, 128, 120, 
  105, 105, 123, 153, 109, 136, 104, 148, 159, 141, 
   77, 165, 157,  69,   0,   0,   0,   0,   0,   0, 
    0,   0
]

text = ''
char = 0

for index, i in enumerate(array):
   if (i == 0):
      break
   char = (i - index*2) ^ index
   text += chr(char)


print(text)