# **8. Debugging**
Debugger là phần mềm hoặc phần cứng dùng để kiểm tra và điều khiển quá trình thực thi của chương trình. Khác với disassembler chỉ cho ta “ảnh chụp tĩnh” của chương trình, debugger cho phép quan sát chương trình khi nó đang chạy: giá trị thanh ghi, vùng nhớ, tham số hàm và sự thay đổi của dữ liệu theo thời gian.
Debugger còn cho phép thay đổi biến, thanh ghi, mã lệnh và luồng thực thi. Vì vậy, đây là công cụ rất quan trọng trong reverse engineering và phân tích malware.
*a) Source-Level vs. Assembly-Level Debuggers*
Có hai loại debugger chính:
- ==Source-level debugger:== làm việc trên mã nguồn, thường tích hợp trong IDE. Có thể đặt breakpoint tại từng dòng code, xem biến và chạy từng dòng.
- ==Assembly-level debugger:== làm việc trực tiếp trên mã assembly. Có thể chạy từng instruction, đặt breakpoint tại địa chỉ mã và kiểm tra thanh ghi hoặc bộ nhớ.
Malware analyst thường sử dụng assembly-level debugger vì họ hầu như không có mã nguồn của malware.

*b) Kernel vs. User-Mode Debugging*
==User-mode debugging== thường diễn ra trên cùng một máy: debugger và chương trình cần phân tích cùng chạy trong user mode. Mỗi tiến trình được hệ điều hành cô lập nên việc debug tương đối đơn giảnKernel-mode debugging== phức tạp hơn vì toàn bộ hệ thống chỉ có một kernel. Khi kernel dừng tại breakpoint, các ứng dụng khác cũng không thể tiếp tục chạy. Vì vậy, mô hình truyền thống thường sử dụng hai máy:
- Target chạy hệ điều hành hoặc driver cần debug.
- Host chạy debugger và điều khiển target.
Hệ điều hành trên target cũng phải được cấu hình để cho phép kernel debugging.
*c) Using a Debugger*
Có hai cách bắt đầu debug:
- ==Khởi chạy chương trình bằng debugger:== chương trình thường dừng trước khi thực thi entry point, giúp ta kiểm soát ngay từ đầu.
- ==Attach debugger vào tiến trình đang chạy:== các thread của tiến trình bị tạm dừng để debugger giành quyền điều khiển.
Attach phù hợp khi chỉ muốn phân tích chương trình sau khi nó đã chạy đến một trạng thái nhất định.
***Single-Stepping***
Single-stepping nghĩa là thực thi một instruction rồi dừng lại, cho phép quan sát chi tiết từng thay đổi trong chương trình.
Tuy nhiên, không nên single-step toàn bộ một chương trình phức tạp vì sẽ mất rất nhiều thời gian. Cần tìm khu vực quan trọng bằng phân tích tĩnh hoặc breakpoint, sau đó chỉ single-step đoạn cần nghiên cứu.
Ví dụ:
```asm
mov edi, DWORD_00406904
mov ecx, 0x0d
LOC_040106B2
xor [edi], 0x9C
inc edi
loopw LOC_040106B2
...
DWORD:00406904: F8FDF3D0
```
Một vòng lặp XOR từng byte với `0x9C`. Khi theo dõi dữ liệu thay đổi từng bước, chuỗi ban đầu khó đọc dần được giải mã thành `LoadLibraryA`. Đây là thông tin khó nhận ra hơn nếu chỉ phân tích tĩnh.
***Stepping-Over vs. Stepping-Into***
Khi gặp lệnh `call`, debugger thường cung cấp ba thao tác:
- ==Step into:== đi vào trong hàm được gọi và dừng tại instruction đầu tiên của hàm đó.
- ==Step over:== chạy toàn bộ hàm rồi dừng tại instruction ngay sau `call`.
- ==Step out:== chạy cho tới khi hàm hiện tại kết thúc và quay lại hàm gọi nó.
Step over giúp giảm lượng code cần phân tích, đặc biệt với các API đã biết như `LoadLibrary`. Tuy nhiên, nếu step over nhầm một hàm không bao giờ return thì debugger có thể không lấy lại được quyền điều khiển.
Ngược lại, nếu liên tục step into, ta rất dễ đi sâu vào các hàm thư viện hoặc hàm phụ không liên quan. Vì vậy, cần luôn xác định mình đang tìm hiểu điều gì trước khi lựa chọn thao tác.
***Pausing Execution with Breakpoints***
Breakpoint làm chương trình tạm dừng tại một vị trí cụ thể để kiểm tra trạng thái của nó. Khi chương trình đang chạy, thanh ghi và bộ nhớ liên tục thay đổi nên rất khó quan sát; breakpoint giúp “đóng băng” trạng thái đó.
Breakpoint đặc biệt hữu ích trong các trường hợp:
- Xác định đích của lệnh gọi gián tiếp như `call eax`.
- Kiểm tra tham số truyền vào API.
- Quan sát dữ liệu trước hoặc sau một hàm biến đổi.
- Tìm instruction đọc hoặc sửa một vùng nhớ.
Ví dụ, có thể đặt breakpoint tại `CreateFileW`, rồi kiểm tra tham số `lpFileName` để biết chương trình đang mở hoặc tạo file nào. Trong ví dụ của tài liệu, tên file được xác định là `LogFile.txt`.
Tương tự, nếu malware mã hóa dữ liệu trước khi gửi, ta có thể đặt breakpoint ngay trước hàm mã hóa để đọc plaintext mà không cần tự phục hồi thuật toán hoặc khóa.
==Software Execution Breakpoints==
Software breakpoint thường là loại breakpoint mặc định.
Debugger triển khai nó bằng cách thay byte đầu tiên của instruction tại vị trí breakpoint bằng `0xCC`, tức opcode của instruction `INT 3`. Khi CPU thực thi `INT 3`, hệ điều hành tạo exception và chuyển quyền điều khiển cho debugger.
Ưu điểm:
- Có thể đặt rất nhiều software breakpoint.
- Dễ sử dụng.
- Chi phí bộ nhớ nhỏ.
Nhược điểm:
- Làm thay đổi code trong bộ nhớ.
- Có thể bị malware phát hiện bằng kiểm tra tính toàn vẹn của code.
- Có thể bị xóa nếu chương trình tự sửa mã.
- Chương trình tự đọc code sẽ nhìn thấy byte `0xCC` thay vì byte ban đầu.
==Hardware Execution Breakpoints==
Hardware breakpoint được CPU hỗ trợ thông qua các thanh ghi debug.
Khác với software breakpoint, nó không sửa byte mã lệnh tại địa chỉ cần theo dõi. Do đó, nó hữu ích khi:
- Code có khả năng tự thay đổi.
- Malware kiểm tra sự toàn vẹn của code.
- Cần dừng khi một vùng nhớ được đọc hoặc ghi.
Hardware breakpoint có thể theo dõi:
- Execution: CPU thực thi tại địa chỉ đó.
- Read: vùng nhớ được đọc.
- Write: vùng nhớ bị ghi.
- Access: vùng nhớ được đọc hoặc ghi.
Hạn chế lớn nhất là x86 chỉ có bốn thanh ghi địa chỉ breakpoint: `DR0`–`DR3`. Thông tin điều khiển được lưu trong `DR7`. Malware có thể kiểm tra hoặc sửa các thanh ghi debug để phát hiện và gây khó khăn cho debugger.
==Conditional Breakpoints==
Conditional breakpoint chỉ thực sự dừng chương trình khi điều kiện chỉ định là đúng.
Ví dụ, `GetProcAddress` có thể được gọi hàng trăm lần, nhưng ta chỉ muốn dừng khi chương trình tìm API `RegSetValue`. Khi đó có thể đặt điều kiện dựa trên tham số truyền vào hàm.
Về bản chất, debugger vẫn nhận breakpoint mỗi lần instruction được thực thi, sau đó:
1. Kiểm tra điều kiện.
2. Nếu đúng thì dừng cho người phân tích.
3. Nếu sai thì tự động tiếp tục chạy.
Do phải kiểm tra điều kiện nhiều lần, loại breakpoint này có thể làm chương trình chậm nghiêm trọng nếu được đặt tại instruction chạy thường xuyên. 
***Exceptions***
Exception là cơ chế chính giúp debugger lấy quyền điều khiển từ chương trình.
Không chỉ breakpoint mới tạo exception. Những sự kiện sau cũng có thể tạo exception:
- Truy cập vùng nhớ không hợp lệ.
- Chia cho 0.
- Thực thi instruction đặc quyền trong user mode.
- Thực thi `INT 3`.
- Single-step.
Exception cũng có thể được chương trình sử dụng như một phần của luồng điều khiển bình thường hoặc kỹ thuật anti-debug.
==First- and Second-Chance Exceptions==
Khi debugger đang attach, một exception thường trải qua hai giai đoạn:
**First-chance exception**
Debugger là bên đầu tiên nhận exception. Nó có thể:
- Tự xử lý exception.
- Chuyển exception cho chương trình.
Nếu chương trình đã đăng ký exception handler, handler đó sẽ có cơ hội xử lý.
**Second-chance exception**
Nếu chương trình không xử lý được exception, debugger sẽ nhận nó lần thứ hai.
Second-chance exception có nghĩa là nếu không có debugger thì chương trình sẽ crash. Vì vậy, nó không thể bị bỏ qua nếu muốn chương trình tiếp tục chạy.
Trong malware analysis:
- First-chance exception đôi khi có thể bỏ qua vì malware có thể cố tình tạo exception để điều khiển luồng hoặc chống debug.
- Second-chance exception thường cho thấy malware bị lỗi hoặc không chấp nhận môi trường hiện tại.
==Common Exceptions==
Một số exception thường gặp:
- **Breakpoint exception:** sinh ra bởi instruction `INT 3`.
- **Single-step exception:** CPU bật Trap Flag, thực thi một instruction rồi tạo exception.
- **Access violation:** chương trình đọc, ghi hoặc thực thi tại vùng nhớ không hợp lệ hoặc không có quyền truy cập.
- **Privileged instruction exception:** chương trình user mode cố thực thi instruction chỉ dành cho kernel mode.
Khi có debugger, debugger nhận first chance trước exception handler của chương trình. Vì thế malware có thể lợi dụng sự khác biệt này để phát hiện debugger.
***Modifying Execution with a Debugger***
Debugger không chỉ quan sát mà còn có thể thay đổi chương trình bằng cách sửa:
- Thanh ghi.
- Instruction pointer.
- Cờ điều khiển.
- Dữ liệu trong bộ nhớ.
- Instruction của chương trình.
Ví dụ, để bỏ qua một lời gọi hàm, ta có thể đặt breakpoint tại `call`, sau đó chỉnh instruction pointer đến instruction nằm sau `call`.
Tuy nhiên, bỏ qua một hàm có thể khiến chương trình crash nếu hàm đó chịu trách nhiệm:
- Khởi tạo dữ liệu.
- Cấp phát bộ nhớ.
- Thiết lập trạng thái.
- Trả về giá trị được dùng ở phía sau.
Ta cũng có thể ép CPU chạy một hàm cụ thể bằng cách tự chuẩn bị tham số, chỉnh instruction pointer về đầu hàm rồi single-step. Cách này có thể phá hỏng stack và trạng thái chương trình, nhưng vẫn hữu ích để nhanh chóng xác định một hàm đang làm gì.
***Modifying Program Execution in Practice***
Ví dụ thực tế trong tài liệu là một virus thay đổi hành vi dựa trên ngôn ngữ hệ thống:
- English: hiển thị thông báo.
- Simplified Chinese: tự gỡ bỏ và không gây hại.
- Japanese hoặc Indonesian: ghi dữ liệu rác lên ổ đĩa.
Chương trình gọi `GetSystemDefaultLCID`, sau đó so sánh giá trị trả về trong `EAX` với các locale ID.
Thay vì thực sự đổi ngôn ngữ của máy, người phân tích có thể:
1. Đặt breakpoint ngay sau `GetSystemDefaultLCID`.
2. Sửa `EAX` thành `0x0411`, tương ứng với Japanese.
3. Tiếp tục chạy để ép chương trình đi vào nhánh dành cho hệ thống Nhật.
Kỹ thuật này cho phép kiểm tra nhiều nhánh chương trình mà không cần thay đổi môi trường thật. Với malware, việc đó chỉ nên được thực hiện trong máy ảo có thể hủy bỏ.

