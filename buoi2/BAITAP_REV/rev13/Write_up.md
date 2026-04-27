```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  char *input_ptr; // r10
  __int64 count_24; // r9
  int input_char; // esi
  unsigned int count_27; // edx
  unsigned __int8 v7; // al
  unsigned __int8 bittest_value; // cl
  int v9; // edx
  __int64 step_41; // rsi
  int v11; // edi
  int shr_value; // eax
  char v13; // cl
  char input_data[264]; // [rsp+0h] [rbp-108h] BYREF

  puts("bit_shuffle");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    input_data[strcspn(input_data, "\r\n")] = 0;
    if ( strlen(input_data) == 33 )
    {
      input_ptr = input_data;
      count_24 = 0LL;
      while ( 1 )
      {
        count_27 = 0;
        v7 = 0;


		//loop_1
        do
        {
          input_char = (unsigned __int8)*input_ptr;
          bittest_value = _bittest(&input_char, count_27++);
          v7 = bittest_value | (2 * v7);
        }
        while ( count_27 != 8 );                // --> v7


        v9 = v7;
        step_41 = 0LL;
        v11 = 0;


		//loop_2
        do
        {
          shr_value = v9 >> step_41;
          v13 = arr_1[step_41++];
          v11 |= (shr_value & 1) << v13;
        }
        while ( step_41 != 8 );



		//check
        if ( arr_2[count_24] != (arr_3[count_24] ^ (unsigned __int8)v11) )
          break;


        ++count_24;
        ++input_ptr;
        if ( count_24 == 33 )
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
_ bittest: Kiểm tra bit ở vị trí j của buffer v5 là 0 hay 1.

_Loop_1_: Tạo giá trị cho biến v7 để làm đầu vào cho loop_2.
_Loop_2_: Tạo giá trị cho biến v11 để làm đầu vào cho khối điều kiện check.

arr_2 và arr_3 đã biết --> biết v11 (arr_2[count_24] ^ arr_3[count_24])

Ở _loop2_, ta thấy v11 có được bằng cách ghép từng bit cuối của giá trị shr_value vào vị trí cho trước bởi arr[1] --> Bảo toàn dữ liệu, có thể tính được shr_value.

Với từng giá trị của shr_value, dịch trái đi step_41 rồi ghép lại với nhau, ta sẽ tính được v9, nghĩa là tìm được v7.

Ở _loop1_, ta thấy v7 có được bằng cách ghép từng bit trong từng byte (chính là từng ký tự của chuỗi đầu vào), sở dĩ có thể nói như vậy vì phép nhân 2 thực chất chính là dịch trái 1 bit. Vì thế, nếu biết v7 ta có thể giải được flag.

code giải mã:
```python


arr_1 = [
    5,   2,   7,   0,   6,   1,   4,   3,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0
]

arr_2 = [
  221, 131, 174, 164, 131, 221, 203,  49, 109, 202, 
  148, 127, 168, 252, 203, 130, 239, 243,  36,  70, 
   25, 126,  33, 227,  13,   8,  45, 126,  98, 212, 
  130, 248, 254,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 
    0,   0,   0,   0
]

arr_3 = [
  145, 158, 171, 184, 197, 210, 223, 236, 249,   6, 
   19,  32,  45,  58,  71,  84,  97, 110, 123, 136, 
  149, 162, 175, 188, 201, 214, 227, 240, 253,  10, 
   23,  36,  49
]

text = ''


def reverse(data:int) -> int:
  value = 0
  i = 0
  while (1):
    value |= (data & 1)
    i += 1
    if (i == 8):
      break
    value <<= 1
    data >>= 1
  return value 

for count_24 in range (0, 33):
  v11 = arr_2[count_24] ^ arr_3[count_24]
  #--> v11
  print("v11: ", v11)


  v9 = 0
  for step_41 in range(0, 8):
    v13 = arr_1[step_41]
    shr_value = v11 >> v13
    v9 |= (shr_value & 1) << step_41
  #--> v9
  print("v9: ", v9)
  


  v7 = v9
  char = reverse(v7)
  print(char)
  text += chr(char)

print(text)

```
Flag là: ISPCLUB{bit_planes_make_homework}


