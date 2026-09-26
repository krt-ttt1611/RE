# **1. Các kỹ thuật phân tích tĩnh cơ bản.**
*a) Quét bằng các trình antivirus.*

*b) Định danh malware bằng hashing.*
Malware được băm bằng các cơ chế băm, để tạo ra 1 mã riêng biệt định danh cho nó.
==MD5== là hàm băm phổ biến nhất được sử dụng, ngoài ra còn có ==SHA-1==
Khi có mã băm, ta có thể search trên mạng để tìm được thông tin về mẫu mã độc đó.

*c) Tìm chuỗi.*

*d) Packed và obfuscated malware.*
Mã độc thưởng sử dụng các cơ chế pack (đóng gói) và obfus (làm rối) để khiến file khó nhận diện và phân tích hơn. 
obfus là chương trình mà tác giả mã độc đã cố gắng che giấu cách thức hoạt động của nó. pack là một dạng chương trình bị làm rối, trong đó mã độc được nén lại nên không thể được phân tích trực tiếp. Cả 2 kỹ thuật đều ngăn cản bạn phân tích tĩnh mã độc.
Các chương trình hợp pháp đều có nhiều chuỗi. Malware bị pack hoặc obfus chứa rất ít strings. nếu khi tìm kiếm chuỗi trong 1 chương trình mà phát hiện ra rất ít chuỗi, khả năng rất cao nó đã bị pack hoặc obfus, và rất có thể nó là malware. Để điều tra sâu hơn, ta cần các phương pháp khác ngoài phân tích tĩnh.

***Đóng gói file.***
Ta biết rằng, để 1 chương trình có thể chạy, nó bắt buộc phải được nạp lên RAM với đúng cấu trúc chuẩn mà hệ điều hành đã định nghĩa. Và với malware cũng vậy. Malware bị pack sẽ đi kèm với 1 đoạn mã giải nén nhỏ. Khi thực thi, nó có nhiệm vụ giải nén chương trình và nạp nó lên RAM.
![[Pasted image 20260907203702.png]]
***Nhận diện packer với PEiD.***
![[Pasted image 20260907203933.png]]
PEiD hiện tại đã không còn được cập nhật nữa, Chúng ta nên chuyển qua các phần mềm mới hơn, như DiE.

*e) PE file format.*

*f) Thư viện liên kết và hàm.*
Một trong những thông tin hữu ích nhất chúng ta có thể thu thập từ 1 file exe đó là danh sách các hàm mà nó nhập. Chúng là các hàm được chương trình sử dụng, nhưng lại được lưu giữ ở 1 file khác, như các thư viện mã chứa các hàm phổ biến với các chương trình. Các thư viện có thể kết nối tới chương trình thực thi chính thông qua việc ==liên kết==.
***Liên kết tĩnh, động và runtime.***
==Liên kết tĩnh:== liên kết lúc biên dịch.
==Liên kết động:== liên kết lúc nạp.
==Liên kết runtime:== nạp DLL và tìm địa chỉ hàm ngay trong khi chạy, thông qua 2 WinAPi chính:
- `LoadLibrary()`: nạp DLL vào không gian địa chỉ của tiến trình.
- `GetProcAddress()`: Tìm địa chỉ của hàm cần gọi trong DLL đó.
- Gọi hàm thông qua con trỏ hàm.
- Có thể dùng `FreeLibary` để giải phóng DLL.
Phần header của PE file chứa thông tin về tất cả các thư viện sẽ được nạp và tất cả các hàm được dụng trong chương trình (nếu chương tình liên kết động). Các thư viện được sử dụng và hàm được gọi là 1 phần quan trong khi phân tích 1 chương trình, nó cho ta đoán được hành vi của chương trình đấy. VD, nếu chương trình gọi hàm `URLDownloadToFile`, có thể đoán được chương trình kết nối đến internet để tải về các nội dung.
***Dùng Dependency Walker để phân tích các hàm liên kết động.***
Chú ý, Dependency Walker cũng là tool cũ, dùng bản thay thế là Dependencies, link: https://github.com/lucasg/Dependencies
![[Pasted image 20260907212331.png]]
Các DLL của 1 chương trình có thể tiết lộ nhiều thông tin về chức năng của nó. VD: Bảng _1.1_ liệt kê các tệp DLL phổ biến và thông tin mà chúng cung cấp về 1 ứng dụng.
![[Pasted image 20260907212648.png]]
***Các hàm xuất.***
Giống như hàm nhập, DLL và EXE cũng xuất ra các hàm để tương tác với chương trình và mã. Về cơ bản, 1 DLL triển khai 1 hoặc nhiều hàm và cho phép chúng được sử dụng bởi các chương trình khác.
PE file chứa thông tin về các hàm được exports. Bởi vì DLL được sinh ra để cung cấp các hàm cho EXE sử dụng nên exported function phổ biến trong DLL hơn. EXE không được thiết kế để cung cấp các hàm, nên sẽ hiếm hơn. Nếu tìm thấy exported function trong 1 file EXE, nó thường chứa nhiều thông tin hữu ích.

