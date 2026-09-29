# **Lab_01-1.malware**

1. 

![[Pasted image 20260912205055.png|405]]

2009-05-15 00:12:41

2. 

*KERNEL32.DLL*

![[Pasted image 20260912205323.png]]

![[Pasted image 20260912205350.png]]

Cụm đầu tiên ta có thể để ý đó là cụm các API:

- `CreatePipe`: Tạo 1 kênh truyền dữ liệu giữa 2 đầu đọc/ghi.
- `CreateProcessA`: Tạo 1 tiến trình mới.
- `ReadFile`: Đọc dữ liệu từ 1 handle.
- `WriteFile`: Ghi dữ liệu vào 1 handle.
- `PeekNamedPipe`: Kiểm tra xem pipe có dữ liệu không.

Cụm các API có thể tạo ra 1 process con rồi giao tiếp với nó qua pipe. Ví dụ malware tạo `cmd.exe`, redirect stdin/stdout qua pipe, sau đó dùng `WriteFile` gửi lệnh và `ReadFile`/`PeekNamedPipe` đọc output. Đây là pattern rất hay gặp trong remote shell/backdoor.

Một cụm khác:

- `CreateThread`: Tạo 1 luồng xử lí mới.
- `TerminateThread`: Kết thúc 1 luồng xử lí.
- `WaitForSingleObject`: Chờ 1 object đạt trạng thái `signaled` (thông báo rằng đối tượng đã đươc thõa mãn, và có thể chạy tiếp), hoặc chờ đến `timeout`.
- `WaitForMultipleObjects`: Giống bên trên, nhưng chờ nhiều object hơn.
- `SetEvent`: Đưa 1 event object sang trạng thái `signaled`.
- `CreateEventA`: Tạo 1 event object mới. 1 event object có 2 trạng thái là `signaled` và `nonsignaled`.

Đây là cơ chế đa luồng và đồng bộ hóa, nó có thể kết hợp với cụm api phía trên để đồng bộ hóa nhiều luồng đọc/ghi vào 1 pipe.

Cụm tiếp theo:

- `GetCurrentProcess`: Trả về 1 pseudo-handle đến chính process đang chạy.
- `GetCurrentThread`: Trả về 1 pseudo-handle đến chính thread đang chạy.
- `SetThreadPriority`: Đổi priority của 1 thread cụ thể (priority là mức độ ưu tiên, dùng trong cơ chế lập lịch của window).
- `SetPriorityClass`: Đặt priorityclass cho 1 process (có thể hiểu là mức priority nền của các thread trong nó).
- `SetProcessPriorityBoost`: Bật/tắt cơ chế $\color{green}{\text{Dynamic priority Boost}}$ cho các thread của nó (tức là Window có thể tự nâng mức priority lên).

Có thể malware định điều chỉnh schedule/priority của chính nó hoặc thread của nó.

Cặp:

- `DuplicateHandle`: Tạo 1 handle mới trỏ tới cùng 1 object với handle đã có.
- `GetCurrentProcess`: Trả về 1 pseudo-handle của tiến trình đang chạy.

Cặp này dùng để duplicate các handle có trong tiến trình.

Cặp:

- `GetModuleFileNameA`: Lấy đường dẫn đầy đủ của 1 module được load.
- `GetShortPathNameA`: format lại chuỗi đường dẫn.

Malware có thể dùng cặp này để tìm vị trí của chính nó.

*SHELL32.DLL*

![[Pasted image 20260913105201.png]]

- `ShellExecuteExA`: Mở 1 resource, thực thi 1 file hoặc chương trình bằng shell của Windows.
- `SHChangeNotify`: Thông báo cho Windows về 1 thứ gì đó trong file system/shell name space đã thay đổi.

API đầu tiên rất khả nghi, malware có thể dùng nó để mở 1 file thực thi khác.

Ngoài ra còn có thư viện `WS2_32.DLL`, là WinSock, cung cấp các API giao tiếp mạng.

3.

![[Pasted image 20260913094542.png]]

Đây là 2 chuỗi đáng chú ý nhất.

Chuỗi đầu là 1 cụm IP + Port, có thể chình là của máy chủ C2.

Chuỗi thứ 2 là phần padding, mặc dù không biết để làm gì, nhưng trông khá kì lạ.

![[Pasted image 20260913094715.png]]

Ngoài ra còn chuỗi `cmd.exe`, rất có thể đấy chính là tiến trình sẽ được mở và giao tiếp qua pipe đọc/ghi.

4. 

T dự đoán malware này sẽ chạy ngầm, nó mở 1 tiến trình `cmd.exe` để làm 1 việc gì đó. Ngoài ra nó còn giao tiếp với mạng bên ngoài.

*Chạy thử.*

Cái đầu tiên có thể thấy, ngay sau khi chạy thì file `exe` biến mất? Khá kì lạ.![[Pasted image 20260913095957.png]]