# **9. OllyDBG**

# **10. Kernel debugging with WinDBG**
WinDbg là debugger miễn phí của Microsoft. So với OllyDbg, ưu thế quan trọng nhất của WinDbg là khả năng debug kernel. Chương này tập trung vào kernel debugging và phân tích rootkit, mặc dù nhiều tính năng của WinDbg cũng dùng được khi debug user mode.
*a) Drivers and Kernel Code*
Trước khi debug mã độc chạy trong kernel, cần hiểu driver hoạt động như thế nào và tại sao malware muốn chạy ở mức này.
Windows device driver cho phép nhà phát triển bên thứ ba thực thi code trong kernel. Driver khó phân tích vì nó:
- Được nạp vào kernel và thường tồn tại lâu dài trong bộ nhớ.
- Phản hồi yêu cầu từ nhiều chương trình khác nhau.
- Không được ứng dụng user mode gọi trực tiếp.
- Hoạt động thông qua các device object.
Device object không nhất thiết đại diện cho phần cứng vật lý. Driver có thể tự tạo và hủy device object để chương trình user mode truy cập.
Ví dụ, khi cắm USB vào máy:
1. Windows đã có driver quản lý USB.
2. Hệ điều hành tạo một device object, chẳng hạn ổ `F:`.
3. Ứng dụng gửi yêu cầu tới `F:`, không gọi trực tiếp driver USB.
4. Windows chuyển yêu cầu từ device object tới driver tương ứng.
5. Nếu cắm thêm USB khác, cùng driver đó có thể quản lý device object `G:`.
Driver được nạp vào kernel tương tự cách DLL được nạp vào tiến trình. Khi driver bắt đầu chạy, Windows gọi hàm `DriverEntry`, gần tương đương `DllMain` của DLL.
Tuy nhiên, driver thường không cung cấp chức năng thông qua export table như DLL. Thay vào đó:
6. Windows tạo một cấu trúc `DRIVER_OBJECT`.
7. Windows truyền con trỏ tới cấu trúc này cho `DriverEntry`.
8. `DriverEntry` điền địa chỉ các callback vào bảng `MajorFunction`.
9. Driver tạo device object.
10. Chương trình user mode mở device object và gửi yêu cầu tới driver.
Ví dụ, khi chương trình gọi `ReadFile` trên handle của một device object, kernel xử lý yêu cầu và cuối cùng gọi callback chịu trách nhiệm xử lý thao tác đọc của driver.
Một API thường gặp khi phân tích driver độc hại là:
```
DeviceIoControl(
    hDevice,
    dwIoControlCode,
    lpInBuffer,
    nInBufferSize,
    lpOutBuffer,
    nOutBufferSize,
    lpBytesReturned,
    lpOverlapped
);
```
`DeviceIoControl` là giao diện tổng quát cho phép chương trình user mode gửi một buffer đầu vào tới driver và nhận lại buffer đầu ra.
Việc trace từ lời gọi user mode xuống driver khá khó vì yêu cầu phải đi qua nhiều lớp code của hệ điều hành:
```
Ứng dụng
    ↓
kernel32.dll
    ↓
ntdll.dll
    ↓
ntoskrnl.exe
    ↓
Device object
    ↓
Driver
```
![[Pasted image 20260919233337.png]]
Một số kernel malware không có thành phần user mode đáng kể. Nó không cần tạo device object mà có thể tự hoạt động hoàn toàn trong kernel.
Driver độc hại thường không thực sự điều khiển phần cứng. Thay vào đó, nó tương tác với:
- `ntoskrnl.exe`: chứa phần lớn chức năng cốt lõi của Windows kernel.
- `hal.dll`: Hardware Abstraction Layer, phụ trách tương tác với phần cứng ở mức thấp.
*b) Setting Up Kernel Debugging*
Kernel debugging phức tạp hơn user-mode debugging. Khi kernel bị dừng tại breakpoint, toàn bộ hệ điều hành target cũng dừng, vì vậy không thể chạy debugger ngay trên hệ thống đó theo cách thông thường.
Mô hình phổ biến gồm:
- ==Target:== máy ảo hoặc máy vật lý chạy kernel/driver cần debug.
- ==Host:== máy chạy WinDbg.
- ==Kết nối debug:== serial, named pipe, USB hoặc mạng.
Tài liệu sử dụng Windows XP trong VMware và cấu hình kết nối bằng virtual serial port. Trước khi chỉnh cấu hình khởi động, nên tạo snapshot của máy ảo.
***Cấu hình Windows XP trong tài liệu***
Tài liệu thêm một entry vào `C:\boot.ini`:
```
[boot loader]
timeout=30
default=multi(0)disk(0)rdisk(0)partition(1)\WINDOWS

[operating systems]
multi(0)disk(0)rdisk(0)partition(1)\WINDOWS="Microsoft Windows XP Professional" /noexecute=optin /fastdetect

multi(0)disk(0)rdisk(0)partition(1)\WINDOWS="Microsoft Windows XP Professional with Kernel Debugging" /noexecute=optin /fastdetect /debug /debugport=COM1 /baudrate=115200
```
Trong đó:
- `/debug`: bật kernel debugging.
- `/debugport=COM1`: sử dụng cổng COM1.
- `/baudrate=115200`: tốc độ truyền của kết nối serial.
Sau khi cấu hình, boot loader cho phép lựa chọn khởi động Windows bình thường hoặc Windows với kernel debugging được bật.
Việc bật chế độ debugging không bắt buộc phải luôn có debugger kết nối. Hệ điều hành vẫn có thể chạy nếu WinDbg chưa attach.
***Cấu hình VMware***
Tài liệu hướng dẫn thêm serial port vào máy ảo:
1. Mở ==VM → Settings==.
2. Chọn ==Add → Serial Port==.
3. Chọn ==Output to Named Pipe==.
4. Đặt tên pipe:
```
\\.\pipe\com_1
```
5. Chọn:
```
This end is the server
The other end is an application
```
6. Bật tùy chọn ==Yield CPU on poll==.
![[Pasted image 20260919233741.png]]
***Kết nối bằng WinDbg
Trên host***
7. Khởi chạy WinDbg.
8. Chọn ==File → Kernel Debug==.
9. Mở tab ==COM==.
10. Nhập named pipe và baud rate `115200`.
11. Đánh dấu tùy chọn ==Pipe==.
12. Khởi động máy ảo.
![[Pasted image 20260919233843.png]]
Khi kết nối thành công, nên bật verbose output để WinDbg thông báo mỗi lần driver được load hoặc unload. Điều này có thể giúp phát hiện driver đáng ngờ.
*c) Using WinDBG*
Phần lớn chức năng nâng cao của WinDbg được điều khiển qua command line. WinDbg cung cấp lệnh để:
- Đọc và ghi bộ nhớ.
- Tính toán địa chỉ.
- Đặt breakpoint.
- Liệt kê module.
- Tải symbol.
- Hiển thị cấu trúc dữ liệu kernel.
- Tìm driver và device object.
***Reading from Memory***
Nhóm lệnh `d` được sử dụng để đọc bộ nhớ:
```
d<kiểu-hiển-thị> địa_chỉ
```

