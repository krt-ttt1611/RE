```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  char *input_ptr; // rsi
  unsigned __int64 count_i; // rcx
  char v5; // r10
  char v6; // dl
  char v7; // al
  char input_data[264]; // [rsp+0h] [rbp-108h] BYREF

  puts("feistel_pair");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    input_data[strcspn(input_data, "\r\n")] = 0;
    if ( strlen(input_data) == 38 )
    {
      input_ptr = input_data;
      count_i = 0LL;
      while ( 1 )
      {
        v5 = input_ptr[1];
        v6 = *input_ptr ^ __ROL1__(v5 + (count_i >> 1) + 17, 1) ^ 0xA3;
        v7 = v5 ^ __ROL1__(v6 + (count_i >> 1) + 55, 2) ^ 0x6C;
        if ( arr_1[count_i] != v7
          || arr_1[count_i + 1] != ((unsigned __int8)(v6 ^ __ROL1__(v7 + (count_i >> 1) + 93, 3)) ^ 0x19) )
        {
          break;
        }
        count_i += 2LL;
        input_ptr += 2;
        if ( count_i == 38 )
        {
          puts("Correct");
          return 0LL;
        }
      }
    }
    puts("Wrong");
  }
  return 1LL;
}
```
- v5 lấy kí tự thứ 2 tính từ con trỏ input_ptr làm tham số đầu vào cho hàm mã hóa.
- v6 sử dụng các kí tự của chuỗi đầu vào để làm tham số cho hàm mã hóa.
- v7 sử dụng v5 và v6 để làm tham số cho hàm mã hóa.
Code giải mã:
```python
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
```
Flag là: ISPCLUB{tiny_feistel_still_reversible}
**Chú ý: Cần chú ý kiểu dữ liệu của các biến, không giống ngôn ngữ bậc cao, nếu khai báo số vượt quá giới hạn thì máy tính sẽ tự động vứt các bit thừa đi, nếu ta sử dụng ngôn ngữ bậc cao khoogn dùng bitmask để xóa bit thừa thì sẽ gây ảnh hưởng đến kết quả (như hàm rol bên trên là ví dụ).** 

