https://tapit.vn/qua-trinh-bien-dich-mot-chuong-trinh-cc/
# TÓM TẮT QUÁ TRÌNH BIÊN DỊCH (COMPILATION PIPELINE)

**Mục tiêu:** Biến mã nguồn (Source Code) thành chương trình chạy được (Executable). **Quy trình chuẩn:** Tiền xử lý ➔ Biên dịch ➔ Hợp ngữ ➔ Liên kết.

### 1. Giai đoạn 1: Tiền xử lý (Preprocessing)

Đây là bước dọn dẹp và chuẩn bị bản vẽ trước khi xây dựng.

- **Đầu vào:** Tệp mã nguồn (`.c`, `.cpp`).
    
- **Nhiệm vụ:** * Xóa bỏ toàn bộ các dòng chú thích (comments).
    
    - Copy ruột các thư viện (`#include <stdio.h>`) dán thẳng vào file code.
        
    - Thay thế các hằng số macro (`#define MAX 100`) thành giá trị thật.
        
- **Đầu ra:** Tệp mã nguồn đã mở rộng (`.i`), kích thước phình to lên rất nhiều.
    

### 2. Giai đoạn 2: Biên dịch (Compiling)

Dịch từ ngôn ngữ bậc cao (con người hiểu) sang ngôn ngữ bậc thấp.

- **Đầu vào:** Tệp `.i` (từ bước 1).
    
- **Nhiệm vụ:** Trình biên dịch (Compiler) kiểm tra lỗi cú pháp (syntax error) và dịch toàn bộ code C/C++ sang mã Assembly (Hợp ngữ).
    
- **Đầu ra:** Tệp Assembly (`.s` hoặc `.asm`). Bên trong chứa các tập lệnh của CPU như `MOV`, `ADD`, `PUSH`...
    

### 3. Giai đoạn 3: Hợp ngữ (Assembling)

Dịch Assembly sang mã máy (Machine code) để CPU có thể đọc được.

- **Đầu vào:** Tệp Assembly (`.s`).
    
- **Nhiệm vụ:** Trình hợp ngữ (Assembler) dịch các lệnh `MOV`, `ADD` thành các dãy số nhị phân `0` và `1`.
    
- **Đầu ra: Tệp đối tượng / Object File (`.o` trên Linux, `.obj` trên Windows).**
    
    - _Lưu ý quan trọng:_ Đây đã là mã máy, nhưng CHƯA CHẠY ĐƯỢC vì nó chỉ là các khối linh kiện rời rạc, chưa biết địa chỉ bộ nhớ của nhau và chưa có mã của các hàm thư viện (như `printf`).
        

### 4. Giai đoạn 4: Liên kết (Linking)

Bước cuối cùng: Lắp ráp các linh kiện rời rạc thành cỗ máy hoàn chỉnh.

- **Đầu vào:** Các Object File (`.o`) và các Thư viện liên kết (`.a`, `.so`, `.lib`, `.dll`).
    
- **Nhiệm vụ:** Trình liên kết (Linker) sẽ:
    
    - Gom tất cả các tệp `.o` lại với nhau.
        
    - Tìm và nhúng mã của các hàm thư viện (ví dụ tìm xem `printf` nằm ở đâu) vào chương trình.
        
    - Cấp phát/Chốt địa chỉ bộ nhớ ảo cho các khối code.
        
- **Đầu ra:** Tệp thực thi cuối cùng (Executable File). Bấm là chạy.

|**Sản phẩm ở từng giai đoạn**|**Hệ điều hành Linux**|**Hệ điều hành Windows**|
|---|---|---|
|**Mã nguồn ban đầu**|`.c`, `.cpp`|`.c`, `.cpp`|
|**Mã máy rời rạc (Object File)**|**`.o` (Định dạng ELF)**|**`.obj` (Định dạng PE)**|
|**Gom nhiều Object File (Thư viện)**|`.a` (Tĩnh) / `.so` (Động)|`.lib` (Tĩnh) / `.dll` (Động)|
|**Thành phẩm cuối (Chạy được)**|Không có đuôi, `.out`, `.elf`|`.exe`|