| Lệnh | Ý nghĩa                                    |
| ---- | ------------------------------------------ |
| `da` | Đọc và hiển thị dưới dạng chuỗi ASCII      |
| `du` | Đọc và hiển thị dưới dạng chuỗi Unicode    |
| `dd` | Đọc và hiển thị dưới dạng các DWORD 32-bit |

Ví dụ, để đọc chuỗi ASCII tại địa chỉ `0x401020`:
```
da 0x401020
```
Nhóm lệnh `e` được sử dụng để ghi dữ liệu vào bộ nhớ:
```
e<kiểu-dữ-liệu> địa_chỉ dữ_liệu
```
Ví dụ:
```
eb 0x401020 41
```
Lệnh trên ghi byte `0x41`, tức ký tự `A`, vào địa chỉ `0x401020`.
***Using Arithmetic Operators***
WinDbg cho phép thực hiện trực tiếp các phép toán trên địa chỉ, thanh ghi và biểu thức:
```
+
-
*
/
```
Điều này hữu ích khi:
- Tính offset của một trường trong structure.
- Lấy tham số từ stack.
- Tạo biểu thức cho conditional breakpoint.
- Tính vị trí phần tử trong một bảng con trỏ.
Tài liệu sử dụng toán tử `dwo` để dereference một con trỏ 32-bit. Giả sử chương trình 32-bit dừng tại đầu hàm và tham số đầu tiên là con trỏ tới chuỗi Unicode, tham số đó nằm tại `esp+4`:
```
du dwo(esp+4)
```
Ý nghĩa:
1. `esp+4` xác định vị trí tham số đầu tiên trên stack.
2. `dwo(...)` đọc DWORD tại đó để lấy giá trị con trỏ.
3. `du` đọc dữ liệu tại địa chỉ con trỏ dưới dạng chuỗi Unicode.
***Setting Breakpoints***
Lệnh `bp` đặt software breakpoint:
```
bp địa_chỉ
```
WinDbg còn cho phép breakpoint tự động thực hiện một chuỗi lệnh. Ví dụ:
```
bp GetProcAddress "da dwo(esp+8); g"
```
Mỗi lần `GetProcAddress` được gọi, breakpoint sẽ:
1. Lấy tham số thứ hai tại `esp+8`.
2. Dereference con trỏ bằng `dwo`.
3. In tên API dưới dạng ASCII bằng `da`.
4. Dùng `g` để tiếp tục chạy ngay lập tức.
Nhờ vậy, ta có thể ghi lại toàn bộ API mà chương trình phân giải động mà không cần dừng thủ công ở mỗi lần gọi.
WinDbg còn hỗ trợ các cấu trúc lệnh như:
```
.if
.else
.while
```
Do đó, có thể viết script hoặc breakpoint có điều kiện khá phức tạp.
Nếu tham số thứ hai của `GetProcAddress` là ordinal thay vì con trỏ chuỗi, WinDbg có thể cố đọc một địa chỉ không hợp lệ. Khi đó nó thường chỉ hiển thị:
```
????
```
thay vì làm debugger crash.
***Listing Modules***
Lệnh `lm` liệt kê các module đã được load:
```
lm
```
Trong user mode, danh sách có thể chứa:
- File thực thi chính.
- Các DLL.
Trong kernel mode, danh sách còn chứa:
- `ntoskrnl.exe`.
- `hal.dll`.
- Các driver `.sys`.
WinDbg hiển thị địa chỉ bắt đầu và kết thúc của từng module, giúp xác định một địa chỉ thuộc module nào.
*d) Microsoft Symbols*
Debugging symbol cung cấp tên và một phần thông tin kiểu dữ liệu từ mã nguồn.
Nếu không có symbol, WinDbg có thể chỉ hiển thị:
```
8050f1a2
```
Khi có symbol, địa chỉ đó có thể được hiển thị thành:
```
nt!MmCreateProcessAddressSpace
```
Tên hàm cho ta manh mối rất lớn về mục đích của code. Symbol có thể đại diện cho:
- Hàm.
- Biến toàn cục.
- Cấu trúc.
- Kiểu dữ liệu.
- Trường bên trong cấu trúc.
Symbol của Microsoft đặc biệt hữu ích khi phân tích kernel vì nó cung cấp thông tin về nhiều cấu trúc nội bộ vốn không được mô tả đầy đủ trong tài liệu công khai.
***Searching for Symbols***
Cú pháp tham chiếu symbol trong WinDbg:
```
module!symbol
```
Ví dụ:
```
nt!NtCreateProcess
```
`nt` là tên module đặc biệt được dùng cho `ntoskrnl.exe`.
Để disassemble hàm:
```
u nt!NtCreateProcess
```
Nếu không chỉ định module, WinDbg phải tìm trong symbol của tất cả module đã load, nên có thể mất nhiều thời gian.
***Deferred breakpoint***
Lệnh `bu` cho phép đặt breakpoint dựa trên symbol ngay cả khi module chưa được load:
```
bu newModule!exportedFunction
```
WinDbg sẽ chờ đến khi `newModule` được load, sau đó tự động kích hoạt breakpoint.
Để đặt breakpoint tại entry point của driver:
```
bu $iment(driverName)
```
Cách này cho phép debugger dừng trước khi code chính của driver bắt đầu thực thi.
***Tìm symbol bằng wildcard***
Lệnh `x` tìm symbol:
```
x nt!*CreateProcess*
```
Kết quả có thể bao gồm:
```
nt!NtCreateProcessEx
nt!NtCreateProcess
nt!PspCreateProcess
nt!ZwCreateProcess
nt!PsSetCreateProcessNotifyRoutine
nt!MmCreateProcessAddressSpace
```
***Tìm symbol gần một địa chỉ***
Lệnh `ln` liệt kê symbol gần nhất:
```
ln 805717aa
```
Ví dụ, kết quả có thể cho biết địa chỉ đó chính xác là:
```
nt!NtReadFile
```
***Viewing Structure Information***
Lệnh `dt` hiển thị định nghĩa của một kiểu hoặc structure:
```
dt nt!_DRIVER_OBJECT
```
Một phần cấu trúc `_DRIVER_OBJECT`:
```
+0x000 Type
+0x002 Size
+0x004 DeviceObject
+0x008 Flags
+0x00c DriverStart
+0x010 DriverSize
+0x014 DriverSection
+0x018 DriverExtension
+0x01c DriverName
+0x02c DriverInit
+0x030 DriverStartIo
+0x034 DriverUnload
+0x038 MajorFunction
```
`DriverStart` cho biết địa chỉ driver được load trong bộ nhớ. `MajorFunction` là bảng chứa các callback xử lý I/O.
Nếu biết địa chỉ một driver object, có thể overlay structure lên dữ liệu thật:
```
dt nt!_DRIVER_OBJECT 828b2648
```
Ví dụ với driver `Beep`:
```
DriverName   : "\Driver\Beep"
DriverInit   : Beep!DriverEntry
DriverUnload : Beep!BeepUnload
MajorFunction: Beep!BeepOpen
```
`DriverInit` rất đáng chú ý vì đây là code được chạy mỗi lần driver được load. Một số malware đặt toàn bộ payload trong hàm khởi tạo này.
***Configuring Windows Symbols***
Symbol phải khớp chính xác với phiên bản của file đang debug. Mỗi bản vá hoặc cập nhật Windows có thể thay đổi địa chỉ và symbol tương ứng.
Tài liệu cấu hình symbol server bằng đường dẫn:
```
SRV*c:\websymbols*http://msdl.microsoft.com/download/symbols
```
Trong đó:
- `SRV` chỉ định nguồn là symbol server.
- `c:\websymbols` là thư mục cache cục bộ.
- URL phía sau là Microsoft Symbol Server.
Cấu hình hiện đại thường sử dụng:
```
.symfix
.reload
```
hoặc:
```
.sympath srv*
.reload
```
Nếu máy phân tích không có Internet, có thể tải trước symbol phù hợp với phiên bản, kiến trúc và bản cập nhật của Windows.

