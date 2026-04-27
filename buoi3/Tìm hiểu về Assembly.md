Assembly là ngôn ngữ lập trình bậc thấp được thiết kế để giao tiếp trực tiếp với phần cứng máy tính. Nó là một dạng ngôn ngữ dễ đọc hơn so với mã máy (mã nhị phân) nhưng vẫn tương ứng một-một với các lệnh CPU. Lý do tồn tại của Assembly là vì nó cho phép lập trình viên kiểm soát chi tiết các hoạt động của phần cứng, tối ưu hóa hiệu suất và quản lý tài nguyên trực tiếp. Trong bài này chỉ tập trung viết về hợp ngữ sử dụng cú pháp của intel và kiến trúc x86-64.

***1. Tập lệnh.***
Kiến trúc x86 sử dụng tập lệnh CISC (single instruction, multiple data). CPU sử dụng một bộ giải mã, phân tách câu lệnh phức tạp thành các vi lệnh đơn giản hơn. Việc này giúp CPU có thể thực hiện được nhiều việc chỉ trong 1 câu lệnh.

***2. Thanh ghi.***
Phần này chỉ giới thiệu các thanh ghi cơ bản.
a) Thanh ghi đa dụng: Các thanh ghi này lưu được cả dữ liệu và địa chỉ.
- Các thanh ghi: RAX, RBX, RCX, RDX, RSI, RDI, R8-R15, RSP, RBP.
- Cấu trúc:1 thanh ghi có độ lớn 64 bit sẽ được chia thành 2 phần, 32 bit cao và 32 bit thấp. 32 bit thấp được coi là 1 thanh ghi khác (tiền tố E), và cũng được chia đôi thành 2 phần 16 bit. 16 bit thấp tiếp tục được chia thành 2 phần, 8 bit cao (h) và 8 bit thấp (l)![](../ảnh/Pasted%20image%2020260419223333.png)
- Một số tác dụng đặc biệt:
	- RSP luôn trỏ về đỉnh stack, RBP trỏ về đáy của khung stack.
	- 
b) Thanh ghi con trỏ lệnh RIP: luôn trỏ đến địa chỉ lệnh tiếp theo được thực thi.
c) Thanh ghi cờ RFLAGS: Lưu các cờ trạng thái của CPU.
- Một số cờ trạng thái phổ biến của CPU:
	- CF (carry flag): tràn số không dấu.
	- ZF (zero flag): kết quả phép toán bằng 0.
	- SF (sign flag): kết quả âm.
	- OF (overflow flag): tràn số có dấu.

***3. Kiểu dữ liệu***
Một số kiểu dữ liệu phổ biến.

| BYTE             | 1 byte |
| ---------------- | ------ |
| WORD             | 2 byte |
| DWORD            | 4 byte |
| QWORD            | 8 byte |
| int8_t/uint8_t   | 1 byte |
| int16_t/uint16_t | 2 byte |
| int32_t/uint32_t | 4 byte |
| int64_t/uint64_t | 8 byte |

***3. Di chuyển dữ liệu.***
Việc chuyển dữ liệu có thể chia thành 5 phương thức cơ bản:
- Giá trị tức thời --> thanh ghi.
- Thanh ghi --> thanh ghi.
- Giá trị tức thời --> bộ nhớ.
- Thanh ghi --> bộ nhớ.
- Bộ nhớ --> thanh ghi.
Các lệnh di chuyển dữ liệu cơ bản:
- Mov a, b: copy dữ liệu từ toán hạng b sang toán hạng a. Trong đó, a, b có thể là 1 trong các cặp toán hạng có ở trên. Ngoài ra còn có một biến thể phổ biến là movzx/movsx. Chúng đều có tác dụng là copy dữ liệu từ một nguồn sang thanh ghi có kích thước lớn hơn. Lệnh movzx di chuyển dữ liệu không dấu, các bit thừa sẽ được đặt thành 0. Lệnh movsx di chuyển dữ liệu có dấu, các bit thừa sẽ được đặt thành 1 nếu là số âm và đặt thành 0 nếu là số dương.  
- Lea a, b: Lấy địa chỉ của vùng nhớ b lưu vào toán hạng a. a và b bắt buộc phải là cặp thanh ghi - vùng nhớ.

***4. Các phép toán số học.***
a) Phép cộng.
- Cú pháp: add a, b.
- Thực hiện, lấy 2 toán hạng cộng lại với nhau rồi lưu vào toán hạng a.
b) Phép trừ .
- Cú pháp: sub a, b.
- Thực hiện: lấy toán hạng a từ toán hạng b rồi lưu vào toán hạng a.
c) Phép tăng/giảm 1 đơn vị.
- Cú pháp: inc/dec a.
- Thực hiện: tăng giảm toán hạng a 1 đơn vị.
d) Phép nhân.
- Imul/Mul a:
	Thực hiện: lấy toán hạng a nhân dữ liệu trong thanh ghi rax rồi lưu lại vào thanh ghi rax. Đặc biệt, nếu kết quả không thể chứa trong 1 thanh ghi thì sẽ bị đẩy 1 phần sang thanh ghi rdx. Cụ thể quy tắc như sau (ở đây lấy ví dụ a là các thanh ghi thuộc RBX hoặc vùng nhớ).

