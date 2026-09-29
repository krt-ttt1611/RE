# Các khái niệm cơ bản

1. **Window API**.

$\color{green}{\text{Win API (Application Programming Interface - giao diện lập trình ứng dụng)}}$ là giao diện lập trình dành cho hệ thống User-mode của Window.

*Các biến thể của Win API*.

Win API nguyên bản chỉ là sự kết hợp của các hàm kiểu C. Hiện tại, đã có hàng ngàn hàm như vậy để phục vụ cho các nhà phát triển. Lý do C được lựa chọn để viết Win API là bởi vì tính đơn giản, cận cấp thấp và có thể truy cập được từ tất cả các ngôn ngữ khác. Điểm yếu của Win API kiểu C đó là số lượng hàm quá lớn, cùng với cách đặt tên thiếu nhất quán. Chính vì thế, các API mới hơn sử dụng cơ chế mới: $\color{green}{\text{COM (Component Object Model - Mô hình đối tượng thành phần)}}$.

Mục đích ban đầu của việc thiết kế COM là hỗ trợ các ứng dụng office có thể giao tiếp và trao đổi dữ liệu giữa những tài liệu $\color{green}{\text{(Object Linking and Embedding - Liên kết và nhúng đối tượng)}}$.... COM được thiết kế dựa trên 2 nguyên tắc chính. Đầu tiên, clients giao tiếp với đối tượng thông qua các $\color{green}{\text{giao diện}}$ - các "bản hợp đồng" được định nghĩa rõ ràng cùng với 1 tập hợp các phương thức logic được gom nhóm lại nhờ vào cơ chế $\color{green}{\text{vtable}}$. Điều này khiến các tên gọi có quy tắc hơn, và giảm số lượng tên xuống. Điều thứ 2 đó là COM được load động thay vì load tĩnh với client.

$\color{green}{\text{Win Runtime}}$: Window 8 giới thiệu 1 cơ chế API và hỗ trợ trong quá trình chạy mới gọi là $\color{green}{\text{Win Runtime}}$. WinRT kêt hợp nhiều nền tảng dịch vụ để hướng tới các nhà phát triển ứng dụng Window App.....

$\color{green}{\text{.NET Framework}}$: (tự đọc đi)

2. **Dịch vụ, hàm và thủ tục.**

Các thuật ngữ trên đối với người dùng Win và tài liệu lập trình có sự khác biêt đối với các ngữ cảnh khác nhau. Ví dụ, từ `service` có thể chỉ đến 1 thủ tục có thể gọi trong hệ điều hành , 1 driver thiết bị, hoặc là 1 tiến trình máy chủ. Trong sách, các thuật ngữ này có nghĩa như sau:

- $\color{green}{\text{Win API function}}$: Các chương trình con được ghi chép lại, có thể gọi trong WinAPI. Ví dụ như `CreateProcess`, `CreateFile`...
- $\color{green}{\text{Native System Services (Syscall)}}$: Các dịch vụ không được ghi chép tài liệu, ẩn sâu trong HĐH nhưng vẫn có thể gọi được từ user mode. Ví dụ, `NtCreateUserProcess` là 1 dịch vụ nội bộ hệ thống được hàm API `CreateProcess` gọi để tạo ra 1 process mới.
- $\color{green}{\text{Kernel support functions (Routines)}}$: Các chương trình con bên trong HĐH và chỉ có thể gọi từ kernel mode. VD: `ExAllocatePoolWithTag` là thủ tục mà driver của thiết bị gọi để cấp phát 1 vùng nhớ từ heaps (gọi là pool).
- $\color{green}{\text{Window services}}$: Là các tiến trình bắt đầu bởi Win service control manager. Ví dụ, Task scheduler.....
- $\color{green}{\text{Dynamic Link Libraries (DLLs)}}$: là các chương trình con có thể gọi được liên kết với nhau như 1 file nhị phân, và có thể được nạp động bởi các ứng dụng sử dụng các chương trình đó. DLLs có thể được dùng chung trên RAM, nên tiết kiệm bộ nhớ hơn.

2. **Tiến trình**.

Mặc dù chương trình và tiến trình có vẻ giống nhau, chúng gần như khác biệt. Chương trình là các file thực thi đang nằm trên đĩa, còn tiến trình là các chương trình khi được nạp lên RAM và chạy. Một tiến trình Window bao gồm những phần sau:

