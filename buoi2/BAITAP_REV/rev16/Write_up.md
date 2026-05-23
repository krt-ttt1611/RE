![](Pasted%20image%2020260511163216.png)
```c
//main
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  _DWORD *arg_1; // rdi
  char *input_ptr; // r8
  int count_1; // r10d
  __int64 count_2; // r9
  __int64 count_3; // rcx
  int v8; // edx
  __int16 out_func_1; // ax
  int out_func_2; // eax
  char input_data[264]; // [rsp+0h] [rbp-108h] BYREF

  puts("matrix_mask");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    input_data[strcspn(input_data, "\r\n")] = 0;
    if ( strlen(input_data) == 40 )
    {
      arg_1 = &arr_1;
      input_ptr = input_data;
      count_1 = 0;
      count_2 = 0LL;
      while ( 1 )
      {
        count_3 = 0LL;
        v8 = 0;
        do
        {
          out_func_1 = ((unsigned int)(*(_DWORD *)input_ptr & arg_1[count_3]) >> 16) ^ *(_DWORD *)input_ptr & LOWORD(arg_1[count_3]);
          out_func_2 = !__SETP__(HIBYTE(out_func_1) ^ out_func_1, 0) << count_3++;
          v8 |= out_func_2;
        }
        while ( count_3 != 32 );
        if ( *(_DWORD *)((char *)&arr_2 + count_2) != (count_1 ^ v8 ^ 2779096485) )
          break;
        count_2 += 4LL;
        count_1 += 286331153;
        arg_1 += 32;
        input_ptr += 4;
        if ( count_2 == 40 )
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
__ SETP__(x, y): set parity, đếm số lượng bit 1 của phép x - y, nếu chẵn thì trả về 1, ngược lại thì 0 (hay nói cách khác là lấy từng bit dữ liệu xor với nhau). Ngoài ra , cụm dữ liệu sẽ bị ép xuống 8 bit (nhằm mục đích mô phỏng thanh ghi PF).

_Type Punning_: Là kỹ thuật thao tác với vùng nhớ, hiểu đơn giản là "đọc 1 đoạn dữ liệu kiểu X và diễn giải nó như là kiểu Y". Trong bài này, kỹ thuật type punning ở đây đó là thông qua việc ép kiểu con trỏ rồi giải tham chiếu, từ đó có thể lấy được từng cụm 4 bytes dữ liệu (dòng 36). Cụ thể:

- Đầu tiên, ép kiểu con trỏ char để lợi dụng, quy luật Pointer Arithmetic, nếu ép kiểu nào thì khi cộng, giá trị cộng thêm sẽ được nhân với kích thước của kiểu dữ liệu đó. Do char có kích thước là 1 byte, việc này giúp con trỏ trượt đi chính xác từng byte một trong bộ nhớ (ví dụ: cộng thêm count_2 sẽ trượt đúng  count_2 bytes) để dừng đúng tại tọa độ cần tìm mà không bị nhảy cóc sai vị trí (ví dụ như nếu thay vì ép kiểu char mà ép là word, thì 1 lần nó sẽ dịch đi count_2 word, là count_2 * 4 bytes).
- Tiếp theo, mở rộng kích thước đọc: Sau khi trượt đến đúng vị trí, ta tiếp tục ép kiểu con trỏ đó lên thành (_ DWORD * ). Việc này giúp thay đổi "thước đo" của CPU tại vị trí đó từ 1 byte lên thành 4 bytes (kích thước của 1 DWORD).
- Cuối cùng, giải tham chiếu để lấy khối dữ liệu 1 dword (4 bytes).

Logic của chương trình như sau:

- Đầu tiên là khối do - while chạy từ dòng 29 đến dòng 35:
	- Dòng 31 thưc chất là lấy 4 bytes liên tiếp trong chuỗi đầu vào, and với từng bộ dword trong mảng arr_1 (có con trỏ là arg_1), sau đó ép về 4 byte, rồi lấy 2 byte cao xor với 2 byte thấp. Kết quả ra được 1 word, đưa vào out_func_1
	- Dòng 32, do tính chất ép về 8 bit của lệnh _ SETP_, nên có thể hiểu là ép tiếp out_func_1 về 8 bit bằng cách xor 8 bit cao 8 bit thấp. Sau đó xor tất cả các bit lại với nhau, rồi dịch phải đi count_3 bit. Kết hợp với việc v8 = v8 or với out_func_2, ta có thể biết rằng v8 chính là các out_func_2 ghép lại.
- Tiếp đến là khối if ở dòng 36, lấy lần lượt 4 byte trong mảng arr_2, kiểm tra xem có bằng count_1 ^ v8 ^ 2779096485 không.

Từ logic trên, ta sẽ viết code giải mã.
```python
from z3 import *
arr_1 = [
  137,   8,   0,   0,  18,   1,   0,   0,  36,   2, 
    0,   0,  72,  68,   0,   0, 144,   8,   0,   0, 
   32,  17,   0,   0,  64,  34,   2,   0, 128,  68, 
    0,   0,   0, 137,   0,   0,   0,  18,  17,   0, 
    0,  36,   2,   0,   0,  72,   4,   0,   0, 144, 
  136,   0,   0,  32,  17,   0,   0,  64,  34,   0, 
    0, 128,  68,   4,   0,   0, 137,   0,   0,   0, 
   18,   1,   0,   0,  36,  34,   0,   0,  72,   4, 
    0,   0, 144,   8,   0,   0,  32,  17,   0,   0, 
   64,  34,   0,   0, 128,  68,   0,   0,   0, 137, 
    0,   0,   0,  18,   0,   0,   0,  36,   0,   0, 
    0,  72,   0,   0,   0, 144,   0,   0,   0,  32, 
    0,   0,   0,  64,   0,   0,   0, 128,   9,   9, 
    0,   0,  18,   2,   0,   0,  36,   4,   0,   0, 
   72,  72,   0,   0, 144,  16,   0,   0,  32,  33, 
    0,   0,  64,  66,   2,   0, 128, 132,   0,   0, 
    0,   9,   1,   0,   0,  18,  18,   0,   0,  36, 
    4,   0,   0,  72,   8,   0,   0, 144, 144,   0, 
    0,  32,  33,   0,   0,  64,  66,   0,   0, 128, 
  132,   4,   0,   0,   9,   1,   0,   0,  18,   2, 
    0,   0,  36,  36,   0,   0,  72,   8,   0,   0, 
  144,  16,   0,   0,  32,  33,   0,   0,  64,  66, 
    0,   0, 128, 132,   0,   0,   0,   9,   0,   0, 
    0,  18,   0,   0,   0,  36,   0,   0,   0,  72, 
    0,   0,   0, 144,   0,   0,   0,  32,   0,   0, 
    0,  64,   0,   0,   0, 128,   9,  10,   0,   0, 
   18,   4,   0,   0,  36,   8,   0,   0,  72,  80, 
    0,   0, 144,  32,   0,   0,  32,  65,   0,   0, 
   64, 130,   2,   0, 128,   4,   1,   0,   0,   9, 
    2,   0,   0,  18,  20,   0,   0,  36,   8,   0, 
    0,  72,  16,   0,   0, 144, 160,   0,   0,  32, 
   65,   0,   0,  64, 130,   0,   0, 128,   4,   5, 
    0,   0,   9,   2,   0,   0,  18,   4,   0,   0, 
   36,  40,   0,   0,  72,  16,   0,   0, 144,  32, 
    0,   0,  32,  65,   0,   0,  64, 130,   0,   0, 
  128,   4,   0,   0,   0,   9,   0,   0,   0,  18, 
    0,   0,   0,  36,   0,   0,   0,  72,   0,   0, 
    0, 144,   0,   0,   0,  32,   0,   0,   0,  64, 
    0,   0,   0, 128, 137,   8,   0,   0,  18,   1, 
    0,   0,  36,   2,   0,   0,  72,  68,   0,   0, 
  144,   8,   0,   0,  32,  17,   0,   0,  64,  34, 
    2,   0, 128,  68,   0,   0,   0, 137,   0,   0, 
    0,  18,  17,   0,   0,  36,   2,   0,   0,  72, 
    4,   0,   0, 144, 136,   0,   0,  32,  17,   0, 
    0,  64,  34,   0,   0, 128,  68,   4,   0,   0, 
  137,   0,   0,   0,  18,   1,   0,   0,  36,  34, 
    0,   0,  72,   4,   0,   0, 144,   8,   0,   0, 
   32,  17,   0,   0,  64,  34,   0,   0, 128,  68, 
    0,   0,   0, 137,   0,   0,   0,  18,   0,   0, 
    0,  36,   0,   0,   0,  72,   0,   0,   0, 144, 
    0,   0,   0,  32,   0,   0,   0,  64,   0,   0, 
    0, 128,   9,   9,   0,   0,  18,   2,   0,   0, 
   36,   4,   0,   0,  72,  72,   0,   0, 144,  16, 
    0,   0,  32,  33,   0,   0,  64,  66,   2,   0, 
  128, 132,   0,   0,   0,   9,   1,   0,   0,  18, 
   18,   0,   0,  36,   4,   0,   0,  72,   8,   0, 
    0, 144, 144,   0,   0,  32,  33,   0,   0,  64, 
   66,   0,   0, 128, 132,   4,   0,   0,   9,   1, 
    0,   0,  18,   2,   0,   0,  36,  36,   0,   0, 
   72,   8,   0,   0, 144,  16,   0,   0,  32,  33, 
    0,   0,  64,  66,   0,   0, 128, 132,   0,   0, 
    0,   9,   0,   0,   0,  18,   0,   0,   0,  36, 
    0,   0,   0,  72,   0,   0,   0, 144,   0,   0, 
    0,  32,   0,   0,   0,  64,   0,   0,   0, 128, 
    9,  10,   0,   0,  18,   4,   0,   0,  36,   8, 
    0,   0,  72,  80,   0,   0, 144,  32,   0,   0, 
   32,  65,   0,   0,  64, 130,   2,   0, 128,   4, 
    1,   0,   0,   9,   2,   0,   0,  18,  20,   0, 
    0,  36,   8,   0,   0,  72,  16,   0,   0, 144, 
  160,   0,   0,  32,  65,   0,   0,  64, 130,   0, 
    0, 128,   4,   5,   0,   0,   9,   2,   0,   0, 
   18,   4,   0,   0,  36,  40,   0,   0,  72,  16, 
    0,   0, 144,  32,   0,   0,  32,  65,   0,   0, 
   64, 130,   0,   0, 128,   4,   0,   0,   0,   9, 
    0,   0,   0,  18,   0,   0,   0,  36,   0,   0, 
    0,  72,   0,   0,   0, 144,   0,   0,   0,  32, 
    0,   0,   0,  64,   0,   0,   0, 128, 137,   8, 
    0,   0,  18,   1,   0,   0,  36,   2,   0,   0, 
   72,  68,   0,   0, 144,   8,   0,   0,  32,  17, 
    0,   0,  64,  34,   2,   0, 128,  68,   0,   0, 
    0, 137,   0,   0,   0,  18,  17,   0,   0,  36, 
    2,   0,   0,  72,   4,   0,   0, 144, 136,   0, 
    0,  32,  17,   0,   0,  64,  34,   0,   0, 128, 
   68,   4,   0,   0, 137,   0,   0,   0,  18,   1, 
    0,   0,  36,  34,   0,   0,  72,   4,   0,   0, 
  144,   8,   0,   0,  32,  17,   0,   0,  64,  34, 
    0,   0, 128,  68,   0,   0,   0, 137,   0,   0, 
    0,  18,   0,   0,   0,  36,   0,   0,   0,  72, 
    0,   0,   0, 144,   0,   0,   0,  32,   0,   0, 
    0,  64,   0,   0,   0, 128,   9,   9,   0,   0, 
   18,   2,   0,   0,  36,   4,   0,   0,  72,  72, 
    0,   0, 144,  16,   0,   0,  32,  33,   0,   0, 
   64,  66,   2,   0, 128, 132,   0,   0,   0,   9, 
    1,   0,   0,  18,  18,   0,   0,  36,   4,   0, 
    0,  72,   8,   0,   0, 144, 144,   0,   0,  32, 
   33,   0,   0,  64,  66,   0,   0, 128, 132,   4, 
    0,   0,   9,   1,   0,   0,  18,   2,   0,   0, 
   36,  36,   0,   0,  72,   8,   0,   0, 144,  16, 
    0,   0,  32,  33,   0,   0,  64,  66,   0,   0, 
  128, 132,   0,   0,   0,   9,   0,   0,   0,  18, 
    0,   0,   0,  36,   0,   0,   0,  72,   0,   0, 
    0, 144,   0,   0,   0,  32,   0,   0,   0,  64, 
    0,   0,   0, 128,   9,  10,   0,   0,  18,   4, 
    0,   0,  36,   8,   0,   0,  72,  80,   0,   0, 
  144,  32,   0,   0,  32,  65,   0,   0,  64, 130, 
    2,   0, 128,   4,   1,   0,   0,   9,   2,   0, 
    0,  18,  20,   0,   0,  36,   8,   0,   0,  72, 
   16,   0,   0, 144, 160,   0,   0,  32,  65,   0, 
    0,  64, 130,   0,   0, 128,   4,   5,   0,   0, 
    9,   2,   0,   0,  18,   4,   0,   0,  36,  40, 
    0,   0,  72,  16,   0,   0, 144,  32,   0,   0, 
   32,  65,   0,   0,  64, 130,   0,   0, 128,   4, 
    0,   0,   0,   9,   0,   0,   0,  18,   0,   0, 
    0,  36,   0,   0,   0,  72,   0,   0,   0, 144, 
    0,   0,   0,  32,   0,   0,   0,  64,   0,   0, 
    0, 128, 137,   8,   0,   0,  18,   1,   0,   0, 
   36,   2,   0,   0,  72,  68,   0,   0, 144,   8, 
    0,   0,  32,  17,   0,   0,  64,  34,   2,   0, 
  128,  68,   0,   0,   0, 137,   0,   0,   0,  18, 
   17,   0,   0,  36,   2,   0,   0,  72,   4,   0, 
    0, 144, 136,   0,   0,  32,  17,   0,   0,  64, 
   34,   0,   0, 128,  68,   4,   0,   0, 137,   0, 
    0,   0,  18,   1,   0,   0,  36,  34,   0,   0, 
   72,   4,   0,   0, 144,   8,   0,   0,  32,  17, 
    0,   0,  64,  34,   0,   0, 128,  68,   0,   0, 
    0, 137,   0,   0,   0,  18,   0,   0,   0,  36, 
    0,   0,   0,  72,   0,   0,   0, 144,   0,   0, 
    0,  32,   0,   0,   0,  64,   0,   0,   0, 128
 ]