*g) Thực hành phân tích tĩnh.*
***PotentialKeylogger.exe: 1 file thực thi không bị pack.***
![[Pasted image 20260907213251.png]]
Hình _1.2_ cho ta thấy danh sách các hàm được import bởi file `PotentialKeylogger.exe`, được thu thập bằng Dependency Walker. Vì ta thấy danh sách có rất nhiều hàm import, ta có thể xác nhận rằng nó không bị pack.
Mặc dù hàm này có rất nhiều hàm import, chỉ có 1 số ít trong đó hữu ích cho việc phân tích. Trong suốt cuốn sách này, chúng ta sẽ đề cập đến các hàm import liên quan đến malware.
Khi không chắc chắn về hành vi của 1 hàm, ta có thể tra cứu trên MSDN.
Thông thường, chúng ta sẽ không biết mã độc này là 1 keylogger, và chúng ta sẽ cần tìm các hàm để có thể đi đến kết luận này.
Các hàm từ `Kernel32.dll` cho ta biết rằng phần mềm này có thể mở và thao tác với các tiến tình (các hàm như `OpenProcess`, `GetCurrentProcess`...) và file (`ReadFile`, `CreateFile`...). Hàm `FindFirstFile` và `FindNextFile` là các hàm thú vị, nó cho phép ta tìm kiếm file trong thư mục.
Các hàm của `User32.dll` còn thú vị hơn nữa, một số lượng lớn các hàm xử lí GUI cho thấy rằng chương trình này có GUI (mặc dù GUI không nhất thiết phải hiện lên cho người dùng xem).
Hàm `SetWindowsHookEx` thường được dùng trong spyware và nó chính là cách phổ biến nhất để keylogger ghi lại input của bàn phím. Hàm này có 1 số cách sử dụng hợp pháp, nhưng nếu xem 1 malware mà thấy hàm này, khả năng cao đây chính là 1 keylogger.
Hàm `RegisterHotKey` cũng rất thú vị. Nó tạo ra 1 hotkey (là 1 tổ hợp phím, như `CTRL-SHIFT-P`) để khi mà người dùng bấm tổ hợp phím này, 1 ứng dụng sẽ được kích hoạt. Không cần biết chương trình nào đang hoạt động, 1 hotkey sẽ đưa người dùng đến ứng dụng đó.
Các hàm từ `GDI32.dll` dùng để xử lí đồ họa, còn các hàm từ `Shell32.dll` cho biết chương trình này có thể khởi chạy chương trình khác.
Các hàm từ `Advapi32.dll` cho ta biết rằng chương trình này sử dụng registry. Chúng ta sẽ tìm kiếm các chuỗi trông như registry key. Chuỗi registry trông giống như 1 đường dẫn thư mục. Trong trường hợp này, chúng ta tìm thấy chuỗi `Software\Microsoft\Windows\CurrentVersion\Run`, là 1 registry key thường được dùng bởi malware, nó điều khiển những chương trình được tự động chạy khi window khởi động.
File thực thi này cũng có 1 vài hàm exports: `LowLevelKeyboardProc` và `LowLevelMouseProc`. Tài liệu của Microsoft nói rằng, "`LowLevelKeyboardProc` là 1 hàm callback do ứng dụng hoặc thư viện tự định nghĩa, sử dụng với hàm `SetWindowsHookEx`". Nói cách khác, hàm này sử dụng cùng `SetWindowsHookEx` để chỉ định hàm nào sẽ được gọi khi 1 sự kiện nhất định xảy ra, trong trường hợp này là sự kiện bàn phím cấp thấp. Tài liệu về `SetWindowsHookEx` giải thích thêm rằng hàm callback này sẽ được gọi khi 1 số sự kiện bàn phím cấp thấp nhất định xảy ra.
![[Pasted image 20260907223323.png]]
Sử dụng các thông tin lấy được từ việc phân tích tĩnh các hàm imports và exports, ta có đưa ra 1 số kết luận về malware này:
- Đầu tiên, nó có vẻ là 1 local kelogger sử dụng `SetWindowHookEX` để ghi lại bàn phím. 
- Chúng ta cũng có thể đoán rằng nó có 1 GUI, nhưng chỉ hiện thị cho 1 số người dùng nhất định, và nếu nhập đúng hot key thì nó với hiện lên. 
- Từ thông tin về Registry, ta cũng biết rằng nó tự khởi chạy mỗi khi hệ thống bật.
***PackedProgram.exe: Một ngõ cụt.***
![[Pasted image 20260907224220.png]]
Hình _1.3_ cho ta thấy 1 danh sách hoàn chỉnh của các hàm import của 1 malware không xác định. Sự ngắn gọn của danh sách này cho ta biết đây là 1 malware bị pack hoặc obfus, điều này còn được khẳng định rõ hơn khi check không có string nào trong chương trình. 1 chương trình Window không thể được tạo ra chỉ với một số hàm ít như vậy.
Việc biết malware bị pack là 1 thông tin hữu ích, nhưng chúng ta sẽ cần phải sử dụng các kỹ thuật khác để phân tích, như phân tích động hoặc unpacking.

