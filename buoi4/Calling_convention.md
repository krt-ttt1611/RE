*1. NASM/MASM là gì.*
- NASM (Netwide assembler) là trình dịch hợp ngữ (assembler, dịch hợp ngữ sang ngôn ngữ máy) đa nền tảng (Linux, Windows, MacOS). Nó sử dụng hợp ngữ cú pháp Intel.
- MASM (Microsoft assembler) là trình dịch hợp ngữ dành cho Windows. Nó cũng sử dụng hợp ngữ cú pháp Intel, nhưng rườm rà hơn NASM.
*2. Calling convention là gì.*
Calling convention (quy ước gọi hàm) là tập hợp các quy tắc chuẩn hóa, định nghĩa cách thức 1 chương trình máy tính truyền tham số, quản lí stack và nhân giá trị trả về giữa 1 hàm gọi (caller) và hàm được gọi (callee).
2.1 Calling convention trên Windows.
a) Một số calling convention phổ biến của Windows x86.
- __ stdcall (standard call): Tham số được đẩy vào stack theo thứ tự lần lượt từ phải sang trái. Sau khi callee thực thi xong, nó sẽ dọn dẹp stack.
- __ cdecl (c declaration): Tham số được đẩy vào stack theo thứ tự từ phải sang trái. Sau khi callee thực thi xong, caller sẽ dọn dẹp stack.
- __ fastcall: 2 tham số đầu tiên (từ trái sang) được truyền vào ecx và edx, các tham số còn lại đẩy vào stack từ phải sang trái. Callee dọn dẹp stack.
- __ thiscall: Con trỏ this (con trỏ ẩn, tự động trỏ đến object đang gọi hàm, ứng dụng trong C++ OOP) được truyền vào ecx, các tham số khác đẩy vào stack từ phải sang trái. Calle dọn stack.
Tất cả các calling convention trên, dữ liệu trả về đều được đưa vào eax hoặc edx:eax. 
b) Calling convention phổ biến của Windows x86-64. 
Trên Window x86-64, chỉ có 1 calling convention duy nhất là Microsoft x64 calling convention. Đặc điểm:
- 4 tham số đầu tiên truyền lần lượt qua thanh ghi: rcx, rdx, r8, r9. Từ tham số thứ 5 trở đi, truyền lần lượt từ phải sang trái vào stack.
- Caller bắt buộc phải cấp phát 32 bytes trên stack trước khi goi hàm. Đây là vùng để callee lưu tham số trong rcx, rdx, r8, r9 nếu cần thiết.
- Dữ liệu trả về: Dữ liệu phổ thông lưu trong rax, dữ liệu số thực lưu trong xmm0 (128 bit).
2.2. Calling convention trên Linux.
Linux x86 chỉ có 1 calling convention duy nhất là __ cdecl. Còn Linux x86-64 cũng có 1 calling convention duy nhất là system V AMD64 ABI. Đặc điểm chính:
- 6 tham số nguyên đầu tiên truyền lần lượt vào các thanh ghi: rdi, rsi, rdx, rcx, r8, r9. Nếu là tham số thực thì truyền vào xmm0 đến xmm7. Các tham số còn lại truyền vào stack từ phải sang trái.
- Caller dọn stack, dữ liệu trả về đưa vào rax hoặc xmm0 nếu là số thực.
*3. ABI là gì.*
ABI (Application Binary Interface) định nghĩa các quy tắc chuẩn về cách mã máy tương tác với nhau, bao gồm việc gọi hàm, truyền tham số qua thanh ghi/stack và sử dụng bộ nhớ.
Các khía cạnh chính của ABI gồm:
- Calling convention.
- Quản lí stack: Quy định cách stack frame được thiết lập, stack alignment và cách thu hồi stack frame trước khi hàm trả về.
- System calls: cách thức thực hiện gọi các dịch vụ từ nhân hệ điều hành.
- Định dạng file thực thi.
- Cách đặt tên symbol trong binary.
- Kích thước kiểu dữ liệu.
Từ định nghĩa trên, ta thấy calling convention là 1 phần nhỏ của ABI.