*e) Kernel Debugging in Practice*
Ví dụ thực hành phân tích một chương trình sử dụng driver để ghi file từ kernel mode.
Việc ghi file từ kernel có thể khó phát hiện hơn vì malware không gọi trực tiếp các API user mode quen thuộc như:
```
CreateFile
WriteFile
```
Thay vào đó, kernel code sử dụng các hàm tương ứng:
```
ZwCreateFile
ZwWriteFile
```
Quá trình phân tích được chia thành hai phần:
1. Phân tích thành phần user mode bằng IDA.
2. Phân tích driver trong kernel bằng WinDbg.
***Looking at the User-Space Code***
Đầu tiên, thành phần user mode gọi `CreateServiceA` để đăng ký driver.
```asm
04001B3D push esi ; lpPassword
04001B3E push esi ; lpServiceStartName
04001B3F push esi ; lpDependencies
04001B40 push esi ; lpdwTagId
04001B41 push esi ; lpLoadOrderGroup
216 Chapter 10
04001B42 push [ebp+lpBinaryPathName] ; lpBinaryPathName
04001B45 push 1 ; dwErrorControl
04001B47 push 3 ; dwStartType
04001B49 push 1 ; dwServiceType
04001B4B push 0F01FFh ; dwDesiredAccess
04001B50 push [ebp+lpDisplayName] ; lpDisplayName
04001B53 push [ebp+lpDisplayName] ; lpServiceName
04001B56 push [ebp+hSCManager] ; hSCManager
04001B59 call ds:__imp__CreateServiceA@52
```
Tham số:
```
dwServiceType = 1
```
tương ứng với:
```
SERVICE_KERNEL_DRIVER
```
Điều này cho biết service được tạo là một kernel driver.
Sau đó, chương trình gọi `CreateFileA` để lấy handle tới device object:
```asm
04001893 xor eax, eax
04001895 push eax ; hTemplateFile
04001896 push 80h ; dwFlagsAndAttributes
0400189B push 2 ; dwCreationDisposition
0400189D push eax ; lpSecurityAttributes
0400189E push eax ; dwShareMode
0400189F push ebx ; dwDesiredAccess
040018A0 push edi ; lpFileName
040018A1 call esi ; CreateFileA
```
Tên device được sử dụng:
```
\\.\FileWriterDevice
```
Ở đây chương trình không mở một file thông thường. Nó mở device object do driver tạo ra.
Khi đã có handle, chương trình gọi `DeviceIoControl`:
```asm
04001910 push 0 ; lpOverlapped
04001912 sub eax, ecx
04001914 lea ecx, [ebp+BytesReturned]
0400191A push ecx ; lpBytesReturned
0400191B push 64h ; nOutBufferSize
0400191D push edi ; lpOutBuffer
0400191E inc eax
0400191F push eax ; nInBufferSize
04001920 push esi ; lpInBuffer
04001921 push 9C402408h ; dwIoControlCode
04001926 push [ebp+hObject] ; hDevice
0400192C call ds:DeviceIoControl
```
Các thông tin đáng chú ý:
```
hDevice        = handle của FileWriterDevice
dwIoControlCode = 0x9C402408
lpInBuffer      = dữ liệu gửi vào driver
lpOutBuffer     = buffer nhận dữ liệu trả về
```
Đây là điểm nối giữa thành phần user mode và code trong driver.
***Looking at the Kernel-Mode Code***
Khi bật verbose output, WinDbg thông báo mỗi lần kernel module được load:
```
ModLoad: f7b0d000 f7b0e780 FileWriter.sys
```
Nếu module xuất hiện đúng lúc chạy mẫu malware, nó có thể là driver đáng ngờ.
Lệnh sau tìm driver object:
```
!drvobj FileWriter
```
```
kd>dt nt!_DRIVER_OBJECT 0x827e3698
nt!_DRIVER_OBJECT
+0x000 Type : 4
+0x002 Size : 168
+0x004 DeviceObject : 0x826eb030 _DEVICE_OBJECT
+0x008 Flags : 0x12
+0x00c DriverStart : 0xf7b0d000
+0x010 DriverSize : 0x1780
+0x014 DriverSection : 0x828006a8
+0x018 DriverExtension : 0x827e3740 _DRIVER_EXTENSION
+0x01c DriverName : _UNICODE_STRING "\Driver\FileWriter"
+0x024 HardwareDatabase : 0x8066ecd8 _UNICODE_STRING "\REGISTRY\MACHINE\
HARDWARE\DESCRIPTION\SYSTEM"
+0x028 FastIoDispatch : (null)
+0x02c DriverInit : 0xf7b0dfcd long +0
+0x030 DriverStartIo : (null)
+0x034 DriverUnload : 0xf7b0da2a void +0
+0x038 MajorFunction : [28] 0xf7b0da06 long +0
```
Kết quả cho biết:
- Địa chỉ driver object.
- Tên driver.
- Danh sách device object.
- Trạng thái symbol.
Nếu `!drvobj` thất bại hoặc tên driver object khác tên file, có thể liệt kê namespace driver:
```
!object \Driver
```
Sau khi lấy địa chỉ driver object, dùng:
```
dt nt!_DRIVER_OBJECT 0x827e3698
```

