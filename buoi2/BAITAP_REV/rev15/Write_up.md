```c
//main
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  __int64 v3; // rbx
  __int64 v4; // rdx
  __int64 v5; // rcx
  __int64 v6; // r8
  __int64 v7; // r9
  __m128i v9; // [rsp+0h] [rbp-138h]
  __m128i v10; // [rsp+10h] [rbp-128h]
  char s[280]; // [rsp+20h] [rbp-118h] BYREF

  v9 = _mm_unpacklo_epi64(_mm_loadl_epi64((const __m128i *)&off_3DD0), (__m128i)(unsigned __int64)sub_12A0);
  v10 = _mm_unpacklo_epi64(_mm_loadl_epi64((const __m128i *)&off_3DD8), (__m128i)(unsigned __int64)sub_12C0);
  puts("dispatch_garden");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(s, 256, stdin) )
  {
    v3 = 0LL;
    s[strcspn(s, "\r\n")] = 0;
    if ( strlen(s) == 42 )
    {
      while ( ((unsigned __int8 (__fastcall *)(_QWORD, __int64, __int64, __int64, __int64, __int64, __int64, __int64, __int64, __int64))v9.m128i_i64[v3 & 3])(
                (unsigned __int8)s[v3],
                v3,
                v4,
                v5,
                v6,
                v7,
                v9.m128i_i64[0],
                v9.m128i_i64[1],
                v10.m128i_i64[0],
                v10.m128i_i64[1]) == byte_2040[v3] )
      {
        if ( ++v3 == 42 )
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
Chương trình này cấu trúc khác hẳn các chương trình trong câu trước. 
- Lệnh __ mm_unpacklo_epi64() là 1 lệnh thuộc nhóm tập lệnh sse2, nhóm tập lệnh này sẽ thao tác với các thanh ghi 128-bit từ xmm0 đến xmm15. Nhiệm vụ lệnh này là lấy 2 64bit thấp của 2 vùng nhớ ghép lại với nhau bằng thanh ghi xmm rồi đẩy vào stack.
- _ mm_loadl_epi64 là lệnh thuộc nhóm sse2, nó sẽ lấy dữ liệu trong 1 vùng nhớ, đưa 64 bit thấp vào thanh ghi xmm 128bit nào đó, 64 bit cao được set về 0.
- const __ m128i là kiểu dữ liệu 128bit, const để cho dữ liệu này không bị sửa đổi.
- sub_ (subroutine): Đây là nhãn của 1 hàm chưa có tên.
Nhảy vào 2 hàm SUB12A0 và SUB12C0 để kiểm tra.
```cpp
//SUB_12A0
char __fastcall sub_12A0(char a1, char a2)
{
  return __ROL1__(a1 + a2 + 23, 2);
}

//SUB_12C0
char __fastcall sub_12C0(char a1, char a2)
{
  return __ROL1__(a1 - 17 - a2, 4);
}
```
 2 hàm mã hóa bằng phép xoay bit với đầu vào là 2 kí tự a1, a2. Đổi tên thành ROL_1 và ROL_2.
Tiếp tục kiểm tra thử 2 địa chỉ &off_3DD0 và &off_3DD8. Nó nhảy đến 1 giao diện mới gọi là disassembly listing: Bảng này liệt kê tất cả nội dung của file binary sau khi được dịch ngược. Gồm code, data và metadata.
![](../../../ảnh/Pasted%20image%2020260501154451.png)
1 dòng sẽ gồm các thành phần chính:
- Tên sections: 1 file được cấu trúc thành nhiều sections khác nhau. Cụ thể:
	- .text: phần này chứa code, các instruction thực thi.
	- .data: chứa các biến toàn cục và các biến tĩnh đã được khởi tạo giá trị cụ thể.
	- .bss (block started by symbol): chứa các biến toàn cục, biến tĩnh chưa khởi tạo, hoặc khởi tạo bằng 0.
	- .ro: chứa dữ liệu chỉ đọc.
	- .rel (relocation): tái định vị, nghĩa là mỗi khi chương trình nạp vào ram thì sẽ được hệ điều hành cấp địa chỉ mới.
	- Ngoài ra còn nhiều phần khác, nhưng sẽ tìm hiểu thêm.
- Địa chỉ: Ở đây là địa chỉ offset so với địa chỉ bắt đầu của chương trình (0x0). Do cơ chế PIE (Position independent executable - file thực thi không phụ thuộc vào vị trí), tức là mỗi khi chương trình bắt đầu thì nó sẽ được đặt vào 1 địa chỉ mới, nên dữ liệu trong chương trinh không được đặt theo địa chỉ vật lý mà chỉ đặt theo địa chỉ offset. Việc này giúp bảo vệ chương trình (ASLR).
- Cuối cùng là symbol, data và comment.
- Loc (location): nhãn/địa chỉ đến một vị trí bên trong code.
Nhảy vào loc_1290 và loc_12B0 để kiểm tra.
```nasm
;loc_1290
loc_1290:                               ; DATA XREF: .data.rel.ro:off_3DD0↓o
.text:0000000000001290 ; __unwind {
.text:0000000000001290                 lea     eax, [rsi+rsi*4+22h]
.text:0000000000001294                 xor     eax, edi
.text:0000000000001296                 retn
.text:0000000000001296 ; } // starts at 1290

