# **1. Tổng quan kiến trúc Window**

a) **Tiến trình.**

$\color{green}{\text{Tiến trình}}$ là 1 đối tượng bao chứa và quản lí đại diện cho 1 phiên bản đang thực thi của chương trình. Vì vậy, khái niệm "tiến trình đang chạy" là không chính xác. Tiến trình không chạy, nó quản lí. Luồng là các thành phần thực thi code, hay chính là "chạy". Từ góc nhìn cấp cao, tiến trình gồm các phần sau:

- *1 chương trình thực thi:* chứa code ban đầu và dữ liệu để chạy code bên trong tiến trình.
- *1 không gian địa chỉ riêng tư:* sử dụng để cấp phát bộ nhớ khi mà code trong tiến trình cần.
- *1 access token:* là 1 đối tượng chứa ngữ cảnh bảo mật mặc định của tiến trình, được sử dụng bởi các luồng thực thi code trong tiến trình. Trừ khi 1 luồng sử dụng token khác  thông qua cơ chế mạo danh.
- *1 bảng handle riêng tư tới các đối tượng do khối executive trong kernel quản lí:* như là events, files...
- *1 hoặc nhiều luồng thực thi:* tiến tình user-mode bình thường được khởi tạo với 1 luồng (thực thi entry point chính). 1 tiến trình user-mode không có thread là 1 tiến trình vô dụng và trong các trường hợp thông thường, nó sẽ bị phá hủy bởi kernel.

Các yếu tố của tiến trình được biểu diễn trong hình _1.1_.

![[Pasted image 20260901212321.png]]

Tiến trình được định danh bằng $\color{green}{\text{Process ID}}$, nó độc nhất với mỗi tiến trình đang tồn tại. Một khi nó bị phá hủy, ID đó sẽ được sử dụng cho 1 tiến trình mới. Chú ý 1 điều rằng file thực thi không giúp định danh tiến trình. VD: có thể có nhiều tiến trình `notepad.exe` cùng chạy vào 1 thời điểm. 

Mỗi tiến trình có 1 không gian địa chỉ, các luồng xử lí, bảng handle, PID... riêng biệt. Tuy nhiên, 5 tiến trình trong ví dụ bên dưới đều sử dụng 1 file ảnh (`notepad.exe` trên đĩa) như là code và dữ liệu khởi tạo của chúng. Hình _1.2_ cho ta thấy 5 tiến trình notepad.exe, với mỗi thuộc tính riêng biệt của từng tiến trình.

![[Pasted image 20260901212824.png]]

b) **Thư viện liên kết động (DLLs).**

$\color{green}{\text{DLLs}}$ là các file thực thi có thể chứa code, dữ liệu và tài nguyên. DLLs được nạp động vào 1 tiến trình cả khi nó được khởi tạo (liên kết tĩnh) hoặc khi tiến trình yêu cầu (liên kết động). Chúng ta sẽ học kỹ hơn về DLLs ở chap15. 

Không giống các file thực thi thông thường, DLL không chứa hàm `main` tiêu chuẩn nên không chạy được trực tiếp. DLLs cho phép chia sẻ code trên bộ nhớ vật lí cho nhiều tiến trình dùng chung (đây là tiêu chuẩn của tất cả các Win DLLs lưu trong`System32`). 1 sô DLLs, được gọi là $\color{green}{\text{subsystem DLLs}}$ triển khai các hàm WinAPI công khai, sẽ được nói kỹ trong sách này.

Hình _1.3_ cho thấy 2 tiến trình sử dụng chung 1 DLLs được ánh xạ tại cùng 1 địa chỉ.

![[Pasted image 20260901215654.png]]

c) **Bộ nhớ ảo.**

(tự đọc).

d) **Luồng.**

$\color{green}{\text{Threads}}$ là các thực thể thực thi code. 1 thread được bao chứa bởi 1 tiến trình, sử dụng tài nguyên do tiến trình cung cấp để thực thi công việc (như là bộ nhớ ảo, handle...). Các thuộc tính quan trong mà thread có bao gồm:

- *Chế độ truy cập hiện tại*: kernel hay user.
- *Ngữ cảnh thực thi*: chứa các giá trị của thanh ghi.
- *Stack:* sử dụng để lưu trữ biến cục bộ và quản lí gọi hàm.
- *Thread Local Storage (TLS):* một mảng, cung cấp cách thức để lưu trữ các dữ liệu riêng tư của thread với các quy tắc truy cập nhất quán.
- *Mức ưu tiên cơ sở và mức ưu tiên hiện tại (ưu tiên động):* Liên quan đến cơ chế lập lịch, chưa học.
- *CPU affinity:* cho biết thread được phép chạy trên những bộ xử lí nào.