*h) PE header và section.*
Phần header của file PE có thể cung cấp nhiều thông tin hơn đáng kể chứ không chỉ có các hàm import.
Định dạng file PE bao gồm một phần header, theo sau là một loạt các section. Header chứa siêu dữ liệu (metadata) mô tả bản thân file. Sau header là các section thực tế của file, mỗi section đều chứa những thông tin hữu ích.
Trong những phần tiếp theo của cuốn sách, chúng ta sẽ tiếp tục tìm hiểu các phương pháp xem và phân tích thông tin trong từng section này. Dưới đây là những section phổ biến và đáng chú ý nhất trong một file PE:
- `.text`:  Section `.text` chứa các chỉ thị mà CPU thực thi. Tất cả các section khác lưu trữ dữ liệu và những thông tin hỗ trợ. Thông thường, đây là section duy nhất có khả năng thực thi và cũng nên là section duy nhất chứa mã lệnh.
- `.rdata`:  Section `.rdata` thường chứa thông tin về các hàm import và export. Đây cũng chính là những thông tin có thể xem được bằng Dependency Walker và PEview. Section này còn có lưu trữ những dữ liệu chỉ đọc khác mà chương trình sử dụng. Đôi khi, một file sẽ có các section `.idata` và `.edata` riêng, dùng để lưu trữ thông tin import và export (xem hình _1.4_).
- `.data`:   Section `.data` chứa dữ liệu toàn cục của chương trình, tức là dữ liệu có thể được truy cập từ bất kỳ vị trí nào trong chương trình. Dữ liệu cục bộ không được lưu trong section này hay ở bất kỳ vị trí nào khác trong file PE. Chủ đề này sẽ được trình bày trong Chương 6.
- `.rsrc`: Section `.rsrc` chứa những tài nguyên được file thực thi sử dụng nhưng không được xem là một phần của mã thực thi, chẳng hạn như biểu tượng, hình ảnh, menu và chuỗi ký tự. Các chuỗi có thể được lưu trong section `.rsrc` hoặc trong phần chương trình chính, nhưng chúng thường được lưu trong `.rsrc` để hỗ trợ nhiều ngôn ngữ
![[Pasted image 20260907230444.png]]
Tên các section thường được đặt nhất quán đối với cùng một trình biên dịch, nhưng có thể khác nhau giữa các trình biên dịch. Ví dụ, Visual Studio sử dụng `.text` cho phần mã có thể thực thi, trong khi Borland Delphi lại sử dụng `CODE`.
Windows không quan tâm đến tên thực tế của section vì nó sử dụng những thông tin khác trong PE header để xác định section đó được dùng như thế nào. Ngoài ra, tên các section đôi khi còn bị làm rối nhằm khiến quá trình phân tích trở nên khó khăn hơn.
May mắn là trong phần lớn trường hợp, các tên mặc định vẫn được sử dụng. Hình _1.4_ liệt kê những tên section phổ biến nhất mà bạn sẽ gặp.