;loc12B0
loc_12B0:                               ; DATA XREF: .data.rel.ro:off_3DD8↓o
.text:00000000000012B0 ; __unwind {
.text:00000000000012B0                 xor     edi, 0FFFFFF9Dh
.text:00000000000012B3                 ror     dil, 3
.text:00000000000012B7                 mov     eax, edi
.text:00000000000012B9                 xor     eax, esi
.text:00000000000012BB                 retn
.text:00000000000012BB ; } // starts at 12B0

```
Ở loc_1290, lệnh lea thực chất là lấy kết quả của phép tính 5 * rsi + 22h lưu vào eax. Sau đó eax sẽ được xor với edi.
Ở LOC_12b0, edi được xor với 0xffffff9d, sau đó dil (8 bit thấp nhất của edi) được xoay phải với step = 3. Sau đó dữ liệu trong edi được copy sang eax rồi đem xor với esi.
Nhớ lại rằng, hàm linux dùng 1 calling convention duy nhất là system V AMD64 ABI, trong đó 6 tham số đầu truyền lần lượt vào rdi, rsi, rdx, rcx, r8, r9 nên thực chất rsi, rdi ở đây chính là tham số truyền vào. Vậy nên khả năng cao 2 cụm loc này phải là 2 hàm, ida thực chất đã dịch sai. bấm p để chuyển lại từ loc thành sub.
```c
//sub_12B0
__int64 __fastcall sub_12B0(int a1, int a2)
{
  unsigned int v2; // edi

  v2 = a1 ^ 0xFFFFFF9D;
  LOBYTE(v2) = __ROR1__(v2, 3);
  return a2 ^ v2;
}