| RBX/QWORD  | Ghi đè lên cặp RDX:RAX (bit cao ở RDX, bit thấp ở RAX) |
| ---------- | ------------------------------------------------------ |
| EBX/DWORD  | Ghi đè lên cặp EDX:EAX (bit cao ở EDX, bit thấp ở EAX) |
| BX/WORD    | Ghi đè lên cặp DX:AX (bit cao ở DX, bit thấp ở AX)     |
| BH/BL/BYTE | AX                                                     |
- Imul a, b:
	Thực hiện: Lấy 2 toán hạng a, b nhân với nhau rồi lưu dữ liệu vào toán hạng a. Toán hạng a luôn là thanh ghi, trong trường hợp tràn số, thanh ghi a sẽ vứt bỏ luôn phần tràn chứ không ghi đè lên thanh ghi khác giống như phép nhân 1 toán hạng.
- Imul a, b, c:
	Thực hiên: Lấy 2 toán hạng b, c (c luôn là giá trị tức thời) nhân với nhau rồi lưu vào toán hạng a. Toán hạng a luôn là thanh ghi, trong trường hợp tràn số, thanh ghi a sẽ vứt bỏ luôn phần tràn chứ không ghi đè lên thanh ghi khác giống như phép nhân 1 toán hạng.
e) Phép chia 
- Div a:
	Dùng cho số không dấu. Lấy cặp thanh ghi rdx:rax làm số bị chia, toán hạng a làm số chia, và cho ra 2 kết quả: thương số và số dư. Ta có bảng quy tắc (ở đây lấy a là thanh ghi thuộc RBX hoặc vùng nhớ).
	
| số chia    | số bị chia | thương số | số dư |
| ---------- | ---------- | --------- | ----- |
| RBX/QWORD  | RDX:RAX    | RAX       | RDX   |
| EBX/DWORD  | EDX:EAX    | EAX       | EDX   |
| BX/WORD    | DX:AX      | AX        | DX    |
| BH/BL/BYTE | AX         | AL        | AH    |
- Idiv a:
	Tương tự div, nhưng phép chia này có dấu.
f) Phép toán trên bit.
- And a, b: a = a & b
- Or a, b: a = a | b
- Xor a, b: a = a ^ b
- Not a: a = phủ định(a)
- shl a, step: dịch bit trái với dữ liệu vào là a, step là số bước.
- shr a, step: dịch bit phải với dữ liệu vào là a, step là số bước.
- ror a, step: xoay bit phải với dữ liệu vào là thanh ghi a, step là số bước.
- rol a, step: xoay bit trái với dữ liệu vào là thanh ghi a, step là số bước.

***5. Stack***
Stack trong Assembly là một vùng nhớ đặc biệt, hoạt động theo nguyên tắc LIFO (Last-In, First-Out - Vào sau, Ra trước). Nó được dùng để lưu trữ tạm thời dữ liệu, địa chỉ trả về (return address) của hàm, và biến cục bộ. Stack phát triển từ địa chỉ cao xuống địa chỉ thấp và được quản lý bởi con trỏ Stack (SP/ESP/RSP).
![](../ảnh/Pasted%20image%2020260420233925.png)
1 số thao tác với stack.
- Push a: đưa dữ liệu vào stack.
- Pop a: Lấy dữ liệu ra khỏi đỉnh stack và lưu vào a.
- Thay đổi kích thước stack: Bằng cách thay đổi địa chỉ RSP.
***6. Lệnh rẽ nhánh và vòng lặp.***
Các lệnh rẽ nhánh thông dụng:
a) Rẽ nhánh có điều kiện.
- B/NAE (Below/Not above or Equal): Dùng để so sánh 2 số không dấu, điều kiện đúng khi cờ CF = 1.
- NB/AE (Not Below/Above or Equal): Dùng để so sánh 2 số không dấu, điều kiện đúng khi CF = 0.
- E/Z (Equal/Zero): Điều kiện đúng khi ZF = 1.
- NE/NZ(Not Equal/Not Zero): Điều kiện đúng khi ZF = 0.
- L (Less): Dùng cho các số có dấu. Điều kiện đúng khi SF ^ OF = 1.
- GE/NL(Greater or Equal/Not Less): Dùng cho các số có dấu, đúng khi SF ^ OF = 0.
- G/NLE(Greater/Not Less or Equal): Dùng cho các số có dấu, đúng khi (SF ^ OF) | ZF = 0
b) Rẽ nhánh không có điều kiện.
- Jump: nhảy đến địa chỉ được chỉ định.
- Call: nhảy đến địa chỉ được chỉ định, đồng thời push địa chỉ của lệnh kế tiếp lệnh call lên stack (phục vụ Ret).
- Ret: nhảy về địa chỉ ở đỉnh stack.
Vòng lặp: Về bản chất, vòng lặp trong asm chính là việc sử dụng kết hợp các câu lệnh rẽ nhánh. Ví dụ: ![](../ảnh/Pasted%20image%2020260421001130.png)
