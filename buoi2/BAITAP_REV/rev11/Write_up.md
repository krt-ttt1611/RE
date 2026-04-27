![](../../../ảnh/Pasted%20image%2020260427072926.png)
Code giải mã:
```python
''' input_ptr = input;
    i = 0LL;
    v5 = 66;
    while ( 1 ){
      v5 = *input_ptr ^ __ROL1__(arr_1[i] + v5, 1);
      if ( arr_2[i] != v5 )
        break;
        ++i;
        ++input_ptr;
'''

arr_1 = [
   19,  22,  25,  28,  31,  34,  37,  40,  43,  46, 
   49,  52,  55,  58,  61,  64,  67,  70,  73,  76, 
   79,  82,  85,  88,  91,  94,  97, 100, 103, 106, 
  109, 112, 115, 118, 121, 124
]

arr_2 = [
  227, 160,  35,  61, 244, 121, 127,  52, 204, 154, 
  251,  50, 187, 133, 226,  27, 207,  94,  46, 128, 
  250, 199,  90,   0, 215,  30, 141, 188,  53,  75, 
    3, 143, 106, 166,  77, 238,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0
]

def rol(data: int, step: int) -> int:
  return ((data << (step)) & 0xff) | ((data >> (8-step)))


char = ''
text = ''
v5 = 66

for i in range(0, 36):
  char = arr_2[i] ^ rol((arr_1[i] + v5) & 0xff, 1)
  v5 = char ^ rol((arr_1[i] + v5) & 0xff, 1)
  text += chr(char)

print(text)
```
flag là: ISPCLUB{rolling_state_beats_strings}