*Xem PE file bằng PEview.*
PEview lỗi thời rồi, xem bằng PE-bear, CFF explorer, Imhex..

*Xem Resource của file bằng Resource Hacker.*

# **2. Sử dụng máy ảo để phân tích mã độc.**

# **3. Các kỹ thuật phân tích động cơ bản.**
*a) Sandboxes: Cách tiếp cận nhanh và đơn giản.*
Rât nhiều các phần mềm tất cả trong một có thể sử dụng để thực hiện phân tích động cơ bản, và cái phổ biến nhất chính là sử dụng công nghệ ==sandbox==. Sanbox là 1 cơ chế bảo mật để chạy các ứng dụng không an toàn trong một môi trường an toàn mà không phải lo lắng về việc ảnh hưởng đến hệ thống bên ngoài. Sandbox bao gồm các môi trường ảo hóa, thường mô phỏng các dịch vụ mạng theo một cách nào đó để đảm bảo rằng phần mềm hoặc mã độc đang được kiểm thử có thể hoạt động bình thường.
***Sử dụng malware sandbox.***
Một số malware sandbox, như là Norman Sandbox, GFI Sandbox.... sẽ phần tích mã độc miễn phí. Hiện tại, Norman Sandbox và GFI Sandbox là nổi tiếng nhất đối với các chuyên gia bảo mật.
Các sandbox này chung cấp các thông tin đầu ra dễ hiểu, rất phù hợp cho việc phân tích, sàng lọc nhanh ban đầu.
Hầu hết các sandbox hoạt động giống nhau, nên ta sẽ chỉ tập trung vào 1 ví dụ, GFI Sandbox. Hình _3.1_ cho ta thấy bảng nội dùng của 1 file pdf report được tạo ra khi chạy 1 file trong GFI's Sanbox automated analysis. Malware report chứa rất nhiều thông tin về malware, như là hành vi mạng, các file nó tạo ra, kết quả khi quét trên virustotal...
![[Pasted image 20260912144527.png]]

***Hạn chế của Sandbox.***
Malware sandbox vẫn có 1 số điểm hạn chế nghiêm trọn. VD, sandbox đơn giản chỉ là chạy file thực thi, mà không có lựa chọn command-line. Nếu malware yêu cầu lựa chọn command-line, nó sẽ không thực thi bất kì code mà chỉ chạy khi 1 lựa chọn được cung cấp. Ngoài ra, nếu malware đang chờ 1 gói tin điều khiển trả về trước khi thực thi backdoor, backdoor sẽ không thể khởi chạy trong sandbox.
...