5. 

Dùng procmon với 2 filter `Lab_01-1.exe` và `cmd.exe`. Lý do rất đơn giản, `Lab_01-1.exe` là tên tiến trình, còn `cmd.exe` là chuỗi tìm được trong file, chúng rất có thể liên quan đến nhau 

6. 

Đầu tiên, dùng procmon để xem các tiến trình.

![[Pasted image 20260913095521.png]]

![[Pasted image 20260913095551.png]]

Ta có thể thấy ngay, đầu tiên nó vẫn chạy bình thường, nhưng sau đó, nó chuyển sang chạy bằng cmd, và xóa đi tiến trình gốc để ẩn mình.

![[Pasted image 20260913101354.png]]

![[Pasted image 20260913101412.png]]

Ngoài ra, nó còn tạo thêm khác nhiều file khác, và cũng đọc, ghi vào registry.

Dùng procexp để so sánh thử chuỗi của 2 tiến trình, không thấy có gì khác lạ, vậy đây vẫn là cmd gốc, có thể nó bị điều khiển thông qua 1 pipe kết nối với máy chủ c2.

Dùng regshot để so sánh registry, ta được kết quả như sau.

![[Pasted image 20260913101559.png]]

Malware đã thêm tối đa 4 key, 27 value và sửa 46 value (có thể các phần mềm khác cũng chỉnh sửa, nhưng từ lịch sử procmon, chắc chắn là malware có chỉnh sửa trong này).

7. 

![[Pasted image 20260913103949.png]]

Malware có hành vi yêu cầu kết nối đến IP 60.248.52.95:443, đúng như đã dự đoán bên trên.

8. 

Không có gì, ngoại trừ việc nó tự xóa file gốc đê ẩn mình. Cái này thì khắc phục cũng đơn giản, dùng procmon là được.

9. 

Đây khả năng cao là reverse shell, máy nạn nhân tự mở yêu cầu kết nối, kết nối đến máy chủ C2.

# **Lab_01-2.malware**

1. 

![[Pasted image 20260913133317.png]]

MD5sum: `02658bc9801f98dfdf167accf57f6a36`

![[Pasted image 20260913133255.png]]

Báo cáo của VT:

- 59/70 phần mềm antivirus nhận diện là mã độc.
- Nhãn phổ biến nhất là: `trojan.connapts/gzdp`.
- Được xếp vào các nhóm: `trojan`, `downloaders`.

2. 

*KERNEL32.DLL*

![[Pasted image 20260913134013.png]]

Cụm đầu tiên:

- `CreateProcess`: Tạo process mới.
- `CreatePipe`: Tạo pipe mới.
- `PeekNamedPipe`: Kiểm tra xem pipe có dữ liệu không.
- `Write/ReadFile`: Đọc/ghi dữ liệu.

Cụm này tạo nên hành vi: tạo tiến trình và giao tiếp ngầm qua pipe I/O.
```
C2 server
   │
   │ command
   ▼
malware
   │ WriteFile(pipe)
   ▼
 cmd.exe
   │
   │ output
   ▼
pipe
   │ PeekNamedPipe / ReadFile
   ▼
malware
   │
   └────────► gửi kết quả về C2
```
*WININET.DLL*

![[Pasted image 20260913134318.png]]

Cụm:

- `InternetOpenA`: Khởi tạo 1 Internet session, trả về 1 `HINTERNET` handle.
- `InternetConnectA`: Tạo kết nối tới 1 server cụ thể.
- `HttpOpenRequestA`: Tạo 1 HTTP request trên connection vừa mở.
- `HttpSendRequestA`: Gửi HTTP request đã tạo.
- `InternetReadFile`: Đọc dữ liệu nhận được từ server.

Tạo ra hành vi: Kết nối tới máy chủ bên ngoài, tạo và đọc phản hồi HTTP response.

Cụm:

- `HttpSendRequestExA`: Gửi 1 request đã tạo
- `InternetWriteFile`: Ghi dữ liệu vào Request đang mở.
- `HttpEndRequestA`: Kết thúc 1 HTTP request.

Đây là hành vi: Gửi dữ liệu lên server.

![[Pasted image 20260913140253.png]]

3. 

Có khá nhiều chuỗi kì lạ:

![[Pasted image 20260913140419.png]]

Đầu tiên là IP: `69.25.50.10`, đây có thể là IP của máy chủ.

Các chuỗi `Begin Download`... trông như thể chương trình thực hiện hành vi download dữ liệu từ phía server.

Ngoài ra còn có `cmd /c`, đây là câu lệnh dùng cmd để thực hiện 1 lệnh nhỏ, rồi tắt.

Có cả các từ khóa `putf`, `getf`... Nó không giống bất kì từ khóa quy ước nào trong các ngôn ngữ lập trình, nhưng trông lại có ý nghĩa trong ngữ cảnh này. Nó có thể là 1 dạng pseudo shell (tức là các lệnh điều khiển mà chỉ malware và c2 server hiểu).

