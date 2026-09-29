# **1. Kernel object.**

Win kernel cung cấp nhiều loại đối tượng khác nhau để các tiến trình user mode, bản thân kernel và các driver ở kernel mode sử dụng.

Mỗi đối tượng thuộc các loại này thực chất là 1 cấu trúc dữ liệu nằm trong không gian kernel. Chúng được Object Manager - một thành phần của Executive tạo và quản lí khi có yêu cầu từ code chạy ở user mode hoặc kernel mode.

Các đối tượng kernel được quản lí bằng số lượng tham chiếu. Vì vậy, một đối tượng bị hủy và vùng nhớ của nó mới được giải phóng khi tham chiếu cuối cùng tới đối tượng đó đã bị loại bỏ.

Có khá nhiều các loại đối tượng được Win kernel hỗ trợ. Để trực quan, chạy `WinObj` tool từ `Sysinternals` và tìm đến thư mục `ObjectTypes`. Hình _2.1_ cho ta thấy nó như thế nào. Các loại này có thể phân loại dựa trên mức độ công khai và cách sử dụng:![[Pasted image 20260903205556.png]]

- *Các loại được cung cấp cho user mode thông qua WinAPI.* VD: mutex, semaphore... Cuốn sách này sẽ thảo luận về 1 số đối tượng này.
- *Các loại không cung cấp cho user mode, nhưng được ghi chép tại Windows Driver Kit (WDK) để được sử dụng bởi các người viết driver thiết bị.* VD: device, driver, callback.
- *Các loại không được ghi chép lại trong WDK.* Các đối tượng loại này chỉ được dùng bởi kernel. VD: partition, keyed event...

Các thuộc tính chỉnh của đối tượng kernel được biểu diễn trong hình _2.2_.

![[Pasted image 20260903210509.png]]

Vì kernel object nằm trong kernel space, nó không thể được truy cập trực tiếp từ user mode. Các ứng dụng cần 1 cơ chế gián tiếp để truy cập các đối tượng kernel, gọi là handle. Handle cung cấp ít nhất 1 lợi ích:

- Bất kì thay đổi nào trong cấu trúc dữ liệu của đối tượng được window ra mắt trong tương lai không ảnh hưởng đến client.
- Truy cập đến object có thể được điều khiển thông qua kiểm tra quyền bảo mật.
- Handle là riêng tư với tiến trình, nên việc có 1 handle tới 1 đối tượng trong 1 tiến trình không mang cùng ý nghĩa trong ngữ cảnh của 1 tiến trình khác.

Các kernel object được quản lí bằng số lượng tham chiếu. Object Manager duy trì 2 bộ đếm:

- *Handle count:* số handle đang tham chiếu đến đối tượng.
- *Pointer count:* số con trỏ kernel đang tham chiếu trực tiếp tới đối tượng - các con trỏ trực tiếp này chỉ có thể lấy được từ kernel mode.

Tổng 2 bộ đếm trên chính là tổng số tham chiếu đến 1 đối tượng.

Khi 1 client ở user mode không cần sử dụng đối tượng nữa, code của client nên gọi `CloseHandle` để đóng handle được dùng để truy cập đối tượng. Từ thời điểm đó, code phải coi handler này là không hợp lệ.

Nếu cố truy cập tới đối tượng thông qua handle đã bị đóng, thao tác sẽ thất bại và `GetLastError` trả về `ERROR_INVALID_HANDLE` - mã lỗi `6`.

Nhìn chung, client không thể biết đối tượng đã thực sự bị hủy hay chưa, bởi vì những handle hoặc con trỏ khác vẫn có thể đang tham chiếu tới nó. Object Manager chỉ xóa đối tượng khi tổng tham chiếu của nó bằng `0`.

Giá trị handle hợp lệ là bội số của `4`, giá trị hợp lệ đầu tiên là `4`, `0` không bao giờ là 1 giá trị hợp lệ. Cơ chế không thay đổi trên hệ thống 64-bit.

![[Pasted image 20260903215217.png]]

Handle là 1 chỉ số của 1 phần tử trong handle table. Mỗi tiến trình có 1 handle table riêng, gồm 1 mảng các entry. Mỗi entry sẽ gián tiếp trỏ tới 1 kernel object nằm trong không gian hệ thống. 

Window cung cấp nhiều hàm `Create*` và `Open*` để tạo hoặc mở các đối tượng, sau đó trả về handle dùng để truy cập các đối tượng đó.