```
kd> dd 827e3698+0x38+e*4 L1

827e3708 f7b0da66

kd> u f7b0da66

FileWriter+0xa66:

f7b0da66 6a68 push 68h

f7b0da68 6838d9b0f7 push offset FileWriter+0x938 (f7b0d938)

f7b0da6d e822faffff call FileWriter+0x494 (f7b0d494)
```
Trường quan trọng:
```
MajorFunction : [28] ...
```
Đây là bảng dispatch routine. Mỗi phần tử tương ứng một loại IRP như:
```
IRP_MJ_CREATE
IRP_MJ_READ
IRP_MJ_WRITE
IRP_MJ_DEVICE_CONTROL
```
`DeviceIoControl` được chuyển tới callback tại chỉ số:
```
IRP_MJ_DEVICE_CONTROL = 0xE
```
Trong ví dụ 32-bit, bảng `MajorFunction` bắt đầu ở offset `0x38`, mỗi con trỏ dài 4 byte:
```
dd 827e3698+0x38+e*4 L1
```
Kết quả:
```
827e3708 f7b0da66
```
Để kiểm tra code tại địa chỉ đó:
```
u f7b0da66
```
```
F7B0DCB1 push offset aDosdevicesCSec ; "\\DosDevices\\C:\\secretfile.txt"
F7B0DCB6 lea eax, [ebp-54h]
F7B0DCB9 push eax ; DestinationString
F7B0DCBA call ds:RtlInitUnicodeString
F7B0DCC0 mov dword ptr [ebp-74h], 18h
F7B0DCC7 mov [ebp-70h], ebx
F7B0DCCA mov dword ptr [ebp-68h], 200h
F7B0DCD1 lea eax, [ebp-54h]
F7B0DCD4 mov [ebp-6Ch], eax
F7B0DCD7 mov [ebp-64h], ebx
F7B0DCDA mov [ebp-60h], ebx
F7B0DCDD push ebx ; EaLength
F7B0DCDE push ebx ; EaBuffer
F7B0DCDF push 40h ; CreateOptions
F7B0DCE1 push 5 ; CreateDisposition
F7B0DCE3 push ebx ; ShareAccess
F7B0DCE4 push 80h ; FileAttributes
F7B0DCE9 push ebx ; AllocationSize
F7B0DCEA lea eax, [ebp-5Ch]
F7B0DCED push eax ; IoStatusBlock
F7B0DCEE lea eax, [ebp-74h]
F7B0DCF1 push eax ; ObjectAttributes
F7B0DCF2 push 1F01FFh ; DesiredAccess
F7B0DCF7 push offset FileHandle ; FileHandle
F7B0DCFC call ds:ZwCreateFile
F7B0DD02 push ebx ; Key
F7B0DD03 lea eax, [ebp-4Ch]
F7B0DD06 push eax ; ByteOffset
F7B0DD07 push dword ptr [ebp-24h] ; Length
F7B0DD0A push esi ; Buffer
F7B0DD0B lea eax, [ebp-5Ch]
F7B0DD0E push eax ; IoStatusBlock
F7B0DD0F push ebx ; ApcContext
F7B0DD10 push ebx ; ApcRoutine
F7B0DD11 push ebx ; Event
F7B0DD12 push FileHandle ; FileHandle
F7B0DD18 call ds:ZwWriteFile
```
Sau khi tìm được dispatch routine, có thể:
- Tiếp tục phân tích động bằng WinDbg.
- Load driver vào IDA để đọc assembly và pseudocode trước.
- Quay lại WinDbg khi cần quan sát dữ liệu runtime.
Tài liệu khuyến nghị phân tích tĩnh bằng IDA trước, sau đó sử dụng WinDbg cho những phần cần kiểm tra động.
Trong dispatch routine của `FileWriter.sys`, malware gọi:
```
RtlInitUnicodeString
ZwCreateFile
ZwWriteFile
```
Tên file được tạo:
```
\DosDevices\C:\secretfile.txt
```
Kernel sử dụng cấu trúc `UNICODE_STRING`, không đơn thuần là chuỗi wide-character kết thúc bằng null như trong nhiều API user mode.
`RtlInitUnicodeString` được dùng để khởi tạo `UNICODE_STRING` từ chuỗi wide-character.
Ngoài `DeviceIoControl`, các API như `CreateFile`, `ReadFile` và `WriteFile` cũng có thể tạo request gửi tới driver. Ví dụ:
```
ReadFile → IRP_MJ_READ
```
Vì:
```
IRP_MJ_READ = 0x3
```
nên với cấu trúc 32-bit, callback đọc được tìm bằng:
```
MajorFunction + 0x3 * 4
```
***Finding Driver Objects***
Không phải lúc nào tên file driver cũng giúp tìm ngay driver object.
Vì chương trình user mode tương tác với device object, ta có thể lần ngược từ device object tới driver object.
Nếu phát hiện chương trình mở:
```
\\.\FileWriterDevice
```
có thể chạy:
```
!devobj FileWriterDevice
```
uả chứa con trỏ:
```
Device object → Driver object
```
Sau khi có driver object, ta có thể xem bảng `MajorFunction` và các callback của driver.
Để tìm chương trình user mode nào đang giữ handle tới device object:
```
!devhandles 826eb030
```
Lệnh này duyệt handle table của các tiến trình nên có thể chạy khá lâu.
```
kd>!devhandles 826eb030
...
Checking handle table for process 0x829001f0
Handle table at e1d09000 with 32 Entries in use
Checking handle table for process 0x8258d548
Handle table at e1cfa000 with 114 Entries in use
Checking handle table for process 0x82752da0
Handle table at e1045000 with 18 Entries in use
PROCESS 82752da0 SessionId: 0 Cid: 0410 Peb: 7ffd5000 ParentCid: 075c
DirBase: 09180240 ObjectTable: e1da0180 HandleCount: 18.
Image: FileWriterApp.exe
07b8: Object: 826eb0e8 GrantedAccess: 0012019f
```
Trong ví dụ, kết quả xác định:
```
Image: FileWriterApp.exe
```
Như vậy, quá trình truy vết có thể đi theo hướng:
```
Device object
    → Driver object
    → Driver callbacks
    → Các tiến trình giữ handle tới device
```

