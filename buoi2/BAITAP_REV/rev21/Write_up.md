```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  char *input_ptr; // rsi
  unsigned __int8 *arg_ptr; // rdi
  __int64 count_1; // rcx
  char char_0; // r8
  char char_1; // dl
  char char_2; // al
  char char_3; // dl
  char input_data[256]; // [rsp+0h] [rbp-108h] BYREF

  puts("chunk_equations");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    input_data[strcspn(input_data, "\r\n")] = 0;
    if ( strlen(input_data) == 36 )
    {
      input_ptr = input_data;
      arg_ptr = (unsigned __int8 *)&arr_1;
      count_1 = 16LL;
      while ( 1 )
      {
        char_0 = *input_ptr;
        char_1 = input_ptr[1];
        if ( (count_1 ^ (unsigned __int8)(*input_ptr + char_1)) != *arg_ptr )
          break;
        char_2 = input_ptr[2];
        if ( ((count_1 + 16) ^ (unsigned __int8)(char_2 + char_1)) != arg_ptr[1] )
          break;
        char_3 = input_ptr[3];
        if ( ((count_1 + 32) ^ (unsigned __int8)(char_3 + char_2)) != arg_ptr[2]
          || ((count_1 + 48) ^ (unsigned __int8)(char_0 ^ char_3)) != arg_ptr[3]
          || ((count_1 + 64) ^ (unsigned __int8)(char_0 + 2 * char_2)) != arg_ptr[4] )
        {
          break;
        }
        ++count_1;
        input_ptr += 4;
        arg_ptr += 5;
        if ( count_1 == 25 )
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
Logic chương trình:

- Chương trình này sẽ xử lí lần lượt từng cụm (chunk) 4 kí tự đầu vào. Đầu tiên, `char_0` (chính là con trỏ `*input_ptr`) cộng với `char_1` rồi xor `count_1` rồi so sánh với `arg_1` (chính là `*arg_ptr`).
- Tiếp theo, `(char_2 + char_1)` sẽ xor với `count_1 + 16` rồi so sánh với `arg_2` (là `arg_ptr[1]`).
- Cuối cùng, lấy `(char_3 + char_2)` xor với `count_1 + 32` so sánh với arg_3 (`arg_ptr[2]`), lấy `char_0 ^ char_3` xor với `count_1 + 48` rồi so sánh với arg_4 (arg_ptr[3]), lấy `char_0 + 2 * char_2` xor với `count_1 + 64` rồi so sánh với arg_5 (arg_ptr[4]).

Từ logic trên, ta có thể thấy đây là 1 hệ phương trình toán học. Ta sẽ dùng thư viện z3solve để giải mã:

```python
from z3 import *

arr_1 = [
  140, 131, 163,  74, 185, 176, 182, 140, 118, 129,
  217, 255, 209,  79,  31, 217, 231, 229,  89, 102,
  194, 241, 233,  88,   9, 200, 196, 231, 117,   0,
  197, 236, 255,  76, 110, 214, 233, 236, 119,  96,
  214, 246, 200,  86,  17
]

solver = Solver()
flag = [BitVec(f'flag_{i}', 8) for i in range(36)]

for count_1 in range(16,25):
	solver.add((flag[(count_1 - 16)*4] + flag[(count_1 - 16)*4 + 1]) ^ BitVecVal(count_1, 8) == BitVecVal(arr_1[(count_1 - 16) * 5], 8))
	solver.add((flag[(count_1 - 16)*4 + 1] + flag[(count_1 - 16)*4 + 2]) ^ BitVecVal(count_1 + 16, 8) == BitVecVal(arr_1[(count_1 - 16) * 5 + 1], 8))
	solver.add((flag[(count_1 - 16)*4 + 2] + flag[(count_1 - 16)*4 + 3]) ^ BitVecVal(count_1 + 32, 8) == BitVecVal(arr_1[(count_1 - 16) * 5 + 2], 8))
	solver.add((flag[(count_1 - 16)*4] ^ flag[(count_1 - 16)*4 + 3]) ^ BitVecVal(count_1 + 48, 8) == BitVecVal(arr_1[(count_1 - 16)*5 + 3], 8))
	solver.add((flag[(count_1 - 16)*4] + flag[(count_1 - 16)*4 + 2] * 2) ^ BitVecVal(count_1 + 64, 8) == BitVecVal(arr_1[(count_1 - 16)*5 + 4], 8))


text = ''
if solver.check() == sat:
    val = solver.model()
    for i in range(0, 36):
    	char = val[flag[i]].as_long()
    	text += chr(char)

print(text)
```
flag: ISPCLUB{chunk_equations_need_blocks}