Nếu không thể tạo hoặc mở đối tường, trong phần lớn trường hợp sẽ trả về `NULL` để biểu thị thất bại. Một ngoại lệ là hàm `CreateFile`, nếu thất bại, hàm này trả về `INVALID_VALUE_HANDLE` (`-1`) thay vì `NULL`.

Ví dụ, hàm `CreateMutex` cho phép tạo 1 mutex mới hoặc mở 1 mutex theo tên (tùy thuộc việc mutex mang tên đó đã tồn tại hay chưa). Nếu thành công, hàm trả về 1 handle trỏ tới mutex đó. Giá trị trả về bằng `0` tương tứng với một handle không hợp lệ.

Ngược lại, hàm `OpenMutex` cố mở 1 handle tới 1 mutex đã có tên chỉ định. Nếu mutex mang tên đó không tồn tại, hàm sẽ thất bại.

Nếu hàm thành công và 1 tên định danh đã được cung cấp, handle trả về có thể thuộc về một mutex mới tạo hoặc thuộc về một mutex sẵn có mang tên đo. Chương trình có thể kiểm tra điều này bằng cách gọi `GetLastError` và so sánh kết quả với `ERROR_ALREADY_EXISTS`. Nếu đúng bằng mã này, nó không phải là 1 đối tượng mới, mà thực chất là 1 handle khác trỏ tới đối tượng đã tồn tại từ trước. Đây là 1 trong những trường hợp hiêm hoi là `GetLastError` có thể được gọi hữu ích ngay cả khi API liên quan đã thực thi thành công.

**a) Chạy 1 tiến trình duy nhất.**

Một ứng dụng khá phổ biến của trường hợp `ERROR_ALREADY_EXIST` là giới hạn 1 file thực thi chỉ có duy nhất một phiên bản tiến trình hoạt động tại 1 thời điểm. Thông thường, nếu nhấn đúp vào 1 file thực thi, một tiến trình mới sẽ được khởi tạo từ file đó.  Nếu lặp đi lặp lại thao tác này, một tiến trình khác lại tiếp tục được tạo ra từ cùng 1 file thực thi. Vậy làm sao để ngăn 1 tiến trình thứ 2 khởi chạy? Hoặc ít nhất là buộc nó tự đóng nếu phát hiện 1 phiên bản tiến trình khác của cùng 1 file thực thi nó đang chạy?

Bí quyết là sử dụng 1 named kernel object (có nhiều loại, nhưng mutex là phổ biến nhất), trong đó 1 đối tượng mang tên định danh cụ thể được tạo ra. Nếu đối tượng đó đã tồn tại từ trước, chác chắn đang có 1 instance khác đang chạy, do đó tiến trình mới có thể tự tắt (đồng thời dửi 1 thoogn báo cho phiên bản "anh em" đang chạy của nó biết điều này).

Demo `SingleInstace` minh hoạc cách thực hiện cơ chế này. Đây là 1 ứng dụng dạng hộp thoại được build bằng WTL. Hình _2.3_ minh họa giao diện của ứng dụng. Nếu thử khởi chạy thêm các phiên bản khác của ứng dụng, bạn sẽ tháy cửa sổ đầu tiên ghi log các thông điệp gửi đến từ tiến trình mới, và tiến trình mới này sau đó sẽ tự thoát.![[Pasted image 20260903233318.png]]

Trong hàm `WinMain`,  trước tiên chương trình tạo ra 1 mutex. Nếu thao tác này thất bại thì có nghĩa là đã xảy ra lỗi khá nghiêm trọng, vì vậy chương trình sẽ thoát.
```cpp
HANDLE hMutex = ::CreateMutex(nullptr, FALSE, L"SingleInstanceMutex");

if (!hMutex) {
	CString text;
	text.Format(L"Failed to create mutex (Error: %d)", ::GetLastError());
	::MessageBox(nullptr, text, L"Single Instance", MB_OK);
	return 0;
}
```
Việc không thể tạo mutex là trường hợp cực kì hiếm. Nguyên nhân có khả năng xảy ra nhất là một kernel object khác - không phải mutex - đã tồn tại với tên đó.