*f) Rootkits*
Rootkit sửa đổi chức năng nội bộ của hệ điều hành để che giấu sự tồn tại của nó. Nó có thể ẩn:
- File.
- Tiến trình.
- Kết nối mạng.
- Registry key.
- Driver.
- Các tài nguyên khác.
Tài liệu tập trung vào kỹ thuật **System Service Descriptor Table hooking**, gọi tắt là **SSDT hooking**.
SSDT là bảng được kernel sử dụng để tìm địa chỉ hàm xử lý system call. Trong ví dụ Windows XP 32-bit:
1. `ntdll.dll` đưa mã số system call vào `EAX`.
2. Chương trình thực thi `SYSENTER`.
3. Kernel dùng giá trị `EAX` làm chỉ số vào SSDT.
4. Entry trong SSDT chỉ tới hàm kernel tương ứng.
Ví dụ:
```
mov eax, 25h
mov edx, 7FFE0300h
call dword ptr [edx]
```
Sau đó:
```
mov edx, esp
sysenter
```
Ở đây `0x25` là mã system call của `NtCreateFile` trên phiên bản Windows trong ví dụ.
```
SSDT[0x22] = 805b28bc (NtCreateaDirectoryObject)
SSDT[0x23] = 80603be0 (NtCreateEvent)
SSDT[0x24] = 8060be48 (NtCreateEventPair)
SSDT[0x25] = 8056d3ca (NtCreateFile)
SSDT[0x26] = 8056bc5c (NtCreateIoCompletion)
SSDT[0x27] = 805ca3ca (NtCreateJobObject)
```

