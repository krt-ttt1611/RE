Đầu tiên, chạy thử chương trình.    
![Pasted image 20260419100745](../../../image/Pasted%20image%2020260419100745.png)    
    
Không có gì đặc biệt.    
Sử dung IDA để phân tích chương trình.    
![Pasted image 20260419100854](../../../image/Pasted%20image%2020260419100854.png)    
    
Dòng 9 đến dòng 12, chương trình yêu cầu nhập chuỗi và xử lí chuỗi đầu vào.    
Dòng 13, ta biết chuỗi nhập cần có độ dài 37.    
Từ dòng 18 trở đi, đây là logic chính của chương trình.    
[__ROL1__](../../__ROL1__.md)    
Ở tham số thứ 2 có 1 hằng số lạ, có thể là magic number, kiểm tra bằng AI.    
![Pasted image 20260419111142](../../../image/Pasted%20image%2020260419111142.png)    
Ngoài ra, phép and 0xfc có tác dụng ép cho 2 bit cuối phải bằng 0. Tóm lại đoạn này có thể biểu diễn bằng công thức toán học.    
$$ v5 mod(5) + 1 $$  
Từ đó, ta có thể biết được 2 tham số trong lệnh xoay bit:    
- Dữ liệu đầu vào là kí tự có index là v5 trong chuỗi cho trước, thực hiện xor với kí tự v3 trong chuỗi nhập vào, sau đó công với v4 xor với 0x37.    
- Số bước xoay là v5 mod(5) + 1.    
Đọc tiếp logic bên dưới, v5 và v3 được tăng 1 sau mỗi vòng lặp, nghĩa là vòng lặp sẽ duyệt từng kí tự trong chuỗi cho trước và chuỗi nhập vào, sau đó thực hiện phép toán trên điều kiện của vòng lặp. v4 được tăng thêm 13 mỗi vòng lặp. Ngoài ra, nếu vòng lặp lặp đủ 37 lần thì sẽ thành công.    
Đây là code giải mã    
```python    
     
array1 = [    
   95,  45, 129, 115, 135, 146,  57, 249,   2, 252,     
  188, 173, 225, 208, 159, 144,  44,  80, 222, 125,     
   56, 148, 175, 159, 180,  54, 175,  40, 203,  24,     
   66,  95, 229,  26,  18, 207,  47, 0    
]    
array2 = [    
   49,  66,  83, 100, 117, 134, 151, 168, 185, 202,     
  219, 236, 253,  14,  31,  48,  65,  82,  99, 116,     
  133, 150, 167, 184, 201, 218, 235, 252,  13,  30,     
   47,  64,  81,  98, 115, 132, 149    
]    
    
    
def ror(data, step):    
   return (data >> step | data << (8-step)) & 0xff #ép dữ liệu của v4 chỉ chưa trong 8 bit bằng bitmask    
    
    
def solve():    
   text = ''    
   for i in range(0, 37):    
      char = array1[i]    
      step = i%5 + 1    
      v4 = (i*13)&0xff    
      char = ror(char, step)    
      char -= v4 ^ 55    
      char ^= array2[i]     
      char &= 0xff    
      text+=chr(char)    
   return text    
    
print(solve())    
```    
Sau khi chạy, ta được chuỗi giải mã là: ISPCLUB{xor_ladders_like_small_steps}. Kiểm tra thử.    
![Pasted image 20260419132911](../../../image/Pasted%20image%2020260419132911.png)    
