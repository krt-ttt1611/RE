```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  FILE *file; // rax
  FILE *v4; // rbp
  size_t data; // r12
  char *ip; // rax
  int arg_1; // edi
  char byte_0; // dl
  __int64 byte_1; // rcx
  bool bool_1; // cc
  char input_data[256]; // [rsp+0h] [rbp-1118h] BYREF
  _BYTE ptr[4120]; // [rsp+100h] [rbp-1018h] BYREF

  file = fopen("program.bin", "rb");
  if ( !file )
  {
    puts("missing program.bin");
    return 1LL;
  }
  v4 = file;
  data = fread(ptr, 1uLL, 0x1000uLL, file);
  fclose(v4);
  puts("vm_branch");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    input_data[strcspn(input_data, "\r\n")] = 0;
    if ( strlen(input_data) == 33 )
    {
      ip = ptr;
      arg_1 = 0;
      if ( data <= 2 )
        goto result;
      byte_0 = ptr[0];
      byte_1 = ptr[1];
      bool_1 = ptr[0] <= 0x40u;
      if ( ptr[0] == 0x40 )
        goto func_3;
func_1:
      if ( bool_1 )
      {
        if ( byte_0 != 32 )
        {
          if ( byte_0 == 48 )
          {
            arg_1 += byte_1;
            goto func_2;
          }
          if ( byte_0 == 16 )
          {
            arg_1 = (unsigned __int8)input_data[byte_1];
            goto func_2;
          }
          goto error;
        }
        arg_1 ^= byte_1;
func_2:
        while ( 1 )
        {
          ip += 3;
          if ( (unsigned __int64)&ip[2LL - (_QWORD)ptr] >= data )
            goto result;
          byte_0 = *ip;
          byte_1 = (unsigned __int8)ip[1];
          bool_1 = (unsigned __int8)*ip <= 0x40u;
          if ( *ip != 64 )
            goto func_1;
func_3:
          LOBYTE(arg_1) = __ROL1__(arg_1, byte_1);
        }
      }
      if ( byte_0 != 80 )
      {
        if ( byte_0 != -1 )
        {
error:
          puts("vm error");
          return 1LL;
        }
result:
        puts("Correct");
        return 0LL;
      }
      if ( (_BYTE)byte_1 == (_BYTE)arg_1 )
        goto func_2;
    }
    puts("Wrong");
  }
  return 1LL;
}
```
Phân tích logic chương trình:

- Đầu tiên, chương trình đọc dữ liệu trong file rồi đưa vào buffer `data` với con trỏ là `ptr`.
- Sau đó yêu cầu nhập dữ liệu từ bàn phím và lưu vào `input_data`. Độ dài là 33 kí tự.
- Vì byte đầu tiên trong file là 0x10 = 16 nên chương trình sẽ nhảy đến dòng 49, và nhảy đến `func_2`.
- Cụm lệnh:
	```c
	if ( (unsigned __int64)&ip[2LL - (_QWORD)ptr] >= data )
            goto result;
	```
	Có nhiệm vụ kiểm tra xem có đọc dữ liệu nằm vượt quá file không (lệnh này dịch ra thực chất là `ip - ptr + 2`, + 2 ý chỉ đến byte cuối cùng của 1 chunk đang xét).

- Tiếp đó, lấy `ip[0]` gán cho `byte 0`, `ip[1]` gán cho `byte 1`. So sánh `byte_0` với 0x40, nếu khác thì nhảy lại về `func_1`, nếu bằng thì đi tiếp xuống dưới.
- `func_1` kiểm tra `byte_0`, nếu bằng 0x30 thì `arg_1 += byte_1`, nếu bằng 0x10 thì `arg_1 = input_data[byte_1]`, còn nếu bằng 0x30 thì `arg_1 ^= byte_1`.
- `func_3` khi `byte_0` = 0x40, byte thấp của `arg_1` sẽ được xoay bit trái đi `byte_1` bước.
- Nếu `byte_0` lớn hơn 0x40 sẽ nhảy ra ngoài và báo lỗi nếu khác 0x50 và 0xff.
- Từ logic trên, ta thấy rằng `byte_0` đóng vai trò như mã lệnh, còn `byte_1` là toán hàng. Ta có  thể xây dựng bảng các lệnh của máy ảo này:

| Mã lệnh | Thực thi                                                  |
| ------- | --------------------------------------------------------- |
| 0x10    | `arg_1 = input_data[byte_1]`                              |
| 0x20    | `arg_1 ^= byte_1`                                         |
| 0x30    | `arg_1 += byte_1`                                         |
| 0x40    | `LOBYTE(arg_1) = __ROL1__(arg_1, byte_1)`                 |
| 0x50    | `if ( (_BYTE)byte_1 == (_BYTE)arg_1 )        goto func_2` |

- Sau khi nhảy ra khỏi vòng lặp, nếu `byte_0` = 0xff (-1) thì sẽ nhảy vào result và in ra correct.
- Bản chất lênh 0x50 như 1 lệnh để check xem kí tự trong chuỗi nhập vào đã đúng chưa.

Từ logic trên, ta xây dựng chương trình giải mã. Ý tưởng như sau:

- Biết `byte_1` nên cũng sẽ biết `arrg_1`.
- Biết `byte_0` nên cũng  sẽ biết được lệnh mà máy ảo thực thi. Ta sẽ viết hàm giãi mã cho từng lệnh. Sau đó với mỗi bộ 3 tham số `byte_0`, `byte_1`, `arg_1` ta sẽ giải ra được chuỗi đầu vào.

Code giải mã:

```python
with open("program.bin", "rb") as f:
    data = f.read()


def ror(d: int, step:int) -> int:
    d &= 0xff
    return 0xff & ((d >> step) | (d << (8 - step)))

flag = [0]*60
for check_ip in range(12, len(data), 15):
    arg_1 = data[check_ip + 1]
    for offset in range (3, -1, -1):
        ip = check_ip - 4*3 + offset * 3
        byte_0 = data[ip]
        byte_1 = data[ip + 1] & 0xff
        if byte_0 == 0x10:
            flag[byte_1] = chr(arg_1 & 0xff)
            print(chr(arg_1), end = "")
        elif byte_0 == 0x20:
            arg_1 ^= byte_1
        elif byte_0 == 0x30:
            arg_1 = (arg_1 - byte_1) & 0xff
        elif byte_0 == 0x40:
            arg_1 = (arg_1 & 0xffffff00) |  ror(arg_1, byte_1)

```