Các trạng thái phổ biến nhất của 1 luồng là:

- *Đang chạy:* đang được thực thi trong bộ xử lí.
- *Sẵn sàng:* chờ được lập lịch để chạy.
- *Chờ:* chờ 1 sự kiện nào đó xảy ra để tiếp tục chạy. Khi sự kiện xảy ra, chuyển sang $\color{green}{\text{sẵn sàng}}$.

e) **Kiến trúc cơ bản.**

Hình _1.4_ cho ta thấy kiến trúc cơ bản của Windows, bao gồm các thành phần user-mode và kernel-mode.

![[Pasted image 20260901222520.png]]

- *Tiến trình người dùng:* là các tiến trình bình thường dựa trên ảnh thực thi, thực thi trên hệ thống.
- *Subsystem DLLs:* là cá DLLs triển khai các API của 1 subsystem. Một subsystem là 1 góc nhìn cụ thể về những khả năng mà kernel cung cấp (kernel cung cấp các khả năng cốt lõi, subsystem tổ chức và trình bày các khả năng đó dưới 1 môi trường/API mà chương trình sử dụng). Về mặt kỹ thuật, từ Win 8.1, Win chỉ còn 1 subsystem duy nhất: Windows Subsystem. Các DLL subsystem bao gồm nhiều file quen thược như `kernel32.dll`, `user32.dll`... Phần lớn WinAPI được Microsoft công khai tài liệu nằm trong các DLL này. Cuốn sách này sẽ tập trung vào việc sử dụng các API do các DLL đó cung cấp.
- *NTDLL.DLL:* là 1 DLL toàn hệ thống, nó triển khai các WinAPI native. Đây là tầng thấp nhất của code mà vẫn đang nằm trong user-mode. Vai trò quan trọng nhất của nó là chuyển đổi sang kernel-mode để gọi các lời gọi hệ thống.NTDLL cũng đồng thời triển Heap Manager, Image Loader và 1 số phần của user-mode thread pool. Mặc dù các native API hầu hết không được tài liệu hóa chính thức, chúng ta vẫn sẽ sử dụng 1 số trong cuốn sách này khi mà các API chuẩn không giúp đạt được mục đích.
- *Tiến trình dịch vụ:* là các tiến trình bình thường, nhưng nó giao tiếp với Service Control Manager (SCM, triển khai trong `service.exe`) và cho phép điều khiển, kiểm soát tiến trình. SCM có thể bắt đầu, kết thúc, tạm dừng, tiếp tục, và gửi các thông điệp cho dịch vụ. Chap 19 sẽ nói kỹ hơn.
- *Executive:* là tầng cao của `NtOskrnl.exe` (kernel). Nó chứa hầu hết code chạy ở kernel mode. Nó bào gồm một số các "trình quản lí": quản lí đối tượng, quản lí bộ nhớ, quản lí I/O... Nó rộng hơn hẳn tầng kernel phía dưới.
- *Kernel:* triển khai những thành phần nền tảng và nhạy cảm về thời gian nhất của code hệ điều hành trong kernel mode. Nó đảm nhiệm việc lập lịch thread, điều phối interrupt và exception, đồng thời triển khai các primitive của kernel như mutex và semaphore. Một phần code của kernel được viết bằng mã máy dành riêng cho từng kiến trúc CPU.
- *Device drivers:* là các kernel module có thể nạp. Mã của chúng thực thi ở kernel mode nên có đầy đủ sức mạnh của kernel. Các trình điều khiển cổ điến kết nối phần cứng với hệ điều hành. 1 số loại khác lại cung cấp khả năng lọc (??). Muốn biết thêm thông tin thì đọc quyển "Windows Kernel Programming".
- *Win32k.sys:* là thành phần thuộc kernel mode của Win subsystem. Nó là kernel module (driver) xử lí giao diện người dùng và các API Graphic Device Interface (GDI). Điều này có nghĩa là tất cả các hoạt động cửa sổ đều được xử lí bởi thành phần này.
- *Hardware Abstraction Layer (HAL - lớp trừu tượng hóa phần cứng):* là lớp trừu tượng nằm trên phần cứng gần CPU nhất. Nó cho phép driver thiết bị sử dụng API mà không cần thông tin và kiến thức về xử lí ngắt hay điều khiển DMA. Lớp này rất hữu ích cho các driver thiết bị được viết để xử lí các thiết bị phần cứng.
- *Subsystem process:* Window subsystem process, chạy từ ảnh thực thi `Csrss.exe`, có thể xem như 1 trợ lí cho kernel trong việc quản lí các tiến trình bên dưới hệ điều hành window. Nó là tiến trình quan trọng, nghĩa là nếu nó bị tắt, hệ thống sẽ bị sập. Thường chỉ có 1 tiến trình `Csrss.exe` chạy tại cho 1 phiên, nên 1 hệ thống thông thường có 2 tiến trình, 1 cho phiên `0` và 1 cho phiên người dùng (`1`). Mặc dù `Csrss.exe` có vai trò quản lí Window subsystem, nó vẫn có những vai trò quan trọng khác.![[Pasted image 20260902200311.png]]
- *Hyper-V Hypervisor:* ....