*b) Chạy malware.*
Các kỹ thuật phân tích động sẽ trở nên vô dụng nếu bạn không chạy malware. Ở đây chúng ta sẽ tập trung vào cách chạy các loại malware phổ biến mà bạn sẽ gặp (EXE và DLL). Mặc dù bạn sẽ thấy nó đơn giản để chạy malware bằng cách click vào nó hoặc chạy từ cmd, nó sẽ cần 1 chút kỹ thuật để chạy DLL malware vì Windows không biết cách làm sao để chạy nó tự động.
Hãy xem cách để chạy được DLLs trong phân tích động.
Chương trình `rundll32.exe` được thêm vào tất cả các phiên bản hiện đại của Windows. Nó cung cập 1 Container để chạy DLL bằng cách sử dụng lệnh sau.
```bash
C:\>rundll32.exe DLLname, Export arguments
```
![[Pasted image 20260912145533.png]]
Giá trị `Export` phải là 1 tên hàm hoặc ordinal number trong bảng exprorted function của DLL. Như bạn đã học ở Chap1, bạn có thể sử dụng các tool như PEview để xem. Ví dụ file `rip.dll` có 2 exports: `Install` và `Uninstall`.
`Install` có lẽ là cách để chạy `rip.dll`, nên ta sẽ chạy như sau.
```bash
C:\>rundll32.exe rip.dll, Install
```
Malware cũng có thể có các hàm được export bằng ordinal number. Trong trường hợp này, chúng ta có thể vẫn gọi được bằng cách dùng `#ordinal_number`
```bash
C:\>rundll32.exe xyzzy.dll, #5
```
Bởi vì các DLL độc hại thường chạy phần lớn code của nó ở `DLLMain` (còn được gọi là DLL entry point), và vì `DLLMain` được thực thi bất kể khi nào DLL được nạp, bạn có thể thu thập thông tin bằng cách ép DLL được nạp bằng cách chạy `rundll32.exe`. Ngoài ra, bạn cũng có thể biến DLL thành 1 file thực thi bằng cách sửa PE header và thay đổi phần mở rộng của nó để ép Windows nạp DLL như thể nó là 1 file thực thi.
Để chỉnh sửa PE header, hãy xóa cờ `IMAGE_FILE_DLL` (`0x2000`)  khỏi trường `Characteristics` trong `IMAGE_FILE_HEADER`. Sự thay đổi này không chạy bất kì hàm nào, nó sẽ chạy `DLLMain`, và nó có thể khiến malware bị crash hoặc sập. 
DLL malware có thể cần phải cài như là 1 dịch vụ, đôi khi có thể cài bằng hàm export như là `InstallService`, nằm trong `ipr32x.dll`.
```bash
C:\>rundll32 ipr32x.dll,InstallService ServiceName
C:\>net start ServiceName
```
Tham số `ServiceName` cần phải được cung cấp cho malware để nó có thể tải và chạy. Lệnh `net start` được sử dụng để khởi động 1 dịch vụ trên Windows.

*c) Giám sát bằng ProcMon*
ProcMon, là 1 công cụ giám sát nâng cao cho Windows, nó cung cấp 1 cách để giám sát registry, hệ thống file, mạng, tiến trình và luồng hoạt động. Nó là sự kết hơp và cải tiến của 2 công cụ: FileMon và RegMon.
Mặc dù procmon thu thập rất nhiều dữ liệu, nó không thể thu thập hết. Ví dụ, nó có thể mis mất hoạt động của device driver của 1 thành phần user-mode giao tiếp với rootkit thông qua I/O, cùng với các GUI call, như là `SetWindowsHookEx`. Mặc dù procmon có thể là 1 tool rất hữu dụng, nó thường không được dùng để ghi chép lại hoạt động network, vì nó không hoạt động ổn định trên các phiên bản Windows.
Procmon giám sát tất cả các syscall mà nó bắt được kể từ lúc nó bắt đầu chạy, Vì có nhiều syscall tồn tại trên Windows (có thể nhiều hơn 50000 mỗi phút), việc quan sát tất cả chúng gần như là không thể. Kết quả là, bởi vì procmon sử dụng RAM để log lại các event, nó có thể dẫn đến crash máy ảo vì sử dụng hết tất cả bộ nhớ. Để tránh việc này, chạy procmon trong 1 khoảng thời gian ngắn.
...

*d) Xem các tiến trình với Process Explorer.*
Process Explorer có thể dùng đế xem các tiến trình đang hoạt động, các DLL được load bởi 1 process, các thuộc tính của process, và thông tin tổng quan của hệ thống...
***Màn hình chính của PE***
![[Pasted image 20260912153226.png]]
***Sử dụng tùy chọn Verify.***
Một tính năng khác biệt và hữu ích của PE là nút ==Verify== ở tab ==Image==. Click vào nút này để verify xem liệu ảnh thực thi của nó ở đĩa thực sự là 1 file nhị phân có chữ kí số của Microsoft không. Vì Microsoft sử dụng chữ kí số cho phần lớn các file thực thi cốt lõi của mình, nên khi PE xác minh rằng chữ kí là hợp lệ, bạn có thể tin rằng file đó thực sụ là file cho MS phát hành.
Tính năng này đặc biệt hữu ích để kiểm tra xem file Windows trên đĩa có bị thay thể hay chỉnh sửa không, bởi malware thường thay thế các file hợp lệ bằng file của chính nó nhằm che dấu sự hiện diện.
Tuy nhiên, nó sẽ vô dung với các kỹ thuật sửa đổi mã trên tiến trình, vì khi này file nó không còn nằm trên đĩa nữa. VD, trong hình 3-6, tiến trình `svchost.exe` đã được xác minh là hợp lệ, nhưng thực tế tiến trình đang chạy lại là malware![[Pasted image 20260912153936.png]]