![[Pasted image 20260913140618.png]]

Đây là tên của chương trình Window update, chưa biết malware làm gì với nó.

![[Pasted image 20260913140745.png]]

Đây cũng là 1 chương trình hệ thống, là service host, dùng để chạy các service.

![[Pasted image 20260913140837.png]]

Có thêm chuỗi padding ở cuối file, không biết để làm gì.

4. 

Khi bấm chạy chương trình, không có gì xảy ra cả. Có lẽ chương trình đã chạy ngầm.

5. 

Dùng 4 filter: `Lab_01-2.exe`, `cmd.exe` và `wuauclt.exe`. Đây đều là các chuỗi xuất hiện trong file. Chuỗi `scvchost.exe` không nên thêm vào, vì nó luôn chạy kể cả khi không dùng malware, nên sẽ gây nhiễu trong quá trình phân tích.

6. 

Đầu tiên dùng procmon để xem hành vi của tiến trình.

![[Pasted image 20260913142624.png]]

Ta có thể thấy malware thực hiện khá nhiều hành vi mở, truy vấn, đóng file. Ngoài ra nó còn mở, chỉnh sửa các registry.

Vì `svchost.exe` luôn mở kể cả khi không dùng malware, nên ta cũng không thể xác nhận được là nó có liên quan gì đến hành vi của malware không.

Dùng regshot để so sánh registry.

![[Pasted image 20260913143145.png]]

3 key được thêm vào, 9 giá trị được thêm vào, 58 giá trị bị sửa đổi. Không thể khẳng định được 100% số thay đổi là do malware làm, nhưng chắc chắn trong này có những thay đổi do malware.

7. 

![[Pasted image 20260913143658.png]]

Malware có những hành vi kết nối mạng với IP `69.25.50.10`, đúng như đã dự đoán bên trên. Ngoài ra, các gói tin còn sử dụng cả giao thức mã hóa, có lẽ để che dấu nội dung.

8. 

Có. Traffic tới C2 sử dụng TLS nên không thể đọc trực tiếp nội dung application data. Ngoài ra, trong môi trường Windows 10 hiện tại tôi không quan sát thấy `wuauclt.exe` được chạy như trong môi trường lab cũ, nên một số hành vi có thể không tái hiện hoàn toàn.

9. 

Như đã nói bên trên, đây có thể là 1 dạng backdoor/reverse shell. Malware điều khiển máy nạn nhân chủ động mở kết nối đến máy chủ C2, thông qua các pseudo-shell, máy chủ C2 sẽ điều khiển máy nạn nhân.

# **Lab_01-3.malware**

1. 

![[Pasted image 20260913153340.png]]

DiE đã nhận diện được dấu hiệu file bị pack bằng upx.

![[Pasted image 20260913153437.png]]

Bảng import cũng cho thấy có dấu hiệu packed. Chỉ mình API `InternetOpenA` thì không thể làm được gì cả. Có lẽ các API khác nằm trong vùng bị packed.

2. 

Nếu đây là upx chuẩn, thì có thể unpack bằng tool, còn nếu là custom upx thì sẽ phải unpack bằng tay (chưa học)

Thử unpack nó.

![[Pasted image 20260913153923.png]]

Vậy khả năng đây là upx custom. Không unpack bằng tay được.

 3. 

Vì không thể unpack, ta sẽ đọc string bằng cách chạy malware, rồi dùng procexp để đọc trực tiếp strings trong tiến trình.

![[Pasted image 20260913155509.png]]

Tìm thấy 1 domain lạ `www.practicalmalwareanalysis.com`. Ngoài ra, malware còn lấy chính đường dẫn của file thực thi. Các API cũng hiện ra rất rõ ràng so với strings trong file thực thi.

4. 

![[Pasted image 20260913155851.png]]

Khi chạy malware thì hiện lên 1 màn hình console, không thể thao tác gì được, nhưng có thể tắt được. Khi tắt thì tiến trình của malware cũng tắt luôn.

5. 

Dùng procmon

![[Pasted image 20260913160703.png]]

Ta thấy malware thực hiện khá nhiều thao tác: mở, đọc, đóng file, load ảnh dll, mở, sửa registry...

![[Pasted image 20260913160836.png]]

Ngoài ra còn gửi và nhận các gói tin UDP.

<bước regshot thì thôi không làm nữa đâu>

6. 

![[Pasted image 20260913161426.png]]

Malware thực hiện trao đổi dữ liệu với domain `www.practicalmalwareanalysis.com`.

7. 

File bị pack, không biết cách unpack.

8. 

Khá khó đoán, hành vi của nó cũng không quá rõ ràng. Có thể nó cũng là 1 reverse shell/back door giống 2 bài trên, hoặc có thể là 1 downloader.