# **2.  Phát triển ứng dụng Window.**

# **3. Làm việc với chuỗi.**

Trong C cổ điển, Strings không phải là 1 kiểu dữ liệu, nó là 1 con trỏ trỏ tới mảng các giá trị char kết thức bằng kí tự `\0`. Windows API sử dụng strings ở dạng này trong nhiều trường hợp, nhưng không phải tất cả. Câu hỏi về mã hóa xuất hiện khi giải quyết các vấn đề về chuỗi. Trong phần này, chúng ta sẽ tìm hiểu về strings và cách nó được sử dụng trong WinAPI.

Trong C cổ điển, chỉ có 1 các để biểu diễn các kí tự, đó là kiểu dữ liệu `char`. Các kí tự biểu diễn bởi `char` có kích thước 8 bit, với 7 bit đầu biểu diễn mã hóa ASCII. Hệ thống hiện nay hỗ trợ đa tập kí tự từ nhiều ngôn ngữ khác nhau, do đó 8 bit không còn đủ nữa. Vì thế, các chuẩn mã hóa mới đã ra đời, gọi chung là $\color{green}{\text{Unicode}}$.

Tổ chức Unicode định nghĩa 1 vài kiểu mã hóa kí tự. Dưới đây là 1 số kiểu phổ biến:

- *UTF - 8:* Chuẩn mã hóa phổ biến được sử dụng cho các trang web. Nó sử dụng 1 byte cho các kí tự Latin thuộc tập ASCII, và nhiều bytes hớn cho các ngôn ngữ khác.
- *UTF - 16:* sử dụng 2 bytes mỗi kí tự trong hầu hết trường hợp và biểu diễn tất cả các ngôn ngữ chỉ bằng 2 bytes. Một số kĩ tự đặc trưng hơn có thể yêu cầu 4 bytes, nhưng hiếm.
- *UTF - 32:* Sử dụng 4 bytes mỗi kí tự. Dễ dàng nhất để làm việc, nhưng cũng tốn kém nhất. 

UTF - 8 có kích thước tối ưu nhất, nhưng ở góc nhìn lập trình, nó là 1 vấn đề vì việc truy cập ngẫu nhiên không thể sử dụng (do kích thước các kí tự khác nhau nhiều, nên nếu chúng ta muốn truy cập đến 1 phần tử nằm giữa chuỗi, phải duyệt tuần tự chứ không thể xác định chính xác vị trí của nó được).

UTF - 16 tiện lợi hơn để làm việc với lập trình.

UTF - 32 quá lãng phí và ít khi được sử dụng.

May mắn rằng, Window sử dụng UTF - 16 bên trong kernel, nơi mỗi kí tự có kích thước chính xác 2 bytes. WinAPI cũng sử dụng UTF - 16, nên không cần chuyển đổi chuỗi khi API đi vào kernel.

a) **Strings trong C/C++ Runtime.**

 C/C++ Runtime có hai bộ hàm xử lý chuỗi. Bộ hàm truyền thống dành cho ASCII có tiền tố `str`, chẳng hạn `strlen`, `strcpy`, `strcat`... Bộ hàm dành cho Unicode có tiền tố `wcs`, chẳng hạn `wcslen`, `wcscpy`, `wcscat`...

Tương tự Windows API, C/C++ Runtime cung cấp một nhóm macro sẽ được mở rộng thành phiên bản ASCII hoặc Unicode tùy thuộc vào hằng số biên dịch `_UNICODE`. Các macro này có tiền tố `_tcs`, chẳng hạn `_tcslen`, `_tcscpy`, `_tcscat`... và đều làm việc với kiểu `TCHAR`.

Visual Studio mặc định định nghĩa `_UNICODE`, vì vậy các macro `_tcs` sẽ được mở rộng thành phiên bản Unicode.![[Pasted image 20260902204531.png]]