***So sánh chuỗi.***
Một cách để nhận ra 1 tiến trình đã bị thay thế là sử dụng ==Strings== tab ở trong ==Process Properties== để so sánh chuỗi chứa trong file trên đĩa và chuỗi trên bộ nhớ. Ví dụ, trong hình _3.7_ chuỗi `FAVORITES.DAT` xuất hiện nhiều lên ở trong bộ nhớ, nhưng không tìm thấy ở file thưc thi trên đĩa.
![[Pasted image 20260912154322.png]]
***Sử dụng Dependency Walker.***
PE cho phép ta chạy `depends.exe` trên 1 tiến trình đang chạy bằng cách click chuột phải vào tên tiến trình, và chon ==Launch Depends==. Nó cũng cho phép tìm kiếm handle hoặc DLL bằng cách chọn ==Find -> Find Handle or DLL==
Tùy chọn ==Find DLL== rất hữu ishc khi tìm thấy 1 DLL độc hại trên đĩa và muốn biết rằng tiến trình nào sử dụng nó. Ngoài ra, nếu muốn biến những DLL nào được nạp tại thời điểm chạy, ta có thể so sánh danh sách DLL trong PE so với bảng import của Dependency Walker.
***Phân tích tài liệu độc hại.***
Bạn cũng có thể sử dụng PE để phân tích các tài liệu độc hại, như là PDF và Word. Cách nhanh nhất để kiểm tra xem tài liệu đó có độc hại không đó là mở PE, và mở tài liệu đó lên, nếu tài liệu đó chạy tiến trình, bạn sẽ thấy tiên trình đó ở PE.

*e) So sánh Registrty Snapshots với Regshot.*
Regshot là 1 công cụ so sánh registry mã nguồn mở, cho phép chụp (take snapshot) và so sánh chúng.
Để sử dụng reg shot cho malware analysis, đầu tiên chụp lần đầu bằng cách click vào nút ==1st Shot==, sau đó chạy malware, rồi chụp lần 2. Cuối cùng, click vào nút ==compare== để so sánh.
Hình _3.1_ cho thấy 1 số kết tạo được tạo ra bởi regshot trong quá trình phân tích.![[Pasted image 20260912155814.png]]
Như bạn có thể thấy, malware tạo 1 giá trị vào `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run` như là 1 cơ chế duy trì sự tồn tại.

