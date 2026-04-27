![](../../../ảnh/Pasted%20image%2020260427154504.png)
Câu lệnh ở dòng 23 là chia lấy dư cho 3 được tối ưu bằng magic number (lấy máy casio ra bấm) rồi cộng thêm 1. Bitmask 0xfe phía sau có tác dụng ép cho bit cuối của phép nhân 2/3 luôn bằng 0, nghĩa là số chẵn.
- BYTE2: lấy byte ở vị trí thứ 2 của dữ liệu.
Code giải mã.
```python
'''input_ptr = input;
   i = 0LL;
   v5 = 322376503;
   while ( 1 )
   {
      v5 = 1103515245 * v5 + 12345;
      if ( arr_1[i] != __ROL1__(*input_ptr ^ BYTE2(v5), i - (i / 3 + (((12297829382473034411uLL * (unsigned __int128)i) >> 64) & 0xFE)) + 1) )
         break;
      ++i;
      ++input_ptr;
'''



arr_1 = [
   35,  14, 229,  57,  18,  73,  56,  80, 132,  12, 
   92, 204,  77,  51,  93, 177, 222,   4, 206, 147, 
  155,  99,  11,  66,  76,  54, 170, 168, 253,  60, 
  128, 188, 211,  58,  11,  82
]


def ror(data: int, step: int) -> int:
   return ((data >> step) | data << (8-step)) & 0xff


v5 = 322376503
text = ''
char = ''

for i in range(0, 36):
   v5 = 1103515245 * v5 + 12345
   char = ror(arr_1[i], i%3+1) ^ ((v5 & 0xff0000) >> 16)
   text += chr(char)

print(text)

```
Flag là: ISPCLUB{lcg_streams_are_predictable}