b) **Chuỗi tham số đầu ra.**

Truyền tham số chuỗi vào 

# **4. Phát triển 32-bit và 64-bit.**

# **5. Coding Conventions.**

# **6. Sử dụng C++.**

# **7. Xử lí lỗi API.**

WinAPI có thể bị lỗi vì nhiều lí do. Không may, cách báo lại thành công hay thất bại là không giống nhau với các hàm. Tuy nhiên, chỉ có một vài trường hợp, được tóm tắt ở bảng _1.3_

![[Pasted image 20260902210148.png]]

Trường hợp phổ biến nhất là trả về 1 kiểu `BOOL`. `BOOL` không giống với kiểu `bool`  trong c++, nó là 1 số nguyên có dấu 32 bit. 1 số khác không được trả về có nghĩa là thành công, còn nếu trả về 0 nghĩa là hàm đã fail. Cần chú ý không được kiểm tra thành công bằng cách test với giá trị `TRUE (1)`, vì giá trị trả về khi thành công có thể khác 1. Nếu hàm fail, mã lỗi có thể lấy được bằng cách dùng hàm `GetLastError`, nhiệm vụ của nó là lấy lỗi cuối cùng khi gọi 1 hàm API xảy ra trong luồng này. Nói cách khác, mỗi luồng có 1 last error riêng, điều này hoàn toàn hợp lí trong môi trường đa luồng như Win, nơi nhiều luồng có thể cùng lúc gọi các hàm API.

Dưới đây là 1 ví dụ về xử lỉ lỗi:
```cpp
BOOL success = ::CallSomeAPIThatReturnsBOOL();
if (!success){
	//error - handle it
	printf("error: %d\n", ::GetLastError());
}
```
Cách xử lí thứ 2 trong bảng _1.3_ dành cho các hàm trả về `void`. Có rất ít hàm kiểu này, và hầu như không thể fail. Không may, vẫn có 1 số hàm có thể fail trong 1 số trường hợp đặc biệt...

Tiếp, các hàm trả về `LSTATUS` hoặc `LONG`, cả 2 đều là số nguyên 32 bit có dấu. Các API phổ biến nhất sử dụng kiểu này là các hàm registry, sẽ được học ở chap 17. Các hàm này trả về `ERROR_SUCCESS (0)` nếu thành công. Ngược lại, nó trả về mã lỗi (`GetLastError` không cần thiết nữa).

Tiếp là loại trả về `HRESULT`, vẫn trả về 1 số nguyên có dấu 32 bit. Kiểu trả về này rất phổ biến với các hàm COM (chap 18). 1 số nguyên >= 0 nghĩa là thành công, còn âm là lỗi, được định danh bằng chính giá trị trả về. Trong hầu hết trường hợp, kiểm tra thành công hay fail được thực hiện bởi macros `SUCCEEDED` hoặc `FAILED`, nó trả về `true` hoặc `fail`. Chỉ có 1 số ít trường hợp cần phải kiểm tra mã lỗi.

Win header chứa 1 macro để chuyển 1 mã lỗi Win32 (`GetLastError`) thành `HRESULT`: `HRESULT_FROM_WIN32`, hữu ích khi 1 hàm COM cần trả về 1 lỗi theo kiểu API trả về `BOOL`

Đây là 1 ví dụ về xử lí 1 lỗi `HRESULT`:
```cpp
IGlobalInterfaceTable* pGit;
HRESULT hr = ::CoCreateInstance(CLSID_StdGlobalInterfaceTable, nullptr, CLSCTX_ALL,
IID_IGlobalInterfaceTable, (void**)&pGit);
if(FAILED(hr)) {
	printf("Error: %08X\n", hr);
}
else {
// do work
	pGit->Release(); // release interface pointer
}
```
Chỉ mục cuối cùng trong bảng _1.3_ là cho các hàm khác, VD, hàm `FormatMessage` chúng ta gặp ở phần trước trả về 1 `DWORD` chỉ ra số lượng kí tự đa được sao chép để buffer chỉ định, hoặc `0` nếu hàm fail...

a) **Định nghĩa custom error code.**

...

# **8. Phiên bản Window.**

# **9. Bài tập**

1. Viết 1 ứng dụng console in ra các thông tin về hệ thống, sử dụng các API sau: `GetNativeSystemInfo`, `GetComputerName`, `GetWindowsDirectory`, `QueryPerformanceCounter`, `GetProductInfo`, `GetComputerObjectName`.