- $\color{green}{\text{Không gian địa chỉ ảo riêng biệt}}$: Mỗi chương trình được cấp 1 không gian địa chỉ ảo riêng biệt, giống hệt nhau. Chương trình có thể làm bất cứ điều gì tùy ý với không gian này. Còn việc nó nằm đâu trên RAM thì sẽ do hệ điều hành quản lí.
- $\color{green}{\text{Chương trình thực thi}}$: Chính là chương trình khi đã được nạp lên RAM.
- $\color{green}{\text{1 danh sách các handle đang mở}}$: Chúng ánh xạ đến các tài nguyên hệ thống như tệp, các đối tượng đồng bộ hóa... Các tài nguyên này được cho phép truy cập đối với mọi luồng của tiến trình này.
- $\color{green}{\text{1 ngữ cảnh bảo mật}}$: là 1 access token định danh người dùng, nhóm bảo mật, quyền hạn....
- $\color{green}{\text{PID}}$: Con số định danh tiến trình.
- $\color{green}{\text{Ít nhất 1 tiến trình được thực thi}}$: Mặc dù 1 tiến trình rỗng là khả thi, nó gần như không hữu dụng.

2. **Luồng**.

1 luồng là 1 thực thể bên trong 1 tiến trình, được Window lập lịch để thực thi. Không có nó, tiến trình không thể chạy. 1 luồng bao gồm các thành phần quan trọng sau:

- Nội dung của tập các thanh ghi đại diện cho trạng thái của bộ xử lí.
- 2 vùng stack, 1 cho luồng khi thực thi ở kernel mode và 1 khi thực thi ở user mode.
- 1 vùng nhớ riêng biệt gọi là $\color{green}{\text{Thread Local Storage (TLS)}}$ được sử dụng bởi hệ thống con, thư viện runtime, và DLLs.
- TID, tương tự PID.

Ngoài ra, các luồng đôi khi còn có ngữ cảnh bảo mật riêng.

3. **Fiber**.

(Tự đọc)

4. **Luồng được lập lịch ở user-mode**.

(Tự đọc nốt).

5. **Jobs**.

Window cung cấp 1 phần mở rộng cho các mô hình tiến trình, gọi là $\color{green}{\text{job}}$. Mục đích của job là cho phép quản lí và thao tác với nhóm các bộ xử lí như 1 đơn vị..... (tự đọc đi).

6. **Virtual Mem**.

(Đoạn này viết giống Linux).

7. **Kernel mode và User mode**

Để bảo vệ ứng dụng người dùng khỏi truy cập và chỉnh sửa các dữ liệu nhạy cảm của HĐH, Win sử dụng 2 chế độ truy cập bộ xử lí: $\color{green}{\text{user mode}}$ và $\color{green}{\text{kernel mode}}$. Các chương trình ứng dụng của người dùng chạy ở user mode, trong khi đó các ứng dụng hệ thống chạy ở kernel mode. Kernel mode là chế độ thực thi ở bộ xử lí mà cho phép truy cập đến tất cả bộ nhớ và tập lệnh của CPU. một số bộ xử lí phân biệt các chế độ trên bằng việc sử dụng thuật ngữ $\color{green}{\text{ring level}}$, trong khi 1 số khác lại dùng $\color{green}{\text{supervisor mode}}$ hoặc $\color{green}{\text{application mode}}$. 

.....

11. **Objects và Handles**.

$\color{green}{\text{Kernel object}}$ là 1 thực thể được tạo ra tại thời điểm chạy từ 1 kiểu đối tượng đã được định nghĩa tĩnh. Một kiểu đối tượng bao gồm: 

- Một kiểu dữ liệu do hệ thống định nghĩa.
- Các hàm thao tác trên các thực thể thuộc kiểu dữ liệu đó.
- Một tập các thuộc tính của đối tượng.

Tiến trình, luồng, file... đều là các đối tượng

Một $\color{green}{\text{thuộc tính của đối tượng}}$ là 1 trường thông tin trong 1 đối tượng, có tác dụng định nghĩa trạng thái của đối tượng đó. VD: 1 tiến trình có thuộc tính PID...

11. **Registry**.

$\color{green}{\text{Registy}}$ là cơ sở dữ liệu của hệ điều hành, nó chứa các thông tin cần thiết để:

- Khởi động và cấu hình hệ thống.
- Lưu các thiết lập phần mềm áp dụng trên toàn hệ thống.
- Điều khiển hoạt động của HĐH.
- Lưu cơ sở dữ liệu bảo mật.
- Lưu thiết lập cấu hình riêng của người dùng.

Ngoài ra, registry còn cung cấp 1 cửa sổ để truy cập những dữ liệu khả biến đang tồn tại trong RAM, chẳng hạn như trạng thái phần cứng hiện tại của hệ thống:

- Những driver thiết bị nào đang được nạp.
- Các driver đó đang sử dụng những tài nguyên nào.
- Các thông tin khác.

....

***Nói chung chương này chỉ nói qua các khái niệm cơ bản thôi, các phần này sẽ được nói cụ thể ở các chương sau.***
