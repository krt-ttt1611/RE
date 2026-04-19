array = [
  173, 216, 203, 203, 157, 151, 203, 196, 146, 161, 
  210, 215, 210, 214, 168, 165, 220, 199, 173, 163, 
  161, 152,  76,   0,   0,   0,   0,   0,   0,   0, 
    0,   0
]
for j in range (32, 127):
  text = '' + chr(j)
  prev = j
  for i in range(0, 25):
    if (array[i]-prev < 0 or array[i]-prev > 255):
      break                  
    else:
      text += chr(array[i]-prev)
      prev = array[i]-prev
  print(text)
