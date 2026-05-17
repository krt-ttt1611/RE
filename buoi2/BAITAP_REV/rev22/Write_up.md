```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  size_t input_data_len; // rsi
  char *input_ptr; // rcx
  __int64 count_1; // rdx
  __int64 char_1; // rax
  __int64 v8; // rcx
  __int64 v9; // rdx
  char input_data[264]; // [rsp+0h] [rbp-108h] BYREF

  puts("opaque_gate");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    input_data[strcspn(input_data, "\r\n")] = 0;
    input_data_len = strlen(input_data);
    if ( (((_BYTE)input_data_len * ((_BYTE)input_data_len + 1)) & 1) == 0 )
      goto LABEL_3;
    char_1 = (unsigned __int8)input_data[0];
    if ( !input_data[0] )
      goto LABEL_3;
    v8 = 0LL;
    v9 = 0LL;
    do
    {
      v8 += ++v9 * char_1;
      char_1 = (unsigned __int8)input_data[v9];
    }
    while ( (_BYTE)char_1 );
    if ( v8 != 3735928559LL )
    {
LABEL_3:
      if ( input_data_len == 42 )
      {
        input_ptr = input_data;
        count_1 = 0LL;
        while ( arr_1[count_1] == __ROR1__(arr_2[count_1] ^ *input_ptr, 3) + (_BYTE)count_1 + 34 )
        {
          ++count_1;
          ++input_ptr;
          if ( count_1 == 42 )
          {
            puts("Correct");
            return 0LL;
          }
        }
      }
    }
    puts("Wrong");
  }
  return 1LL;
}
```
Đoạn code phía trước dòng 31 là làm rối, logic kiểm tra thật sự nằm phía dưới `LABLE_3` (trace thử là biết).

Code giải mã:
```python
arr_1 = [
    7, 234, 168,  44, 255, 194, 130, 198, 104, 229, 
  229, 133,  39, 195,  34,  40, 198,  74,  68, 133, 
  104,  74, 198, 133, 233, 132, 235, 103,  39,  12, 
  169, 170,  38, 136, 106, 197, 136, 170,  43,  41, 
  235, 106,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0
]
arr_2 = [
  102, 109, 116, 123, 130, 137, 144, 151, 158, 165, 
  172, 179, 186, 193, 200, 207, 214, 221, 228, 235, 
  242, 249,   0,   7,  14,  21,  28,  35,  42,  49, 
   56,  63,  70,  77,  84,  91,  98, 105, 112, 119, 
  126, 133
]


def ror(data: int, step: int) -> int:
  data &= 0xff
  return (data >> (8 - step)) | ((data << (step)) & 0xff)


flag = ''
for count_1 in range(0, 42):
  char =  ror(arr_1[count_1] - count_1 - 34, 3) ^ arr_2[count_1]
  flag += chr(char)

print(flag)
```
flag: ISPCLUB{opaque_predicates_are_stage_props}