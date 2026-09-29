1. **Tổng quan kiến trúc**.

Phiên bản đơn giản hóa của kiến trúc hệ điều hành Windows được mô tả trong hình _2.1_.

![[Pasted image 20260830224355.png]]

- Các ô nằm trên cùng đại diện cho các tiến trình chạy ở user-mode. 
- Các ô nằm phía dưới đại diện cho các tiến trình chạy ở kernel-mode.

Như đã giới thiệu ở phần 1, các luồng thực thi ở user-mode thực thi trong 1 không gian địa chỉ riêng tư (tuy nhiên khi thực thi ở kernel-mode, nó có thể truy cập đến không gian hệ thống chung). Do đó, các tiến trình hệ thồn, dịch vụ, người dùng và phân hệ môi trường (environment subsystem, cung cấp 1 môi trường/API cụ thể để ứng dụng thực thi), đều có không gian địa chỉ tiến trình riêng.

Nói một cách chính xác, tiến trình hypervisor vẫn chạy với đăc quyền cpu level 0, nhưng nó sử dụng các tập lệnh đặc biệt, nó có thể vừa tự cách li khỏi kernel vừa giám sát kernel.![[Pasted image 20260830231515.png]]![[Pasted image 20260830231640.png]]![[Pasted image 20260830231547.png]]

4 loại tiến trình cơ bản chạy ở user-mode là:

- *Tiến trình người dùng*: Các tiến trình này có thể thuộc 1 trong các loại sau: win32, win634....
- *Tiến trình dịch vụ*: Các tiến trình điều khiển các dịch vụ Windows, như task scheduler...
- *Tiến trình hệ thống*: Các tiến trình cố định, gắn chặt vào thiết kế của windows, như tiến trình khởi động... Chúng không phải dịch vụ Windows, nghĩa là chúng không được khởi chạy bằng Service Control Manager.
- *Tiến trình dịch vụ phân hệ môi trường*: Chạy các thành phần hỗ trợ cho hệ điều hành, hoặc đại diện cho người dùng và lập trình viên.

Trong hình _2.1_, chú ý đến Subsystem DLLs bên dưới tiến trình dịch vụ và tiến trình người dùng. Bên dưới hđh, các ứng dụng người dùng không gọi trực tiếp đến các dịch vụ native của hệ điều hành trực tiếp. Thay vào đó, nó thông qua 1 hoặc nhiều $\color{green}{\text{Subsystem DLLs}}$. Vai trò của chúng là dịch 1 hàm đã được ghi chép công khai thành các dịch vụ native nội bộ được cung cấp trong `Ntdll.dll`. Việc dịch này có thể cần hoặc không cần  đến việc gửi 1 message tới 1 tiến trình phân hệ môi trường đang phục vụ tiến trình người dùng.

Các thành phần của kernel-mode bao gồm:

- *Executive*: Khối điều hành window bao gồm các dịch vụ OS cơ bản.
- *Nhân*: Chứa các hàm hệ điều hành cấp thấp. Đồng thời cung cấp 1 tập các thủ tục và đối tượng cơ bản mà khối điều hành dùng để triển khai các cấu trúc cấp cao.
- *Drivers thiết bị*: Bao gồm cả driver phần cứng, dịch các hàm I/O của người dùng thành các yêu cầu thiết bị I/O, và các driver phần mềm, như là driver hệ thống file...
- *Hardware Abstraction Layer (Lớp trừu tượng hóa phần cứng - HAL)*: Là lớp code cô lập kernel, driver thiết bị, và phần còn lại của khối thực thi khỏi các sự khác biệt về phần cứng (kiểu nhờ có HAL mà hệ điều hành có thể chạy trên nhiều mẫu phần cứng khác nhau).
- *Hệ thống cửa sổ và đồ họa*: Triển khai các hàm GUI.
- *Lớp hypervisor*: Lớp này chỉ gồm 1 thành phần duy nhất là chính hypervisor. Tuy nhiên, bản thân hypervisor lại được cấu thành từ nhiều lớp và dịch vụ cục bộ khác... 

1. **Environment Subsystem và Subsystem DLLs**.

Vai trò của ES là cung cấp cho các chương trình ứng dụng 1 tập các dịch vụ của khối thực thi. Mỗi subsystem cung cấp quyền truy cập đến 1 tập khác nhau các dịch vụ native của Win. Điều này có nghĩa là một số thao tác có thể chạy được từ 1 ứng dụng xây dựng trên ES này, nhưng không thể thực hiện trên ứng dụng xây dựng trên ES khác.

Mỗi chương trình thực thi được ràng buộc tới 1 và chỉ 1 ES. Khi nó chạy, đoạn mã tạo tiến trình kiểm tra loại mã trong image header để thông báo cho ES tương ứng về tiến trình mới...

Như đã giới thiệu, các ứng dụng người dùng không gọi trực tiếp các dịch vụ Win. Thay vào đó, nó thông qua 1 hoặc nhiều SD. Các DLLs xuất các giao diện của hàm công khai mà chương trình thuộc subsystem đó có thể sử dụng. Ví dụ, Win subsystem DLLs (Kernel32.dll...) cung cấp các hàm API...

***Đoạn này viết cực kì lủng củng, hiểu khái quát là ES thì chứa SD, SD cung cấp các hàm để chương trình chạy trên ES thao tác.***

Khi 1 ứng dụng gọi 1 hàm của SD, 1 trong 3 khả năng sau có thể xảy ra:

- Hàm này được triển khai ở user mode bên trong SD, nói cách khác, không có message nào được gửi tới tiến trình ES, và không có dịch vụ hệ thống của khối thực thi hđh nào được gọi. Hàm thực thi ở user mode, và kết quả trả về cho caller.
- Hàm này cần 1 hoặc nhiều lời gọi đến khối thực thi hđh. Ví dụ, `ReadFile` gọi đến 1 dịch vụ nội bộ ngầm trong I/O của hệ điều hành là `NtReadFile`.
- Hàm này cần phải thực thi 1 số phần ở tiến tình ES. Khi này, 1 request sẽ được gửi tới ES thông qua message ALPC để yêu cầu thực hiện. SD sẽ chờ phản hồi trước khi trả về cho caller.