//sub_1290
__int64 __fastcall sub_1290(int a1, int a2)
{
  return a1 ^ (unsigned int)(5 * a2 + 34);
}
```
Từ đây, ta có thể hiểu được hai lệnh ở dòng 13 và 14, thực chất mỗi thanh ghi xmm đang lưu 2 địa chỉ hàm. Khi trỏ tới thanh ghi bằng chỉ số giống như array thì sẽ hàm sẽ được gọi (xem dòng 23).
1 chi tiết rất đặc biệt có thể thấy ở đoạn gọi địa chỉ hàm:
```c
v9.m128i_i64[v3 & 3]
```
Việc sử dụng bitmask với 3, giúp các giá trị sẽ chạy theo vòng lặp từ 0 đến 3. Tại sao lại như vậy? Ta biết rằng các địa chỉ lệnh sẽ được gọi bằng chỉ số như array. Tuy nhiên v9 chỉ lưu 2 giá trị, nên khi gọi đến 2 và 3 sẽ bị tràn ra các ô nhớ bên cạnh. Nhưng ở đây, v9 và v10 ở 2 vị trí liền kề nhau, nên khi bị tràn, nó sẽ trỏ đến 2 địa chỉ trong v10.
Ở dòng 23, ta thấy từng địa chỉ hàm đang được gọi, với từng kí tự của chuỗi đầu vào (s[v3]) là tham số thứ nhất, biến đếm (v3) là tham số thứ 2... Theo calling convention, ta sẽ biết được s[v3] chính là rdi, v3 là rsi. Như đã check bên trên thì các hàm chỉ sử dụng đúng 2 tham số đầu, lí do mà IDA liệt kê nhiều tham số là do khi gọi hàm từ 1 pointer, CPU không biết hàm nhận bao nhiêu tham số, nên cứ liệt kê ra như vậy cho chắc.

Từ những thông tin trên, ta có thể đổi tên các biến lại như sau.
```c
//main
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  __int64 count_1; // rbx
  __int64 v4; // rdx
  __int64 v5; // rcx
  __int64 v6; // r8
  __int64 v7; // r9
  __m128i func_ptr_1; // [rsp+0h] [rbp-138h]
  __m128i func_ptr_2; // [rsp+10h] [rbp-128h]
  char input_data[280]; // [rsp+20h] [rbp-118h] BYREF

  func_ptr_1 = _mm_unpacklo_epi64(_mm_loadl_epi64((const __m128i *)&addr_func_1), (__m128i)(unsigned __int64)func_2);
  func_ptr_2 = _mm_unpacklo_epi64(_mm_loadl_epi64((const __m128i *)&addr_func_3), (__m128i)(unsigned __int64)func_4);
  puts("dispatch_garden");
  fwrite("flag> ", 1uLL, 6uLL, stdout);
  if ( fgets(input_data, 256, stdin) )
  {
    count_1 = 0LL;
    input_data[strcspn(input_data, "\r\n")] = 0;
    if ( strlen(input_data) == 42 )
    {
      while ( ((unsigned __int8 (__fastcall *)(_QWORD, __int64, __int64, __int64, __int64, __int64, __int64, __int64, __int64, __int64))func_ptr_1.m128i_i64[count_1 & 3])(
                (unsigned __int8)input_data[count_1],
                count_1,
                v4,
                v5,
                v6,
                v7,
                func_ptr_1.m128i_i64[0],
                func_ptr_1.m128i_i64[1],
                func_ptr_2.m128i_i64[0],
                func_ptr_2.m128i_i64[1]) == arr_1[count_1] )
      {
        if ( ++count_1 == 42 )
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
Và 4 function có tác dụng xáo trộn dữ liệu.
```c
//func_1
__int64 __fastcall func_1(int input_char, int count_1)
{
  return input_char ^ (unsigned int)(5 * count_1 + 34);
}

//func_2
char __fastcall func_2(char input_char, char count_1)
{
  return __ROL1__(input_char + count_1 + 23, 2);
}

//func_3
__int64 __fastcall func_3(int input_char, int count_1)
{
  unsigned int v2; // edi
  
  v2 = input_char ^ 0xFFFFFF9D;
  LOBYTE(v2) = __ROR1__(v2, 3);
  return count_1 ^ v2;
}

//func_4
char __fastcall func_4(char input_char, char count_1)
{
  return __ROL1__(input_char - 17 - count_1, 4);
}
```
Ý tưởng của thuật toán giải mã đó là: Ta sẽ viết từng hàm giải mã cho các hàm từ func_1 đến func_4, rồi cho chạy 1 vòng for duyệt từng kí tự trong arr_1, với mỗi cặp arr_1[count_i] với i, ta sẽ chọn ra hàm giải mã của cặp đó rồi giải mã ra kí tự. Kết hợp tất cả các kí tự lại để có flag.

Code giải mã:
```python
arr_1 = [
  107, 173, 187, 242, 122, 197, 253,  54,  46,  38, 
  215,  69,  63,  98, 209, 132,  45, 114, 141, 227, 
  234,  70, 203, 115, 249, 126, 100, 163, 219, 158, 
    1, 242, 160, 118, 125,  83, 184, 170,  57, 163, 
  153, 246
]

def ror(data: int, step: int) -> int:
  data &= 0xff
  return 0xff & (data << (8 - step)) | (data >> (step))

def rol(data: int, step: int) -> int:
  data &= 0xff
  return 0xff & (data << step) | (data >> (8-step))

def func_1(char: int, count: int) -> int:
  return 0xff & (char ^ (5 * count + 34))

def func_2(char: int, count: int) -> int:
  return 0xff & (ror(char, 2) - 23 - count)

def func_3(char: int, count: int) -> int:
  return 0xff & (rol(char ^ count, 3) ^ 0xffffff9d)

def func_4(char: int, count: int) -> int:
  return 0xff & (ror(char, 4) + count + 17)


text = ''
char = 0;
for count_1 in range(0, 42):
  step = count_1 % 4
  if step == 0:
    char = func_1(arr_1[count_1], count_1)
  elif step == 1:
    char = func_2(arr_1[count_1], count_1)
  elif step == 2:
    char = func_3(arr_1[count_1], count_1)
  else:
    char = func_4(arr_1[count_1], count_1)
  text += chr(char)

print(text)
```
flag là: ISPCLUB{dispatch_tables_confuse_beginners}