Sau khi nhận được 1 handle hợp lệ tới mutex, câu hỏi duy nhất còn lại là: mutex này vừa được tạo mới, hay chương trình chỉ nhận được 1 handle khác tới mutex đã tồn tại - có thể được tạo bới 1 instance trước đó của file thực thi này.
```cpp
if (::GetLastError() == ERROR_ALREADY_EXISTS) {
	NotifyOtherInstance();
	return 0;
}
```
Nếu object đã tồn tại trước khi `CreateMutex` được gọi, chương trình sẽ gọi 1 hàm hỗ trợ để gửi thông báo tới instance đang tồn tại, sao đó thoát. Dưới đây là hàm `NotifyOtherInstance`
```cpp
#define WM_NOTIFY_INSTANCE (WM_USER + 100)

void NotifyOtherInstance() {
    auto hWnd = ::FindWindow(
        nullptr,
        L"Single Instance"
    );

    if (!hWnd) {
        ::MessageBox(
            nullptr,
            L"Failed to locate other instance window",
            L"Single Instance",
            MB_OK
        );

        return;
    }

    ::PostMessage(
        hWnd,
        WM_NOTIFY_INSTANCE,
        ::GetCurrentProcessId(),
        0
    );

    ::ShowWindow(hWnd, SW_NORMAL);
    ::SetForegroundWindow(hWnd);
}
```
Hàm này sử dụng `FindWindow` để tìm cửa sổ instance đang tồn tại, tiêu chí sử dụng là tiêu đề cửa sổ `Single Instance`.

Cách tìm này không thực sự lí tưởng trong trường hợp tổng quát, vì một cửa sổ khác cũng có thể dùng cùng tiêu đề. Tuy nhiên, đổi với ví dụ này thì nó đã đủ dùng.

Sau khi tìm được cửa sổ, chương trình gửi tới cửa sổ đó một thông điệp tùy chỉnh bằng `PostMessage`. ID của tiến trình hiện tại, được lấy bằng `GetCurrentProcessId`, được truyền kèm theo thông điệp dưới dạng một đối số. PID này sau đó sẽ xuất hiện trong hộp danh sách của cửa sổ dialog.

Hai lệnh sau dùng để hiện và đưa cửa sổ của instance trước lên phía trước:
```cpp
::ShowWindow(hWnd, SW_NORMAL);
::SetForegroundWindow(hWnd);
```
Mảnh ghép cuối cùng là xử lý thông điệp `WM_NOTIFY_INSTANCE` tại cửa sổ dialog. Trong WTL, các thông điệp cửa sổ được ánh xạ tới những hàm xử lý bằng macro. Phần message map của lớp dialog `CMainDlg`, được định nghĩa trong `MainDlg.h`, được trình bày ở dưới.
```cpp
BEGIN_MSG_MAP(CMainDlg)
    MESSAGE_HANDLER(WM_NOTIFY_INSTANCE, OnNotifyInstance)
    MESSAGE_HANDLER(WM_INITDIALOG, OnInitDialog)
    COMMAND_ID_HANDLER(IDCANCEL, OnCancel)
END_MSG_MAP()
```
Thông điệp tùy chỉnh `WM_NOTIFY_INSTANCE` được ánh xạ tới hàm thành viên `OnNotifyInstance`, được triển khai như sau:
```cpp
LRESULT CMainDlg::OnNotifyInstance(
    UINT,
    WPARAM wParam,
    LPARAM,
    BOOL &
) {
    CString text;

    text.Format(
        L"Message from another instance (PID: %d)",
        wParam
    );

    AddText(text);
    return 0;
}
```
ID của tiến trình được lấy từ tham số `wParam`. Sau đó, một dòng văn bản chứa PID được thêm vào hộp danh sách bằng hàm hỗ trợ `AddText`:
```cpp
void CMainDlg::AddText(PCWSTR text) {
    CTime dt = CTime::GetCurrentTime();

    m_List.AddString(
        dt.Format(L"%T") + L": " + text
    );
}
```
Biến `m_List` có kiểu `CListBox`. Đây là lớp wrapper của WTL dành cho control list box của Windows.

Trong hàm `AddText`:

- `CTime::GetCurrentTime()` lấy thời gian hiện tại.
- `dt.Format(L"%T")` định dạng thời gian theo dạng `giờ:phút:giây`.
- Thời gian được nối với nội dung thông báo.
- `m_List.AddString(...)` thêm chuỗi hoàn chỉnh vào list box.

Ví dụ dòng được thêm vào sẽ có dạng:
```output
21:35:56: Message from another instance (PID: 15132)
```

# **2. Handle.**

