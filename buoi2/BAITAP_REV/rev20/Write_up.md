```c
//main
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  FILE *file; // rax
  FILE *v4; // rbp
  size_t data; // r12
  char *input_ptr; // rdi
  char *data_ptr; // rsi
  __int64 count_1; // rdx
  char input_data[256]; // [rsp+0h] [rbp-518h] BYREF
  _DWORD ptr[262]; // [rsp+100h] [rbp-418h] BYREF

  file = fopen("blob.dat", "rb");
  if ( file )
  {
    v4 = file;
    data = fread(ptr, 1uLL, 0x400uLL, file);
    fclose(v4);
    if ( data > 72 && ptr[0] == 0x42304C42 )
    {
      puts("blob_runner");
      fwrite("flag> ", 1uLL, 6uLL, stdout);
      if ( fgets(input_data, 256, stdin) )
      {
        input_data[strcspn(input_data, "\r\n")] = 0;
        if ( strlen(input_data) == 37 )
        {
          input_ptr = input_data;
          data_ptr = (char *)ptr;
          count_1 = 0LL;
          while ( data_ptr[36] == __ROL1__(
                                    *input_ptr ^ *((_BYTE *)&ptr[7] + (count_1 & 7)) ^ *((_BYTE *)&ptr[3]
                                                                                       + (count_1 & 0xF)),
                                    *((_BYTE *)&ptr[1] + (count_1 & 7))) )
          {
            ++count_1;
            ++input_ptr;
            ++data_ptr;
            if ( count_1 == 37 )
            {
              puts("Correct");
              return 0LL;
            }
          }
        }
        puts("Wrong");
      }
    }
    else
    {
      puts("bad blob");
    }
  }
  else
  {
    puts("missing blob.dat");
  }
  return 1LL;
}
```
Phân tích logic chương trình: 

- Đầu tiên, chương trình sẽ đọc file và kiểm tra magic number, nếu đúng thì sẽ yêu cầu nhập chuỗi kí tự.
- Sau đó, chương trình sẽ thực hiện duyệt từng byte bắt đầu từ byte thứ 36 trong dữ liệu của file blob, so sánh với kết quả của phép tính:
```c
__ROL1__(*input_ptr ^ *((_BYTE *)&ptr[7] + (count_1 & 7)) ^ *((_BYTE *)&ptr[3] + (count_1 & 0xF)), *((_BYTE *)&ptr[1] + (count_1 & 7))) )
```
Từ logic chương trình, ta sẽ xây dựng code giải mã. Ta biết toàn bộ dự liệu trong file blob, nên chỉ cần dùng hàm xoay bit phải để đảo ngược lại dữ liệu, ta sẽ tìm được flag.
```python
with open("blob.dat", "rb") as f:
    data = f.read()

def ror(data: int, step: int) -> step:
    data & 0xff
    return (data >> step%8) | (0xff & (data << (8 - step % 8)))

text = ''
for count_1 in range(0, 37):
    data_ptr = 0xff & data[36 + count_1];
    step = 0xff & data[4*1 + (count_1 & 7)]
    char = ror(data_ptr, step)
    char ^= data[4*7 + (count_1 & 7)] ^ data[4*3 + (count_1 & 0xf)]
    text += chr(char)
print(text)
```
flag: ISPCLUB{external_blobs_are_just_data}