*f) Tạo mạng giả.*
Malware thường sẽ gửi tín hiệu beacon ra ngoài rồi cuối cùng thiết lập liên lạc với một máy chủ command-and-control (C2); chúng ta sẽ tìm hiểu kỹ hơn về vấn đề này trong Chương 14. Bạn có thể tạo một mạng giả lập và nhanh chóng thu thập được các chỉ dấu mạng (network indicators) mà không cần thực sự kết nối Internet. Những chỉ dấu này có thể bao gồm tên miền DNS, địa chỉ IP và chữ ký gói tin.
Để giả lập mạng thành công, bạn phải ngăn malware nhận ra rằng nó đang được thực thi trong một môi trường ảo hóa. (Xem Chương 2 để biết cách thiết lập mạng ảo bằng VMware.) Bằng cách kết hợp các công cụ được trình bày ở đây với một cấu hình mạng máy ảo hợp lý, bạn sẽ tăng đáng kể khả năng phân tích thành công.
***Sử dụng ApateDNS***
ApateDNS, 1 tool miễn phí của Mandiant, là các nhanh nhất để xem các DNS request được tạo bởi malware. ApateDNS làm giả phản hồi DNS để trả về 1 IP được người dùng chỉ định, bằng cách lẳng nghe trên cổng UDP 53 của máy cục bộ. 
Khi nhận được 1 yêu cầu DNS, nó sẽ phản hồi với 1 bản ghi DNS trỏ tới địa chỉ IP mà bạn đã cấu hình trước. Ngoài ra, ApateDNS còn có thể hiển thị nội dung của tất cả các yêu cầu mà nó nhận được dưới cả 2 dạng: hex và ascii.![[Pasted image 20260912161941.png]]
***Giám sát bằng Netcat.***
Netcat có thể được sử dụng cho cả kết nối đi vào (inbound) và kêt nối đi ra (outbound) để thực hiện nhiều tác vụ như quét cồng, tunneling, proxy, chuyển tiếp cổng và nhiều việc khác.
Ở chê độ listen, Netcat hoạt động như 1 server, còn ở chế độ connect, nó hoạt động như 1 client. Netcat lấy dữ liệu từ standard input (stdin) để truyền qua mạng. Toàn bộ dữ liệu mà nó nhận được sẽ được xuất ra màn hình thông qua stdout.
Bây giờ hãy xem cách mà ban có thể dùng Netcat đẻ phân tích malware `RShell` trong hình _3.9_. Bằng cách sử dụng ApateDNS, ta chuyển hướng truy vấn DNS dành cho `evil.malwa3.com` về máy cục bộ của mình. Giả sử malware kết nối ra ngoài qua cổng 80, thì trước khi thực thi malware, ta có thể dùng Netcat để lắng nghe các kết nối đến.
Malware thường dùng các cổng 80 hoặc 443 là ==http== hoặc ==https==, vì các cổng này không bị chặn hoặc giám sát chặt với kết nối outbound. Hình _3.2_ là 1 ví dụ.
![[Pasted image 20260912161954.png]]
`-l` nghĩa là listen, `-p` với số cổng dùng để chỉ định cổng để nghe. Malware kết nối tới Netcat vì chúng ta dùng ApateDNS để điều hướng. Như chúng ta thấy, RShell là reverse shell (là loại malware điều khiển máy nạn nhân để chủ động mở kết nối đến máy chủ tấn công), nhưng nó không cung cấp shell ngay. Kêt nối mạng đầu tiên xuất hiện như là 1 HTTP POST tới `www.google.com`, dữ liệu giả mà malware thêm vào để che giấu reverse shell thật, vì các người phân tích mạng thường nhìn vào đầu của 1 phiên kết nối.

*g) Chặn bắt gói tin với Wireshark.*

*h) Sử dụng INetSim.*
INetSim là 1 công cụ miễn p;hí để giả các dịch vụ mạng phổ biến. Cách dễ nhất để chạy INetSim nếu dùng hđh Win ddos là tải nó trên máy ảo linux, và setup nó vào cùng 1 mạng ảo với máy ảo chứa malware.
INetSim là tool free tốt nhất cung cấp việc giả mạo các dịch vụ, cho phép chúng ta phân tích hành vi mạng của các mẫu malware không xác định bằng cách mô phỏng các dịch vụ như HTTP, HTTPS, FTP, IRC, DNS... Hình _3.3_ liệt kê tất cả các dịch vụ mà INetSim mô phỏng mặc định.
![[Pasted image 20260912163358.png]]
INetSim làm hết mức có thể để trông giống như 1 server thật, và nó có các tính năng có thể chỉnh sửa dễ dang để đảm bảo thành công.
Một số tính năng tốt nhất của INetSim được xây dựng từ mô phỏng server HTTP và HTTPS. VD, INetSim có thể phục vụ gần như bât kì file request nào. VD, nếu malware yêu cầu 1 JPEG file, INetSim sẽ phản hồi lại 1 JPEG file hoàn chỉnh. Cho dù ảnh đó có thể không phải thứ malware tìm, server vẫn không trả về 404 hay lỗi, nhằm để malware tiếp tục chạy.
INetSim cũng ghi lại các request vào và kết nối, bạn sẽ thấy nó hữu ích khi xem xét xem malware có kết nối đến 1 dịch vụ chuẩn hay để xem request được tạo ra.....