arr_2 = [
   43,  94,  25, 238,  76, 233, 225, 192,  87, 182, 
  124, 211,  28, 145,  76, 234, 180, 171, 124, 129, 
  193, 234, 206, 141, 198, 208, 191, 160, 178,  15, 
   17, 134,  63, 159, 208,  68, 254,  34,  15,  78, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0 
]




def byte_to_dword_arr_2(count: int) -> int:
  data = 0
  for i in range(count, count + 4):
    data |= arr_2[i] << ((i % 4)*8)
  return data
def byte_to_dword_arr_1(count: int) -> int:
  data = 0
  for i in range(count, count + 4):
    data |= arr_1[i] << ((i % 4)*8)
  return data

text = ''
for count in range(0, 10):
  count_1 = 286331153 * count
  count_2 = 4 * count
  v8 = byte_to_dword_arr_2(count_2) ^  2779096485 ^ count_1
  solver = Solver()
  data = BitVec('data', 32)
  for count_3 in range(0, 32):
    out_func_1 = BitVecVal(byte_to_dword_arr_1(count*128 + count_3*4), 32)
    out_func_1 &= data
    out_func_1 = (LShR(out_func_1, 16) ^ out_func_1) & BitVecVal(0xffff, 32)
    out_func_2 = BitVecVal(0, 1)
    for i in range(0, 16):
      bit = Extract(i, i, out_func_1)
      out_func_2 ^= bit
    out_func_2 = out_func_2
    bit_check = Extract(count_3, count_3, BitVecVal(v8, 32))
    solver.add(out_func_2 == bit_check)
#đoạn này bí quá r nên gemini :((
  for byte_pos in range(4):
      b = Extract(byte_pos*8 + 7, byte_pos*8, data)
      solver.add(b >= 0x20, b <= 0x7E)   # printable ASCII

  if solver.check() == sat:
      val = solver.model()[data].as_long()
      import struct
      chunk = struct.pack('<I', val).decode()
      text += chunk
      print(f"Chunk {count}: '{chunk}'")
  else:
      print(f"Chunk {count}: UNSAT")

print(f"\nFlag: {text}")
```
Flag: ISPCLUB{gf2_matrix_means_linear_algebra}