```
SSDT[0x25] = địa chỉ NtCreateFile
```
Rootkit có thể thay entry này bằng địa chỉ hook của nó:
```
SSDT[0x25] = địa chỉ hook trong driver độc hại
```
Khi chương trình gọi `NtCreateFile`, luồng thực thi đi qua hook trước. Hook có thể:
1. Gọi `NtCreateFile` gốc.
2. Kiểm tra tên file.
3. Chặn hoặc lọc các file cần ẩn.
4. Trả kết quả giả cho chương trình user mode.
Chỉ hook `NtCreateFile` chưa chắc ẩn được file khỏi directory listing, vì việc liệt kê thư mục có thể sử dụng system call khác.
***Rootkit Analysis in Practice***
Cách trực tiếp để phát hiện SSDT hook là kiểm tra các địa chỉ trong SSDT.
Các entry hợp lệ thông thường phải trỏ vào phạm vi địa chỉ của `ntoskrnl.exe`. Trước tiên dùng `lm` để xác định vùng địa chỉ của module `nt`:
```
lm m nt
```
Sau đó kiểm tra SSDT tại:
```
nt!KeServiceDescriptorTable
```
Nếu một entry trỏ ra ngoài phạm vi `nt`, nó có thể đã bị hook.
```
kd> lm m nt
...
8050122c 805c9928 805c98d8 8060aea6 805aa334
8050123c 8060a4be 8059cbbc 805a4786 805cb406
8050124c 804feed0 8060b5c4 8056ae64 805343f2
8050125c 80603b90 805b09c0 805e9694 80618a56
8050126c 805edb86 80598e34 80618caa 805986e6
8050127c 805401f0 80636c9c 805b28bc 80603be0
8050128c 8060be48 f7ad94a4 8056bc5c 805ca3ca
8050129c 805ca102 80618e86 8056d4d8 8060c240
805012ac 8056d404 8059fba6 80599202 805c5f8e
```
Trong ví dụ, entry tại offset `0x25` trỏ tới:
```
f7ad94a4
```
Địa chỉ này nằm ngoài `ntoskrnl.exe`, nên rất đáng ngờ.
Dùng `lm` để xác định module chứa địa chỉ:
```
kd>lm
...
f7ac7000 f7ac8580 intelide (deferred)
f7ac9000 f7aca700 dmload (deferred)
f7ad9000 f7ada680 Rootkit (deferred)
f7aed000 f7aee280 vmmouse (deferred)
...
```
Kết quả cho thấy địa chỉ nằm trong:
```
Rootkit.sys
```
Sau khi xác định driver, cần tìm:
- Code cài hook.
- Hàm hook thực sự xử lý request.
```
00010D0D push offset aNtcreatefile ; "NtCreateFile"
00010D12 lea eax, [ebp+NtCreateFileName]
00010D15 push eax ; DestinationString
00010D16 mov edi, ds:RtlInitUnicodeString
00010D1C call edi ; RtlInitUnicodeString
00010D1E push offset aKeservicedescr ; "KeServiceDescriptorTable"
00010D23 lea eax, [ebp+KeServiceDescriptorTableString]
00010D26 push eax ; DestinationString
00010D27 call edi ; RtlInitUnicodeString
00010D29 lea eax, [ebp+NtCreateFileName]
00010D2C push eax ; SystemRoutineName
00010D2D mov edi, ds:MmGetSystemRoutineAddress
00010D33 call edi ; MmGetSystemRoutineAddress
00010D35 mov ebx, eax
00010D37 lea eax, [ebp+KeServiceDescriptorTableString]
00010D3A push eax ; SystemRoutineName
00010D3B call edi ; MmGetSystemRoutineAddress
00010D3D mov ecx, [eax]
00010D3F xor edx, edx
00010D41 ; CODE XREF: sub_10CE7+68 j
00010D41 add ecx, 4
00010D44 cmp [ecx], ebx
00010D46 jz short loc_10D51
00010D48 inc edx
00010D49 cmp edx, 11Ch
224 Chapter 10
00010D4F jl short loc_10D41
00010D51 ; CODE XREF: sub_10CE7+5F j
00010D51 mov dword_10A0C, ecx
00010D57 mov dword_10A08, ebx
00010D5D mov dword ptr [ecx], offset sub_104A4
```
Code mẫu thực hiện:
1. Tạo chuỗi `NtCreateFile`.
2. Tạo chuỗi `KeServiceDescriptorTable`.
3. Gọi `MmGetSystemRoutineAddress` để lấy địa chỉ hai symbol này.
4. Duyệt SSDT để tìm entry chứa địa chỉ `NtCreateFile`.
5. Ghi địa chỉ hàm hook vào entry đó.
`MmGetSystemRoutineAddress` có vai trò gần giống `GetProcAddress` trong kernel, nhưng chỉ tra cứu một số routine được export bởi các module kernel phù hợp.
```
000104A4 mov edi, edi
000104A6 push ebp
000104A7 mov ebp, esp
000104A9 push [ebp+arg_8]
000104AC call sub_10486
000104B1 test eax, eax
000104B3 jz short loc_104BB
000104B5 pop ebp
000104B6 jmp NtCreateFile
000104BB -----------------------------
000104BB ; CODE XREF: sub_104A4+F j
000104BB mov eax, 0C0000034h
000104C0 pop ebp
000104C1 retn 2Ch
```
Hàm hook kiểm tra `ObjectAttributes`, trong đó có thông tin như tên file:
```
Nếu cho phép:
    jmp NtCreateFile gốc

Nếu muốn chặn:
    return 0xC0000034
```
Mã lỗi:
```
0xC0000034 = STATUS_OBJECT_NAME_NOT_FOUND
```
Vì vậy, ứng dụng nhận thông báo rằng file không tồn tại, mặc dù file thực sự vẫn có trên hệ thống.
***Interrupts***
Interrupt cho phép phần cứng báo cho CPU rằng một sự kiện đã xảy ra hoặc một thao tác đã hoàn thành.
Driver có thể gọi:
```
IoConnectInterrupt
```
để đăng ký một **Interrupt Service Routine – ISR**. Khi interrupt tương ứng xuất hiện, Windows gọi ISR đó.
Thông tin ISR được lưu trong **Interrupt Descriptor Table – IDT**. Có thể xem IDT trong WinDbg bằng:
```
!idt
```

```
kd> !idt
37: 806cf728 hal!PicSpuriousService37
3d: 806d0b70 hal!HalpApcInterrupt
41: 806d09cc hal!HalpDispatchInterrupt
50: 806cf800 hal!HalpApicRebootService
62: 8298b7e4 atapi!IdePortInterrupt (KINTERRUPT 8298b7a8)
63: 826ef044 NDIS!ndisMIsr (KINTERRUPT 826ef008)
73: 826b9044 portcls!CKsShellRequestor::`vector deleting destructor'+0x26
(KINTERRUPT 826b9008)
USBPORT!USBPORT_InterruptService (KINTERRUPT 826df008)
82: 82970dd4 atapi!IdePortInterrupt (KINTERRUPT 82970d98)
83: 829e8044 SCSIPORT!ScsiPortInterrupt (KINTERRUPT 829e8008)
93: 826c315c i8042prt!I8042KeyboardInterruptService (KINTERRUPT 826c3120)
a3: 826c2044 i8042prt!I8042MouseInterruptService (KINTERRUPT 826c2008)
b1: 829e5434 ACPI!ACPIInterruptServiceRoutine (KINTERRUPT 829e53f8)
b2: 826f115c serial!SerialCIsrSw (KINTERRUPT 826f1120)
c1: 806cf984 hal!HalpBroadcastCallService
d1: 806ced34 hal!HalpClockInterrupt
e1: 806cff0c hal!HalpIpiHandler
e3: 806cfc70 hal!HalpLocalApicErrorService
fd: 806d0464 hal!HalpProfileInterrupt
fe: 806d0604 hal!HalpPerfInterrupt
```
IDT bình thường thường trỏ tới các handler của những module quen thuộc như:
```
hal
atapi
NDIS
USBPORT
SCSIPORT
ACPI
i8042prt
```
Nếu một interrupt trỏ tới:
- Driver không có tên.
- Driver không được ký.
- Module ở vùng địa chỉ đáng ngờ.
- Driver không liên quan tới loại phần cứng đó.
thì đó có thể là dấu hiệu của rootkit hoặc driver độc hại.

*g) Loading Drivers*
Nếu chỉ có file driver độc hại mà không có chương trình user mode dùng để cài đặt nó, tài liệu đề xuất sử dụng **OSR Driver Loader**.
Quy trình:
1. Chọn file `.sys`.
2. Chọn **Register Service**.
3. Chọn **Start Service**.
4. Theo dõi quá trình load bằng WinDbg.
![[Pasted image 20260920000210.png]]
Driver không đáng tin cậy chỉ nên được nạp trong máy ảo phân tích có snapshot và được cô lập phù hợp.

*h) Kernel Issues for Windows Vista, Windows 7, and x64 Versions*
Các phiên bản Windows mới hơn Windows XP thay đổi đáng kể việc debug kernel và hoạt động của kernel malware.
***BCDEdit thay thế boot.ini***
Từ Windows Vista trở đi, Windows không còn dùng `boot.ini`. Boot configuration được quản lý bằng:
```
BCDEdit
```
Do đó, muốn bật kernel debugging trên Windows mới phải cấu hình BCD thay vì sửa `boot.ini`.
***PatchGuard***
Windows x64 triển khai **Kernel Patch Protection**, thường gọi là **PatchGuard**.
PatchGuard chống việc code bên thứ ba sửa đổi:
- Kernel code.
- System service table.
- IDT.
- Một số cấu trúc và vùng kernel quan trọng khác.
Mục đích là ngăn rootkit patch trực tiếp kernel, nhưng cơ chế này cũng ảnh hưởng tới phần mềm bảo mật và công cụ debug sử dụng kỹ thuật tương tự.
Tài liệu nói rằng nếu kernel debugger đã attach từ lúc boot thì PatchGuard có thể không hoạt động theo cách bình thường; còn attach sau khi boot trong một số cấu hình cũ có thể làm hệ thống crash.
***Driver signing***
Windows x64 từ Vista bắt đầu thực thi yêu cầu chữ ký số đối với kernel driver. Điều này khiến việc load driver tùy ý khó hơn.
Tài liệu cũ đề cập tùy chọn:
```
nointegritychecks
```
để vô hiệu hóa kiểm tra chữ ký trong môi trường lab. Tuy nhiên, trên Windows hiện đại, cơ chế driver signing, Secure Boot, HVCI và các chính sách bảo vệ kernel đã thay đổi đáng kể, nên không nên xem hướng dẫn này là quy trình hiện hành.